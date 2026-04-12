# TMenu Dark 模式下菜单背景色与弹出面板背景色不一致

> **组件**: `TMenu`
> **文件**: `src/tyto_ui_lib/styles/templates/menu.qss.j2`
> **关联文档**: [menu-item-padding-and-indent.md](./menu-item-padding-and-indent.md)
> **日期**: 2026-04-12
> **状态**: 已修复

---

## 目录

1. [问题描述](#1-问题描述)
2. [根因分析](#2-根因分析)
3. [解决方案](#3-解决方案)
4. [影响评估](#4-影响评估)
5. [修改文件清单](#5-修改文件清单)
6. [经验总结](#6-经验总结)

---

## 1. 问题描述

在 Dark 模式下，TMenu 的侧边栏背景色（深黑色）与 hover 弹出的子菜单面板背景色（灰色）存在明显色差。弹出面板由 `_MenuPopupContainer` 使用 `colors.popover_color` 自绘背景，而菜单主体通过 QSS 使用 `colors.bg_default` 作为背景色，两者在 Dark 主题下对应不同的颜色值，导致视觉上不统一。

NaiveUI 的 Dark 模式下，菜单主体与弹出面板的背景色是一致的。

---

## 2. 根因分析

### 2.1 Token 值差异

`menu.qss.j2` 中 TMenu 的背景色使用 `colors.bg_default`：

```css
TMenu {
    background-color: {{ colors.bg_default }};
}
```

而弹出面板 `_MenuPopupContainer.paintEvent` 中使用 `colors.popover_color` 自绘背景。

两个 Token 在不同主题下的值如下：

| Token | Light 值 | Dark 值 |
|-------|---------|---------|
| `colors.bg_default` | `#ffffff` | `#18181c` |
| `colors.popover_color` | `#ffffff` | `rgb(72, 72, 78)` |

Light 模式下两者相同（均为白色），因此无视觉差异。Dark 模式下 `bg_default`（`#18181c`）远深于 `popover_color`（`rgb(72, 72, 78)`），导致菜单主体与弹出面板之间出现明显的色差断层。

### 2.2 语义分析

- `bg_default`：页面/容器的默认背景色，适用于全局布局背景
- `popover_color`：弹出层/浮动面板的背景色，适用于 popover、dropdown、popup 等浮动元素

TMenu 在折叠模式下本质上是一个弹出式交互组件，其视觉语义更接近 popover 而非页面背景。使用 `popover_color` 作为菜单背景色在语义上更准确。

---

## 3. 解决方案

在 `menu.qss.j2` 中，将 TMenu 的背景色从 `colors.bg_default` 改为 `colors.popover_color`：

```css
/* 修改前 */
TMenu {
    background-color: {{ colors.bg_default }};
    border: none;
    outline: none;
}

/* 修改后 */
TMenu {
    background-color: {{ colors.popover_color }};
    border: none;
    outline: none;
}
```

修改后各主题下的效果：

| 主题 | 菜单背景色 | 弹出面板背景色 | 是否一致 |
|------|-----------|--------------|---------|
| Light | `#ffffff` | `#ffffff` | ✅ |
| Dark | `rgb(72, 72, 78)` | `rgb(72, 72, 78)` | ✅ |

---

## 4. 影响评估

### 4.1 Light 模式

无影响。`bg_default` 和 `popover_color` 在 Light 主题下均为 `#ffffff`。

### 4.2 Dark 模式

菜单主体背景色从 `#18181c`（深黑）变为 `rgb(72, 72, 78)`（中灰），与弹出面板统一。这与 NaiveUI Dark 模式下的菜单视觉效果一致。

### 4.3 测试验证

修改后全部 24 项 menu 相关测试通过，无回归。

---

## 5. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `styles/templates/menu.qss.j2` | TMenu 背景色从 `colors.bg_default` 改为 `colors.popover_color` |

---

## 6. 经验总结

### 6.1 弹出式组件应统一使用 popover_color

当组件包含弹出面板（popup/dropdown/popover）时，组件主体与弹出面板应使用同一背景色 Token（`popover_color`），避免在特定主题下出现色差。这是 NaiveUI 的设计规范：弹出式交互组件的所有可见区域在视觉上应作为一个整体。

### 6.2 多主题下的 Token 等价性不可假设

两个不同的 Token 在某个主题下值相同（如 Light 模式下 `bg_default` = `popover_color` = `#ffffff`），不代表在所有主题下都相同。选择 Token 时应基于语义而非当前值，确保在所有主题下都能产生正确的视觉效果。
