# 需求文档：TMenu 组件重新实现

## 简介

按照 NaiveUI Menu 控件的视觉效果和交互行为，重新实现 Tyto 组件库的 TMenu 菜单组件。新实现需支持水平/垂直两种布局模式、多级嵌套菜单、图标、展开/收缩动画、折叠模式（仅显示图标）、分组标题，以及选中项高亮等功能。组件位于 organisms 层级，继承 BaseWidget，样式通过 Design Token + Jinja2 QSS 渲染。

## 术语表

- **TMenu**：顶层菜单容器组件，管理菜单项集合、布局模式和全局状态
- **TMenuItem**：叶子菜单项，包含 key、label、可选图标，可被选中
- **TMenuItemGroup**：可展开/收缩的子菜单分组，包含子项（TMenuItem 或嵌套 TMenuItemGroup）
- **MenuMode**：菜单布局模式枚举，包含 VERTICAL（垂直）和 HORIZONTAL（水平）
- **Design_Token**：设计令牌，定义颜色、间距、字号等视觉属性的语义化变量
- **QSS**：Qt Style Sheet，Qt 框架的样式表语言
- **折叠模式（Collapsed Mode）**：垂直菜单的紧凑显示模式，仅显示图标，隐藏文字标签
- **路由感知（Route Awareness）**：根据路由路径自动匹配并高亮对应菜单项的功能

## 需求

### 需求 1：多级菜单结构

**用户故事：** 作为开发者，我希望菜单支持多级嵌套结构，以便构建复杂的导航层级。

#### 验收标准

1. THE TMenu SHALL 支持添加 TMenuItem 和 TMenuItemGroup 作为顶层子项
2. THE TMenuItemGroup SHALL 支持添加 TMenuItem 和嵌套的 TMenuItemGroup 作为子项，形成多级嵌套
3. WHEN 通过 add_item 方法添加子项时，THE TMenu SHALL 将子项插入到布局中并连接信号
4. THE TMenuItem SHALL 包含唯一的 key 标识符和 label 显示文本

### 需求 2：菜单项图标支持

**用户故事：** 作为开发者，我希望菜单项标题前能设置图标，以便提升菜单的可识别性和视觉效果。

#### 验收标准

1. THE TMenuItem SHALL 支持通过 icon 参数设置 QIcon 图标，图标显示在 label 文本左侧
2. THE TMenuItemGroup SHALL 支持通过 icon 参数设置 QIcon 图标，图标显示在 label 文本左侧
3. WHEN icon 参数为 None 时，THE TMenuItem SHALL 隐藏图标区域
4. WHEN 处于折叠模式时，THE TMenuItem SHALL 仅显示图标，隐藏文字标签

### 需求 3：水平布局模式

**用户故事：** 作为开发者，我希望菜单支持水平方向布局，以便用于顶部导航栏场景。

#### 验收标准

1. WHEN MenuMode 设置为 HORIZONTAL 时，THE TMenu SHALL 使用水平布局（QHBoxLayout）排列顶层菜单项
2. WHEN MenuMode 设置为 HORIZONTAL 时，THE TMenuItemGroup SHALL 以弹出下拉菜单的方式展示子项
3. WHEN 水平模式下鼠标悬停在 TMenuItemGroup 上时，THE TMenuItemGroup SHALL 显示弹出子菜单
4. WHEN 水平模式下鼠标离开 TMenuItemGroup 及其弹出子菜单时，THE TMenuItemGroup SHALL 在延迟后隐藏弹出子菜单
5. WHEN 水平模式下存在多级嵌套时，THE TMenuItemGroup SHALL 以级联弹出方式展示子菜单（子菜单从父菜单右侧弹出）
6. WHEN 水平模式下菜单项被选中时，THE TMenuItem SHALL 在底部显示高亮指示条（border-bottom）

### 需求 4：垂直布局模式

**用户故事：** 作为开发者，我希望菜单支持垂直方向布局，以便用于侧边栏导航场景。

#### 验收标准

