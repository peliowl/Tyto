# TMenu Dark 模式视觉缺陷 — 问题与解决方案记录

> **组件**: `TMenu` / `_CollapseToggleButton` / `_MenuArrowWidget` / `TTimeline`
> **文件**: `src/tyto_ui_lib/components/organisms/menu.py`, `src/tyto_ui_lib/components/molecules/timeline.py`
> **关联 Spec**: `.kiro/specs/menu-collapse-toggle/`
> **日期**: 2026-04-12

---

## 目录

1. [问题总览](#1-问题总览)
2. [根因分析：QColor 不支持 CSS rgba() 小数 alpha](#2-根因分析qcolor-不支持-css-rgba-小数-alpha)
3. [影响范围评估](#3-影响范围评估)
4. [解决方案](#4-解决方案)
5. [附带修复：收缩按钮 Hover 效果移除](#5-附带修复收缩按钮-hover-效果移除)
6. [附带修复：子菜单 Popup 主题切换](#6-附带修复子菜单-popup-主题切换)
7. [附带修复：TMenu 背景色与容器区分](#7-附带修复tmenu-背景色与容器区分)
8. [排查过程中的无效方案记录](#8-排查过程中的无效方案记录)
9. [修改文件清单](#9-修改文件清单)
10. [经验总结](#10-经验总结)

---

## 1. 问题总览

在 Dark 模式下，TMenu 组件存在以下视觉缺陷：

| 序号 | 现象 | 严重程度 |
|------|------|----------|
| 1 | `_MenuArrowWidget`（展开/收缩箭头 ∨）在深色背景上几乎不可见 | 高 |
| 2 | `_CollapseToggleButton`（边栏收缩按钮）的边框和图标在深色背景上几乎不可见 | 高 |
| 3 | TMenu 背景色与 Playground 容器背景色相同，无法区分 | 中 |
| 4 | 子菜单 Popup 面板在主题切换后颜色不更新 | 中 |
| 5 | 收缩按钮存在不必要的 Hover 效果 | 低 |

---

## 2. 根因分析：QColor 不支持 CSS rgba() 小数 alpha

### 核心问题

Qt 的 `QColor(string)` 构造函数**不支持** CSS `rgba(r, g, b, alpha_float)` 格式中的小数 alpha 值。

### 复现

```python
from PySide6.QtGui import QColor

c = QColor("rgba(255, 255, 255, 0.82)")
print(c.isValid())  # False
print(c.red(), c.green(), c.blue())  # 0, 0, 0 — 纯黑色
```

### 影响链路

Dark 主题的 Design Token 中大量使用 `rgba()` 格式：

```json
{
  "text_primary": "rgba(255, 255, 255, 0.82)",
  "text_secondary": "rgba(255, 255, 255, 0.52)",
  "text_disabled": "rgba(255, 255, 255, 0.38)",
  "border": "rgba(255, 255, 255, 0.24)",
  "hover_color": "rgba(255, 255, 255, 0.09)",
  "divider": "rgba(255, 255, 255, 0.09)"
}
```

当 QPainter 自绘控件通过 `QColor(token_string)` 解析这些值时，得到的是无效颜色（回退为纯黑 `#000000`），导致图标、边框等元素在深色背景上完全不可见。

### 为什么 QSS 不受影响

Qt 的 QSS 解析器有独立的颜色解析逻辑，能正确处理 `rgba()` 中的小数 alpha。因此通过 QSS 模板（`.qss.j2`）设置的颜色不受此问题影响。只有在 Python 代码中直接使用 `QColor(string)` 构造函数的场景才会触发。

---

## 3. 影响范围评估

### 排查方法

在 `src/tyto_ui_lib/components/` 目录下搜索所有 `QColor(变量)` 调用，筛选出接收 token 字符串（可能为 `rgba()` 格式）的位置。

### 排查结果

| 文件 | 状态 | 说明 |
|------|------|------|
| `organisms/menu.py` — `_MenuArrowWidget` | **需修复** | `QColor(self._icon_color)` |
| `organisms/menu.py` — `_CollapseToggleButton` | **需修复** | `QColor(self._bg_color)` 等 |
| `organisms/menu.py` — `TMenu.paintEvent` | **需修复** | `QColor(self._menu_bg_color)` |
| `molecules/timeline.py` | **需修复** | `QColor(upper.get_resolved_color())` |
| `atoms/button.py` | 已安全 | 已使用 `parse_color()` |
| `atoms/radio.py` | 已安全 | 已使用 `parse_color()` |
| `atoms/checkbox.py` | 已安全 | 已使用 `parse_color()` |
| `atoms/spin.py` | 已安全 | `QColor(color)` 中 `color` 是 QColor 对象（拷贝构造） |
| `atoms/backtop.py` | 已安全 | 已使用 `parse_color()` |
| `atoms/switch.py` | 已安全 | 已使用 `parse_color()` |
| `atoms/input.py` | 已安全 | 有独立的 `_parse_color()` 处理 rgba |
| `atoms/inputnumber.py` | 已安全 | 已使用 `parse_color()` |
| `molecules/popconfirm.py` | 已安全 | 仅在 fallback 中使用硬编码 hex |
| `molecules/alert.py` | 已安全 | 仅在 fallback 中使用硬编码 hex |

---

## 4. 解决方案

### 方案：使用 `parse_color()` 替代 `QColor()`

项目已有 `tyto_ui_lib.utils.color.parse_color()` 工具函数，能正确解析 CSS `rgba()` 格式：

```python
# tyto_ui_lib/utils/color.py
def parse_color(value: str, fallback: str = "#000000") -> QColor:
    """Supports hex, named colors, and rgba(r, g, b, alpha_float)."""
```

### 修复内容

#### 4.1 `menu.py` — 添加 import

```python
from tyto_ui_lib.utils.color import parse_color
```

#### 4.2 `_MenuArrowWidget.paintEvent`

```python
# Before:  color = QColor(self._icon_color)
# After:   color = parse_color(self._icon_color)
```

#### 4.3 `_CollapseToggleButton.paintEvent`

```python
# Before:  bg = QColor(self._bg_color)
# After:   bg = parse_color(self._bg_color)
# （border_color、icon_color 同理）
```

#### 4.4 `TMenu.paintEvent`

```python
# Before:  painter.fillRect(self.rect(), QColor(bg))
# After:   painter.fillRect(self.rect(), parse_color(bg))
```

#### 4.5 `timeline.py`

```python
from tyto_ui_lib.utils.color import parse_color

# Before:  line_color = QColor(upper.get_resolved_color())
# After:   line_color = parse_color(upper.get_resolved_color())
```

---

## 5. 附带修复：收缩按钮 Hover 效果移除

### 问题

`_CollapseToggleButton` 的 `enterEvent`/`leaveEvent` 切换 `_hovered` 状态并触发重绘，产生不必要的 hover 背景色变化。

### 解决方案

- 移除 `_hovered` 状态字段和 `_hover_bg_color` token
- `enterEvent`/`leaveEvent` 不再修改状态或触发 `update()`
- `paintEvent` 中移除 hover 背景色判断
- 移除 `setMouseTracking(True)`
- 更新测试 `test_hover_state_no_effect`

---

## 6. 附带修复：子菜单 Popup 主题切换

### 问题

`TMenuItemGroup` 的 popup 是顶层窗口（`Qt.WindowType.Tool`），不在 TMenu 的 QSS 继承链中。主题切换时 popup 的 QSS 不会自动更新。

### 解决方案

1. `TMenuItemGroup.apply_theme` 中检查 popup 是否存在，存在则重新渲染 `menu.qss.j2` 并 `setStyleSheet`
2. `_show_popup` 中每次显示时重新应用 QSS 并对子项调用 `apply_theme()`

---

## 7. 附带修复：TMenu 背景色与容器区分

### 问题

Playground 的 preview panel 容器和 TMenu 都使用 `bg_default` token，在 dark 模式下颜色完全相同（`#18181c`），无法区分。

### 解决方案

1. 在 dark/light token 中添加 `body_color` token（Dark: `#101014`, Light: `#f5f5f5`）
2. Playground 的 `preview_panel_style` 使用 `body_color` 替代 `bg_default`
3. TMenu 使用 `paintEvent` + `QPainter.fillRect` 手动绘制 `bg_default` 背景
4. TMenu 添加 `WA_StyledBackground` 属性

---

## 8. 排查过程中的无效方案记录

| 方案 | 结果 | 原因 |
|------|------|------|
| `menu.qss.j2` 设置 `TMenu { background-color: bg_default }` | 无效 | Playground QSS 优先级更高 |
| `self.setStyleSheet("TMenu { background-color: ... }")` | 无效 | 类选择器优先级不够 |
| `self.setStyleSheet("background-color: ...")` 裸属性 | 无效 | 仍被父级 QSS 覆盖 |
| 仅依赖全局 QSS + `unpolish/polish` | 无效 | 全局 QSS 被 per-widget QSS 覆盖 |
| 修改 Playground QSS 为 `transparent` | 无效 | 影响其他组件预览 |

最终有效方案：`paintEvent` + `QPainter.fillRect` 手动绘制背景。

---

## 9. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/tyto_ui_lib/components/organisms/menu.py` | 添加 `parse_color` import；`_MenuArrowWidget` 添加 `apply_theme`/`_icon_color`；`_CollapseToggleButton` paintEvent 用 `parse_color`、token 改用 `text_primary`、移除 hover；`TMenu` 添加 `paintEvent`/`WA_StyledBackground`；`TMenuItemGroup.apply_theme` 传播到 arrow 和 popup |
| `src/tyto_ui_lib/components/molecules/timeline.py` | 添加 `parse_color` import；`QColor(...)` → `parse_color(...)` |
| `src/tyto_ui_lib/styles/tokens/dark.json` | 添加 `body_color: "#101014"` |
| `src/tyto_ui_lib/styles/tokens/light.json` | 添加 `body_color: "#f5f5f5"` |
| `src/tyto_ui_lib/styles/templates/menu.qss.j2` | TMenu 背景色改为 `{{ colors.bg_default }}` |
| `examples/playground/styles/playground_styles.py` | `_tokens` 添加 `body_color`；`preview_panel_style` 使用 `body_color` |
| `tests/test_organisms/test_menu_collapse_toggle.py` | hover 测试更新 |

---

## 10. 经验总结

### 规则 1：QPainter 自绘控件必须使用 `parse_color()` 而非 `QColor()`

当颜色值来源于 Design Token 时，必须使用 `parse_color()` 解析。`QColor()` 不支持 CSS `rgba()` 小数 alpha，会静默返回纯黑。

**适用**：所有 `paintEvent` 中通过 QPainter 绘制的控件。
**不适用**：QSS 模板中的颜色引用（Qt QSS 解析器能正确处理）。

### 规则 2：新增 QPainter 自绘控件检查清单

1. ✅ 颜色解析使用 `parse_color()` 而非 `QColor()`
2. ✅ 非 BaseWidget 子类需从父级 `apply_theme` 手动调用
3. ✅ 被 reparent 的控件考虑 QSS 背景覆盖（可能需要 `WA_NoSystemBackground`）
4. ✅ 默认颜色值使用 light 模式 hex 作为 fallback

### 规则 3：Playground 预览面板 QSS 优先级

`QScrollArea#preview_panel > QWidget > QWidget` 规则会覆盖子组件 QSS 背景色。需要独立背景色的组件应通过 `paintEvent` 手动绘制。
