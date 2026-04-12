# TMenu 折叠按钮圆形边框裁剪问题

> **组件**: `TMenu` / `_CollapseToggleButton`
> **文件**: `src/tyto_ui_lib/components/organisms/menu.py`
> **关联文档**: [menu-collapse-toggle-bugfix.md](./menu-collapse-toggle-bugfix.md)
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

TMenu 组件的边栏折叠切换按钮（`_CollapseToggleButton`）是一个通过 `QPainter` 自绘的圆形按钮，定位在菜单右边缘、半突出于菜单边界之外。在实际渲染中，圆形边框的上方和左方各有约 1px 被裁剪，导致圆形不完整。

### 表现

- 圆形边框的右侧和下侧正常显示
- 圆形边框的上侧和左侧各缺失约 1px，边框线直接消失
- 问题在 Light 和 Dark 主题下均可复现

---

## 2. 环境与复现条件

| 项目 | 值 |
|------|-----|
| 框架 | PySide6 (Latest) |
| 操作系统 | Windows |
| Python | 3.12 |
| 复现路径 | Playground → 选择 Menu 组件 → 观察右侧折叠按钮 |
| 按钮尺寸 | 28×28px（由 Design Token `component_sizes.small.height` 决定） |

---

## 3. 根因分析

### 3.1 QPainter.drawEllipse 的坐标语义

`QPainter.drawEllipse(x, y, width, height)` 在开启抗锯齿（`RenderHint.Antialiasing`）时，描边（stroke）以几何路径为中心向两侧扩展。对于 `pen_width = 1.0` 的描边，路径两侧各扩展 0.5px。

### 3.2 原始代码的问题

原始代码直接在 widget 的完整区域绘制椭圆：

```python
# 原始代码（有问题）
painter.drawEllipse(0, 0, w, h)
```

此时椭圆的几何边界恰好在 widget 的 `(0, 0)` 和 `(w, h)` 处。1px 描边向外扩展 0.5px，导致：

- 上边界：描边从 `y = -0.5` 到 `y = 0.5`，其中 `y < 0` 的部分超出 widget 边界被裁剪
- 左边界：描边从 `x = -0.5` 到 `x = 0.5`，其中 `x < 0` 的部分超出 widget 边界被裁剪
- 下边界和右边界：描边从 `y = h - 0.5` 到 `y = h + 0.5`，超出部分同样被裁剪

### 3.3 为何只有上方和左方可见

Qt 的抗锯齿渲染在亚像素级别存在不对称性。`drawEllipse(0, 0, w, h)` 的几何中心在 `(w/2, h/2)`，当 `w` 和 `h` 为偶数（如 28）时：

- 上方和左方的描边亚像素落在 `y ∈ [-0.5, 0.5)` 和 `x ∈ [-0.5, 0.5)` 区间，被 widget 边界裁剪后视觉上缺失明显
- 下方和右方的描边亚像素落在 `y ∈ [h-0.5, h+0.5)` 和 `x ∈ [w-0.5, w+0.5)` 区间，由于像素对齐方向的差异，视觉上缺失不明显

这是 Qt 的 `QPainter` 在整数像素坐标系下的已知行为特征。

---

## 4. 排查过程

### 第一轮：inset = pen_width / 2（0.5px）

将绘制区域向内缩进半个描边宽度：

```python
pen_width = 1.0
inset = pen_width / 2.0  # 0.5
painter.drawEllipse(inset, inset, w - pen_width, h - pen_width)
```

**结果**：上方和左方仍有约 1px 裁剪。原因是 0.5px 的 inset 在抗锯齿渲染下仍不足以将所有亚像素完全收入 widget 边界内。

### 第二轮：在 TMenu.paintEvent 中调用 raise_()

怀疑是 z-order 问题（TMenu 的背景绘制覆盖了按钮），在 TMenu 的 `paintEvent` 结束后调用 `self._collapse_toggle.raise_()`。

**结果**：无效。问题不是 z-order 导致的遮挡，而是 QPainter 的亚像素裁剪。

### 第三轮：inset = 1.0px（最终方案）

将 inset 增大到 1 个完整像素：

```python
pen_width = 1.0
inset = 1.0
painter.drawEllipse(inset, inset, w - inset * 2, h - inset * 2)
```

**结果**：圆形边框四个方向均完整显示，问题解决。

---

## 5. 解决方案

### 5.1 核心修改

在 `_CollapseToggleButton.paintEvent` 中，将椭圆绘制区域向内缩进 1 个完整像素，确保抗锯齿描边的所有亚像素都落在 widget 边界内：

```python
def paintEvent(self, event: object) -> None:
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    w = self.width()
    h = self.height()

    # Inset by 1 full pixel so the anti-aliased stroke never touches
    # the widget boundary (prevents top/left 1px clipping artifacts).
    pen_width = 1.0
    inset = 1.0

    # Draw circular background
    bg = parse_color(self._bg_color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(bg)
    painter.drawEllipse(inset, inset, w - inset * 2, h - inset * 2)

    # Draw circular border
    border_color = parse_color(self._border_color)
    painter.setPen(QPen(border_color, pen_width))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(inset, inset, w - inset * 2, h - inset * 2)

    # ... chevron icon drawing unchanged
```

### 5.2 辅助修改

在 `TMenu.paintEvent` 中，背景绘制完成后确保折叠按钮保持在最上层 z-order，防止菜单背景重绘覆盖按钮的重叠区域：

```python
def paintEvent(self, event: object) -> None:
    painter = QPainter(self)
    bg = getattr(self, "_menu_bg_color", None)
    if bg:
        painter.fillRect(self.rect(), parse_color(bg))
    painter.end()
    # Ensure the collapse toggle stays above the menu background.
    if hasattr(self, "_collapse_toggle") and self._collapse_toggle.isVisible():
        self._collapse_toggle.raise_()
```

### 5.3 视觉影响

圆形直径从 28px 缩小到 26px（每边各减少 1px），视觉差异极小，肉眼几乎不可察觉。

---

## 6. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `src/tyto_ui_lib/components/organisms/menu.py` | `_CollapseToggleButton.paintEvent`：椭圆 inset 从 0 调整为 1.0px |
| `src/tyto_ui_lib/components/organisms/menu.py` | `TMenu.paintEvent`：添加 `_collapse_toggle.raise_()` 调用 |

---

## 7. 经验总结

### 7.1 QPainter 抗锯齿描边的安全边距规则

在使用 `QPainter` 绘制带描边的图形时，如果开启了抗锯齿（`Antialiasing`），绘制区域必须向内缩进至少 1 个完整像素（而非仅 `pen_width / 2`）。这是因为：

- 抗锯齿渲染会在描边边缘产生亚像素混合
- 亚像素混合可能扩展到几何边界之外 0.5 ~ 1px
- Widget 边界会硬裁剪所有超出区域的像素

**推荐公式**：

```python
inset = max(pen_width, 1.0)
painter.drawEllipse(inset, inset, w - inset * 2, h - inset * 2)
```

### 7.2 适用范围

此规则适用于所有通过 `QPainter` 自绘的圆形、圆角矩形等带描边的图形控件，包括但不限于：

- `_CollapseToggleButton`（本次修复）
- 自定义圆形按钮
- 带圆角边框的自绘面板

### 7.3 与 NaiveUI 风格的一致性

NaiveUI 的折叠按钮同样采用圆形边框设计。本次修复后，Tyto 的折叠按钮在视觉上与 NaiveUI 保持一致，圆形边框完整无裁剪。
