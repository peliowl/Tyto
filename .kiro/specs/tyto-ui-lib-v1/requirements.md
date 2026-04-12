# 需求文档：Tyto UI 组件库 V1.0.0

## 简介

Tyto 是一个基于 PySide6 的现代化 UI 组件库，采用原子设计（Atomic Design）方法论，提供从基础控件到复杂业务模块的分层组件体系。V1.0.0 版本目标是交付一套仿 NaiveUI 风格、支持 Light/Dark 双主题、具备丰富交互动效的高质量 Python 桌面 UI 组件集。

## 术语表

- **Theme_Engine**：主题引擎，负责管理设计令牌（Design Tokens）并在运行时生成和注入 QSS 样式
- **Design_Token**：语义化的样式变量（如 ColorPrimary、SpacingMedium），作为样式系统的唯一真实来源
- **QSS**：Qt Style Sheet，Qt 框架的样式表语言，类似 CSS
- **Atom**：原子级组件，最小功能单元，零业务逻辑依赖
- **Molecule**：分子级组件，由多个原子组件组合而成的功能簇
- **Organism**：有机体级组件，具备独立业务语境的复杂 UI 模块
- **Mixin**：混入类，用于将通用交互行为（如悬停、拖拽）解耦注入到组件中
- **State_Machine**：状态机，管理组件在不同交互状态间的转换逻辑
- **Gallery**：组件预览画廊，用于展示和测试所有组件的示例应用

## 需求

### 需求 1：设计令牌与主题引擎

**用户故事：** 作为一名开发者，我希望通过语义化的设计令牌来定义和管理所有视觉样式，以便在整个组件库中保持视觉一致性并支持主题切换。

#### 验收标准

1. THE Theme_Engine SHALL 提供一套完整的语义化设计令牌体系，包含颜色（ColorPrimary、ColorSuccess、ColorWarning、ColorError、ColorInfo）、间距（SpacingSmall、SpacingMedium、SpacingLarge）、圆角（RadiusSmall、RadiusMedium、RadiusLarge）和字体尺寸定义
2. THE Theme_Engine SHALL 支持 Light 和 Dark 两套完整的主题配置
3. WHEN 用户调用主题切换接口时，THE Theme_Engine SHALL 在运行时重新生成并注入 QSS 样式，且界面无可感知的闪烁
4. THE Theme_Engine SHALL 基于 Jinja2 模板引擎在运行时动态渲染 QSS 字符串
5. WHEN 主题切换完成后，THE Theme_Engine SHALL 确保内存占用增量控制在切换前的 5% 以内
6. THE Theme_Engine SHALL 从外部 JSON 或 TOML 文件加载设计令牌定义，禁止在组件代码中硬编码任何像素值或颜色值
7. WHEN 设计令牌定义文件格式错误时，THEN THE Theme_Engine SHALL 返回包含具体错误位置的描述性错误信息

### 需求 2：组件基类与行为混入体系

**用户故事：** 作为一名开发者，我希望有一套统一的组件基类和可复用的行为混入，以便快速构建具有一致交互行为的新组件。

#### 验收标准

1. THE Base_Widget SHALL 提供统一的组件生命周期管理，包括初始化、样式绑定和销毁清理
2. THE Base_Widget SHALL 自动订阅 Theme_Engine 的主题变更信号，并在主题切换时自动更新自身样式
3. THE Base_Widget SHALL 包含 Agent 友好的详细 Docstrings，描述组件的用途、参数、信号和使用示例
4. WHEN HoverEffect Mixin 被应用到组件时，THE 组件 SHALL 在鼠标悬停时以 200ms 的过渡时间平滑渐变背景色，并将光标变为 PointingHand
5. WHEN ClickRipple Mixin 被应用到组件时，THE 组件 SHALL 在按下时将背景色加深并产生 Scale 0.98 的轻微下陷视觉效果
6. WHEN FocusGlow Mixin 被应用到组件时，THE 组件 SHALL 在获得焦点时显示 2px 的半透明主色扩散光晕效果
7. WHEN Disabled 状态被设置时，THE 组件 SHALL 将整体透明度降至 0.5 并将光标变为 Forbidden
8. THE Mixin 体系 SHALL 支持多个 Mixin 同时应用到同一组件而不产生冲突

### 需求 3：原子级组件 - Button

**用户故事：** 作为一名开发者，我希望使用功能完备的按钮组件，以便在应用中实现各种交互操作。

#### 验收标准

1. THE Button SHALL 支持 Primary、Default、Dashed、Text 四种视觉类型，每种类型具有独立的样式定义
2. WHEN Button 的 loading 属性被设置为 True 时，THE Button SHALL 在文字旁显示 SVG 旋转动画并屏蔽所有鼠标点击事件
3. WHEN Button 的 disabled 属性被设置为 True 时，THE Button SHALL 将透明度降至 0.5、光标变为 Forbidden 并屏蔽所有交互事件
4. WHEN 用户点击 Button 时，THE Button SHALL 发射 clicked 信号
5. WHEN Button 处于 loading 状态且用户点击时，THE Button SHALL 不发射 clicked 信号
6. THE Button SHALL 通过 Design_Token 获取所有样式值，不包含任何硬编码的颜色或尺寸值

### 需求 4：原子级组件 - Checkbox

**用户故事：** 作为一名开发者，我希望使用支持三态的复选框组件，以便实现灵活的多选交互。

#### 验收标准

1. THE Checkbox SHALL 支持选中（Checked）、未选中（Unchecked）和半选（Indeterminate）三种状态
2. WHEN Checkbox 的状态发生变化时，THE Checkbox SHALL 发射 state_changed 信号并携带新的状态值
3. WHEN Checkbox 在状态间切换时，THE Checkbox SHALL 播放平滑的动画过渡效果
4. THE Checkbox SHALL 支持通过文本标签（label）描述选项内容

### 需求 5：原子级组件 - Radio

**用户故事：** 作为一名开发者，我希望使用支持分组管理的单选框组件，以便实现互斥选择交互。

#### 验收标准

1. THE Radio SHALL 在选中和取消选中时播放圆环平滑缩放动画
2. WHEN 同一 RadioGroup 中的某个 Radio 被选中时，THE RadioGroup SHALL 自动取消该组内其他 Radio 的选中状态
3. WHEN Radio 的选中状态发生变化时，THE Radio SHALL 发射 toggled 信号并携带当前选中状态
4. THE RadioGroup SHALL 提供 get_selected_value 方法返回当前选中项的值

### 需求 6：原子级组件 - Input

**用户故事：** 作为一名开发者，我希望使用功能丰富的输入框组件，以便收集用户的文本输入。

#### 验收标准

1. THE Input SHALL 支持在输入框的前缀（Prefix）和后缀（Suffix）位置插入图标
2. WHEN Input 的 clearable 属性为 True 且输入框内有文本时，THE Input SHALL 显示一键清空按钮
3. WHEN 用户点击清空按钮时，THE Input SHALL 清空输入框内容并发射 cleared 信号
4. WHEN Input 的 password 属性为 True 时，THE Input SHALL 以掩码形式显示文本并提供可见性切换按钮
5. WHEN 用户点击密码可见性切换按钮时，THE Input SHALL 在掩码显示和明文显示之间切换
6. WHEN Input 的文本内容发生变化时，THE Input SHALL 发射 text_changed 信号并携带当前文本值

### 需求 7：原子级组件 - Switch

**用户故事：** 作为一名开发者，我希望使用具有流畅动画的开关组件，以便实现布尔值的切换交互。

#### 验收标准

1. THE Switch SHALL 以仿 iOS/NaiveUI 风格呈现，包含滑块和轨道两个视觉元素
2. WHEN 用户点击 Switch 时，THE Switch SHALL 播放滑块的平滑位移与缩放动画并切换开关状态
3. WHEN Switch 的状态发生变化时，THE Switch SHALL 发射 toggled 信号并携带当前布尔状态值
4. THE Switch SHALL 在 Light 和 Dark 主题下呈现对应的配色方案

### 需求 8：原子级组件 - Tag

**用户故事：** 作为一名开发者，我希望使用支持多尺寸和可关闭的标签组件，以便展示分类信息或状态标记。

#### 验收标准

1. THE Tag SHALL 支持 Small、Medium、Large 三种尺寸
2. WHEN Tag 的 closable 属性为 True 时，THE Tag SHALL 显示关闭按钮
3. WHEN 用户点击 Tag 的关闭按钮时，THE Tag SHALL 发射 closed 信号
4. THE Tag SHALL 支持通过 Design_Token 定义的多种预设颜色类型（Default、Primary、Success、Warning、Error）


### 需求 9：分子级组件 - SearchBar

**用户故事：** 作为一名开发者，我希望使用集成了输入框和按钮的搜索栏组件，以便快速实现搜索功能。

#### 验收标准

1. THE SearchBar SHALL 由 Input 原子组件和 Button 原子组件组合而成
2. WHEN 用户在 SearchBar 的输入框中输入文本时，THE SearchBar SHALL 发射 search_changed 信号并携带当前搜索文本
3. WHEN 用户点击搜索按钮或按下 Enter 键时，THE SearchBar SHALL 发射 search_submitted 信号并携带当前搜索文本
4. THE SearchBar SHALL 支持 clearable 属性以允许一键清空搜索内容

### 需求 10：分子级组件 - Breadcrumb

**用户故事：** 作为一名开发者，我希望使用面包屑导航组件，以便展示页面层级路径并支持快速跳转。

#### 验收标准

1. THE Breadcrumb SHALL 接受一个路径项列表并按顺序渲染每个路径项
2. THE Breadcrumb SHALL 支持自定义分隔符（默认为 "/"）
3. WHEN 用户点击某个路径项时，THE Breadcrumb SHALL 发射 item_clicked 信号并携带该路径项的索引和数据
4. THE Breadcrumb SHALL 将最后一个路径项渲染为不可点击的当前位置样式

### 需求 11：分子级组件 - InputGroup

**用户故事：** 作为一名开发者，我希望将按钮和输入框紧凑地横向拼接，以便构建复合输入交互。

#### 验收标准

1. THE InputGroup SHALL 支持将多个 Input 和 Button 组件紧凑横向排列
2. THE InputGroup SHALL 自动处理子组件的圆角合并，使首尾组件保留外侧圆角，中间组件圆角为零
3. WHEN InputGroup 中的子组件数量或顺序发生变化时，THE InputGroup SHALL 自动重新计算并应用圆角合并规则

### 需求 12：有机体级组件 - Message

**用户故事：** 作为一名开发者，我希望使用全局提示组件，以便向用户展示操作反馈信息。

#### 验收标准

