# TCollapse 组件视觉缺陷修复 — 需求文档

## 概述

TCollapse 组件存在 4 个视觉缺陷，需要修复以与 NaiveUI 的 Collapse 效果保持一致。

---

## 用户故事

### 用户故事 1: 箭头图标与标题文本间距

作为用户，我希望 collapse 的展开/收缩箭头图标与标题文本之间的间距与 NaiveUI 保持一致，使界面看起来紧凑协调。

#### 验收标准

- 1.1 arrow_placement="left" 时，箭头右侧与标题文本之间的间距为 4px（通过 `spacing.small` token）
- 1.2 arrow_placement="right" 时，箭头左侧与标题文本之间的间距为 4px（通过 `spacing.small` token）
- 1.3 箭头容器不应有多余的固定宽度，宽度应由图标内容自适应决定（约 18px）

### 用户故事 2: 箭头图标形状与大小

作为用户，我希望 collapse 的展开/收缩图标使用与 NaiveUI 一致的 chevron-right（">"）形状 SVG 图标，而非实心三角形 Unicode 字符。

#### 验收标准

- 2.1 收缩状态下，箭头显示为朝右的 chevron（">"）形状 SVG 图标
- 2.2 展开状态下，箭头通过旋转 90 度变为朝下方向
- 2.3 箭头图标大小为 18px，与 NaiveUI 的 `font-size: 18px` 一致（通过 `component_sizes.medium.icon_size` token）
- 2.4 箭头颜色使用 `colors.text_primary` token，与 NaiveUI 的 `arrowColor: textColor2` 对应

### 用户故事 3: arrow_placement="right" 时箭头位置

作为用户，我希望设置 arrow_placement="right" 时，箭头图标正确显示在标题文本的右侧末端。

#### 验收标准

- 3.1 arrow_placement="right" 时，标题文本在左侧占满剩余空间，箭头紧贴右侧
- 3.2 arrow_placement="right" 时，箭头与标题之间仅有 4px 间距（margin-left）
- 3.3 arrow_placement 在 "left" 和 "right" 之间切换时，布局正确重建

### 用户故事 4: 内容项交界处分割线

作为用户，我希望 collapse 中各面板之间显示分割线，且第一个面板上方不显示分割线，与 NaiveUI 效果一致。

#### 验收标准

- 4.1 第一个 TCollapseItem 上方不显示 border-top 分割线
- 4.2 第二个及后续 TCollapseItem 上方显示 1px 的分割线，颜色使用 `colors.divider` token
- 4.3 分割线在 Light 和 Dark 主题下均正确显示
