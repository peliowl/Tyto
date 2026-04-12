# 需求文档

## 简介

优化 Tyto UI 组件库中 TMenu 组件的弹出子菜单面板（popup）样式，使其视觉效果对齐 NaiveUI 的 popover/dropdown 风格。当前 popup 面板存在圆角过小、缺少阴影、无间距、边框过重等问题，需要通过调整圆角半径、添加阴影效果、引入面板间距、优化边框样式来实现 NaiveUI 风格的弹出面板视觉效果。

## 术语表

- **Popup**：弹出子菜单面板，当鼠标悬停在水平模式的 TMenuItemGroup 或折叠模式的菜单项组上时显示的浮动面板
- **Design_Token**：设计令牌，定义颜色、间距、圆角、阴影等视觉属性的标准化变量
- **QSS**：Qt Style Sheet，Qt 框架的样式表语言，类似 CSS
- **ThemeEngine**：Tyto 的主题引擎，负责管理和渲染 Design Token 到 QSS
- **Shadow_Effect**：阴影效果，通过 QGraphicsDropShadowEffect 或 QPainter 自绘实现的视觉阴影
- **Translucent_Background**：半透明背景属性（WA_TranslucentBackground），允许窗口背景透明以支持圆角和阴影的组合渲染
- **Inner_Container**：内部容器控件，在 Translucent_Background 的 Popup 窗口内部负责绘制圆角背景和边框的子控件

## 需求

### 需求 1：Popup 圆角优化

**用户故事：** 作为用户，我希望弹出子菜单面板具有与 NaiveUI 一致的圆角效果（8px），使界面看起来更加现代和精致。

#### 验收标准

1. WHEN Popup 显示时，THE Inner_Container SHALL 使用 Design_Token 中 `radius.large`（8px）作为圆角半径进行绘制
2. WHEN 主题切换时，THE Inner_Container SHALL 从 ThemeEngine 重新获取 `radius.large` 的值并更新圆角绘制

### 需求 2：Popup 阴影效果

**用户故事：** 作为用户，我希望弹出子菜单面板具有柔和的阴影效果，使面板在视觉上与背景内容产生层次分离感。

#### 验收标准

1. THE Popup SHALL 通过 QGraphicsDropShadowEffect 应用 Design_Token 中 `shadows.medium` 定义的阴影参数
2. WHEN 主题切换时，THE Popup SHALL 从 ThemeEngine 重新获取阴影参数并更新 Shadow_Effect
3. WHEN Popup 显示时，THE Popup SHALL 设置 Translucent_Background 属性以确保阴影在窗口边界外正确渲染

### 需求 3：Popup 内部容器自绘

**用户故事：** 作为开发者，我希望 Popup 使用内部容器自绘背景和边框，以便在 Translucent_Background 模式下正确渲染圆角和背景色。

#### 验收标准

1. THE Popup SHALL 包含一个 Inner_Container 子控件，该控件通过 QPainter 自绘圆角矩形背景
2. WHEN Inner_Container 绘制时，THE Inner_Container SHALL 使用 Design_Token 中 `colors.popover_color` 作为背景色
3. WHEN Inner_Container 绘制时，THE Inner_Container SHALL 使用 Design_Token 中 `colors.divider` 作为边框颜色，绘制 1px 宽度的边框
4. WHEN 主题切换时，THE Inner_Container SHALL 从 ThemeEngine 重新获取颜色 Token 并触发重绘

### 需求 4：Popup 与父菜单间距

**用户故事：** 作为用户，我希望弹出子菜单面板与父菜单之间有适当的间距，使两者在视觉上清晰分离。

#### 验收标准

1. WHEN Popup 在水平模式下方弹出时，THE Popup SHALL 与父菜单项之间保持 Design_Token 中 `spacing.small`（4px）的垂直间距
2. WHEN Popup 在侧边弹出时（嵌套子菜单或折叠模式），THE Popup SHALL 与父菜单之间保持 Design_Token 中 `spacing.small`（4px）的水平间距

### 需求 5：Popup 内边距与布局

**用户故事：** 作为用户，我希望弹出面板内的菜单项有适当的内边距，使内容不会紧贴面板边缘。

#### 验收标准

1. THE Inner_Container SHALL 在垂直方向上设置 Design_Token 中 `spacing.small`（4px）的内边距
2. THE Inner_Container SHALL 在水平方向上不设置额外内边距（菜单项自身已有水平内边距）

### 需求 6：主题兼容性

**用户故事：** 作为用户，我希望弹出面板在 Light 和 Dark 主题下都能正确显示，包括背景色、边框色和阴影效果。

#### 验收标准

1. WHEN Light 主题激活时，THE Inner_Container SHALL 使用 Light 主题的 `popover_color`（#ffffff）作为背景色
2. WHEN Dark 主题激活时，THE Inner_Container SHALL 使用 Dark 主题的 `popover_color`（rgb(72, 72, 78)）作为背景色
3. WHEN 主题从 Light 切换到 Dark（或反向）时，THE Popup SHALL 在无需关闭重开的情况下实时更新所有视觉属性