1. THE Message SHALL 支持 Info、Success、Warning、Error 四种消息类型，每种类型具有独立的图标和配色
2. WHEN Message 被触发时，THE Message SHALL 从屏幕顶部以动画形式悬浮弹出
3. WHEN Message 的显示时长到达后（默认 3 秒），THE Message SHALL 自动以动画形式消失并释放资源
4. THE Message SHALL 支持同时显示多条消息，并按出现顺序自上而下堆叠排列
5. WHEN 多条 Message 同时显示时，THE Message_Manager SHALL 管理消息的堆叠位置，确保消息之间保持固定间距

### 需求 13：有机体级组件 - Modal

**用户故事：** 作为一名开发者，我希望使用模态对话框组件，以便在需要用户确认或输入时阻断主界面交互。

#### 验收标准

1. WHEN Modal 被打开时，THE Modal SHALL 显示半透明遮罩层覆盖主界面并阻断遮罩层下方的所有交互
2. WHEN Modal 打开时，THE Modal SHALL 以平滑的缩放动画从中心弹出
3. THE Modal SHALL 支持自定义标题栏内容、主体内容和底部操作按钮区域
4. WHEN 用户点击遮罩层或关闭按钮时，THE Modal SHALL 以动画形式关闭并发射 closed 信号
5. THE Modal SHALL 支持通过 closable 属性控制是否显示关闭按钮和是否允许点击遮罩层关闭

### 需求 14：项目工程化与分发

**用户故事：** 作为一名开发者，我希望项目具备完善的工程化配置，以便高效地开发、测试和分发组件库。

#### 验收标准

1. THE 项目 SHALL 使用 pyproject.toml 作为唯一的项目配置文件，包含 uv 依赖管理、Ruff 代码检查和 Pyright 类型检查的配置
2. THE 项目 SHALL 提供 pytest + pytest-qt 测试框架配置，支持通过 pytest-xdist 进行并行测试执行
3. THE 项目 SHALL 提供 hypothesis 属性基测试框架配置，用于组件状态机和样式渲染的属性验证
4. THE 项目 SHALL 通过 Setuptools 构建为标准的 Python wheel 包，可通过 pip install 安装使用
5. WHEN 开发者导入 tyto_ui_lib 包时，THE 包 SHALL 通过 __init__.py 导出所有公开组件和核心 API

### 需求 15：组件预览画廊

**用户故事：** 作为一名开发者，我希望有一个组件预览画廊应用，以便直观地查看和测试所有组件的外观与交互效果。

#### 验收标准

1. THE Gallery SHALL 提供一个独立的 PySide6 应用程序，展示所有已实现组件的实时预览
2. THE Gallery SHALL 提供主题切换功能，允许在 Light 和 Dark 模式间实时切换以预览效果
3. THE Gallery SHALL 为每个组件提供独立的展示区域，包含不同状态和配置的示例


---

# 需求文档：Tyto UI 组件库 V1.0.1

## 简介

V1.0.1 版本聚焦于 Gallery 预览画廊的全面重构，采用 MVVM 架构模式，将原有的单文件 Gallery 拆分为模块化、可扩展的结构。新版 Gallery 提供左侧分类导航菜单和右侧组件特性展示面板，提升开发者的组件浏览和测试体验。

## 术语表

- **MVVM**：Model-View-ViewModel 架构模式，将数据模型、视图展示和业务逻辑分离
- **ViewModel**：视图模型，负责管理视图状态和业务逻辑，连接 Model 与 View
- **NavigationMenu**：左侧导航菜单，按原子/分子/有机体分类展示所有组件
- **ComponentShowcase**：右侧组件展示面板，展示选中组件的所有特性示例
- **ShowcaseSection**：展示区块，对应组件的一个特性维度（如基础用法、形状、尺寸、禁用等）

## 需求

### 需求 16：Gallery MVVM 架构重构

**用户故事：** 作为一名开发者，我希望 Gallery 采用 MVVM 架构进行模块化重构，以便代码结构清晰、易于维护和扩展新组件。

#### 验收标准

1. THE Gallery SHALL 采用 MVVM 架构模式，将视图（View）、视图模型（ViewModel）和数据模型（Model）分离到独立模块中
2. THE Gallery SHALL 将代码组织为 `examples/gallery/` 目录结构，包含 models/、viewmodels/、views/、styles/ 子模块
3. THE Gallery 的入口 SHALL 保持为 `examples/gallery.py`，内部委托给 `examples/gallery/` 包启动
4. WHEN 新增一个组件时，开发者 SHALL 仅需添加一个 Showcase 模块并在注册表中注册，无需修改 Gallery 框架代码

### 需求 17：Gallery 左侧导航菜单

**用户故事：** 作为一名开发者，我希望 Gallery 左侧有一个分类导航菜单，以便快速定位和切换到目标组件的展示页面。

#### 验收标准

1. THE NavigationMenu SHALL 显示三个一级分类菜单项：原子组件（Atoms）、分子组件（Molecules）、有机体组件（Organisms）
2. WHEN 用户展开某个分类时，THE NavigationMenu SHALL 列出该分类下的所有已注册组件名称
3. THE NavigationMenu SHALL 高亮显示当前选中的组件项
4. WHEN 用户点击某个组件项时，THE NavigationMenu SHALL 通知 ViewModel 更新当前选中组件
5. THE NavigationMenu 的组件列表 SHALL 自动从组件注册表中获取，无需硬编码

### 需求 18：Gallery 右侧组件展示面板

**用户故事：** 作为一名开发者，我希望选中组件后右侧展示该组件的所有特性示例，以便全面了解组件的功能和外观。

#### 验收标准

1. WHEN 用户在左侧菜单选中一个组件时，THE ComponentShowcase SHALL 在右侧面板展示该组件的所有特性区块
2. THE ComponentShowcase SHALL 为每个组件提供多个 ShowcaseSection，至少包含：基础用法（Basic Usage）
3. THE ComponentShowcase SHALL 根据组件特性动态展示相关区块，例如：
   - Button：基础用法、类型、加载状态、禁用状态
   - Checkbox：基础用法、三态展示
   - Switch：基础用法、禁用状态
   - Tag：基础用法、颜色类型、尺寸、可关闭
   - Input：基础用法、可清空、密码模式
   - Radio：基础用法、分组互斥
   - SearchBar：基础用法、可清空
   - Breadcrumb：基础用法、自定义分隔符
   - InputGroup：基础用法
   - Message：基础用法（触发各类型消息）
   - Modal：基础用法（打开/关闭对话框）
4. EACH ShowcaseSection SHALL 包含标题、描述文字和组件实例展示区域
5. THE ComponentShowcase SHALL 支持垂直滚动以容纳所有特性区块

### 需求 19：Gallery 主题切换保持

**用户故事：** 作为一名开发者，我希望重构后的 Gallery 仍然支持 Light/Dark 主题实时切换。

#### 验收标准

1. THE Gallery SHALL 在顶部栏保留主题切换开关（TSwitch）
2. WHEN 用户切换主题时，THE Gallery 的所有区域（导航菜单、展示面板、顶部栏）SHALL 同步更新为对应主题样式


---

# 需求文档：Tyto UI 组件库 V1.0.1 - Bug 修复

## 简介

V1.0.1 Bug 修复版本聚焦于解决 V1.0.0 中发现的组件样式渲染和交互逻辑缺陷。涉及 Button、Input、Tag、SearchBar 和 Message 五个组件，主要问题集中在 QSS 动态属性选择器未生效、清空按钮布局错位、Tag 关闭功能缺失以及 Message 弹出位置和样式异常。

## 需求

### 需求 20：Button 类型样式修复

**用户故事：** 作为一名开发者，我希望不同类型的按钮能正确显示对应的边框效果和背景颜色，以便用户能直观区分按钮的功能层级。

#### 验收标准

1. WHEN TButton 的 button_type 为 PRIMARY 时，THE Button SHALL 显示绿色背景（`colors.primary`）和对应边框
2. WHEN TButton 的 button_type 为 DASHED 时，THE Button SHALL 显示虚线边框
3. WHEN TButton 的 button_type 为 TEXT 时，THE Button SHALL 显示透明背景且无边框
4. WHEN TButton 的 button_type 为 DEFAULT 时，THE Button SHALL 显示白色背景和实线边框
5. THE Button 的 QSS 动态属性选择器（`[buttonType="xxx"]`）SHALL 在组件创建后立即生效，无需额外操作

### 需求 21：Input 清空按钮位置修复

**用户故事：** 作为一名开发者，我希望输入框的清空按钮显示在输入框内部靠右边界处，而不是输入框外部，以保持视觉一致性。

#### 验收标准

1. WHEN TInput 的 clearable 属性为 True 且输入框内有文本时，THE 清空按钮 SHALL 显示在 QLineEdit 内部的右侧区域
2. THE 清空按钮 SHALL 不超出 QLineEdit 的边框范围
3. WHEN 用户点击清空按钮时，THE Input SHALL 正常清空文本并发射 cleared 信号（功能不变）

### 需求 22：Tag 样式与交互修复

**用户故事：** 作为一名开发者，我希望标签组件能正确显示不同类型的边框和背景颜色，并且关闭按钮能正常工作，以便标签组件可用于实际业务场景。

#### 验收标准

1. WHEN TTag 的 tag_type 为 PRIMARY/SUCCESS/WARNING/ERROR 时，THE Tag SHALL 显示对应的背景颜色和边框颜色
2. WHEN TTag 的 tag_type 为 DEFAULT 时，THE Tag SHALL 显示默认背景色和边框
3. THE Tag 的 QSS 动态属性选择器（`[tagType="xxx"]`）SHALL 在组件创建后立即生效
4. THE Tag SHALL 始终显示可见的边框和背景颜色，以便用户能清晰辨识标签的尺寸和边界
5. WHEN TTag 的 closable 属性为 True 且用户点击关闭按钮时，THE Tag SHALL 从界面中隐藏或删除自身

### 需求 23：SearchBar 清空按钮位置修复

**用户故事：** 作为一名开发者，我希望搜索栏内部输入框的清空按钮位置正确，与 Input 组件的修复保持一致。

#### 验收标准

1. THE SearchBar 内部的 TInput 组件 SHALL 遵循需求 21 的清空按钮位置规则
2. THE 清空按钮 SHALL 显示在搜索输入框内部的右侧区域，不超出输入框边框

### 需求 24：Message 组件综合修复

**用户故事：** 作为一名开发者，我希望全局提示消息能在正确的位置显示、具有可见的背景色和边框，并且触发按钮样式正常，以便提供良好的用户反馈体验。

#### 验收标准