1. WHEN MenuMode 设置为 VERTICAL 时，THE TMenu SHALL 使用垂直布局（QVBoxLayout）排列菜单项
2. WHEN 垂直模式下 TMenuItemGroup 展开时，THE TMenuItemGroup SHALL 显示子项列表，子项相对父项有递进缩进
3. WHEN 垂直模式下 TMenuItemGroup 收缩时，THE TMenuItemGroup SHALL 隐藏子项列表
4. WHEN 垂直模式下点击 TMenuItemGroup 头部时，THE TMenuItemGroup SHALL 切换展开/收缩状态，并播放平滑的高度动画
5. WHEN 垂直模式下 TMenuItemGroup 展开时，THE TMenuItemGroup SHALL 在头部右侧显示向上箭头指示符
6. WHEN 垂直模式下 TMenuItemGroup 收缩时，THE TMenuItemGroup SHALL 在头部右侧显示向下箭头指示符
7. THE TMenuItemGroup SHALL 根据嵌套层级递增缩进量，每级缩进量由 Design_Token 中的 menu.indent 值决定
8. WHEN 垂直模式下菜单项被选中时，THE TMenuItem SHALL 在左侧显示高亮指示条（border-left）

### 需求 5：折叠模式

**用户故事：** 作为开发者，我希望垂直菜单能折叠为仅显示图标的窄条模式，以便节省侧边栏空间。

#### 验收标准

1. WHEN TMenu 的 collapsed 属性设置为 True 时，THE TMenu SHALL 将宽度动画收缩至 Design_Token 中 menu.collapsed_width 指定的值
2. WHEN 处于折叠模式时，THE TMenuItem SHALL 仅显示图标，隐藏文字标签
3. WHEN 处于折叠模式时，THE TMenuItemGroup SHALL 仅显示图标，隐藏文字标签、箭头指示符和子项列表
4. WHEN TMenu 的 collapsed 属性从 True 恢复为 False 时，THE TMenu SHALL 将宽度动画恢复至正常尺寸，并恢复所有文字标签和子项的显示

### 需求 6：选中状态与信号

**用户故事：** 作为开发者，我希望菜单能管理选中状态并发出信号，以便响应用户的导航操作。

#### 验收标准

1. WHEN 用户点击一个 TMenuItem 时，THE TMenu SHALL 将该项设为活跃状态，取消其他项的活跃状态，并发出 item_selected 信号
2. WHEN 调用 set_active_key 方法时，THE TMenu SHALL 递归遍历所有菜单项，将匹配 key 的项设为活跃状态
3. THE TMenuItem SHALL 在活跃状态下通过 QSS property "active" 为 "true" 来应用高亮样式（primary 颜色文字和指示条）
4. WHEN TMenuItem 的 disabled 属性为 True 时，THE TMenuItem SHALL 忽略点击事件，不发出 clicked 信号

### 需求 7：禁用状态

**用户故事：** 作为开发者，我希望能禁用整个菜单或单个菜单项，以便控制用户的交互权限。

#### 验收标准

1. WHEN TMenu 的 disabled 属性设置为 True 时，THE TMenu SHALL 递归将 disabled 状态传播到所有子项
2. WHEN TMenu 处于 disabled 状态时，THE TMenuItem SHALL 显示禁用样式（text_disabled 颜色）并忽略点击事件
3. WHEN TMenu 处于 disabled 状态时，THE TMenuItemGroup SHALL 显示禁用样式并忽略展开/收缩操作
4. WHEN TMenu 的 disabled 从 True 恢复为 False 时，THE TMenu SHALL 恢复所有子项的交互能力，但保留各子项自身的 disabled 状态

### 需求 8：路由感知

**用户故事：** 作为开发者，我希望菜单能根据路由路径自动高亮对应菜单项，以便与应用路由系统集成。

#### 验收标准

1. WHEN route_awareness 为 True 且调用 set_route 方法时，THE TMenu SHALL 使用最长前缀匹配算法查找匹配的菜单项 key，并将其设为活跃状态
2. WHEN route_awareness 为 False 时，THE TMenu SHALL 忽略 set_route 调用
3. WHEN set_route 未找到匹配项时，THE TMenu SHALL 保持当前活跃状态不变

### 需求 9：主题与样式

**用户故事：** 作为开发者，我希望菜单组件能自动响应主题切换，以便与应用的 Light/Dark 主题保持一致。

#### 验收标准

1. THE TMenu SHALL 通过 menu.qss.j2 模板渲染样式，所有颜色、间距、字号均引用 Design_Token
2. WHEN ThemeEngine 发出 theme_changed 信号时，THE TMenu SHALL 重新渲染 QSS 并应用新样式
3. THE menu.qss.j2 模板 SHALL 定义水平模式和垂直模式下不同的活跃状态指示样式（水平用 border-bottom，垂直用 border-left）
4. THE menu.qss.j2 模板 SHALL 定义 disabled 状态下使用 text_disabled 颜色且 hover 背景透明的样式规则
