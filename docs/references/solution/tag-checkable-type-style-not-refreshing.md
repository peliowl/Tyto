# TTag Checkable 模式下切换 Type 属性样式未实时刷新

> **组件**: `TTag`
> **文件**: `src/tyto_ui_lib/components/atoms/tag.py`, `src/tyto_ui_lib/styles/templates/tag.qss.j2`
> **日期**: 2026-04-12
> **状态**: 已修复

---

## 目录

1. [问题描述](#1-问题描述)
2. [环境与复现条件](#2-环境与复现条件)
3. [根因分析](#3-根因分析)
4. [解决方案](#4-解决方案)
5. [修改文件清单](#5-修改文件清单)
6. [经验总结](#6-经验总结)

---

## 1. 问题描述

在 Playground 中，当 TTag 设置 `checkable=True` 并点击选中后，通过属性面板切换 `tag_type`（如从 `default` 切换到 `warning`），标签的背景色未实时更新为对应类型的颜色，始终显示为 `primary` 绿色。

### 表现

- 设置 `checkable=True`，点击标签使其进入 `checked=true` 状态
- 切换 `tag_type` 为 `warning`、`error` 等类型
- 背景色始终为 `colors.primary`（绿色），未切换为对应类型颜色

---

## 2. 环境与复现条件

| 项目 | 值 |
|------|-----|
| 框架 | PySide6 (Latest) |
| 操作系统 | Windows |
| Python | 3.12 |
| 复现路径 | Playground → 选择 Tag → 勾选 Checkable → 点击标签选中 → 切换 Type 下拉框 |

---

## 3. 根因分析

### 3.1 QSS 选择器缺失

`tag.qss.j2` 中仅定义了通用的 checkable+checked 选择器：

```css
TTag[checkable="true"][checked="true"] {
    background-color: {{ colors.primary }};
    color: {{ colors.white }};
    border-color: {{ colors.primary }};
}
```

该选择器不区分 `tagType`，导致所有已选中的 checkable 标签都显示为 `primary` 颜色。缺少类型特定的三属性组合选择器（如 `TTag[checkable="true"][checked="true"][tagType="warning"]`）。

### 3.2 Playground 直接操作私有属性

`tag_props.py` 中的 `_apply_tag_type` 直接操作 `w._tag_type` 私有属性，而非通过公开 setter 方法。虽然调用了 `_repolish()`，但由于 QSS 中缺少对应的组合选择器，repolish 无法匹配到正确的样式规则。

---

## 4. 解决方案

### 4.1 QSS 模板：添加类型特定的 checkable 选择器

在 `tag.qss.j2` 中为每种 `tagType` 添加 `checkable+checked` 和 `checkable+unchecked` 的组合选择器：

```css
/* Checkable checked — type-specific */
TTag[checkable="true"][checked="true"][tagType="warning"] {
    background-color: {{ colors.warning }};
    border-color: {{ colors.warning }};
}

/* Checkable unchecked — type-specific */
TTag[checkable="true"][checked="false"][tagType="warning"] {
    background-color: {{ colors.bg_elevated }};
    color: {{ colors.warning }};
    border-color: {{ colors.warning }};
}
```

为 `primary`、`success`、`info`、`warning`、`error` 五种类型均添加了对应规则。

### 4.2 组件类：添加公开 setter 方法

在 `TTag` 中新增 `set_tag_type()`、`set_size()`、`set_checkable()` 公开方法：

```python
def set_tag_type(self, tag_type: TagType) -> None:
    self._tag_type = tag_type
    self.setProperty("tagType", tag_type.value)
    self._repolish()
```

### 4.3 Playground：使用公开 API

将 `tag_props.py` 中的 `_apply_tag_type`、`_apply_tag_size`、`_apply_checkable` 改为调用公开 setter，消除对私有属性的直接访问。

同步修复了 `TButton` 的相同问题：新增 `set_button_type()` 方法，更新 `button_props.py`。

---

## 5. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/tyto_ui_lib/styles/templates/tag.qss.j2` | 添加 5 种类型的 checkable+checked 和 checkable+unchecked 组合选择器 |
| `src/tyto_ui_lib/components/atoms/tag.py` | 新增 `set_tag_type()`、`set_size()`、`set_checkable()` 公开方法 |
| `src/tyto_ui_lib/components/atoms/button.py` | 新增 `set_button_type()` 公开方法 |
| `examples/playground/definitions/tag_props.py` | `_apply_tag_type`、`_apply_tag_size`、`_apply_checkable` 改用公开 setter |
| `examples/playground/definitions/button_props.py` | `_apply_button_type` 改用公开 setter |

---

## 6. 经验总结

### 6.1 QSS 多属性选择器的优先级规则

Qt QSS 中，属性选择器的数量决定特异性（specificity）。三属性选择器 `[a][b][c]` 优先于二属性选择器 `[a][b]`。当组件同时具有多个 QSS 动态属性时，必须为所有有效组合提供对应的选择器规则。

### 6.2 Playground 属性应用的最佳实践

Playground 的属性定义应始终通过组件的公开 setter 方法修改属性，而非直接操作私有属性。公开 setter 封装了属性更新、QSS 动态属性设置和 repolish 的完整流程，确保样式一致性。
