# TButton Circle 模式加载图标居中与颜色问题

> **组件**: `TButton`, `_SpinnerWidget`
> **文件**: `src/tyto_ui_lib/components/atoms/button.py`
> **日期**: 2026-04-12
> **状态**: 已修复

---

## 目录

1. [问题描述](#1-问题描述)
2. [环境与复现条件](#2-环境与复现条件)
3. [根因分析](#3-根因分析)
4. [解决方案](#4-解决方案)
5. [影响范围排查](#5-影响范围排查)
6. [修改文件清单](#6-修改文件清单)
7. [经验总结](#7-经验总结)

---

## 1. 问题描述

TButton 在 Circle + Loading 模式下存在两个视觉缺陷：

### 1.1 加载图标未居中

设置 `circle=True` 和 `loading=True` 时，旋转加载图标偏向左侧，未在圆形按钮中居中显示。

### 1.2 Dark 模式下加载图标不可见

在 Dark 模式下，加载图标颜色为黑色，与深色按钮背景几乎相同，导致图标不可见。

---

## 2. 环境与复现条件

| 项目 | 值 |
|------|-----|
| 框架 | PySide6 (Latest) |
| 操作系统 | Windows |
| Python | 3.12 |
| 复现路径（居中）| Playground → Button → 勾选 Circle + Loading |
| 复现路径（颜色）| Playground → 切换 Dark 模式 → Button → 勾选 Loading |

---

## 3. 根因分析

### 3.1 居中问题

TButton 内部布局为 `[icon_left] [spinner] [label] [icon_right]`。

- `_apply_size_from_tokens()` 设置了水平 content margins，在 circle 模式下将内容区域向内挤压
- `set_loading()` 未隐藏 label，label 文本占据布局空间将 spinner 推向左侧
- spinner 固定 16×16，在大尺寸 circle 按钮中显得过小

### 3.2 颜色问题

原始 SVG 使用 `stroke="currentColor"`：

- Qt `QSvgRenderer` 不支持 CSS `currentColor`，始终解析为黑色
- Dark 主题 `text_primary` 为 `rgba(255, 255, 255, 0.82)`，SVG `stroke` 属性不支持 `rgba()` 语法

---

## 4. 解决方案

### 4.1 居中修复

`_apply_circle_geometry()` 在 circle 模式下归零 margins/spacing 并缩放 spinner：

```python
if self._circle:
    self.setFixedSize(QSize(side, side))
    self._layout.setContentsMargins(0, 0, 0, 0)
    self._layout.setSpacing(0)
    spinner_size = max(12, side // 3)
    self._spinner.setFixedSize(QSize(spinner_size, spinner_size))
```

`set_loading()` 在 circle 模式下隐藏 label：

```python
if loading and self._circle:
    self._label.setVisible(False)
```

### 4.2 颜色修复

SVG 改为模板化颜色注入，`_SpinnerWidget` 新增 `set_color()` 方法。`apply_theme()` 根据按钮类型选择颜色：

- 有色背景按钮：白色 `#ffffff`
- 默认/dashed/text 按钮：`colors.primary`（hex 格式，双主题均有良好对比度）

---

## 5. 影响范围排查

| 组件 | 状态 |
|------|------|
| `TButton._SpinnerWidget` | 已修复 |
| `TInput._InputSpinnerWidget` | 无需修复 — 已有 `_to_svg_color()` |
| `TInputNumber._SpinnerWidget` | 已修复 — `_to_svg_color()` 从 no-op 改为 QColor 转换 |

---

## 6. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/tyto_ui_lib/components/atoms/button.py` | SVG 模板化 + `set_color()`；circle 布局归零；loading 隐藏 label；`_update_spinner_color()` |
| `src/tyto_ui_lib/components/atoms/inputnumber.py` | `_to_svg_color()` 从 no-op 改为 QColor 转换 |

---

## 7. 经验总结

### 7.1 QSvgRenderer 不支持 CSS `currentColor`

Qt `QSvgRenderer` 将 `currentColor` 始终解析为黑色。需使用字符串模板注入实际颜色值。

### 7.2 SVG stroke/fill 不支持 `rgba()` 语法

Design Token 中的 `rgba()` 颜色值必须先转换为 SVG 兼容的 `rgb(r,g,b)` 格式。标准转换函数：

```python
def _to_svg_color(color: str) -> str:
    c = QColor(color.strip())
    if c.isValid():
        return f"rgb({c.red()},{c.green()},{c.blue()})"
    return color.strip()
```

### 7.3 Circle 模式布局特殊处理

Circle 按钮的内部布局需要：content margins 归零、loading 时隐藏 label、spinner 按比例缩放。
