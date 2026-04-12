# 需求文档

## 简介

为 Tyto UI 组件库的 TMenu 组件增加一个内置的折叠/展开切换按钮（Collapse Toggle Button）。该按钮仅在垂直模式下显示，位于菜单右边缘并半露出菜单边界，对标 NaiveUI Menu 的 collapsed sidebar 视觉效果。点击按钮可在 collapsed（图标模式）和 expanded（完整模式）之间切换。

## 术语表

- **TMenu**: Tyto UI 组件库中的菜单组件，支持垂直和水平两种布局模式
- **Collapse_Toggle_Button**: 圆形切换按钮，位于 TMenu 右边缘，用于切换 collapsed 状态
- **Collapsed_Mode**: 菜单的压缩模式，仅显示图标，隐藏文字标签
- **Expanded_Mode**: 菜单的展开模式，同时显示图标和文字标签
- **Design_Token**: 设计令牌，定义颜色、间距、尺寸等视觉属性的抽象变量
- **Chevron_Icon**: V 形箭头图标，用于指示展开/收缩方向
- **Playground**: 组件演示环境，用于交互式预览和调试组件

## 需求

### 需求 1：折叠切换按钮的创建与定位

**用户故事：** 作为开发者，我希望 TMenu 在垂直模式下提供一个可见的切换按钮，以便用户可以直观地切换菜单的折叠/展开状态。

#### 验收标准

1. WHEN TMenu is in vertical mode, THE Collapse_Toggle_Button SHALL be rendered as a circular button positioned at the vertical center of the menu's right edge
2. WHEN TMenu is in vertical mode, THE Collapse_Toggle_Button SHALL protrude beyond the menu's right boundary to create a half-exposed visual effect
3. WHEN TMenu is in horizontal mode, THE Collapse_Toggle_Button SHALL remain hidden
4. WHEN TMenu switches from vertical mode to horizontal mode, THE Collapse_Toggle_Button SHALL be hidden automatically
5. WHEN TMenu switches from horizontal mode to vertical mode, THE Collapse_Toggle_Button SHALL be shown automatically

### 需求 2：折叠切换按钮的交互行为

**用户故事：** 作为用户，我希望点击切换按钮能够在折叠和展开状态之间切换菜单，以便我可以控制侧边栏的宽度。

#### 验收标准

1. WHEN the user clicks the Collapse_Toggle_Button while TMenu is in Expanded_Mode, THE TMenu SHALL transition to Collapsed_Mode
2. WHEN the user clicks the Collapse_Toggle_Button while TMenu is in Collapsed_Mode, THE TMenu SHALL transition to Expanded_Mode
3. WHEN TMenu transitions to Collapsed_Mode via the Collapse_Toggle_Button, THE TMenu SHALL invoke the existing set_collapsed method to perform the transition
4. WHEN the Collapse_Toggle_Button is clicked, THE Collapse_Toggle_Button SHALL update its Chevron_Icon direction to reflect the new state

### 需求 3：折叠切换按钮的视觉表现

**用户故事：** 作为开发者，我希望切换按钮的视觉风格与 NaiveUI 一致，以便保持组件库的设计统一性。

#### 验收标准

1. WHILE TMenu is in Expanded_Mode, THE Collapse_Toggle_Button SHALL display a left-pointing chevron indicating the collapse direction
2. WHILE TMenu is in Collapsed_Mode, THE Collapse_Toggle_Button SHALL display a right-pointing chevron indicating the expand direction
3. THE Collapse_Toggle_Button SHALL obtain all visual properties (background color, border color, icon color, size) from Design_Token values
4. WHEN the user hovers over the Collapse_Toggle_Button, THE Collapse_Toggle_Button SHALL display a hover state with a distinct background color obtained from Design_Token values
5. WHEN the active theme changes, THE Collapse_Toggle_Button SHALL update its appearance to match the new theme

### 需求 4：与现有 collapsed API 的集成

**用户故事：** 作为开发者，我希望切换按钮与 TMenu 现有的 collapsed API 保持同步，以便程序化控制和按钮控制产生一致的结果。

#### 验收标准

1. WHEN set_collapsed is called programmatically, THE Collapse_Toggle_Button SHALL update its Chevron_Icon direction to match the new collapsed state
2. WHEN the Collapse_Toggle_Button triggers a state change, THE TMenu SHALL use the existing set_collapsed method to perform the transition
3. WHEN TMenu is initialized with collapsed=True, THE Collapse_Toggle_Button SHALL display the correct Chevron_Icon direction for Collapsed_Mode

### 需求 5：Playground 演示更新

**用户故事：** 作为开发者，我希望在 Playground 中能够看到折叠切换按钮的效果，以便我可以交互式地测试和预览该功能。

#### 验收标准

1. WHEN the menu Playground is loaded, THE Playground SHALL display TMenu with the Collapse_Toggle_Button visible in vertical mode
2. WHEN the user interacts with the Collapse_Toggle_Button in the Playground, THE Playground SHALL reflect the collapsed/expanded state change in real time

### 需求 6：禁用状态处理

**用户故事：** 作为开发者，我希望当菜单被禁用时，切换按钮也相应禁用，以便保持一致的交互状态。

#### 验收标准

1. WHILE TMenu is in disabled state, THE Collapse_Toggle_Button SHALL be visually dimmed and non-interactive
2. WHEN TMenu transitions from disabled to enabled state, THE Collapse_Toggle_Button SHALL restore its interactive behavior and normal appearance
