# TMenu 折叠切换按钮 — 问题与解决方案记录

> **组件**: `TMenu` / `_CollapseToggleButton`
> **文件**: `src/tyto_ui_lib/components/organisms/menu.py`
> **关联 Spec**: `.kiro/specs/menu-collapse-toggle/`
> **日期**: 2026-04-11

---

## 目录

1. [初始化顺序异常](#1-初始化顺序异常)
2. [按钮被父控件裁剪](#2-按钮被父控件裁剪)
3. [按钮无法响应点击事件](#3-按钮无法响应点击事件)
4. [模式切换导致 C++ 对象被销毁](#4-模式切换导致-c-对象被销毁)
5. [Popup 销毁导致子菜单项丢失](#5-popup-销毁导致子菜单项丢失)
6. [Collapsed 模式下图标未居中对齐](#6-collapsed-模式下图标未居中对齐)
7. [Collapsed 模式下子菜单无 Popup 弹出](#7-collapsed-模式下子菜单无-popup-弹出)
8. [收缩/展开动画行为异常](#8-收缩展开动画行为异常)
9. [Chevron 图标旋转动画](#9-chevron-图标旋转动画)
10. [Playground 布局对齐问题](#10-playground-布局对齐问题)
11. [Dark 模式下按钮样式被 QSS 覆盖（未解决）](#11-dark-模式下按钮样式被-qss-覆盖未解决)

---

## 1. 初始化顺序异常

### 问题描述

在 Playground 中点击 menu 菜单时抛出 `AttributeError: 'TMenu' object has no attribute '_collapse_toggle'`。

### 根因分析

`BaseWidget.__init__` 在 `super().__init__(parent)` 中调用 `apply_theme()`，而此时 `TMenu.__init__` 尚未执行到创建 `_collapse_toggle` 的代码行。`TMenu.apply_theme` 中直接访问 `self._collapse_toggle.apply_theme()` 导致属性不存在。

### 解决方案

在 `TMenu.apply_theme` 中添加 `hasattr` 守卫，与 `TMenuItem.apply_theme` 的现有模式保持一致：

```python
if hasattr(self, "_collapse_toggle"):
    self._collapse_toggle.apply_theme()
```

### 经验总结

`BaseWidget` 子类中，`super().__init__()` 会触发 `apply_theme()`。所有在 `__init__` 中延迟创建的成员，在 `apply_theme` 中必须用 `hasattr` 守卫。

---

## 2. 按钮被父控件裁剪

### 问题描述

按钮设计为半露出菜单右边界，但 Qt 默认裁剪子控件到父控件边界内，导致按钮右半部分不可见。

### 根因分析

`_CollapseToggleButton` 是 `TMenu` 的子控件，定位在 `x = parent.width() - btn_size // 2`。Qt 的 QWidget 会裁剪超出父控件边界的子控件区域。

### 解决方案

在 `reposition()` 中将按钮 reparent 到 TMenu 的父控件上，使用父控件坐标系定位：

```python
menu_parent = menu.parentWidget()
if menu_parent is not None and self.parentWidget() is not menu_parent:
    self.setParent(menu_parent)
    self.show()

menu_pos = menu.pos()
x = menu_pos.x() + menu.width() - half
y = menu_pos.y() + (menu.height() - self._btn_size) // 2
```

### 已知限制

Reparent 后按钮会继承新父控件的 QSS 样式，在 dark 模式下可能导致样式异常。详见 [第 11 节](#11-dark-模式下按钮样式被-qss-覆盖未解决)。

---

## 3. 按钮无法响应点击事件

### 问题描述

按钮可见但点击无反应。

### 根因分析

1. 按钮初始未设置 `setFixedSize`，在 `apply_theme` 调用前可能为 0×0 尺寸
2. 布局中的 TMenuItem 等兄弟控件覆盖在按钮上方
3. `mousePressEvent` 未调用 `event.accept()`，事件可能传播到父控件

### 解决方案

1. 在 `__init__` 中调用 `self.setFixedSize(self._btn_size, self._btn_size)`
2. 在 `reposition()` 和 `_build_ui` 末尾调用 `self._collapse_toggle.raise_()` 提升 z-order
3. 在 `mousePressEvent` 中添加 `event.accept()`：

```python
def mousePressEvent(self, event: object) -> None:
    if not self._disabled:
        self.clicked.emit()
    if isinstance(event, QMouseEvent):
        event.accept()
```

---

## 4. 模式切换导致 C++ 对象被销毁

### 问题描述

从 horizontal 切换到 vertical 模式后，点击菜单项抛出 `RuntimeError: Internal C++ object (TMenuItem) already deleted`。

### 根因分析

`TMenu.set_mode` 在重建布局时调用 `w.setParent(None)`，PySide6 在清除 parent 时可能直接销毁底层 C++ 对象，但 Python 层的 `_items` 列表仍持有已失效的引用。

### 解决方案

从布局中移除 widget 时，仅调用 `takeAt(0)` 而不改变 parent：

```python
while self._root_layout.count():
    self._root_layout.takeAt(0)
```

### 经验总结

PySide6 中 `setParent(None)` 是危险操作，可能触发 C++ 对象销毁。从布局中移除 widget 时，应仅使用 `takeAt` 或 `removeWidget`，不要改变 parent。

---

## 5. Popup 销毁导致子菜单项丢失

### 问题描述

在 horizontal 模式下点击子菜单项后切换到 vertical 模式，再点击菜单项抛出 `Internal C++ object (TMenuItem) already deleted`。

### 根因分析

`TMenuItemGroup._create_popup` 将子菜单项 reparent 到 popup 窗口。切回 vertical 模式时 `_popup.deleteLater()` 销毁 popup，连带销毁了其子控件（TMenuItem），但 `_items` 列表仍持有已失效的引用。

### 解决方案

在销毁 popup 前，先将子项 reparent 回 `_children_wrapper`：

```python
if self._popup is not None:
    for item in self._items:
        item.setParent(self._children_wrapper)
        self._children_layout.addWidget(item)
    self._popup.hide()
    self._popup.deleteLater()
    self._popup = None
```

### 经验总结

销毁容器 widget 前，必须先将需要保留的子 widget reparent 到其他容器。此规则适用于所有使用 `deleteLater()` 的场景。

---

## 6. Collapsed 模式下图标未居中对齐

### 问题描述

垂直菜单收缩后，各菜单项的图标水平位置不一致。

### 根因分析

1. 不同缩进级别的菜单项有不同的左边距（`set_indent_level` 设置的 `contentsMargins`）
2. `TMenuItem` 的 row layout 中有 `addStretch()` 占据剩余空间，与 expanding 的 icon label 竞争
3. `setAlignment(AlignCenter)` 对含有 stretch 的 QHBoxLayout 无效

### 解决方案

在 `set_collapsed_mode` 中：

1. 清除左右 margins 为 0
2. 移除 row layout 中的 stretch spacer item
3. 将 `_icon_label` 设为 `Expanding` size policy（利用 label 自身的 `AlignCenter` 属性居中 pixmap）
4. 展开时恢复 `fixedWidth(24)`、重新添加 stretch、恢复缩进

```python
# Collapsed: 移除 stretch，icon 扩展填满
last_idx = row_layout.count() - 1
if last_idx >= 0:
    spacer = row_layout.itemAt(last_idx)
    if spacer is not None and spacer.widget() is None:
        row_layout.removeItem(spacer)
self._icon_label.setFixedWidth(16777215)
self._icon_label.setSizePolicy(QSizePolicy.Policy.Expanding, ...)
```

---

## 7. Collapsed 模式下子菜单无 Popup 弹出

### 问题描述

垂直菜单收缩后，带子菜单的 `TMenuItemGroup` 仅显示图标，但 hover 时不弹出子菜单 popup。

### 根因分析

原有的 popup 机制仅在 `_is_horizontal_mode()` 为 True 时触发，collapsed 模式下不会激活。

### 解决方案

1. 在 `TMenuItemGroup` 中添加 `_collapsed_mode` 标志
2. `set_collapsed_mode` 中管理 popup 生命周期
3. `enterEvent`/`leaveEvent` 中同时响应 `_collapsed_mode`
4. `mousePressEvent` 在 collapsed 模式下跳过点击展开
5. `_show_popup` 在 collapsed 模式下将 popup 定位到右侧

```python
def enterEvent(self, event):
    if (self._is_horizontal_mode() or self._collapsed_mode) and not self._menu_disabled:
        self._show_popup()
```

---

## 8. 收缩/展开动画行为异常

### 问题描述

1. 收缩时菜单项图标瞬间跳到居中位置（在宽度动画开始前）
2. 展开时宽度瞬间跳到全宽（无动画）

### 根因分析

1. `set_collapsed` 先调用 `item.set_collapsed_mode(collapsed)` 切换图标布局，再调用 `_animate_collapse` 开始宽度动画
2. 展开方向的 `_animate_collapse(False)` 直接设置 `setMinimumWidth(0); setMaximumWidth(16777215)` 而无动画

### 解决方案

1. 收缩时：先动画宽度，动画完成后再通过 `finished` 信号切换 item 的 collapsed mode
2. 展开时：先切换 item 回正常模式，再动画宽度从 collapsed_width 到 expanded_width
3. 记住 `_expanded_width` 以便展开时恢复

```python
if collapsed:
    self._animate_collapse(True)  # 动画完成后触发 _on_collapse_finished
else:
    for item in self._items:
        item.set_collapsed_mode(False)
    self._animate_collapse(False)  # 双向都有动画
```

---

## 9. Chevron 图标旋转动画

### 问题描述

收缩/展开时，按钮的 chevron 箭头方向瞬间切换，无过渡动画。

### 解决方案

1. 添加 `_rotation` 浮点属性和 `Property` 声明
2. `set_collapsed` 中使用 `QPropertyAnimation` 动画化旋转角度（180° ↔ 0°）
3. `paintEvent` 使用 `_rotation` 值而非硬编码角度

```python
rotation = Property(float, _get_rotation, _set_rotation)

def set_collapsed(self, collapsed: bool) -> None:
    target = 0.0 if collapsed else 180.0
    self._rotation_anim = QPropertyAnimation(self, b"rotation", self)
    self._rotation_anim.setDuration(200)
    self._rotation_anim.setStartValue(self._rotation)
    self._rotation_anim.setEndValue(target)
    self._rotation_anim.start()
```

---

## 10. Playground 布局对齐问题

### 问题描述

菜单收缩后整体居中显示，而非保持左侧不动、右侧向左收缩。

### 根因分析

`ComponentPreview.show_component` 中 container layout 使用了 `AlignCenter`。

### 解决方案

改为 `AlignTop | AlignLeft`：

```python
layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
```

---

## 11. Dark 模式下按钮样式被 QSS 覆盖（未解决）

### 问题描述

按钮 reparent 到 Playground 的 container 后，在 dark 模式下按钮显示为纯黑色，QPainter 自绘内容被 QSS 背景覆盖。

### 根因分析

Playground 的 `preview_panel_style` 包含规则：

```css
QScrollArea#preview_panel > QWidget > QWidget {
    background-color: {bg_default};
}
```

按钮 reparent 到 container 后成为该规则的匹配目标，Qt 在 `paintEvent` 之前绘制 QSS 背景，覆盖了 QPainter 的自绘内容。

### 已尝试方案及结果

| 方案 | 结果 |
|------|------|
| `WA_StyledBackground = False` | 无效，QSS 仍然绘制背景 |
| `WA_NoSystemBackground + WA_OpaquePaintEvent` | 圆形外角落出现黑色方块 |
| `CompositionMode_Source` 填充透明 | backing store 不支持 alpha，light 模式出现黑色方块 |
| `setStyleSheet("background: transparent")` + objectName | QSS 优先级不够，被父级规则覆盖 |
| `fillRect(_parent_bg_color)` 预填充 | 需要额外 token，且圆形外角落颜色在菜单边界处不一致 |
| 修改 playground QSS 排除按钮 | ID 选择器优先级仍不够 |
| ToolTip 顶层窗口方案 | 可行但增加复杂度，需要 `mapToGlobal` 定位 |

### 当前状态

回退到旋转动画任务完成时的版本（reparent + `bg_default` + hover + 1px 边框）。Dark 模式下的 QSS 覆盖问题暂未解决，待后续在组件库层面统一处理 QPainter 自绘控件与 QSS 的兼容性问题。

### 可能的后续方向

1. **ToolTip 窗口方案**：将按钮做成独立顶层窗口（`Qt.WindowType.ToolTip | FramelessWindowHint + WA_TranslucentBackground`），完全脱离 QSS 继承链。已验证技术可行，但需要处理窗口跟随菜单移动的问题。
2. **修改 Playground QSS 规则**：将 `> QWidget > QWidget` 改为更精确的选择器，避免匹配到按钮。
3. **统一 QPainter 自绘控件基类**：为所有 QPainter 自绘控件提供统一的 QSS 隔离机制。

---

## 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/tyto_ui_lib/components/organisms/menu.py` | `_CollapseToggleButton` 类、`TMenu` 集成、`TMenuItemGroup` collapsed popup、动画逻辑 |
| `examples/playground/views/component_preview.py` | container layout 对齐方式 |
| `examples/playground/definitions/menu_props.py` | menu 工厂函数 |
