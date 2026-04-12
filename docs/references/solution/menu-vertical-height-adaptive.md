# TMenu 垂直菜单高度未自适应父容器问题

> **组件**: `TMenu`
> **文件**: `src/tyto_ui_lib/components/organisms/menu.py`、`examples/playground/definitions/menu_props.py`
> **日期**: 2026-04-12
> **状态**: 已修复

---

## 目录

1. [问题描述](#1-问题描述)
2. [环境与复现条件](#2-环境与复现条件)
3. [根因分析](#3-根因分析)
4. [排查过程](#4-排查过程)
5. [解决方案](#5-解决方案)
6. [修改文件清单](#6-修改文件清单)
7. [经验总结](#7-经验总结)

---

## 1. 问题描述

TMenu 组件在垂直模式（`MenuMode.VERTICAL`）下，菜单的高度仅由菜单项内容撑开，未自适应填充父容器的高度。当父容器高度大于菜单项总高度时，菜单底部出现大面积空白区域，菜单背景色未覆盖整个容器。

### 期望行为

- **垂直菜单**：高度自适应为父容器的高度，背景色填满整个容器区域
- **水平菜单**：高度固定为菜单项的高度，不随父容器高度变化

### 实际表现

- 垂直菜单的白色背景仅覆盖菜单项区域，下方大面积灰色空白
- 在 Playground 中设置 Container Height 属性后，菜单高度不随容器高度变化

---

## 2. 环境与复现条件

| 项目 | 值 |
|------|-----|
| 框架 | PySide6 (Latest) |
| 操作系统 | Windows |
| Python | 3.12 |
| 复现路径 | Playground → 选择 Menu 组件 → 观察垂直菜单高度 |
| 容器高度 | 400px（默认），菜单项总高度约 200px |

---

## 3. 根因分析

问题由两个层面的原因共同导致：

### 3.1 TMenu 未设置垂直方向的 QSizePolicy

`TMenu.__init__` 和 `_build_ui` 中未显式设置 `QSizePolicy`。QWidget 的默认 size policy 为 `(Preferred, Preferred)`，这意味着 widget 倾向于使用其 `sizeHint()`（即内容的自然高度），而不会主动扩展以填充父容器的可用空间。

```python
# 原始代码（_build_ui 中无 size policy 设置）
def _build_ui(self) -> None:
    if self._mode == self.MenuMode.HORIZONTAL:
        self._root_layout = QHBoxLayout(self)
    else:
        self._root_layout = QVBoxLayout(self)
    # ... 无 setSizePolicy 调用
```

### 3.2 Playground 预览容器的布局约束

`ComponentPreview.show_component` 创建的预览容器使用了 `AlignTop | AlignLeft` 的布局级别对齐方式，并在末尾添加了 stretch spacer：

```python
container = QWidget()
layout = QVBoxLayout(container)
layout.setContentsMargins(32, 32, 32, 32)
layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)  # 问题点 1
layout.addWidget(widget)
layout.addStretch()  # 问题点 2
```

这两个约束的叠加效果：

- **`AlignTop | AlignLeft`**：布局级别的对齐设置会强制所有子 widget 使用其 `sizeHint()` 尺寸，完全忽略 `QSizePolicy.Expanding` 策略
- **`addStretch()`**：在 widget 下方添加弹性空间，将 widget 推向顶部，进一步阻止垂直扩展

### 3.3 布局级别对齐 vs 控件级别对齐

Qt 的 `QBoxLayout` 提供两种对齐设置方式：

| 方式 | API | 作用范围 | 对 size policy 的影响 |
|------|-----|---------|---------------------|
| 布局级别 | `layout.setAlignment(flags)` | 所有子 widget | **覆盖** size policy，强制使用 sizeHint |
| 控件级别 | `layout.setAlignment(widget, flags)` | 指定 widget | 仅影响指定 widget |

原始代码使用的是布局级别对齐，这是导致 `Expanding` size policy 失效的直接原因。

---

## 4. 排查过程

### 第一轮：仅设置 TMenu 的 QSizePolicy

在 `TMenu._build_ui` 和 `set_mode` 中为垂直模式设置 `(Preferred, Expanding)` size policy：

```python
if self._mode == self.MenuMode.HORIZONTAL:
    self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
else:
    self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
```

**结果**：菜单高度仍未变化。原因是 Playground 预览容器的布局级别 `AlignTop` 对齐覆盖了 size policy。

### 第二轮：清除控件级别对齐

在 `_apply_container_height` 回调中使用 `layout.setAlignment(widget, Qt.AlignmentFlag(0))` 清除控件级别对齐：

```python
layout.setAlignment(w, Qt.AlignmentFlag(0))  # 仅清除控件级别对齐
```

**结果**：菜单高度仍未变化。原因是布局级别的 `AlignTop | AlignLeft` 仍然生效，控件级别的清除无法覆盖布局级别的约束。

### 第三轮：清除布局级别对齐 + 移除 stretch（最终方案）

在 `_apply_container_height` 回调中使用 `layout.setAlignment(Qt.AlignmentFlag(0))`（无 widget 参数）清除布局级别对齐，并移除末尾的 stretch spacer：

```python
layout.setAlignment(Qt.AlignmentFlag(0))  # 清除布局级别对齐
# 移除 stretch spacer
for i in range(layout.count() - 1, -1, -1):
    item = layout.itemAt(i)
    if item is not None and item.widget() is None and item.spacerItem() is not None:
        layout.removeItem(item)
```

**结果**：菜单高度正确填充容器，问题解决。

---

## 5. 解决方案

### 5.1 TMenu 组件层：设置模式感知的 QSizePolicy

在 `TMenu._build_ui` 和 `TMenu.set_mode` 中，根据菜单模式设置不同的垂直 size policy：

```python
def _build_ui(self) -> None:
    if self._mode == self.MenuMode.HORIZONTAL:
        self._root_layout = QHBoxLayout(self)
        # 水平菜单：高度固定为菜单项高度
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    else:
        self._root_layout = QVBoxLayout(self)
        # 垂直菜单：高度扩展以填充父容器
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
```

同样的逻辑在 `set_mode` 的布局重建分支中重复应用，确保运行时模式切换后 size policy 同步更新。

### 5.2 Playground 层：Container Height 属性与布局约束清除

在 `menu_props.py` 中新增 `container_height` 属性定义，其 `apply` 回调在设置容器高度的同时清除阻止扩展的布局约束：

```python
def _apply_container_height(w: Any, v: Any) -> None:
    height = int(v) if v else 0
    parent = w.parentWidget()
    if parent is None:
        return
    layout = parent.layout()
    if height > 0:
        parent.setFixedHeight(height)
        if layout is not None:
            # 清除布局级别对齐（关键：无 widget 参数）
            layout.setAlignment(Qt.AlignmentFlag(0))
            # 移除 stretch spacer
            for i in range(layout.count() - 1, -1, -1):
                item = layout.itemAt(i)
                if item is not None and item.widget() is None and item.spacerItem() is not None:
                    layout.removeItem(item)
    else:
        parent.setMinimumHeight(0)
        parent.setMaximumHeight(16777215)
```

### 5.3 辅助修改：移除 Playground 工厂中的硬编码最小高度

`_make_menu` 工厂函数中移除了 `menu.setMinimumHeight(200)` 调用，因为垂直菜单的 `Expanding` size policy 已能自动填充父容器，硬编码最小高度不再必要。

---

## 6. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/tyto_ui_lib/components/organisms/menu.py` | `TMenu._build_ui`：根据模式设置 `QSizePolicy`（垂直 Expanding / 水平 Fixed） |
| `src/tyto_ui_lib/components/organisms/menu.py` | `TMenu.set_mode`：运行时模式切换时同步更新 `QSizePolicy` |
| `examples/playground/definitions/menu_props.py` | 新增 `_apply_container_height` 回调函数 |
| `examples/playground/definitions/menu_props.py` | 新增 `container_height` 属性定义（默认 400，类型 int） |
| `examples/playground/definitions/menu_props.py` | `_make_menu`：移除 `setMinimumHeight(200)` 调用 |
| `examples/playground/definitions/menu_props.py` | 新增 `from PySide6.QtCore import Qt` 导入 |

---

## 7. 经验总结

### 7.1 QBoxLayout 的对齐层级优先级

Qt 的 `QBoxLayout` 存在两个独立的对齐层级，布局级别对齐具有更高优先级：

```
布局级别对齐 > 控件级别对齐 > QSizePolicy
```

- `layout.setAlignment(flags)`：设置布局级别对齐，**覆盖所有子 widget 的 size policy**
- `layout.setAlignment(widget, flags)`：设置控件级别对齐，仅影响指定 widget
- `widget.setSizePolicy(...)`：仅在无布局级别对齐约束时生效

**关键结论**：如果需要某个子 widget 的 `Expanding` size policy 生效，必须确保其父布局未设置布局级别对齐，或通过 `layout.setAlignment(Qt.AlignmentFlag(0))` 显式清除。

### 7.2 清除布局对齐的正确 API

| 目标 | API | 效果 |
|------|-----|------|
| 清除布局级别对齐 | `layout.setAlignment(Qt.AlignmentFlag(0))` | 所有子 widget 的 size policy 恢复生效 |
| 清除控件级别对齐 | `layout.setAlignment(widget, Qt.AlignmentFlag(0))` | 仅恢复指定 widget 的 size policy |

### 7.3 垂直菜单的 Size Policy 设计模式

对于需要填充父容器高度的垂直导航菜单，推荐的 size policy 组合：

```python
# 垂直菜单：宽度由内容决定，高度填充父容器
self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

# 水平菜单：宽度由内容决定，高度固定为菜单项高度
self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
```

同时需确保垂直菜单的内部布局包含 stretch spacer（`addStretch()`），使菜单项靠顶排列，剩余空间由 stretch 填充。

### 7.4 适用范围

此 size policy 设计模式适用于所有需要填充父容器高度的侧边栏组件，包括但不限于：

- `TMenu`（垂直模式）
- 自定义侧边导航面板
- 属性面板等固定宽度、自适应高度的容器组件
