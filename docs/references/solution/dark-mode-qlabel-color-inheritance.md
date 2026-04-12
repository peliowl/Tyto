# Dark 模式下 QLabel 文本颜色未正确继承

> **组件**: `TTag`, `TCheckbox`, `TRadio`, `TRadioButton`
> **文件**: `tag.qss.j2`, `checkbox.qss.j2`, `radio.qss.j2`, `radiobutton.qss.j2`
> **日期**: 2026-04-12
> **状态**: 已修复

---

## 目录

1. [问题描述](#1-问题描述)
2. [环境与复现条件](#2-环境与复现条件)
3. [根因分析](#3-根因分析)
4. [影响范围排查](#4-影响范围排查)
5. [解决方案](#5-解决方案)
6. [修改文件清单](#6-修改文件清单)
7. [经验总结](#7-经验总结)

---

## 1. 问题描述

在 Dark 模式下，TTag 的标签文本颜色显示为黑色（或接近黑色），在深色背景上几乎不可见。正确效果应为浅色文本。同类问题存在于 TCheckbox、TRadio、TRadioButton 的标签文本。

### 表现

- Dark 模式下，TTag 的 "Tag" 文本几乎不可见
- 关闭按钮 "✕" 颜色正常（已有显式 QSS `color` 规则）
- Light 模式下文本颜色正常（默认黑色与 `#333639` 接近）

---

## 2. 环境与复现条件

| 项目 | 值 |
|------|-----|
| 框架 | PySide6 (Latest) |
| 操作系统 | Windows |
| Python | 3.12 |
| 复现路径 | Playground → 切换 Dark 模式 → 选择 Tag/Checkbox/Radio 组件 |
| Dark 主题 text_primary | `rgba(255, 255, 255, 0.82)` |

---

## 3. 根因分析

### 3.1 Qt QSS 的 color 属性不可靠继承

在 Qt QSS 中，父组件上设置的 `color` 属性**不会**可靠地传播到子 QLabel 组件。这与 CSS 的行为不同。

以 TTag 为例，QSS 中定义了：

```css
TTag {
    color: {{ colors.text_primary }};  /* Dark: rgba(255,255,255,0.82) */
}

TTag QLabel {
    background-color: transparent;
    border: none;
    /* 缺少 color 属性 — QLabel 使用系统默认黑色 */
}
```

### 3.2 为何 Light 模式下不明显

Light 模式的 `text_primary` 为 `#333639`（深色），QLabel 的默认黑色文本与之接近，视觉差异不明显。Dark 模式下默认黑色文本与深色背景几乎相同，问题才暴露。

---

## 4. 影响范围排查

对全部 25 个 QSS 模板进行了系统排查。

### 4.1 需要修复的模板（4 个）

| 模板 | 问题 |
|------|------|
| `tag.qss.j2` | `TTag QLabel` 缺少 `color` |
| `checkbox.qss.j2` | `TCheckbox QLabel` 缺少 `color` |
| `radio.qss.j2` | `TRadio QLabel` 缺少 `color` |
| `radiobutton.qss.j2` | `TRadioButton QLabel` 缺少 `color` |

### 4.2 已正确设置的模板

`button.qss.j2`、`alert.qss.j2`、`card.qss.j2`、`collapse.qss.j2`、`menu.qss.j2`、`message.qss.j2`、`modal.qss.j2`、`breadcrumb.qss.j2`、`timeline.qss.j2`、`popconfirm.qss.j2`、`spin.qss.j2`、`slider.qss.j2`、`empty.qss.j2` — 均已有显式 QLabel `color` 规则。

### 4.3 不涉及 QLabel 的模板

`input.qss.j2`、`switch.qss.j2`、`inputnumber.qss.j2`、`inputgroup.qss.j2`、`layout.qss.j2`、`searchbar.qss.j2` — 使用 QLineEdit 或自绘，无 QLabel 子组件。

---

## 5. 解决方案

在每个包含 QLabel 子组件的 QSS 模板中，为 QLabel 显式设置 `color` 属性，覆盖所有状态变体。

### 5.1 TTag 修复

```css
TTag QLabel {
    background-color: transparent;
    border: none;
    color: {{ colors.text_primary }};
}

TTag[tagType="primary"] QLabel { color: {{ colors.white }}; }
TTag[checkable="true"][checked="true"] QLabel { color: {{ colors.white }}; }
```

### 5.2 TCheckbox / TRadio 修复

```css
TCheckbox QLabel {
    color: {{ colors.text_primary }};
    background-color: transparent;
}
TCheckbox:disabled QLabel { color: {{ colors.text_disabled }}; }
```

### 5.3 TRadioButton 修复

```css
TRadioButton QLabel { color: {{ colors.text_primary }}; }
TRadioButton[checked="true"] QLabel { color: {{ colors.white }}; }
TRadioButton:hover QLabel { color: {{ colors.primary_hover }}; }
TRadioButton:disabled QLabel { color: {{ colors.text_disabled }}; }
```

---

## 6. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/tyto_ui_lib/styles/templates/tag.qss.j2` | `TTag QLabel` 添加 `color`；所有类型变体和 checkable 状态添加 QLabel color 规则 |
| `src/tyto_ui_lib/styles/templates/checkbox.qss.j2` | 添加 `TCheckbox QLabel` 和 disabled 状态 QLabel 规则 |
| `src/tyto_ui_lib/styles/templates/radio.qss.j2` | 添加 `TRadio QLabel` 和 disabled 状态 QLabel 规则 |
| `src/tyto_ui_lib/styles/templates/radiobutton.qss.j2` | 添加 QLabel color 规则覆盖所有状态 |

---

## 7. 经验总结

### 7.1 Qt QSS color 继承规则

**关键结论**：Qt QSS 中，`color` 属性不会从父组件自动传播到子 QLabel。必须在每个 QLabel 选择器中显式设置 `color`。这与 Web CSS 的可继承 `color` 属性行为不同。

### 7.2 QSS 模板编写规范

1. 每个包含 QLabel 子组件的父组件，必须为 QLabel 显式设置 `color`
2. 父组件的每个状态变体如果改变了 `color`，必须同步添加对应的 QLabel `color` 规则
3. 使用 `objectName` 选择器（如 `QLabel#card_title`）可以精确控制特定 QLabel 的颜色

### 7.3 排查方法

检查 QSS 模板时，搜索所有 `QLabel` 规则，确认每个规则都包含显式的 `color` 属性。缺少 `color` 的 QLabel 规则在 Dark 模式下必然出现文本不可见问题。
