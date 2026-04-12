# 需求文档：TCollapse 箭头图标变形修复

## 简介

TCollapse 组件的展开/折叠箭头图标存在视觉缺陷。由于 QSS 模板中仅约束了箭头控件的宽度而未约束高度，箭头控件在 QHBoxLayout 中被垂直拉伸至与 header 等高（≥32px），导致 `paintEvent` 中的非等比缩放使 chevron 图标呈现为波浪形/扭曲形状，而非 NaiveUI 风格的干净 chevron（">"）图标。

## 术语表

- **Arrow_Widget**：`_CollapseArrowWidget`，负责绘制 chevron 箭头图标的内部 QWidget
- **QSS_Template**：`collapse.qss.j2`，TCollapse 组件的 Jinja2 QSS 样式模板
- **Uniform_Scaling**：等比缩放，使用 scale_x 和 scale_y 中的较小值进行缩放，保持图标宽高比不变
- **Icon_Size**：Design Token 中定义的图标尺寸（medium 为 18px）
- **Chevron_Path**：NaiveUI ChevronRight SVG 路径数据（viewBox 0 0 16 16）

## 需求

### 需求 1：箭头控件高度约束

**用户故事：** 作为用户，我希望 TCollapse 的箭头图标保持正方形比例，以便箭头不会因布局拉伸而变形。

#### 验收标准

1. THE QSS_Template SHALL 为 `collapse_arrow` 控件同时定义 `min-height` 和 `max-height` 约束，其值与 `min-width` 和 `max-width` 一致，均引用 `component_sizes.medium.icon_size` Token
2. WHEN Arrow_Widget 被放置在 QHBoxLayout 中时，THE Arrow_Widget SHALL 保持宽度与高度相等的正方形尺寸

### 需求 2：等比缩放绘制

**用户故事：** 作为用户，我希望箭头图标在任何控件尺寸下都保持正确的宽高比，以便即使控件尺寸不完全为正方形时图标也不会变形。

#### 验收标准

1. WHEN Arrow_Widget 执行 `paintEvent` 时，THE Arrow_Widget SHALL 使用 Uniform_Scaling（取 scale_x 和 scale_y 的较小值）来缩放 Chevron_Path
2. WHEN Uniform_Scaling 导致绘制区域小于控件尺寸时，THE Arrow_Widget SHALL 将 Chevron_Path 居中绘制在控件区域内
3. FOR ALL 有效的控件宽度 w 和高度 h，对 Chevron_Path 进行缩放后，路径的宽高比 SHALL 与原始 viewBox（16×16）中的宽高比保持一致

### 需求 3：箭头旋转行为保持不变

**用户故事：** 作为用户，我希望修复后的箭头图标仍然能正确旋转以指示展开/折叠状态。

#### 验收标准

1. WHEN TCollapseItem 处于折叠状态时，THE Arrow_Widget SHALL 以 0 度旋转绘制 chevron（指向右方）
2. WHEN TCollapseItem 处于展开状态时，THE Arrow_Widget SHALL 以 90 度旋转绘制 chevron（指向下方）
3. WHEN 展开状态切换时，THE Arrow_Widget SHALL 立即更新旋转角度并重绘

### 需求 4：主题兼容性

**用户故事：** 作为用户，我希望修复后的箭头在 Light 和 Dark 主题下都能正确显示。

#### 验收标准

1. WHEN 主题从 Light 切换到 Dark（或反向）时，THE Arrow_Widget SHALL 使用当前主题的 `text_primary` 颜色绘制箭头
2. THE QSS_Template SHALL 在 disabled 状态下继续使用 `text_disabled` 颜色约束箭头控件
