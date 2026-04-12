# TInputNumber 组件问题修复记录

> 模块路径：`src/tyto_ui_lib/components/atoms/inputnumber.py`
> QSS 模板：`src/tyto_ui_lib/styles/templates/inputnumber.qss.j2`
> 记录日期：2026-04-10

---

## 1. Loading 状态下 QEasingCurve 未定义

**问题描述**

设置 `loading=True` 时抛出 `NameError: name 'QEasingCurve' is not defined`。

**根因分析**

`_SpinnerWidget.__init__` 中局部导入了 `QPropertyAnimation`，但遗漏了同属 `PySide6.QtCore` 的 `QEasingCurve`。

**修复方案**

将局部导入补全：

```python
# 修复前
from PySide6.QtCore import QPropertyAnimation

# 修复后
from PySide6.QtCore import QEasingCurve, QPropertyAnimation
```

**涉及文件**

- `inputnumber.py` — `_SpinnerWidget.__init__`

---

## 2. 按钮与输入框交界处出现多余边框

**问题描述**

"right" 布局模式下，`-` 和 `+` 按钮之间、按钮与输入框之间出现了不应有的 1px 边框线。

**根因分析**

QSS 模板中 `buttonPlacement="right"` 规则为两个按钮都设置了 `border-left`，产生了内部分隔线。外部边框已由 `paintEvent` 绘制，内部按钮不需要任何边框。

**修复方案**

将所有布局模式下的按钮边框统一设为 `border: none`：

```css
/* right 模式 */
TInputNumber[buttonPlacement="right"] QToolButton#btn_minus { border: none; }
TInputNumber[buttonPlacement="right"] QToolButton#btn_plus  { border: none; }

/* both 模式 */
TInputNumber[buttonPlacement="both"] QToolButton#btn_minus { border: none; }
TInputNumber[buttonPlacement="both"] QToolButton#btn_plus  { border: none; }
```

**涉及文件**

- `inputnumber.qss.j2` — button placement 规则段

---

## 3. Loading 图标位置偏移

**问题描述**

Spinner 图标显示在输入框左上角 (0,0) 位置，而非右侧垂直居中。

**根因分析**

`_SpinnerWidget` 作为 `QLineEdit` 的子控件创建后，未设置任何定位逻辑，默认停留在父控件原点。

**修复方案**

1. 新增 `_position_spinner()` 方法，将 Spinner 定位到 QLineEdit 右侧垂直居中。
2. 在 `_setup_spinner()` 末尾调用 `_position_spinner()`。
3. 新增 `resizeEvent` 重写，确保窗口尺寸变化时重新定位。

**涉及文件**

- `inputnumber.py` — `_position_spinner`、`_setup_spinner`、`resizeEvent`

---

## 4. Tiny/Small 尺寸下内容未垂直居中

**问题描述**

当 `size` 设为 `tiny` 或 `small` 时，输入框、按钮、加载图标在控件中偏上显示。

**根因分析**

QSS 中外层 `TInputNumber` 仅设置了 `max-height`，缺少 `min-height`。当父布局分配了更大空间时，控件被拉伸，子控件无法居中。

**修复方案**

为所有四个尺寸变体同时设置 `min-height` 和 `max-height`：

```css
TInputNumber[inputNumberSize="tiny"] {
    min-height: {{ component_sizes.tiny.height }}px;
    max-height: {{ component_sizes.tiny.height }}px;
}
/* small / medium / large 同理 */
```

**涉及文件**

- `inputnumber.qss.j2` — 四个尺寸段

---

## 5. 设置 Size 属性后不实时渲染

**问题描述**

通过 `set_size()` 切换尺寸后，界面不更新，需切换主题才生效。

**根因分析**

`set_size()` 仅调用 `_repolish()`，该方法只重新评估已有 QSS 的属性选择器，但不会重新渲染 Jinja2 模板。子控件的尺寸约束未被刷新。

**修复方案**

将 `_repolish()` 替换为完整的主题重新应用流程：

```python
def set_size(self, size: InputNumberSize) -> None:
    self._size = size
    self.setProperty("inputNumberSize", size.value)
    self.apply_theme()        # 重新渲染 QSS
    self.updateGeometry()     # 触发布局重算
    self._position_spinner()  # 重定位 Spinner
```

**涉及文件**

- `inputnumber.py` — `set_size`

---

## 6. Clearable 清空按钮显示异常

**问题描述**

清空按钮（✕）显示模糊、位置偏移、颜色与其他按钮不一致。同时设置 `clearable` 和 `loading` 时两个图标重叠。

**根因分析**

1. 清空按钮使用 `QAction.setText("✕")` 渲染为纯文本，无法控制大小和颜色。
2. QSS 中 `QToolButton` 的尺寸约束同时作用于 QLineEdit 内部的 action 按钮，导致其被撑出边界。
3. Loading 状态未隐藏清空按钮。

**修复方案**

1. 新增 `_text_icon()` 辅助函数，将 Unicode 字符渲染为 `QIcon`（20×20 像素）。
2. 清空按钮改用 `setIcon(_text_icon(...))` 替代 `setText()`。
3. 新增 `_current_icon_color()` 方法，使用 `text_primary` 颜色（与 `-`/`+` 按钮一致）。
4. QSS 中使用 `>` 直接子选择器区分外层按钮和 QLineEdit 内部 action 按钮。
5. 尺寸约束仅作用于 `#btn_minus` 和 `#btn_plus`。
6. `set_loading()` 中隐藏清空按钮；`_update_clear_visibility()` 增加 `not self._loading` 条件。
7. `apply_theme()` 中使用 `hasattr` 防护初始化顺序问题。

**涉及文件**

- `inputnumber.py` — `_text_icon`、`_current_icon_color`、`set_loading`、`_update_clear_visibility`、`apply_theme`
- `inputnumber.qss.j2` — 按钮选择器、尺寸段

---

## 7. 按钮与图标间距优化

**问题描述**

清空按钮、`-`/`+` 按钮、加载图标之间的间距过大，视觉不够紧凑。

**修复方案**

| 调整项 | 修改前 | 修改后 |
|--------|--------|--------|
| 布局间距 | `setSpacing(0)` | `setSpacing(2)` |
| 按钮宽度 | `height`（正方形） | `icon_size`（仅图标宽度） |
| 按钮字号 | `font_size` | `icon_size`（更大图标） |
| QLineEdit padding | `0 spacing.small` | 仅 `padding-left` |
| Action 按钮 padding | `2px` | `0px` |
| Spinner margin | `4px` | `2px` |
| 布局左右 margin | `1px` | `6px` |

**涉及文件**

- `inputnumber.py` — 布局初始化、`_position_spinner`
- `inputnumber.qss.j2` — 按钮宽度、字号、padding 规则
