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