1. WHEN Message 被触发时，THE Message SHALL 显示在其所属窗口的顶部水平居中位置（相对于窗口而非屏幕）
2. THE Message SHALL 具有可见的背景色（`colors.bg_default`）和边框（`colors.border`），不因透明背景属性而丢失样式
3. THE Message 展示面板中的触发按钮 SHALL 正确显示对应的边框效果和背景颜色（与需求 20 的 Button 修复一致）
4. WHEN 多条 Message 同时显示时，THE Message_Manager SHALL 确保所有消息在窗口顶部居中堆叠，位置计算正确


---

# 需求文档：Tyto UI 组件库 V1.0.1 - Dark 模式颜色修复

## 简介

V1.0.1 Dark 模式修复版本聚焦于解决在 "dark" 主题下，多个组件和 Gallery 界面元素的颜色显示异常问题。涉及 Button、Input、Switch、Tag、SearchBar 等组件的背景色、文本颜色、边框颜色在 dark 模式下与 NaiveUI 参考效果图不一致，以及 Gallery 界面中导航菜单、列表项的颜色显示不正确。

## 参考效果图

- "dark" 模式下的 Button 参考图：`docs/image/reference/v1.0.1_1.png`
- "dark" 模式下的 Input 参考图：`docs/image/reference/v1.0.1_2.png`
- "dark" 模式下的 Switch 参考图：`docs/image/reference/v1.0.1_3.png`
- "dark" 模式下的 Tag 参考图：`docs/image/reference/v1.0.1_4.png`
- "dark" 模式下的 SearchBar 参考图：`docs/image/reference/v1.0.1_5.png`
- "dark" 模式下的列表及列表项参考图：`docs/image/reference/v1.0.1_6.png`

## 需求

### 需求 25：Button 组件 Dark 模式颜色修复

**用户故事：** 作为一名开发者，我希望在 dark 模式下 Button 组件的背景色、文本颜色和边框颜色与 NaiveUI dark 主题参考图一致，以便在深色主题下提供正确的视觉体验。

#### 验收标准

1. WHEN 主题为 dark 时，THE TButton（DEFAULT 类型）SHALL 显示深色背景（`colors.bg_default`）、浅色文本（`colors.text_primary`）和深色边框（`colors.border`），与参考图 v1.0.1_1.png 一致
2. WHEN 主题为 dark 时，THE TButton（PRIMARY 类型）SHALL 显示绿色背景（`colors.primary`）和白色文本，与参考图一致
3. WHEN 主题为 dark 时，THE TButton（DASHED 类型）SHALL 显示深色背景和虚线边框，边框颜色使用 dark 主题的 `colors.border`
4. WHEN 主题为 dark 时，THE TButton（TEXT 类型）SHALL 显示透明背景和浅色文本
5. WHEN 主题从 light 切换到 dark 时，THE TButton SHALL 立即更新为 dark 主题对应的颜色方案，无残留的 light 主题颜色

### 需求 26：Input 组件 Dark 模式颜色修复

**用户故事：** 作为一名开发者，我希望在 dark 模式下 Input 组件的背景色、文本颜色、边框颜色和占位符颜色与 NaiveUI dark 主题参考图一致。

#### 验收标准

1. WHEN 主题为 dark 时，THE TInput 的 QLineEdit SHALL 显示深色背景（`colors.bg_default`）、浅色文本（`colors.text_primary`）和深色边框（`colors.border`），与参考图 v1.0.1_2.png 一致
2. WHEN 主题为 dark 时，THE TInput 的占位符文本 SHALL 使用 `colors.text_secondary` 颜色显示
3. WHEN 主题为 dark 时，THE TInput 获得焦点时 SHALL 显示 `colors.border_focus` 颜色的边框
4. WHEN 主题从 light 切换到 dark 时，THE TInput SHALL 立即更新为 dark 主题对应的颜色方案

### 需求 27：Switch 组件 Dark 模式颜色修复

**用户故事：** 作为一名开发者，我希望在 dark 模式下 Switch 组件的轨道颜色和滑块颜色与 NaiveUI dark 主题参考图一致。

#### 验收标准

1. WHEN 主题为 dark 且 Switch 未选中时，THE TSwitch 的轨道 SHALL 显示 dark 主题的 `colors.border` 颜色，与参考图 v1.0.1_3.png 一致
2. WHEN 主题为 dark 且 Switch 已选中时，THE TSwitch 的轨道 SHALL 显示 dark 主题的 `colors.primary` 颜色
3. WHEN 主题从 light 切换到 dark 时，THE TSwitch SHALL 立即重绘轨道为 dark 主题对应的颜色

### 需求 28：Tag 组件 Dark 模式颜色修复

**用户故事：** 作为一名开发者，我希望在 dark 模式下 Tag 组件的背景色、文本颜色和边框颜色与 NaiveUI dark 主题参考图一致。

#### 验收标准

1. WHEN 主题为 dark 时，THE TTag（DEFAULT 类型）SHALL 显示深色背景（`colors.bg_elevated`）、浅色文本（`colors.text_primary`）和深色边框（`colors.border`），与参考图 v1.0.1_4.png 一致
2. WHEN 主题为 dark 时，THE TTag（PRIMARY/SUCCESS/WARNING/ERROR 类型）SHALL 显示对应的颜色背景和白色文本
3. WHEN 主题从 light 切换到 dark 时，THE TTag SHALL 立即更新为 dark 主题对应的颜色方案

### 需求 29：SearchBar 组件 Dark 模式颜色修复

**用户故事：** 作为一名开发者，我希望在 dark 模式下 SearchBar 组件的输入框和搜索按钮颜色与 NaiveUI dark 主题参考图一致。

#### 验收标准

1. WHEN 主题为 dark 时，THE TSearchBar 内部的 TInput 和 TButton SHALL 显示 dark 主题对应的颜色方案，与参考图 v1.0.1_5.png 一致
2. THE TSearchBar 的 dark 模式颜色修复 SHALL 自动受益于 TInput（需求 26）和 TButton（需求 25）的修复

### 需求 30：Gallery 界面 Dark 模式颜色修复

**用户故事：** 作为一名开发者，我希望在 dark 模式下 Gallery 的导航菜单、列表项、顶部栏等界面元素的颜色与 NaiveUI dark 主题参考图一致。

#### 验收标准

1. WHEN 主题为 dark 时，THE NavigationMenu SHALL 显示深色背景（`colors.bg_elevated`）和深色边框（`colors.border`），与参考图 v1.0.1_6.png 一致
2. WHEN 主题为 dark 时，THE NavigationMenu 的分类标题 SHALL 使用 `colors.text_secondary` 颜色
3. WHEN 主题为 dark 时，THE NavigationMenu 的组件列表项 SHALL 使用 `colors.text_primary` 颜色，悬停时使用深色高亮背景
4. WHEN 主题为 dark 时，THE NavigationMenu 的选中项 SHALL 使用 `colors.primary` 颜色高亮
5. WHEN 主题为 dark 时，THE TopBar SHALL 显示深色背景和浅色标题文本
6. WHEN 主题为 dark 时，THE ComponentShowcase 的展示面板背景 SHALL 使用 `colors.bg_default` 深色背景
7. WHEN 主题为 dark 时，THE BaseShowcase 的 section 标题和描述文本 SHALL 使用对应的 dark 主题文本颜色
8. WHEN 主题从 light 切换到 dark 时，THE Gallery 的所有界面元素 SHALL 同步更新为 dark 主题颜色，无残留的 light 主题颜色


---

# 需求文档：Tyto UI 组件库 V1.0.2 - 原子组件特性增强

## 简介

V1.0.2 版本聚焦于补齐原子组件（Atom）在 V1.0.0/V1.0.1 中尚未实现的特性，使 Tyto 组件库的原子组件功能覆盖度对齐 NaiveUI。涉及 TButton、TInput、TCheckbox、TRadio、TSwitch、TTag 六个原子组件的属性扩展、新增子组件（TCheckboxGroup、TRadioButton）以及 Gallery Showcase 的同步更新。

## 术语表

- **Size_Variant**：尺寸变体，组件支持的预设尺寸（tiny / small / medium / large）
- **Ghost_Button**：幽灵按钮，透明背景 + 彩色边框/文字的按钮样式
- **Block_Button**：块级按钮，宽度撑满父容器的按钮
- **Textarea_Mode**：多行文本输入模式，支持自适应高度和行数控制
- **Checkable_Tag**：可选中标签，类似 toggle 的标签交互模式
- **RadioButton**：按钮样式的单选组件，在 RadioGroup 中呈现为按钮组样式

## 需求

### 需求 31：TButton 特性增强

**用户故事：** 作为一名开发者，我希望按钮组件支持更多尺寸变体、样式变体和自定义选项，以便在不同业务场景中灵活使用。

#### 验收标准

1. THE TButton SHALL 支持 tiny / small / medium / large 四种尺寸变体，通过 `size` 属性设置，默认为 medium
2. THE TButton SHALL 新增 tertiary / info / success / warning / error 五种类型变体，与现有 primary / default / dashed / text 共存
3. WHEN TButton 的 `circle` 属性为 True 时，THE TButton SHALL 渲染为正圆形按钮
4. WHEN TButton 的 `round` 属性为 True 时，THE TButton SHALL 渲染为全圆角（胶囊形）按钮
5. WHEN TButton 的 `ghost` 属性为 True 时，THE TButton SHALL 显示透明背景 + 对应类型的彩色边框和文字
6. THE TButton SHALL 支持 `secondary`、`tertiary`、`quaternary` 三种层级样式变体
7. WHEN TButton 的 `strong` 属性为 True 时，THE TButton 的文字 SHALL 以加粗字体显示
8. WHEN TButton 的 `block` 属性为 True 时，THE TButton 的宽度 SHALL 撑满父容器
9. WHEN TButton 的 `color` 属性被设置时，THE TButton SHALL 使用该自定义颜色作为主色调
10. WHEN TButton 的 `text_color` 属性被设置时，THE TButton SHALL 使用该颜色作为文字颜色
11. THE TButton SHALL 支持 `bordered` 属性控制是否显示边框，默认为 True
12. THE TButton SHALL 支持 `icon_placement` 属性（left / right）控制图标相对于文字的位置
13. THE TButton SHALL 支持通过 `icon` 参数传入自定义 QIcon 图标
14. THE TButton SHALL 支持 `attr_type` 属性设置原生 button type（button / submit / reset）
15. THE TButton SHALL 支持 `focusable` 属性控制是否可聚焦，默认为 True

### 需求 32：TInput 特性增强

**用户故事：** 作为一名开发者，我希望输入框组件支持多行文本、尺寸变体、字数统计和验证状态等高级功能，以便满足复杂表单场景的需求。

#### 验收标准

