# TMenu 多级菜单弹出子菜单面板系列问题修复

> **组件**: `TMenu` / `TMenuItem` / `TMenuItemGroup`
> **文件**: `src/tyto_ui_lib/components/organisms/menu.py`、`examples/playground/definitions/menu_props.py`
> **关联文档**: [menu-item-padding-and-indent.md](./menu-item-padding-and-indent.md)、[menu-collapse-toggle-circle-clipping.md](./menu-collapse-toggle-circle-clipping.md)
> **日期**: 2026-04-12
> **状态**: 已修复

---

## 目录

1. [背景](#1-背景)
2. [问题一：二级 Popup 定位错误](#2-问题一二级-popup-定位错误)
3. [问题二：嵌套 Group 在 Popup 内 Inline 展开](#3-问题二嵌套-group-在-popup-内-inline-展开)
4. [问题三：模式切换后嵌套 Group 无法展开](#4-问题三模式切换后嵌套-group-无法展开)
5. [问题四：点击菜单项后 Popup 链未关闭](#5-问题四点击菜单项后-popup-链未关闭)
6. [问题五：应用失焦后 Popup 浮在其他窗口上方](#6-问题五应用失焦后-popup-浮在其他窗口上方)
7. [问题六：三级 Popup 关闭后二级 Popup 未跟随关闭](#7-问题六三级-popup-关闭后二级-popup-未跟随关闭)
8. [问题七：多级菜单图标未递归应用](#8-问题七多级菜单图标未递归应用)
9. [问题八：应用关闭时 eventFilter 抛出 RuntimeError](#9-问题八应用关闭时-eventfilter-抛出-runtimeerror)
10. [修改文件清单](#10-修改文件清单)
11. [经验总结](#11-经验总结)

---

## 1. 背景

TMenu 组件支持多级菜单嵌套（`TMenuItemGroup` 内嵌 `TMenuItemGroup`）。在水平模式和折叠模式下，子菜单通过 popup 浮动面板显示。`_create_popup` 方法将子项从内联容器 reparent 到 popup 的 `_MenuPopupContainer` 中。

这一 reparent 操作改变了 Qt 的 parent chain，导致一系列依赖 parent chain 的逻辑失效，引发了以下连锁问题。

---

## 2. 问题一：二级 Popup 定位错误

### 问题描述

水平模式下，hover 一级菜单组（如 "Content"）弹出 popup 后，hover popup 内的二级菜单组（如 "Articles"），其子菜单 popup 应在右侧弹出，但实际在下方弹出，与一级 popup 重叠。

### 根因分析

`_show_popup` 通过 `_is_nested_group()` 判断定位分支：嵌套 group 走"侧边弹出"，顶层 group 走"下方弹出"。

`_is_nested_group()` 遍历 Qt parent chain 查找 `TMenuItemGroup` 类型的祖先。但 `_create_popup` 将子项 reparent 到 `_MenuPopupContainer` 后，parent chain 变为：

```
_MenuPopupContainer → QWidget#menu_popup → None
```

链中不再包含 `TMenuItemGroup`，导致 `_is_nested_group()` 返回 `False`，定位走了错误的"下方弹出"分支。

### 解决方案

在 `_is_nested_group()` 中增加对 `_MenuPopupContainer` 的检测：

```python
def _is_nested_group(self) -> bool:
    p = self.parent()
    while p is not None:
        if isinstance(p, TMenuItemGroup):
            return True
        if isinstance(p, _MenuPopupContainer):
            return True
        p = p.parent()
    return False
```

如果 parent chain 中存在 `_MenuPopupContainer`，说明当前 group 被某个父级 group 放入了 popup，逻辑上仍然是嵌套的。

---

## 3. 问题二：嵌套 Group 在 Popup 内 Inline 展开

### 问题描述

折叠模式下，一级 popup 内的二级菜单组（如 "Articles"）以 inline 方式展开子项（Tech、Design 直接显示在同一面板内，箭头朝下），而非以独立 popup 在右侧弹出。面板内出现大片空白区域。

### 根因分析

`_create_popup` 将嵌套 group reparent 到 popup 容器后，未修改其显示模式。嵌套 group 仍保持垂直模式的 inline 展开行为：

1. `_children_wrapper` 仍然可见，占据面板空间
2. `enterEvent` 只在 `_is_horizontal_mode() or _collapsed_mode` 时触发 popup，但嵌套 group 两个标志都为 `False`
3. `mousePressEvent` 响应点击进行 inline 展开/折叠

### 解决方案

#### 3.1 在 `_create_popup` 中强制嵌套 Group 进入 Popup 模式

```python
for item in self._items:
    item.setParent(container)
    container_layout.addWidget(item)
    item.set_indent_level(0)
    if isinstance(item, TMenuItemGroup):
        item._children_wrapper.setVisible(False)
        item._arrow_label.setVisible(True)
        item._arrow_label.set_expanded(False)
        item._owner_group = self
```

#### 3.2 新增 `_should_use_popup()` 统一判断

```python
def _should_use_popup(self) -> bool:
    return self._is_horizontal_mode() or self._collapsed_mode or self._is_inside_popup()

def _is_inside_popup(self) -> bool:
    p = self.parent()
    while p is not None:
        if isinstance(p, _MenuPopupContainer):
            return True
        p = p.parent()
    return False
```

#### 3.3 替换 `enterEvent`、`leaveEvent`、`mousePressEvent` 中的条件

将 `_is_horizontal_mode() or _collapsed_mode` 替换为 `_should_use_popup()`，使 popup 容器内的嵌套 group 也能正确触发 hover popup 并阻止 click 展开。

---

## 4. 问题三：模式切换后嵌套 Group 无法展开

### 问题描述

折叠模式下点击三级菜单项后，边栏展开回垂直模式，点击二级菜单组无法展开三级菜单面板。

### 根因分析

`_create_popup` 中对嵌套 group 做了以下修改：

- `_children_wrapper.setVisible(False)`
- `_arrow_label.set_expanded(False)`
- 嵌套 group 可能创建了自己的 popup（用于三级菜单）

`set_collapsed_mode(False)` 和 `set_menu_mode(vertical)` 恢复时：

1. 将子项从 popup reparent 回 `_children_wrapper`
2. 但未恢复嵌套 group 的 `_children_wrapper` 可见性
3. 未销毁嵌套 group 自己的 popup，导致其子项仍在已销毁的 popup 容器中

### 解决方案

在 `set_collapsed_mode(False)` 和 `set_menu_mode(vertical)` 的恢复逻辑中，对嵌套 group 执行完整的状态恢复：

```python
if isinstance(item, TMenuItemGroup):
    if item._popup is not None:
        for child in item._items:
            child.setParent(item._children_wrapper)
            item._children_layout.addWidget(child)
        item._popup.hide()
        item._popup.deleteLater()
        item._popup = None
    item._arrow_label.setVisible(True)
    item._update_arrow()
    if item._expanded:
        item._children_wrapper.setVisible(True)
    item._apply_indent_to_children()
    item._owner_group = None
```

---

## 5. 问题四：点击菜单项后 Popup 链未关闭

### 问题描述

在多级 popup 中点击三级菜单项后，如果鼠标未划过二级或一级菜单，所有 popup 面板保持显示。

### 根因分析

`TMenu._on_item_clicked` 只设置 active key 和发射信号，未关闭任何 popup。

### 解决方案

在 `_on_item_clicked` 中调用 `_hide_all_popups()`，递归关闭整个 popup 链：

```python
def _on_item_clicked(self, key: str) -> None:
    if self._disabled:
        return
    self.set_active_key(key)
    self.item_selected.emit(key)
    self._hide_all_popups()

def _hide_all_popups(self) -> None:
    for item in self._items:
        if isinstance(item, TMenuItemGroup):
            self._hide_popups_recursive(item)

def _hide_popups_recursive(self, group: TMenuItemGroup) -> None:
    if group._popup is not None and group._popup.isVisible():
        group._popup.hide()
    if group._hide_timer is not None:
        group._hide_timer.stop()
    for child in group._items:
        if isinstance(child, TMenuItemGroup):
            self._hide_popups_recursive(child)
```

---

## 6. 问题五：应用失焦后 Popup 浮在其他窗口上方

### 问题描述

切换到其他应用程序后，TMenu 的 popup 面板仍然显示在其他窗口上方，遮挡内容。

### 根因分析

Popup 使用 `Qt.WindowType.WindowStaysOnTopHint` 创建，当应用失去焦点时没有隐藏机制。

### 解决方案

在 `TMenu.__init__` 中监听 `QApplication.focusChanged` 信号：

```python
app = QApplication.instance()
if app is not None:
    app.focusChanged.connect(self._on_app_focus_changed)

def _on_app_focus_changed(self, _old: QWidget | None, now: QWidget | None) -> None:
    if now is None:
        self._hide_all_popups()
```

当 `now` 为 `None` 时，表示焦点离开了应用，此时隐藏所有 popup。

---

## 7. 问题六：三级 Popup 关闭后二级 Popup 未跟随关闭

### 问题描述

弹出三级菜单后，鼠标直接移到空白区域（不经过二级或一级 popup），三级 popup 正确隐藏，但二级 popup 保持显示。

### 根因分析

事件流程：

1. 鼠标从三级 popup 移到空白区域 → 三级 group 的 `eventFilter` 收到 Leave → 启动 hide timer
2. 200ms 后三级 group 的 `_do_hide_popup` 隐藏三级 popup
3. 但二级 group 的 hide timer 从未被触发 — 鼠标从未经过二级 popup，二级 group 的 `eventFilter` 没有收到 Leave 事件
4. 二级 group 的 `_do_hide_popup` 中"子级 popup 可见则保持"的检查在三级 popup 隐藏后本应通过，但没有人触发这个检查

### 解决方案

#### 7.1 新增 `_owner_group` 反向引用

在 `TMenuItemGroup.__init__` 中新增 `_owner_group` 字段，在 `_create_popup` 中设置：

```python
self._owner_group: TMenuItemGroup | None = None
```

#### 7.2 在 `_do_hide_popup` 末尾通知父级

```python
def _do_hide_popup(self) -> None:
    # ... 隐藏逻辑 ...
    self._popup.hide()
    self._notify_parent_hide()

def _notify_parent_hide(self) -> None:
    if self._owner_group is not None:
        self._owner_group._hide_popup()
```

当子级 popup 隐藏后，通过 `_owner_group` 触发父级 group 的 `_hide_popup()`（200ms 延迟）。父级的 `_do_hide_popup` 会检查鼠标是否在其 popup 上，如果不在则也隐藏。

---

## 8. 问题七：多级菜单图标未递归应用

### 问题描述

Playground 中设置图标后，一级菜单项和一级菜单组正确显示图标，但二级菜单组（如 "Articles"）及其子项（Tech、Design）未显示图标。

### 根因分析

`menu_props.py` 中的 `_apply_icon` 函数只遍历两层：

```python
for item in items:
    if isinstance(item, TMenuItem):
        item.set_icon(icon)
    elif isinstance(item, TMenuItemGroup):
        item.set_icon(icon)
        for child in item.get_items():
            if isinstance(child, TMenuItem):
                child.set_icon(icon)  # 只处理 TMenuItem，忽略嵌套 TMenuItemGroup
```

嵌套的 `TMenuItemGroup` 及其子项未被遍历。

### 解决方案

改为递归遍历：

```python
def _apply_icon(w: Any, v: Any) -> None:
    path = str(v) if v else ""
    icon = QIcon(path) if path else None

    def _apply_recursive(items: list[Any]) -> None:
        for item in items:
            if isinstance(item, TMenuItem):
                item.set_icon(icon)
            elif isinstance(item, TMenuItemGroup):
                item.set_icon(icon)
                _apply_recursive(item.get_items())

    _apply_recursive(getattr(w, "_items", []))
    w.updateGeometry()
    w.adjustSize()
```

---

## 9. 问题八：应用关闭时 eventFilter 抛出 RuntimeError

### 问题描述

关闭 Playground 应用时，控制台输出异常：

```
RuntimeError: Internal C++ object (PySide6.QtWidgets.QWidget) already deleted.
```

异常发生在 `eventFilter` 中访问 `self._popup.findChild()` 时。

### 根因分析

PySide6 应用关闭时，C++ 对象的销毁顺序不确定。Qt 的 C++ 层可能先于 Python 层销毁 popup widget，但 Python 的 `eventFilter` 仍被调用（atexit callback），此时访问已删除的 C++ 对象抛出 `RuntimeError`。

### 解决方案

在 `eventFilter` 和 `_do_hide_popup` 中用 `try/except RuntimeError` 保护对 `self._popup` 的 C++ 方法调用：

```python
def eventFilter(self, obj, event):
    if self._popup is None or not hasattr(event, "type"):
        return False
    try:
        container = self._popup.findChild(QWidget, "menu_popup_container")
    except RuntimeError:
        return False
    # ...

def _do_hide_popup(self) -> None:
    if self._popup is None:
        return
    try:
        if self._popup.underMouse():
            return
        container = self._popup.findChild(QWidget, "menu_popup_container")
        if container is not None and container.underMouse():
            return
    except RuntimeError:
        return
    # ...
```

---

## 10. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `menu.py` — `TMenuItemGroup.__init__` | 新增 `_owner_group` 字段 |
| `menu.py` — `_is_nested_group` | 增加 `_MenuPopupContainer` 检测 |
| `menu.py` — `_create_popup` | 嵌套 group 隐藏 `_children_wrapper`、显示右箭头、设置 `_owner_group` |
| `menu.py` — 新增 `_should_use_popup` | 统一判断是否使用 popup 模式 |
| `menu.py` — 新增 `_is_inside_popup` | 检测是否在 popup 容器内 |
| `menu.py` — 新增 `_notify_parent_hide` | 子级 popup 隐藏后通知父级 |
| `menu.py` — `enterEvent` / `leaveEvent` | 使用 `_should_use_popup()` 替代原条件 |
| `menu.py` — `mousePressEvent` | 使用 `_should_use_popup()` 阻止 popup 内 click 展开 |
| `menu.py` — `_do_hide_popup` | 子级 popup 可见保持 + 级联隐藏 + 通知父级 + RuntimeError 保护 |
| `menu.py` — `eventFilter` | RuntimeError 保护 |
| `menu.py` — `set_collapsed_mode` | 恢复时销毁嵌套 group 的 popup、恢复状态、清除 `_owner_group` |
| `menu.py` — `set_menu_mode` | 同上 |
| `menu.py` — `TMenu.__init__` | 连接 `focusChanged` 信号 |
| `menu.py` — `TMenu._on_item_clicked` | 调用 `_hide_all_popups()` |
| `menu.py` — 新增 `_hide_all_popups` / `_hide_popups_recursive` | 递归关闭所有 popup |
| `menu.py` — 新增 `_on_app_focus_changed` | 应用失焦时隐藏 popup |
| `menu_props.py` — `_apply_icon` | 改为递归遍历所有层级 |

---

## 11. 经验总结

### 11.1 Reparent 操作的连锁影响

`setParent()` 改变 Qt parent chain 后，所有依赖 parent chain 的逻辑都需要重新审视：

- 类型检测（`_is_nested_group`）
- 事件传播（`enterEvent`、`leaveEvent`）
- 状态管理（`_children_wrapper` 可见性、箭头方向）

建议在执行 reparent 时，建立显式的逻辑引用（如 `_owner_group`）来维护组件间的关系。

### 11.2 Popup 生命周期的完整管理

Popup 模式涉及三个阶段，每个阶段都需要正确处理：

| 阶段 | 操作 |
|------|------|
| 创建 | 隐藏 `_children_wrapper`、设置箭头、建立 `_owner_group` |
| 运行 | hover 触发 popup、级联隐藏、父级保持 |
| 销毁 | 恢复 `_children_wrapper`、恢复箭头、销毁嵌套 popup、清除 `_owner_group` |

遗漏任何一个阶段的处理都会导致状态不一致。

### 11.3 多级 Popup 的隐藏链

多级 popup 的隐藏需要双向传播：

- **向下级联**：父级隐藏时，所有子级 popup 也必须隐藏
- **向上通知**：子级隐藏后，父级需要重新评估自己是否也该隐藏

仅靠 `underMouse()` 检查不够，因为鼠标可能从深层 popup 直接离开而不经过中间层级。

### 11.4 PySide6 关闭时的 C++ 对象生命周期

PySide6 应用关闭时，C++ 对象可能先于 Python 对象销毁。所有在 `eventFilter`、timer callback 等异步入口点中访问 Qt C++ 对象的代码，都应使用 `try/except RuntimeError` 保护。
