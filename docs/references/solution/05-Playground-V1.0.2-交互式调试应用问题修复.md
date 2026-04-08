# BUG-005：Playground V1.0.2 交互式调试应用问题修复

| 属性 | 值 |
|------|-----|
| 版本 | V1.0.2 |
| 严重程度 | 中-高 |
| 影响组件 | `TButton`、`TInput`、`TCheckbox`、`TRadio`、`TSwitch`、`TTag`、Playground 全局 |
| 涉及文件 | `examples/playground/definitions/*.py`、`examples/playground/views/*.py`、`src/tyto_ui_lib/components/atoms/button.py`、`src/tyto_ui_lib/components/atoms/input.py`、`src/tyto_ui_lib/styles/templates/button.qss.j2` |
| 修复日期 | 2026-04-08 |

---

## 1. 问题概述

Playground 交互式调试应用在验证阶段发现多类问题，涵盖启动失败、属性面板交互无效、组件渲染异常、Dark 模式图标颜色错误等。本文档按问题类别分组记录根因分析与解决方案。

---

## 2. 启动与基础架构问题

### 2.1 Playground 无法启动（ModuleNotFoundError）

**现象：** 运行 `uv run python examples/playground.py` 报错 `ModuleNotFoundError: No module named 'examples'`。

**根因：** `examples/` 目录缺少 `__init__.py`，无法作为 Python 包被导入。入口脚本使用 `from examples.playground import main`，但 `examples` 不在 `sys.path` 上。

**修复：**
1. 创建 `examples/__init__.py`
2. 在 `examples/playground.py` 和 `examples/gallery.py` 中添加项目根目录到 `sys.path`：

```python
import sys
from pathlib import Path
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
```

---

## 3. 属性面板 str 枚举序列化问题

### 3.1 枚举属性切换崩溃（AttributeError）

**现象：** 切换 Button 的 Type 或 Size 属性时抛出 `AttributeError: 'str' object has no attribute 'value'`，随后触发 `QBackingStore::endPaint()` 错误。

**根因：** PySide6 的 `QComboBox.addItem(label, userData)` 在存储 `str` 枚举成员时，将其序列化为普通字符串。`combo.itemData(index)` 返回 `"medium"` 而非 `ButtonSize.MEDIUM`。apply 回调中调用 `v.value` 时失败。

**修复：**
1. `_enum_options` 存储 `m.value`（字符串）而非 `m`（枚举成员）作为 item data
2. 添加 `_to_enum()` 辅助函数，在 apply 回调中将字符串转回枚举成员
3. 对于直接操作内部属性的回调（如 `button_type`、`tag_type`），使用命名函数替代 lambda

```python
def _to_enum(enum_cls, v):
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)
```

**影响范围：** `button_props.py`、`input_props.py`、`checkbox_props.py`、`radio_props.py`、`switch_props.py`、`tag_props.py`

---

## 4. Button 组件渲染问题

### 4.1 Round 按钮出现双层背景

**现象：** 设置 `round=True` 后，按钮内部出现一个较小的矩形背景层，与外部圆角形状不匹配。

**根因：** `paintEvent` 自定义绘制了圆角背景，但 QSS 也同时绘制了自己的 `background-color` 和 `border`。两层叠加导致视觉异常。

**修复：** 在 `button.qss.j2` 中为 `round="true"` 和 `circle="true"` 添加 `background-color: transparent; border: none`。

### 4.2 Round 按钮 Hover 时变为方形

**现象：** Round 按钮在鼠标悬停时显示为方形彩色背景。

**根因：** QSS 的 `:hover` 伪状态规则（如 `TButton[buttonType="info"]:hover`）具有更高的选择器特异性（2 属性 + 1 伪类），覆盖了 `TButton[round="true"]` 的 `transparent` 规则（1 属性）。

**修复：** 使用双属性选择器提升特异性：

```css
TButton[round="true"][round="true"],
TButton[round="true"][round="true"]:hover,
TButton[round="true"][round="true"]:pressed,
TButton[round="true"][round="true"]:disabled {
    background-color: transparent;
    border: none;
}
```

### 4.3 按钮文本缺少左右内边距

**现象：** 输入较长文本后，文字紧贴按钮边框，无水平间距。

**根因：** `_apply_circle_geometry` 的 `else` 分支中，`_apply_size_from_tokens()` 设置了正确的 padding，但紧接着 `setContentsMargins(0, 0, 0, 0)` 将其覆盖。

**修复：**
1. `_apply_size_from_tokens` 从 Token 的 `component_sizes.padding_h` 读取水平内边距
2. 移除 `_apply_circle_geometry` 中多余的 `setContentsMargins(0, 0, 0, 0)` 调用

### 4.4 自定义 Color 与 Round 模式冲突

**现象：** 同时设置 `round=True` 和自定义 `color` 后，圆角效果失效。

**根因：** `_apply_custom_colors` 通过 per-widget `setStyleSheet` 设置 `background-color`，该内联样式优先级高于全局 QSS 的 `transparent` 规则。

**修复：**
1. `_apply_custom_colors` 检测 round/circle 状态，跳过 `background-color`/`border-color` 的 QSS 设置
2. `paintEvent` 新增 `self._color` 检查，使用自定义颜色作为圆角背景填充色
3. `set_round`/`set_circle` 在状态变更后重新调用 `_apply_custom_colors`

### 4.5 自定义 Color/TextColor 设置不生效

**现象：** 在属性面板中设置 color 和 text_color 无视觉变化。

**根因：** `set_color`/`set_text_color` 仅设置 QSS 动态属性 `customColor`/`customTextColor`，但 QSS 模板中无对应选择器规则。

**修复：** 改为通过 per-widget inline stylesheet 直接设置 `background-color`、`border-color`、`color`。