1. THE TInput SHALL 支持 tiny / small / medium / large 四种尺寸变体，通过 `size` 属性设置，默认为 medium
2. THE TInput SHALL 支持 text / textarea / password 三种输入模式，通过 `type` 属性设置
3. WHEN TInput 的 `type` 为 textarea 时，THE TInput SHALL 渲染为多行文本输入区域
4. WHEN TInput 的 `round` 属性为 True 时，THE TInput SHALL 渲染为全圆角输入框
5. THE TInput SHALL 支持 `bordered` 属性控制是否显示边框，默认为 True
6. WHEN TInput 的 `maxlength` 属性被设置时，THE TInput SHALL 限制输入文本的最大长度
7. WHEN TInput 的 `minlength` 属性被设置时，THE TInput SHALL 在文本长度不足时标记为无效状态
8. WHEN TInput 的 `show_count` 属性为 True 时，THE TInput SHALL 在输入框右下角显示当前字数 / 最大字数
9. WHEN TInput 的 `readonly` 属性为 True 时，THE TInput SHALL 允许选择和复制文本但禁止编辑
10. WHEN TInput 的 `autosize` 属性被设置时（支持 min_rows / max_rows），THE textarea SHALL 根据内容自适应高度
11. THE TInput SHALL 支持 `rows` 属性设置 textarea 的默认行数
12. WHEN TInput 的 `loading` 属性为 True 时，THE TInput SHALL 在后缀位置显示加载旋转动画
13. THE TInput SHALL 支持 `status` 属性设置验证状态（success / warning / error），显示对应的边框颜色
14. WHEN TInput 的 `resizable` 属性为 True 时，THE textarea SHALL 支持用户拖拽调整大小
15. THE TInput SHALL 支持 `show_password_on` 属性设置密码可见触发方式（mousedown / click）

### 需求 33：TCheckbox 特性增强

**用户故事：** 作为一名开发者，我希望复选框组件支持尺寸变体、禁用状态和分组管理，以便在表单中实现灵活的多选交互。

#### 验收标准

1. THE TCheckbox SHALL 支持 small / medium / large 三种尺寸变体，通过 `size` 属性设置，默认为 medium
2. WHEN TCheckbox 的 `disabled` 属性为 True 时，THE TCheckbox SHALL 降低透明度、显示 Forbidden 光标并屏蔽所有交互
3. THE TCheckbox SHALL 支持 `value` 属性，用于在 TCheckboxGroup 中标识该选项
4. THE TCheckbox SHALL 支持 `focusable` 属性控制是否可聚焦，默认为 True
5. THE TCheckbox SHALL 支持 `checked_value` / `unchecked_value` 属性，自定义选中/未选中时的返回值
6. THE TCheckbox SHALL 支持 `default_checked` 属性设置默认选中状态（非受控模式）
7. THE TCheckboxGroup SHALL 管理一组 TCheckbox 的选中状态，提供 `value` / `default_value` 属性
8. THE TCheckboxGroup SHALL 支持 `min` / `max` 属性限制最少/最多可选数量
9. THE TCheckboxGroup SHALL 支持 `size` 属性统一设置组内所有 TCheckbox 的尺寸
10. THE TCheckboxGroup SHALL 支持 `disabled` 属性统一禁用组内所有 TCheckbox

### 需求 34：TRadio 特性增强

**用户故事：** 作为一名开发者，我希望单选框组件支持尺寸变体、禁用状态和按钮样式变体，以便在不同 UI 场景中灵活使用。

#### 验收标准

1. THE TRadio SHALL 支持 small / medium / large 三种尺寸变体，通过 `size` 属性设置，默认为 medium
2. WHEN TRadio 的 `disabled` 属性为 True 时，THE TRadio SHALL 降低透明度、显示 Forbidden 光标并屏蔽所有交互
3. THE TRadio SHALL 支持 `name` 属性设置原生 radio name
4. THE TRadioButton SHALL 作为独立组件提供按钮样式的单选交互
5. THE TRadioGroup SHALL 支持 `name` 属性统一设置组内所有 TRadio 的 name
6. THE TRadioGroup SHALL 支持 `size` 属性统一设置组内所有 TRadio 的尺寸
7. THE TRadioGroup SHALL 支持 `disabled` 属性统一禁用组内所有 TRadio
8. THE TRadioGroup SHALL 支持 `default_value` 属性设置默认选中值
9. WHEN TRadioGroup 包含 TRadioButton 子项时，THE TRadioGroup SHALL 自动切换为按钮组样式布局

### 需求 35：TSwitch 特性增强

**用户故事：** 作为一名开发者，我希望开关组件支持尺寸变体、加载状态和自定义值，以便在更多业务场景中使用。

#### 验收标准

1. THE TSwitch SHALL 支持 small / medium / large 三种尺寸变体，通过 `size` 属性设置，默认为 medium
2. WHEN TSwitch 的 `loading` 属性为 True 时，THE TSwitch SHALL 在滑块上显示旋转加载动画并屏蔽交互
3. WHEN TSwitch 的 `round` 属性为 False 时，THE TSwitch SHALL 渲染为方形轨道和滑块
4. THE TSwitch SHALL 支持 `checked_value` / `unchecked_value` 属性，自定义开/关时的返回值（支持 str / int / bool）
5. THE TSwitch SHALL 支持 `rubber_band` 属性启用橡皮筋回弹效果
6. THE TSwitch SHALL 支持 `checked_text` / `unchecked_text` 属性，在轨道内显示开/关状态文字

### 需求 36：TTag 特性增强

**用户故事：** 作为一名开发者，我希望标签组件支持更多类型变体、可选中交互和自定义颜色，以便在标签筛选和状态展示场景中使用。

#### 验收标准

1. THE TTag SHALL 新增 info 类型变体，与现有 default / primary / success / warning / error 共存
2. THE TTag SHALL 新增 tiny 尺寸变体，与现有 small / medium / large 共存
3. WHEN TTag 的 `round` 属性为 True 时，THE TTag SHALL 渲染为全圆角标签
4. WHEN TTag 的 `disabled` 属性为 True 时，THE TTag SHALL 降低透明度并屏蔽所有交互
5. THE TTag SHALL 支持 `bordered` 属性控制是否显示边框，默认为 True
6. WHEN TTag 的 `color` 属性被设置时（包含 color / border_color / text_color），THE TTag SHALL 使用自定义颜色覆盖类型预设
7. WHEN TTag 的 `checkable` 属性为 True 时，THE TTag SHALL 支持点击切换选中/未选中状态
8. WHEN TTag 的 `checkable` 为 True 且 `checked` 状态变化时，THE TTag SHALL 发射 `checked_changed` 信号
9. WHEN TTag 的 `strong` 属性为 True 时，THE TTag 的文字 SHALL 以加粗字体显示

### 需求 37：Gallery Showcase 同步更新

**用户故事：** 作为一名开发者，我希望 Gallery 的组件展示面板同步展示 V1.0.2 新增的所有特性，以便直观预览和测试新功能。

#### 验收标准

1. THE ButtonShowcase SHALL 新增展示区块：尺寸变体、圆形/圆角、幽灵按钮、块级按钮、图标按钮
2. THE InputShowcase SHALL 新增展示区块：尺寸变体、Textarea 模式、字数统计、验证状态、圆角输入框
3. THE CheckboxShowcase SHALL 新增展示区块：尺寸变体、禁用状态、CheckboxGroup
4. THE RadioShowcase SHALL 新增展示区块：尺寸变体、禁用状态、RadioButton 按钮组
5. THE SwitchShowcase SHALL 新增展示区块：尺寸变体、加载状态、方形开关、轨道文字
6. THE TagShowcase SHALL 新增展示区块：Tiny 尺寸、Info 类型、圆角标签、可选中标签、自定义颜色


---

# 需求文档：Tyto UI 组件库 V1.0.2 - Playground 交互式调试应用

## 简介

V1.0.2 Playground 版本新增一个独立的交互式调试应用（Playground），允许开发者和用户自由设置 Tyto 控件的属性并实时查看效果。Playground 的布局与 Gallery 保持一致（左侧导航 + 中部展示），并在右侧新增属性面板（Property Panel），支持动态修改控件的所有可配置属性。目标是为开发人员提供便捷的控件调试工具，同时让用户能够快速体验 Tyto 组件库的全部能力。

## 术语表

- **Playground**：交互式调试应用，支持实时修改控件属性并预览效果
- **PropertyPanel**：属性面板，位于布局右侧，提供控件属性的编辑控件
- **PropertyEditor**：属性编辑器，单个属性的编辑控件（如下拉框、复选框、输入框等）
- **ComponentPreview**：组件预览区域，位于布局中部，展示当前控件的实时状态
- **PropertyDefinition**：属性定义，描述控件某个属性的名称、类型、默认值和可选值

## 需求

### 需求 38：Playground 应用架构

**用户故事：** 作为一名开发者，我希望有一个独立的 Playground 应用，采用与 Gallery 一致的 MVVM 架构，以便代码结构清晰、易于维护。

#### 验收标准

1. THE Playground SHALL 作为独立应用存放在 `examples/playground/` 目录下，入口文件为 `examples/playground.py`
2. THE Playground SHALL 采用 MVVM 架构模式，复用 Gallery 的 Model 层（ComponentRegistry、ComponentInfo）
3. THE Playground SHALL 提供三栏布局：左侧导航菜单、中部组件预览区域、右侧属性面板
4. THE Playground 的顶部栏 SHALL 包含标题 "Tyto UI Playground" 和 Light/Dark 主题切换开关
5. WHEN 新增一个组件时，开发者 SHALL 仅需添加一个 PropertyDefinition 配置并注册，无需修改 Playground 框架代码

### 需求 39：Playground 左侧导航菜单

**用户故事：** 作为一名开发者，我希望 Playground 左侧有与 Gallery 一致的分类导航菜单，以便快速切换到目标控件。

#### 验收标准

1. THE Playground 的 NavigationMenu SHALL 显示三个一级分类：原子组件（Atoms）、分子组件（Molecules）、有机体组件（Organisms）
2. THE NavigationMenu SHALL 列出每个分类下的所有已注册组件
3. WHEN 用户点击某个组件项时，THE NavigationMenu SHALL 通知 ViewModel 更新当前选中组件
4. THE NavigationMenu SHALL 高亮显示当前选中的组件项

### 需求 40：Playground 中部组件预览区域

**用户故事：** 作为一名开发者，我希望在左侧选择控件后，中部区域展示该控件的默认状态实例，以便直观查看控件效果。

#### 验收标准

1. WHEN 用户在左侧菜单选中一个组件时，THE ComponentPreview SHALL 在中部区域创建并展示该组件的一个实时实例
2. THE ComponentPreview SHALL 以默认属性值创建组件实例
3. WHEN 右侧属性面板的属性值发生变化时，THE ComponentPreview SHALL 实时更新组件实例的对应属性
4. THE ComponentPreview SHALL 支持垂直滚动以容纳不同尺寸的组件

