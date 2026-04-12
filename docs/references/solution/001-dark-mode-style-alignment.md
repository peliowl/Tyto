# SOL-001: Dark 模式样式对齐 NaiveUI 标准

| 属性 | 值 |
|------|-----|
| 编号 | SOL-001 |
| 版本 | V1.1.0+ |
| 状态 | 已解决 |
| 影响范围 | InputNumber, Slider, Alert, Collapse, Switch |
| 关联需求 | user_task.md — 严格按照 NaiveUI 样式更新控件 |

---

## 1. 问题描述

在将 Tyto 组件库的 dark 模式样式对齐 NaiveUI 标准的过程中，发现以下问题：

1. **Design Token 值偏差**：`dark.json` 中多个颜色 token 与 NaiveUI dark 主题的实际值不一致（如 `text_secondary`、`text_disabled`、`border` 的 alpha 值偏差）。
2. **Token 键缺失**：NaiveUI dark 主题中使用的多个语义化颜色（如 `inputColor`、`railColor`、`dividerColor`、`popoverColor`）在 Tyto 的 token 体系中没有对应定义。
3. **Alert 组件**：背景色和边框色使用了简单的主色 alpha 叠加，而非 NaiveUI 的 `*ColorSuppl` 体系。
4. **Collapse 组件**：使用 `bg_default` 作为背景和 `border` 作为分隔线，与 NaiveUI 的透明背景 + `dividerColor` 分隔线风格不一致。

## 2. 根因分析

### 2.1 Token 值偏差

对比 NaiveUI 源码 `src/_styles/common/dark.ts`，Tyto 的 `dark.json` 存在以下偏差：

| Token | Tyto 旧值 | NaiveUI 标准值 | 说明 |
|-------|----------|---------------|------|
| `text_secondary` | `rgba(255,255,255,0.50)` | `rgba(255,255,255,0.52)` | alpha3 = 0.52 |
| `text_disabled` | `rgba(255,255,255,0.24)` | `rgba(255,255,255,0.38)` | alpha4 = 0.38 |
| `border` | `rgba(255,255,255,0.12)` | `rgba(255,255,255,0.24)` | alphaBorder = 0.24 |

### 2.2 Token 键缺失

NaiveUI 的组件主题系统使用了多个 Tyto 未定义的语义化颜色：

| NaiveUI 变量 | 用途 | 计算方式 |
|-------------|------|---------|
| `inputColor` | 输入框背景 | `overlay(alphaInput)` = `rgba(255,255,255,0.1)` |
| `railColor` | 滑动条轨道 | `overlay(alphaRail)` = `rgba(255,255,255,0.2)` |
| `dividerColor` | 分隔线 | `overlay(alphaDivider)` = `rgba(255,255,255,0.09)` |
| `popoverColor` | 弹出层背景 | `rgb(72,72,78)` |
| `textColor1` | 标题文本 | `overlay(alpha1)` = `rgba(255,255,255,0.9)` |

### 2.3 Alert 背景色体系差异

NaiveUI dark 模式下 Alert 使用 `*ColorSuppl`（补充色）而非主色：

- 背景：`changeColor(*ColorSuppl, { alpha: 0.25 })`
- 边框：`changeColor(*ColorSuppl, { alpha: 0.35 })`

例如 success 类型：`successColorSuppl = rgb(42, 148, 125)`，背景为 `rgba(42,148,125,0.25)`。

## 3. 解决方案

### 3.1 修正 Token 值

更新 `dark.json` 中的偏差值，使其与 NaiveUI `src/_styles/common/dark.ts` 完全一致。

### 3.2 扩展 Token 键

在 `light.json` 和 `dark.json` 中新增以下 token，确保两套主题键集合一致：

```
colors.input_color          — 输入框背景色
colors.input_color_disabled — 输入框禁用背景色
colors.text_title           — 标题文本色（NaiveUI textColor1）
colors.text_placeholder     — 占位符文本色
colors.divider              — 分隔线颜色
colors.rail_color           — 滑动条轨道颜色
colors.popover_color        — 弹出层背景色
colors.indicator_color      — 滑动条 tooltip 背景色
colors.close_icon           — 关闭按钮图标色
colors.close_hover_bg       — 关闭按钮悬停背景色
colors.close_pressed_bg     — 关闭按钮按下背景色
colors.alert_*_border       — Alert 各类型边框色
colors.hover_color          — 悬停背景色
colors.pressed_color        — 按下背景色
```

### 3.3 更新 QSS 模板

- **alert.qss.j2**：标题使用 `text_title`，描述使用 `text_primary`，默认边框使用 `divider`，各类型使用 `alert_*_border` 边框色，关闭按钮使用 `close_icon` / `close_hover_bg`。
- **collapse.qss.j2**：背景改为透明，分隔线使用 `divider`，标题使用 `text_title`，箭头使用 `text_primary`。
- **slider.qss.j2**：tooltip 使用 `indicator_color` 背景 + `white` 文字。
- **inputnumber.qss.j2**：无模板结构变更，token 值更新自动生效。

### 3.4 更新组件 paintEvent

InputNumber 的 `paintEvent` 中背景色从 `bg_default` 改为 `input_color`，使 dark 模式下输入框呈现 NaiveUI 标准的半透明白色叠加效果。

## 4. 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `styles/tokens/dark.json` | 修改 | 修正偏差值，新增 20+ token 键 |
| `styles/tokens/light.json` | 修改 | 新增对应 token 键保持键集合一致 |
| `styles/templates/alert.qss.j2` | 重写 | 对齐 NaiveUI Alert 样式体系 |
| `styles/templates/collapse.qss.j2` | 重写 | 对齐 NaiveUI Collapse 样式体系 |
| `styles/templates/slider.qss.j2` | 修改 | tooltip 使用 indicator_color |
| `styles/templates/inputnumber.qss.j2` | 修改 | 按钮 pressed 色使用 primary_pressed |
| `components/atoms/inputnumber.py` | 修改 | paintEvent 背景色改用 input_color |
| `components/atoms/slider.py` | 修改 | 轨道色改用 rail_color，tooltip 改用 indicator_color |

## 5. 验证

- 394 个单元测试全部通过
- Gallery 中 InputNumber、Slider、Alert、Collapse 在 light/dark 模式下视觉效果与 NaiveUI 参考一致