---

## 5. Input 组件问题

### 5.1 Clearable 取消勾选后清空按钮仍显示

**现象：** 取消 clearable 后输入文本，清空按钮重新出现。

**根因：** `_on_text_changed` 中 `self._clear_action.setVisible(bool(text))` 未检查 `self._clearable` 标志。

**修复：** 改为 `self._clear_action.setVisible(bool(text) and self._clearable)`。

### 5.2 Textarea 模式切换后属性不生效

**现象：** 切换到 textarea 后，placeholder、maxlength、show_count 等属性设置无效。

**根因：** `_apply_input_type` 通过遍历 widget 树查找 `ComponentPreview` 来更新 `_current_widget` 引用，但 `QScrollArea` 的 viewport 层级导致查找失败。

**修复：** 在 `ComponentPreview.show_component` 中存储反向引用 `widget._preview_owner = self`，`_apply_input_type` 通过 `getattr(w, "_preview_owner")` 直接更新引用。

### 5.3 Show Count 动态切换不生效

**现象：** 勾选 show_count 后无字数统计显示。

**根因：** `_count_label` 仅在构造时 `show_count=True` 时创建，运行时切换时为 `None`。

**修复：** `_apply_show_count` 在 `_count_label` 为 `None` 时动态创建 QLabel。

### 5.4 Loading 图标位置错误与重叠

**现象：** Loading spinner 显示在输入框外部；同时启用多个 trailing action 时图标重叠。

**修复：**
1. Spinner 作为 QLineEdit 子 widget，定位到右侧 trailing 区域
2. Loading 激活时隐藏 clear/password 按钮；结束时恢复

### 5.5 Dark 模式图标颜色错误

**现象：** Dark 模式下所有 trailing 图标显示为黑色。

**根因链：**

| 层级 | 问题 |
|------|------|
| Token 值 | `text_secondary` = `rgba(255, 255, 255, 0.50)` |
| QColor 解析 | `QColor("rgba(...)")` → **无效** → 默认黑色 |
| SVG 渲染 | `fill`/`stroke` 不支持 CSS `rgba()` |

**修复：** 添加 `_parse_color()` 和 `_to_svg_color()` 函数处理 rgba 格式。

### 5.6 密码切换图标不符合 NaiveUI 风格

**修复：** Unicode 圆点（●/○）替换为 SVG 眼睛图标。

---

## 6. 属性面板缺失 apply 回调

| 组件 | 属性 | 问题 | 修复 |
|------|------|------|------|
| TCheckbox | label | 修改无效 | `w._label.setText(str(v))` |
| TRadio | label | 修改无效 | `w._label.setText(str(v))` |
| TTag | closable | 勾选无效 | 动态创建/显示/隐藏关闭按钮 |
| TTag | checkable | 勾选无效 | 切换 checkable 模式和 QSS 属性 |
| TSwitch | checked_text / unchecked_text | 显示但无法生效 | 移除属性定义 |
| TInput | password | 勾选无效 | `setEchoMode` 切换 |
| TInput | maxlength | 设置无效 | `setMaxLength` 调用 |

---

## 7. 属性面板 UX 增强

### 7.1 颜色属性改为颜色选择器

QPushButton + QColorDialog，点击弹出系统颜色选择器，附带 "×" 清除按钮。

### 7.2 新增图标文件选择器

新增 `file` 属性类型，QPushButton + QFileDialog 选择本地图标文件，显示缩略图预览。

---

## 8. 修改文件汇总

| 文件 | 修改内容 |
|------|----------|
| `examples/__init__.py` | 新建，使 examples 可作为包导入 |
| `examples/playground.py` | 添加 sys.path 修复 |
| `examples/gallery.py` | 添加 sys.path 修复 |
| `examples/playground/views/property_panel.py` | 新增颜色选择器、文件选择器 |
| `examples/playground/views/component_preview.py` | 添加 `_preview_owner` 反向引用 |
| `examples/playground/definitions/button_props.py` | 枚举修复、icon 属性、自定义颜色 |
| `examples/playground/definitions/input_props.py` | 枚举修复、textarea/password/clearable/maxlength/show_count |
| `examples/playground/definitions/checkbox_props.py` | 枚举修复、label apply |
| `examples/playground/definitions/radio_props.py` | 枚举修复、label apply |
| `examples/playground/definitions/switch_props.py` | 枚举修复、移除无效属性 |
| `examples/playground/definitions/tag_props.py` | 枚举修复、closable/checkable apply |
| `src/.../button.py` | Round/Circle 渲染、自定义颜色兼容、水平 padding |
| `src/.../input.py` | clearable 检查、`_parse_color`、SVG 图标、Loading 位置 |
| `styles/templates/button.qss.j2` | Round/Circle 透明背景、双属性选择器 |

---

## 9. 验证

```bash
uv run pytest tests/ -x -q
# 174 passed
```

---

## 10. 经验总结

> **规则 1：** PySide6 的 `QComboBox.itemData()` 会将 `str` 枚举成员序列化为普通字符串。存储时应使用 `.value`，取出时通过 `EnumClass(value)` 重建。

> **规则 2：** `QColor` 不支持 CSS `rgba()` 格式。Token 值为 `rgba()` 时必须手动解析。SVG `fill`/`stroke` 同样不支持，需转为 `rgb(r,g,b)`。

> **规则 3：** 组件同时使用 QSS 和自定义 `paintEvent` 时，QSS 层必须设置 `background-color: transparent`，否则双层渲染。特异性需通过双属性选择器提升。

> **规则 4：** Playground 中切换构造参数（如 input_type）需销毁旧 widget + 创建新 widget，通过反向引用更新 `_current_widget`。