### 需求 41：Playground 右侧属性面板

**用户故事：** 作为一名开发者，我希望在右侧有一个属性面板，能够设置当前选中控件的所有可配置属性，以便实时调试控件效果。

#### 验收标准

1. WHEN 用户选中一个组件时，THE PropertyPanel SHALL 动态生成该组件所有可配置属性的编辑控件
2. THE PropertyPanel SHALL 根据属性类型自动选择合适的编辑控件：
   - 枚举类型（如 ButtonType、ButtonSize）：使用下拉选择框（QComboBox）
   - 布尔类型（如 disabled、loading）：使用复选框（QCheckBox）
   - 字符串类型（如 text、placeholder）：使用文本输入框（QLineEdit）
   - 整数类型（如 maxlength、rows）：使用数字输入框（QSpinBox）
   - 颜色类型（如 color、text_color）：使用颜色输入框（QLineEdit，支持 hex 格式）
3. WHEN 用户修改属性面板中的某个属性值时，THE PropertyPanel SHALL 立即通知 ViewModel，触发组件预览区域的实时更新
4. THE PropertyPanel SHALL 为每个属性显示属性名称和当前值
5. THE PropertyPanel SHALL 支持垂直滚动以容纳所有属性编辑控件
6. WHEN 用户切换到另一个组件时，THE PropertyPanel SHALL 清除旧属性并重新生成新组件的属性编辑控件

### 需求 42：Playground 属性定义与组件注册

**用户故事：** 作为一名开发者，我希望通过声明式的属性定义来配置每个组件的可编辑属性，以便快速扩展新组件的 Playground 支持。

#### 验收标准

1. THE PropertyDefinition SHALL 描述组件属性的名称（name）、显示标签（label）、属性类型（prop_type）、默认值（default）和可选值列表（options，仅枚举类型需要）
2. THE Playground SHALL 为以下原子组件提供完整的属性定义：
   - TButton：text、button_type、size、loading、disabled、circle、round、ghost、strong、block、bordered、color、text_color
   - TInput：placeholder、input_type、size、clearable、password、round、bordered、maxlength、show_count、readonly、loading、status
   - TCheckbox：label、size、disabled、default_checked
   - TRadio：label、size、disabled
   - TSwitch：size、disabled、loading、round、checked_text、unchecked_text
   - TTag：text、tag_type、size、closable、round、disabled、bordered、checkable、strong
3. THE Playground SHALL 为分子和有机体组件提供基础属性定义：
   - TSearchBar：placeholder、clearable
   - TBreadcrumb：separator
   - TMessage：触发各类型消息的按钮（非属性编辑，而是操作按钮）
4. EACH 属性定义 SHALL 包含一个 `apply` 回调函数，用于将属性值应用到组件实例上

### 需求 43：Playground 主题切换

**用户故事：** 作为一名开发者，我希望 Playground 支持 Light/Dark 主题实时切换，以便在不同主题下调试控件效果。

#### 验收标准

1. THE Playground SHALL 在顶部栏保留主题切换开关（TSwitch）
2. WHEN 用户切换主题时，THE Playground 的所有区域（导航菜单、预览区域、属性面板、顶部栏）SHALL 同步更新为对应主题样式
3. WHEN 用户切换主题时，THE ComponentPreview 中的组件实例 SHALL 自动响应主题变化并更新样式


---

# 需求文档：Tyto UI 组件库 V1.1.0 - 新增组件与架构增强

## 简介

V1.1.0 版本大幅扩展 Tyto 组件库的组件覆盖度和底层架构能力。新增 5 个原子组件（Spin、Slider、InputNumber、Empty、BackTop）、4 个分子组件（Alert、Collapse、Popconfirm、Timeline）和 3 个有机体组件（Layout、Card、Menu），同时引入全局事件总线、贝塞尔曲线动画引擎和响应式容器查询系统三项架构增强。所有新增组件严格遵循 NaiveUI 标准，明确指标数据。

## 术语表

- **TSpin**：加载中组件，提供嵌套遮罩和独立模式的加载指示器
- **TSlider**：滑动条组件，支持单滑块和双滑块范围选择
- **TInputNumber**：数字输入框组件，精确控制数值步长、范围和精度
- **TEmpty**：空状态组件，提供标准占位符逻辑
- **TBackTop**：回到顶部组件，支持滚动阈值触发和平滑滚动
- **TAlert**：警告提示组件，常驻式非悬浮提示
- **TCollapse**：折叠面板组件，支持手风琴模式
- **TPopconfirm**：气泡确认框组件，轻量化确认窗口
- **TTimeline**：时间线组件，用于日志和状态流转追踪
- **TLayout**：标准布局容器，实现 Header/Sider/Content/Footer 结构
- **TCard**：卡片容器组件，标准化内容展示容器
- **TMenu**：菜单组件，支持垂直/水平模式和多级嵌套
- **EventBus**：全局事件总线，非父子组件间的通讯机制
- **EasingEngine**：贝塞尔曲线动画引擎，提供标准缓动函数
- **ContainerQuery**：容器查询系统，组件根据父容器尺寸自适应

## 需求

### 需求 44：原子组件 - Spin（加载中）

**用户故事：** 作为一名开发者，我希望使用加载中组件，以便在异步操作期间向用户展示加载状态。

#### 验收标准

1. THE TSpin SHALL 支持独立模式（standalone）和嵌套模式（nested），通过 `mode` 属性设置
2. WHEN TSpin 的 `mode` 为 nested 时，THE TSpin SHALL 作为容器遮罩覆盖其子组件，遮罩层使用半透明背景（opacity 0.38）
3. THE TSpin SHALL 提供三种内置动画形态：旋转环（ring）、跳动点（dots）、呼吸灯（pulse），通过 `animation_type` 属性设置
4. THE TSpin SHALL 支持 small / medium / large 三种尺寸变体，对应动画元素尺寸分别为 20px / 28px / 36px
5. WHEN TSpin 的 `spinning` 属性为 True 时，THE TSpin SHALL 显示加载动画；为 False 时 SHALL 隐藏动画并显示子组件内容
6. THE TSpin SHALL 支持 `description` 属性，在动画下方显示加载提示文本
7. WHEN TSpin 的 `delay` 属性被设置（单位毫秒）时，THE TSpin SHALL 在 spinning 变为 True 后延迟指定时间再显示加载动画，避免短暂加载时的闪烁
8. THE TSpin 的所有动画帧率 SHALL 保持在 60fps，CPU 占用增量不超过 2%

### 需求 45：原子组件 - Slider（滑动条）

**用户故事：** 作为一名开发者，我希望使用滑动条组件，以便让用户通过拖拽方式选择数值或数值范围。

#### 验收标准

1. THE TSlider SHALL 支持单滑块模式和双滑块模式（Range Selector），通过 `range` 属性（布尔值）切换
2. WHEN TSlider 为单滑块模式时，THE TSlider SHALL 通过 `value` 属性（int | float）表示当前值
3. WHEN TSlider 为双滑块模式时，THE TSlider SHALL 通过 `value` 属性（tuple[int | float, int | float]）表示范围，且 value[0] ≤ value[1] 始终成立
4. THE TSlider SHALL 支持 `min` 和 `max` 属性定义取值范围，默认 min=0、max=100
5. THE TSlider SHALL 支持 `step` 属性定义步长，默认 step=1，滑块位置 SHALL 吸附到最近的步长刻度
6. WHEN TSlider 的 `marks` 属性被设置（dict[int | float, str]）时，THE TSlider SHALL 在轨道下方对应位置显示刻度标签
7. WHEN TSlider 的 `tooltip` 属性为 True 时，THE TSlider SHALL 在滑块拖拽时显示当前数值的悬浮提示
8. WHEN TSlider 的值发生变化时，THE TSlider SHALL 发射 `value_changed` 信号并携带当前值
9. THE TSlider SHALL 支持 `disabled` 属性，禁用时降低透明度至 0.5 并屏蔽所有交互
10. THE TSlider SHALL 支持 `vertical` 属性切换为垂直方向布局

### 需求 46：原子组件 - InputNumber（数字输入框）

**用户故事：** 作为一名开发者，我希望使用数字输入框组件，以便精确控制数值输入。

#### 验收标准

1. THE TInputNumber SHALL 支持 `step` 属性定义增减步长，默认 step=1
2. THE TInputNumber SHALL 支持 `min` 和 `max` 属性定义取值范围，输入值 SHALL 始终被约束在 [min, max] 范围内
3. THE TInputNumber SHALL 支持 `precision` 属性定义小数精度（0 表示整数），显示值 SHALL 按精度格式化
4. WHEN 用户按下键盘上箭头键时，THE TInputNumber SHALL 将当前值增加一个 step
5. WHEN 用户按下键盘下箭头键时，THE TInputNumber SHALL 将当前值减少一个 step
6. WHEN 用户长按增减按钮超过 500ms 时，THE TInputNumber SHALL 以 100ms 间隔连续增减数值
7. THE TInputNumber SHALL 在输入框两侧显示增减按钮（+ / -）
8. WHEN TInputNumber 的值发生变化时，THE TInputNumber SHALL 发射 `value_changed` 信号并携带当前数值
9. THE TInputNumber SHALL 支持 small / medium / large 三种尺寸变体
10. WHEN 用户输入非数字字符时，THE TInputNumber SHALL 拒绝该输入并保持当前值不变
11. THE TInputNumber SHALL 支持 `disabled` 属性，禁用时屏蔽所有交互

### 需求 47：原子组件 - Empty（空状态）

**用户故事：** 作为一名开发者，我希望使用空状态组件，以便在无数据时向用户展示友好的占位提示。

#### 验收标准

1. THE TEmpty SHALL 提供默认的空状态图标（SVG 矢量图）
2. THE TEmpty SHALL 支持 `description` 属性设置描述文本，默认为 "暂无数据"
3. THE TEmpty SHALL 支持 `image` 属性传入自定义 QIcon 或 QPixmap 替换默认图标
4. THE TEmpty SHALL 支持 `image_size` 属性控制图标尺寸，默认为 96px
5. THE TEmpty SHALL 支持在描述文本下方嵌入自定义操作区域（通过 `set_extra(widget)` 方法）
6. THE TEmpty SHALL 将图标、描述文本和操作区域垂直居中排列

### 需求 48：原子组件 - BackTop（回到顶部）

**用户故事：** 作为一名开发者，我希望使用回到顶部组件，以便在长页面中提供快速返回顶部的功能。

#### 验收标准

