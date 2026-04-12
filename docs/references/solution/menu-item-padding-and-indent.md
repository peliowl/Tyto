# TMenu 菜单项内边距不足与子菜单缩进问题

> **组件**: `TMenu` / `TMenuItem` / `TMenuItemGroup`
> **文件**: `src/tyto_ui_lib/components/organisms/menu.py`、`src/tyto_ui_lib/styles/tokens/light.json`、`src/tyto_ui_lib/styles/tokens/dark.json`
> **关联文档**: [menu-collapse-toggle-bugfix.md](./menu-collapse-toggle-bugfix.md)
> **日期**: 2026-04-12
> **状态**: 已修复

---

## 目录

1. [问题一：菜单项左右内边距过小](#1-问题一菜单项左右内边距过小)
2. [问题二：父子菜单缩进层级不明显](#2-问题二父子菜单缩进层级不明显)
3. [问题三：弹出子菜单项存在多余缩进](#3-问题三弹出子菜单项存在多余缩进)
4. [解决方案](#4-解决方案)
5. [修改文件清单](#5-修改文件清单)
6. [经验总结](#6-经验总结)

---

## 1. 问题一：菜单项左右内边距过小

### 问题描述

垂直菜单中，菜单项（`TMenuItem`）和菜单组头部（`TMenuItemGroup` header）的文本、图标内容紧贴左右边界，水平内边距仅 8px，视觉上过于拥挤，与 NaiveUI 的菜单风格不一致。

### 根因分析

`TMenuItem._build_ui` 和 `TMenuItemGroup._build_ui` 中，row layout 的水平内边距 `h_pad` 读取的是通用 token `spacing.medium`（值为 8px）：

```python
# 原始代码
h_pad = tokens.spacing.get("medium", 8)  # → 8px
row_layout.setContentsMargins(h_pad, 0, h_pad, 0)
```

NaiveUI 的垂直菜单项水平内边距约为 20px，8px 明显不足。且菜单项的内边距属于组件级别的专用尺寸，不应复用通用 spacing token。

---

## 2. 问题二：父子菜单缩进层级不明显

### 问题描述

垂直菜单展开后，父菜单（如 "Content"）和子菜单（如 "Articles"、"Categories"）的文本缩进几乎一致，无法通过视觉层级区分父子关系。

### 根因分析

`set_indent_level` 使用 `left_margin = indent * level` 直接替换 row layout 的左边距，覆盖了 `_build_ui` 中设置的基础 `h_pad`：

```python
# 原始代码
left_margin = indent * level  # level=0 → 0px, level=1 → 24px
layout.setContentsMargins(left_margin, m.top(), m.right(), m.bottom())
```

当 `level = 0` 时，左边距被设为 0px（丢失了基础 padding）。当 `level = 1` 时，左边距为 24px，而父菜单在 `_build_ui` 中有 `h_pad`（修复后为 20px），两者差距仅 4px，层级区分不明显。

正确的行为应该是：缩进叠加在基础内边距之上。

---

## 3. 问题三：弹出子菜单项存在多余缩进

### 问题描述

水平菜单和垂直菜单收缩模式下，hover 弹出的子菜单（popup）中的菜单项带有额外缩进，与一级菜单项不一致。NaiveUI 的弹出子菜单中所有项目都是平级的，只有基础内边距。

### 根因分析

`TMenuItemGroup._create_popup` 将子项从内联容器移动到 popup 窗口时，子项仍保留着之前 `set_indent_level(1)` 设置的缩进值（`base_pad + 24 = 44px`），未重置为 level 0。

同时，`set_menu_mode` 从水平切回垂直模式时，子项从 popup 恢复到内联容器后，未调用 `_apply_indent_to_children()` 恢复正确的缩进层级。

---

## 4. 解决方案

### 4.1 新增 Design Token

在 `light.json` 和 `dark.json` 的 `menu` 节点中新增 `item_padding_h` token，专门控制菜单项的水平基础内边距：

```json
"menu": {
    "indent": 24,
    "item_height": 40,
    "item_padding_h": 20,
    "collapsed_width": 48
}
```

### 4.2 修改 _build_ui 读取新 token

`TMenuItem._build_ui` 和 `TMenuItemGroup._build_ui` 中，`h_pad` 改为读取 `menu.item_padding_h`：

```python
# 修改后
h_pad = 20  # fallback = menu.item_padding_h
if engine.current_theme():
    tokens = engine.current_tokens()
    if tokens and tokens.menu:
        h_pad = tokens.menu.get("item_padding_h", 20)
```

### 4.3 修改 set_indent_level 叠加基础内边距

`TMenuItem.set_indent_level` 和 `TMenuItemGroup.set_indent_level` 中，缩进值叠加在基础 `item_padding_h` 之上：

```python
# 修改后
base_pad = tokens.menu.get("item_padding_h", 20)
indent = tokens.menu.get("indent", 24)
left_margin = base_pad + indent * level
```

最终效果：

| 层级 | 左边距计算 | 值 |
|------|-----------|-----|
| level 0（顶层） | 20 + 24 × 0 | 20px |
| level 1（子项） | 20 + 24 × 1 | 44px |
| level 2（孙项） | 20 + 24 × 2 | 68px |

### 4.4 Popup 子项重置缩进

`_create_popup` 中，子项移入 popup 后重置为 level 0：

```python
for item in self._items:
    item.setParent(popup)
    popup_layout.addWidget(item)
    # Reset indent to level 0 inside popup
    item.set_indent_level(0)
```

### 4.5 模式切换恢复缩进

`set_menu_mode` 从水平切回垂直模式时，子项从 popup 恢复到内联容器后，调用 `_apply_indent_to_children()` 恢复正确的缩进层级：

```python
self._arrow_label.setVisible(True)
if self._expanded:
    self._children_wrapper.setVisible(True)
# Restore child indent levels after reparenting from popup
self._apply_indent_to_children()
```

`set_collapsed_mode` 的恢复路径已有 `set_indent_level(self._indent_level)` 会自动触发 `_apply_indent_to_children()`，无需额外修改。

---

## 5. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `styles/tokens/light.json` | `menu` 节点新增 `item_padding_h: 20` |
| `styles/tokens/dark.json` | `menu` 节点新增 `item_padding_h: 20` |
| `components/organisms/menu.py` — `TMenuItem._build_ui` | `h_pad` 改为读取 `menu.item_padding_h` |
| `components/organisms/menu.py` — `TMenuItemGroup._build_ui` | `h_pad` 改为读取 `menu.item_padding_h` |
| `components/organisms/menu.py` — `TMenuItem.set_indent_level` | 缩进叠加基础 `item_padding_h` |
| `components/organisms/menu.py` — `TMenuItemGroup.set_indent_level` | 缩进叠加基础 `item_padding_h` |
| `components/organisms/menu.py` — `TMenuItemGroup._create_popup` | 子项重置 `set_indent_level(0)` |
| `components/organisms/menu.py` — `TMenuItemGroup.set_menu_mode` | 恢复时调用 `_apply_indent_to_children()` |

---

## 6. 经验总结

### 6.1 组件专用 Token 优于通用 Token

菜单项的水平内边距是组件级别的专用尺寸，不应复用 `spacing.medium` 等通用 token。为组件新增专用 token（如 `menu.item_padding_h`）可以：

- 独立调整菜单内边距而不影响其他组件
- 语义更清晰，代码可读性更好
- 符合 Design Token 的分层设计原则

### 6.2 缩进应叠加而非替换基础内边距

`set_indent_level` 设置的缩进值应叠加在基础内边距之上（`base_pad + indent * level`），而非直接替换左边距。替换会导致：

- level 0 时丢失基础内边距
- 不同层级之间的视觉差距不符合预期

### 6.3 Popup 子项的缩进生命周期管理

子项在内联模式和 popup 模式之间切换时，缩进状态需要正确管理：

- 移入 popup 时：重置为 level 0（popup 内所有项平级）
- 恢复到内联时：通过 `_apply_indent_to_children()` 恢复正确的层级缩进

这是一个典型的"状态随容器迁移"问题，在任何涉及 widget reparent 的场景中都需要注意。