1. THE TBackTop SHALL 监听目标滚动区域（QScrollArea 或 QAbstractScrollArea）的滚动事件
2. WHEN 滚动区域的垂直滚动距离超过 `visibility_height` 阈值（默认 200px）时，THE TBackTop SHALL 以淡入动画显示
3. WHEN 滚动区域的垂直滚动距离低于 `visibility_height` 阈值时，THE TBackTop SHALL 以淡出动画隐藏
4. WHEN 用户点击 TBackTop 时，THE TBackTop SHALL 以线性插值算法平滑滚动到顶部，滚动时长为 300ms
5. THE TBackTop SHALL 默认定位在目标滚动区域的右下角，距离右边界 40px、距离底边界 40px
6. THE TBackTop SHALL 支持 `right` 和 `bottom` 属性自定义定位偏移量
7. THE TBackTop SHALL 支持通过 `set_content(widget)` 方法自定义按钮内容，默认显示向上箭头图标

### 需求 49：分子组件 - Alert（警告提示）

**用户故事：** 作为一名开发者，我希望使用常驻式警告提示组件，以便在页面中展示重要的提示信息。

#### 验收标准

1. THE TAlert SHALL 支持 success / info / warning / error 四种语义类型，通过 `alert_type` 属性设置，每种类型具有独立的图标和配色
2. THE TAlert SHALL 为非悬浮的常驻式提示，直接嵌入页面布局中（区别于 Message 的悬浮弹出）
3. THE TAlert SHALL 支持 `title` 属性设置标题文本
4. THE TAlert SHALL 支持 `description` 属性设置多行内容描述
5. WHEN TAlert 的 `closable` 属性为 True 时，THE TAlert SHALL 在右上角显示关闭按钮
6. WHEN 用户点击 TAlert 的关闭按钮时，THE TAlert SHALL 以淡出动画隐藏并发射 `closed` 信号
7. THE TAlert SHALL 支持通过 `set_action(widget)` 方法在描述文本下方嵌入操作按钮
8. THE TAlert SHALL 支持 `bordered` 属性控制是否显示左侧彩色边框条，默认为 True

### 需求 50：分子组件 - Collapse（折叠面板）

**用户故事：** 作为一名开发者，我希望使用折叠面板组件，以便在有限空间内组织和展示大量内容。

#### 验收标准

1. THE TCollapse SHALL 管理一组 TCollapseItem，每个 item 包含标题栏和可折叠的内容区域
2. WHEN 用户点击某个 TCollapseItem 的标题栏时，THE TCollapse SHALL 以动画形式展开或收起该 item 的内容区域
3. WHEN TCollapse 的 `accordion` 属性为 True 时，THE TCollapse SHALL 在展开一个 item 时自动收起其他所有已展开的 item（手风琴模式）
4. THE TCollapseItem 的展开/收起动画 SHALL 使用 ease-in-out 缓动曲线，动画时长 200ms
5. THE TCollapseItem 的展开/收起动画 SHALL 在嵌套大量复杂 Widget（≥50 个子组件）时保持 60fps 无掉帧
6. THE TCollapse SHALL 支持 `expanded_names` 属性（list[str]）控制初始展开的 item
7. WHEN TCollapseItem 的展开状态变化时，THE TCollapse SHALL 发射 `item_expanded` 信号并携带 item 名称和展开状态
8. THE TCollapseItem SHALL 支持 `disabled` 属性，禁用时标题栏点击无响应

### 需求 51：分子组件 - Popconfirm（气泡确认框）

**用户故事：** 作为一名开发者，我希望使用气泡确认框组件，以便在用户执行危险操作前提供轻量化的确认交互。

#### 验收标准

1. WHEN 用户点击 TPopconfirm 的触发元素时，THE TPopconfirm SHALL 在触发元素旁弹出确认窗口
2. THE TPopconfirm SHALL 支持 `title` 属性设置确认提示文本
3. THE TPopconfirm SHALL 支持 `confirm_text` 和 `cancel_text` 属性自定义确认和取消按钮文字，默认为 "确认" 和 "取消"
4. THE TPopconfirm SHALL 支持 `icon` 属性自定义提示图标，默认显示警告图标
5. WHEN 用户点击确认按钮时，THE TPopconfirm SHALL 关闭弹窗并发射 `confirmed` 信号
6. WHEN 用户点击取消按钮时，THE TPopconfirm SHALL 关闭弹窗并发射 `cancelled` 信号
7. WHEN 用户点击弹窗外部区域时，THE TPopconfirm SHALL 关闭弹窗
8. THE TPopconfirm SHALL 支持 `placement` 属性设置弹窗位置（top / bottom / left / right），默认为 top
9. THE TPopconfirm 的弹出和关闭 SHALL 使用 150ms 的淡入淡出动画

### 需求 52：分子组件 - Timeline（时间线）

**用户故事：** 作为一名开发者，我希望使用时间线组件，以便展示日志、版本演进或状态流转记录。

#### 验收标准

1. THE TTimeline SHALL 管理一组 TTimelineItem，按顺序垂直排列
2. THE TTimelineItem SHALL 支持 `status` 属性设置节点状态：pending / finished / error / default，每种状态具有独立的节点颜色
3. THE TTimelineItem SHALL 支持 `color` 属性自定义节点颜色，覆盖 status 预设
4. THE TTimelineItem SHALL 支持 `title` 属性设置标题文本和 `content` 属性设置详细描述
5. THE TTimelineItem SHALL 支持 `time` 属性设置时间标签，显示在节点右侧或左侧
6. THE TTimeline SHALL 支持 `mode` 属性设置布局模式：left（默认，内容在右）、right（内容在左）
7. THE TTimelineItem SHALL 支持通过 `set_dot(widget)` 方法自定义节点图标，替换默认圆点
8. THE TTimeline SHALL 在相邻节点之间绘制连接线，连接线颜色跟随上方节点的颜色

### 需求 53：有机体组件 - Layout（标准布局容器）

**用户故事：** 作为一名开发者，我希望使用标准布局容器组件，以便快速构建经典的 Header/Sider/Content/Footer 页面结构。

#### 验收标准

1. THE TLayout SHALL 提供 TLayoutHeader、TLayoutSider、TLayoutContent、TLayoutFooter 四个子组件
2. THE TLayout SHALL 支持经典的布局组合：Header + Content + Footer、Header + Sider + Content + Footer、Sider + Content 等
3. THE TLayoutSider SHALL 支持 `collapsed` 属性控制折叠/展开状态
4. WHEN TLayoutSider 的 `collapsed` 状态变化时，THE TLayoutSider SHALL 以 200ms 的宽度过渡动画折叠或展开
5. THE TLayoutSider SHALL 支持 `width` 属性设置展开宽度（默认 240px）和 `collapsed_width` 属性设置折叠宽度（默认 48px）
6. THE TLayoutSider SHALL 支持 `breakpoint` 属性设置响应式断点（sm=640 / md=768 / lg=1024 / xl=1280），当窗口宽度低于断点时自动折叠
7. WHEN TLayoutSider 的折叠状态变化时，THE TLayoutSider SHALL 发射 `collapsed_changed` 信号并携带当前折叠状态
8. THE TLayoutHeader SHALL 支持 `height` 属性设置高度，默认 64px
9. THE TLayoutFooter SHALL 支持 `height` 属性设置高度，默认 64px
10. THE TLayout 的各子组件 SHALL 通过 Design_Token 获取背景色和边框样式

### 需求 54：有机体组件 - Card（卡片容器）

**用户故事：** 作为一名开发者，我希望使用卡片容器组件，以便以标准化的方式展示内容块。

#### 验收标准

1. THE TCard SHALL 提供三个区域：Header 操作区、Body 渲染区、Footer 统计区
2. THE TCard SHALL 支持 `title` 属性设置 Header 区域的标题文本
3. THE TCard SHALL 支持通过 `set_header_extra(widget)` 方法在 Header 右侧嵌入操作控件
4. THE TCard SHALL 支持通过 `set_content(widget)` 方法设置 Body 区域的内容
5. THE TCard SHALL 支持通过 `set_footer(widget)` 方法设置 Footer 区域的内容
6. WHEN TCard 的 `hoverable` 属性为 True 时，THE TCard SHALL 在鼠标悬停时将阴影从 `shadows.small` 加深至 `shadows.medium`，过渡时间 200ms
7. THE TCard SHALL 支持 `bordered` 属性控制是否显示边框，默认为 True
8. THE TCard SHALL 支持 `size` 属性（small / medium / large）控制内边距，对应 padding 分别为 12px / 20px / 24px
9. THE TCard SHALL 支持 `closable` 属性，为 True 时在 Header 右上角显示关闭按钮
10. WHEN 用户点击 TCard 的关闭按钮时，THE TCard SHALL 发射 `closed` 信号

### 需求 55：有机体组件 - Menu（垂直/水平菜单）

**用户故事：** 作为一名开发者，我希望使用菜单组件，以便构建应用的导航结构。

#### 验收标准

1. THE TMenu SHALL 支持 `mode` 属性切换垂直（vertical）和水平（horizontal）布局模式
2. THE TMenu SHALL 管理一组 TMenuItem 和 TMenuItemGroup（子菜单分组）
3. THE TMenuItem SHALL 支持 `key` 属性作为唯一标识，`label` 属性作为显示文本，`icon` 属性设置前置图标
4. THE TMenuItemGroup SHALL 支持多级嵌套，每级子菜单缩进 24px
5. WHEN 用户点击某个 TMenuItem 时，THE TMenu SHALL 发射 `item_selected` 信号并携带该 item 的 key
6. THE TMenu SHALL 支持 `active_key` 属性设置当前激活项，激活项 SHALL 显示高亮样式（左侧彩色指示条 + 主色文本）
7. THE TMenu SHALL 支持 `collapsed` 属性，折叠时仅显示图标，隐藏文本标签
8. WHEN TMenu 的 `collapsed` 状态变化时，THE TMenu SHALL 以 200ms 的宽度过渡动画折叠或展开
9. THE TMenu SHALL 支持 `route_awareness` 属性，为 True 时根据外部传入的路径自动匹配并高亮对应的 TMenuItem
10. WHEN TMenuItemGroup 被点击时，THE TMenuItemGroup SHALL 以动画形式展开或收起子菜单列表
11. THE TMenu SHALL 支持 `disabled` 属性禁用整个菜单的交互

### 需求 56：全局事件总线（Global Event Bus）

**用户故事：** 作为一名开发者，我希望使用全局事件总线，以便在非父子组件间进行通讯，降低跨层级信号槽连接的复杂度。

#### 验收标准

1. THE EventBus SHALL 作为单例提供全局事件发布/订阅机制
2. THE EventBus SHALL 支持 `emit(event_name, *args, **kwargs)` 方法发布事件
3. THE EventBus SHALL 支持 `on(event_name, callback)` 方法订阅事件
4. THE EventBus SHALL 支持 `off(event_name, callback)` 方法取消订阅
5. THE EventBus SHALL 支持 `once(event_name, callback)` 方法订阅一次性事件，触发后自动取消订阅
6. WHEN 事件被发布时，THE EventBus SHALL 按订阅顺序依次调用所有已注册的回调函数
7. IF 某个回调函数执行时抛出异常，THEN THE EventBus SHALL 捕获异常并记录日志，继续执行后续回调
8. THE EventBus SHALL 支持 `clear(event_name)` 方法清除指定事件的所有订阅，以及 `clear_all()` 方法清除所有订阅

### 需求 57：动画引擎 - 贝塞尔曲线缓动函数（Easing Functions）

**用户故事：** 作为一名开发者，我希望组件库提供统一的贝塞尔曲线缓动函数，以便所有 UI 动画具有一致的"肉感"与弹性。

#### 验收标准

1. THE EasingEngine SHALL 提供以下标准缓动函数：ease_in_cubic、ease_out_cubic、ease_in_out_cubic、ease_in_quad、ease_out_quad、ease_in_out_quad
2. THE EasingEngine 的每个缓动函数 SHALL 接受归一化时间参数 t（0.0 ≤ t ≤ 1.0）并返回归一化进度值（0.0 ≤ result ≤ 1.0）
3. THE EasingEngine 的每个缓动函数 SHALL 满足边界条件：f(0.0) = 0.0 且 f(1.0) = 1.0
4. THE EasingEngine SHALL 提供 `custom_bezier(p1x, p1y, p2x, p2y)` 方法，支持自定义三次贝塞尔曲线
5. THE EasingEngine SHALL 作为全局默认缓动引擎，所有组件的位移和缩放动画 SHALL 默认使用 ease_in_out_cubic 曲线
6. THE EasingEngine 的缓动函数计算 SHALL 在单次调用中完成，耗时不超过 1μs

### 需求 58：响应式系统 - 容器查询（Container Queries）

**用户故事：** 作为一名开发者，我希望组件能根据其父容器的尺寸自动调整布局和展示等级，以便在不同布局槽位中获得最佳展示效果。

#### 验收标准

1. THE ContainerQuery 系统 SHALL 提供 `ContainerQueryMixin`，组件通过混入该 Mixin 获得容器查询能力
2. WHEN 应用了 ContainerQueryMixin 的组件的父容器尺寸发生变化时，THE 组件 SHALL 收到 `container_resized` 回调并携带新的容器宽度和高度
3. THE ContainerQueryMixin SHALL 支持 `add_breakpoint(name, min_width, max_width)` 方法注册断点规则
4. WHEN 父容器宽度跨越某个断点时，THE ContainerQueryMixin SHALL 发射 `breakpoint_changed` 信号并携带当前匹配的断点名称
5. THE ContainerQueryMixin SHALL 支持 `current_breakpoint()` 方法返回当前匹配的断点名称
6. THE ContainerQuery 系统 SHALL 使用 `QResizeEvent` 监听父容器尺寸变化，不使用轮询机制
7. THE ContainerQuery 系统 SHALL 在父容器尺寸变化时以不超过 16ms 的延迟触发回调（确保 60fps 响应）


---

# 需求文档：Tyto UI 组件库 V1.1.0 - 组件特性增强（第二批）

## 简介

V1.1.0 特性增强（第二批）聚焦于补齐 V1.1.0 新增组件中尚未实现的 NaiveUI 特性。涉及 5 个原子组件（TSpin、TSlider、TInputNumber、TEmpty、TBackTop）和 4 个分子组件（TAlert、TCollapse、TPopconfirm、TTimeline）的属性扩展、交互增强和 Bug 修复。所有增强严格参照 NaiveUI 标准。

## 术语表

- **rotate**：TSpin 自定义图标是否旋转的控制属性
- **contentClass / contentStyle**：TSpin 嵌套模式下内容区域的自定义样式
- **strokeWidth / stroke**：TSpin 加载环的线条宽度和颜色自定义
- **reverse**：TSlider 反向滑动条模式
- **step="mark"**：TSlider 步长吸附到刻度标记的特殊模式
- **buttonPlacement**：TInputNumber 增减按钮的位置（right 或 both）
- **showButton**：TInputNumber 是否显示增减按钮
- **arrowPlacement**：TCollapse 箭头位置（left 或 right）
- **triggerAreas**：TCollapse 触发展开的区域配置
- **positiveButtonProps / negativeButtonProps**：TPopconfirm 确认/取消按钮的自定义属性
- **horizontal**：TTimeline 水平时间线模式
- **lineType**：TTimeline 连接线类型（default 或 dashed）

## 需求

### 需求 59：TSpin 特性增强

**用户故事：** 作为一名开发者，我希望加载中组件支持自定义图标、自定义加载环样式和更灵活的尺寸控制，以便在不同业务场景中提供个性化的加载体验。

#### 验收标准

1. WHEN TSpin 的 `rotate` 属性为 True（默认）时，THE TSpin 的自定义图标 SHALL 以旋转动画显示；为 False 时 SHALL 静态显示
2. THE TSpin SHALL 支持 `content_class` 属性，用于为嵌套模式下的内容区域设置自定义 CSS 类名
3. THE TSpin SHALL 支持 `content_style` 属性（dict），用于为嵌套模式下的内容区域设置自定义内联样式
4. THE TSpin SHALL 支持 `stroke_width` 属性（int | float），自定义加载环的线条宽度，默认为 2
5. THE TSpin SHALL 支持 `stroke` 属性（str），自定义加载环的颜色，默认使用 `colors.primary`
6. THE TSpin SHALL 支持通过 `set_icon(widget)` 方法传入自定义图标 widget，替换默认旋转环动画
7. THE TSpin 的 `size` 属性 SHALL 支持传入具体数字（int），除现有的 SpinSize 枚举外，允许精确控制动画元素尺寸

### 需求 60：TSlider 特性增强

**用户故事：** 作为一名开发者，我希望滑动条组件支持反向滑动、键盘操作控制、tooltip 位置配置和刻度吸附模式，以便提供更灵活的数值选择交互。

#### 验收标准

1. WHEN TSlider 的 `reverse` 属性为 True 时，THE TSlider SHALL 反转滑动方向（水平模式下值从右到左递增，垂直模式下值从上到下递增）
2. THE TSlider SHALL 支持 `keyboard` 属性（bool），默认为 True，控制是否支持键盘左右/上下箭头操作
3. WHEN TSlider 的 `keyboard` 属性为 False 时，THE TSlider SHALL 忽略键盘箭头键事件
4. THE TSlider SHALL 支持 `placement` 属性（str），设置 tooltip 弹出位置（"top" | "bottom" | "left" | "right"），默认为 "top"
5. WHEN TSlider 的 `step` 属性被设置为字符串 `"mark"` 时，THE TSlider SHALL 将滑块位置吸附到最近的 marks 刻度标记位置
6. THE TSlider SHALL 支持 `drag_start` 信号，在用户开始拖拽滑块时发射
7. THE TSlider SHALL 支持 `drag_end` 信号，在用户结束拖拽滑块时发射

### 需求 61：TInputNumber 特性增强

**用户故事：** 作为一名开发者，我希望数字输入框组件支持更多交互控制、样式变体和自定义功能，以便在复杂表单场景中灵活使用。

#### 验收标准

1. WHEN TInputNumber 的 `autofocus` 属性为 True 时，THE TInputNumber SHALL 在创建后自动获得焦点
2. WHEN TInputNumber 的 `loading` 属性为 True 时，THE TInputNumber SHALL 在输入框内显示加载旋转动画并屏蔽增减操作
3. THE TInputNumber SHALL 支持 `placeholder` 属性设置占位符文本
4. THE TInputNumber SHALL 支持 `bordered` 属性控制是否显示边框，默认为 True
5. THE TInputNumber SHALL 支持 `show_button` 属性控制是否显示增减按钮，默认为 True；为 False 时隐藏增减按钮
6. THE TInputNumber SHALL 支持 `button_placement` 属性（"right" | "both"），默认为 "right"；为 "both" 时减号按钮在左侧、加号按钮在右侧
7. WHEN TInputNumber 的 `readonly` 属性为 True 时，THE TInputNumber SHALL 允许查看数值但禁止编辑和增减操作
8. WHEN TInputNumber 的 `clearable` 属性为 True 时，THE TInputNumber SHALL 在有值时显示清空按钮，点击后清空输入值
9. WHEN TInputNumber 的 `round` 属性为 True 时，THE TInputNumber SHALL 渲染为全圆角输入框
10. THE TInputNumber SHALL 支持 `status` 属性设置验证状态（"success" | "warning" | "error"），显示对应的边框颜色
11. THE TInputNumber SHALL 支持 `validator` 属性（Callable），自定义验证函数，返回 True 表示有效
12. THE TInputNumber SHALL 支持 `parse` 属性（Callable[[str], int | float | None]），自定义将字符串解析为数值的函数
13. THE TInputNumber SHALL 支持 `format_func` 属性（Callable[[int | float], str]），自定义将数值格式化为显示字符串的函数
14. THE TInputNumber SHALL 支持 `update_value_on_input` 属性（bool），默认为 True，控制是否在输入时实时更新值
15. THE TInputNumber SHALL 支持 `keyboard` 属性（dict），配置键盘操作（`{"ArrowUp": bool, "ArrowDown": bool}`），默认均为 True
16. THE TInputNumber SHALL 支持 `input_props` 属性（dict），透传给内部 QLineEdit 的原生属性
17. THE TInputNumber SHALL 支持 tiny / small / medium / large 四种尺寸变体，通过 `size` 属性设置
18. THE TInputNumber SHALL 支持通过 `set_prefix(widget)` 和 `set_suffix(widget)` 方法设置前缀/后缀自定义内容
19. THE TInputNumber SHALL 支持通过 `set_add_icon(icon)` 和 `set_minus_icon(icon)` 方法自定义增减按钮图标
20. THE TInputNumber SHALL 支持 `focused` 信号，在获得焦点时发射
21. THE TInputNumber SHALL 支持 `blurred` 信号，在失去焦点时发射
22. THE TInputNumber SHALL 支持 `cleared` 信号，在清空值时发射

### 需求 62：TEmpty 特性增强

**用户故事：** 作为一名开发者，我希望空状态组件支持更多尺寸变体和显示控制，以便在不同容器尺寸中灵活使用。

#### 验收标准

1. THE TEmpty SHALL 支持 tiny / small / medium / large / huge 五种尺寸变体，通过 `size` 属性设置，默认为 medium
2. THE TEmpty SHALL 支持 `show_description` 属性（bool），默认为 True，控制是否显示描述文本
3. WHEN TEmpty 的 `show_description` 属性为 False 时，THE TEmpty SHALL 隐藏描述文本区域
4. THE TEmpty SHALL 支持 `show_icon` 属性（bool），默认为 True，控制是否显示图标
5. WHEN TEmpty 的 `show_icon` 属性为 False 时，THE TEmpty SHALL 隐藏图标区域

### 需求 63：TBackTop 特性增强

**用户故事：** 作为一名开发者，我希望回到顶部组件支持受控显示模式、渲染目标容器和灵活的监听目标配置，以便在复杂布局中灵活使用。

#### 验收标准

1. THE TBackTop SHALL 支持 `show` 属性（bool | None），为 None 时使用自动显示/隐藏逻辑（默认行为），为 True/False 时受控显示/隐藏
2. THE TBackTop SHALL 支持 `to` 属性（QWidget | None），指定渲染目标容器（类似 teleport），默认为 None（渲染在 parent 中）
3. THE TBackTop SHALL 支持 `listen_to` 属性，接受字符串（objectName）、QWidget 实例或 Callable 返回 QWidget，指定监听滚动事件的目标
4. THE TBackTop SHALL 支持 `visibility_changed` 信号，在显示/隐藏状态变化时发射并携带当前可见状态

### 需求 64：TAlert 特性增强

**用户故事：** 作为一名开发者，我希望警告提示组件支持 default 类型变体、图标显示控制和自定义图标，以便提供更灵活的提示展示。

#### 验收标准

1. THE TAlert 的 `alert_type` 属性 SHALL 新增 `"default"` 变体，与现有 success / info / warning / error 共存，default 类型使用中性配色
2. THE TAlert SHALL 支持 `show_icon` 属性（bool），默认为 True，控制是否显示类型图标
3. WHEN TAlert 的 `show_icon` 属性为 False 时，THE TAlert SHALL 隐藏左侧类型图标
4. THE TAlert SHALL 支持通过 `set_icon(widget)` 方法传入自定义图标 widget，替换默认类型图标

### 需求 65：TCollapse 特性增强

**用户故事：** 作为一名开发者，我希望折叠面板组件支持箭头位置配置、触发区域控制和更丰富的标题栏自定义，以便在不同 UI 场景中灵活使用。

#### 验收标准

1. THE TCollapse SHALL 支持 `arrow_placement` 属性（"left" | "right"），默认为 "left"，控制展开/收起箭头图标的位置
2. THE TCollapse SHALL 支持 `trigger_areas` 属性（list[str]），可选值为 `["main", "extra", "arrow"]`，控制哪些区域点击可触发展开/收起，默认为 `["main", "extra", "arrow"]`
3. WHEN `trigger_areas` 不包含 "main" 时，THE TCollapseItem 的标题文本区域点击 SHALL 不触发展开/收起
4. WHEN `trigger_areas` 不包含 "arrow" 时，THE TCollapseItem 的箭头图标点击 SHALL 不触发展开/收起
5. THE TCollapse SHALL 支持 `item_header_clicked` 信号，在任意 TCollapseItem 的标题栏被点击时发射，携带 item 名称
6. THE TCollapseItem SHALL 支持通过 `set_title(widget)` 方法传入自定义标题内容 widget，替换默认文本标题
7. THE TCollapseItem SHALL 支持通过 `set_header_extra(widget)` 方法在标题栏右侧（箭头旁）嵌入额外内容
8. THE TCollapseItem SHALL 支持通过 `set_arrow(widget)` 方法传入自定义箭头图标 widget，替换默认箭头

### 需求 66：TPopconfirm 特性增强与 Bug 修复

**用户故事：** 作为一名开发者，我希望气泡确认框组件支持图标显示控制、按钮自定义、多种触发方式和事件回调，并修复点击非按钮区域关闭弹窗的 Bug。

#### 验收标准

1. THE TPopconfirm SHALL 支持 `show_icon` 属性（bool），默认为 True，控制是否显示提示图标
2. WHEN TPopconfirm 的 `show_icon` 属性为 False 时，THE TPopconfirm SHALL 隐藏提示图标
3. THE TPopconfirm SHALL 支持 `positive_button_props` 属性（dict），用于自定义确认按钮的 TButton 属性（如 type、size、loading 等）
4. THE TPopconfirm SHALL 支持 `negative_button_props` 属性（dict），用于自定义取消按钮的 TButton 属性
5. THE TPopconfirm SHALL 支持 `trigger` 属性（"click" | "hover" | "focus" | "manual"），默认为 "click"，控制弹窗的触发方式
6. WHEN TPopconfirm 的 `trigger` 属性为 "hover" 时，THE TPopconfirm SHALL 在鼠标悬停触发元素时显示弹窗
7. WHEN TPopconfirm 的 `trigger` 属性为 "focus" 时，THE TPopconfirm SHALL 在触发元素获得焦点时显示弹窗
8. WHEN TPopconfirm 的 `trigger` 属性为 "manual" 时，THE TPopconfirm SHALL 仅通过 `show_popup()` / `hide_popup()` 方法控制显示
9. THE TPopconfirm SHALL 支持 `on_positive_click` 回调属性（Callable），在用户点击确认按钮时调用
10. THE TPopconfirm SHALL 支持 `on_negative_click` 回调属性（Callable），在用户点击取消按钮时调用
11. THE TPopconfirm SHALL 支持通过 `set_icon(widget)` 方法传入自定义提示图标 widget
12. **Bug 修复**：WHEN TPopconfirm 弹窗已显示时，点击弹窗内非按钮区域 SHALL NOT 关闭弹窗；弹窗 SHALL 仅通过点击确认按钮或取消按钮关闭
13. WHEN 用户点击弹窗外部区域（非弹窗内部）时，THE TPopconfirm SHALL 关闭弹窗（此行为保持不变）

### 需求 67：TTimeline 特性增强

**用户故事：** 作为一名开发者，我希望时间线组件支持水平布局、尺寸变体、自定义节点图标尺寸和更丰富的节点配置，以便在不同展示场景中灵活使用。

#### 验收标准

1. WHEN TTimeline 的 `horizontal` 属性为 True 时，THE TTimeline SHALL 以水平方向排列所有 TTimelineItem，节点从左到右排列
2. THE TTimeline SHALL 支持 `size` 属性（"medium" | "large"），默认为 "medium"，控制时间线的整体尺寸
3. THE TTimeline SHALL 支持 `icon_size` 属性（int），自定义节点图标的尺寸（像素），默认为 12
4. THE TTimelineItem 的 `status` 属性 SHALL 支持 NaiveUI 完整的类型集合：default / success / error / warning / info
5. THE TTimelineItem SHALL 支持 `line_type` 属性（"default" | "dashed"），控制该节点下方连接线的类型，默认为 "default"（实线）
6. WHEN TTimelineItem 的 `line_type` 属性为 "dashed" 时，THE TTimelineItem 下方的连接线 SHALL 以虚线样式绘制
7. THE TTimelineItem SHALL 支持通过 `set_icon(widget)` 方法传入自定义节点图标 widget，替换默认圆点（与现有 `set_dot()` 统一）
8. THE TTimelineItem SHALL 支持通过 `set_title(widget)` 方法传入自定义标题内容 widget，替换默认文本标题
9. THE TTimelineItem SHALL 支持通过 `set_footer(widget)` 方法在内容区域下方嵌入自定义底部内容


---

# 需求文档：Tyto UI 组件库 V1.1.0 - Gallery/Playground 同步更新与工具模块

## 简介

V1.1.0 Gallery/Playground 同步更新版本确保 Gallery 预览画廊和 Playground 交互式调试应用同步展示所有 V1.1.0 新增组件。同时新增 `utils/color.py` 颜色解析工具模块，为组件的 CSS 颜色字符串解析提供统一支持。

## 需求

### 需求 68：Gallery Showcase V1.1.0 同步更新

**用户故事：** 作为一名开发者，我希望 Gallery 的组件展示面板同步展示 V1.1.0 新增的所有组件，以便直观预览和测试新功能。

#### 验收标准

1. THE Gallery SHALL 为以下 V1.1.0 新增原子组件提供独立的 Showcase 展示模块：Spin、Slider、InputNumber、Empty、BackTop
2. THE Gallery SHALL 为以下 V1.1.0 新增分子组件提供独立的 Showcase 展示模块：Alert、Collapse、Popconfirm、Timeline
3. THE Gallery SHALL 为以下 V1.1.0 新增有机体组件提供独立的 Showcase 展示模块：Layout、Card、Menu
4. THE Gallery 的 NavigationMenu SHALL 自动从组件注册表中获取并展示所有 V1.1.0 新增组件
5. EACH 新增 Showcase SHALL 至少包含基础用法（Basic Usage）展示区块

### 需求 69：Playground 属性定义 V1.1.0 同步更新

**用户故事：** 作为一名开发者，我希望 Playground 的属性面板同步支持 V1.1.0 新增的所有组件，以便交互式调试新组件的属性。

#### 验收标准

1. THE Playground SHALL 为以下 V1.1.0 新增原子组件提供完整的属性定义：Spin、Slider、InputNumber、Empty、BackTop
2. THE Playground SHALL 为以下 V1.1.0 新增分子组件提供完整的属性定义：Alert、Collapse、Popconfirm、Timeline
3. THE Playground SHALL 为以下 V1.1.0 新增有机体组件提供完整的属性定义：Layout、Card、Menu、Message、Modal
4. EACH 属性定义 SHALL 包含 `apply` 回调函数，用于将属性值应用到组件实例上
5. THE Playground 的 NavigationMenu SHALL 自动从组件注册表中获取并展示所有 V1.1.0 新增组件

### 需求 70：颜色解析工具模块

**用户故事：** 作为一名开发者，我希望组件库提供统一的 CSS 颜色字符串解析工具，以便在组件中正确解析 Design Token 中的 `rgba()` 和 `rgb()` 格式颜色值。

#### 验收标准

1. THE `parse_color` 函数 SHALL 支持解析 hex 格式颜色字符串（#RGB、#RRGGBB、#AARRGGBB）
2. THE `parse_color` 函数 SHALL 支持解析 `rgba(r, g, b, a)` 格式颜色字符串，其中 a 为 [0, 1] 范围的浮点数
3. THE `parse_color` 函数 SHALL 支持解析 `rgb(r, g, b)` 格式颜色字符串
4. THE `parse_color` 函数 SHALL 支持解析 Qt 命名颜色（如 "red"、"blue"）
5. WHEN 传入无效颜色字符串时，THE `parse_color` 函数 SHALL 返回 fallback 参数指定的默认颜色（默认为 "#000000"）
6. THE `parse_color` 函数 SHALL 位于 `src/tyto_ui_lib/utils/color.py` 模块中
