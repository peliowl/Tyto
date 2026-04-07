这是一个新的项目，根据以下的项目内容描述，生成kiro的specs相关文档、hook及AGENTS.md文档：
1. 技术栈
   - 核心框架：Pyside6（Latest）
   - 构建系统：Setuptools
   - 包管理及分发：uv、Twine
   - 静态资源编译：Pyside6-rcc
   - 类型支持：Pyright、Mypy
   - 代码质量：Ruff
   - 样式引擎：Jinja2 + QSS
   - 文档体系：MkDocs-Material、mkdocstrings、markdown
   - 测试工具：pytest-qt、pytest、pytest-xdist
2. 项目结构
Tyto/
├── .github/                   # 自动化流水线
├── .venv/                     # 本地 Python 虚拟环境（由 uv/venv 生成，.gitignore 忽略）
├── assets/                    # 静态资源
│   ├── fonts/                 # 品牌字体
│   ├── icons/                 # 原始 SVG 矢量图标
│   └── themes/                # 设计令牌 (Design Tokens) 定义文件
├── bin/                       # 可执行脚本（如快速启动 Gallery 预览）
├── build/                     # 构建中间产物（由 uv/setuptools 自动生成）
├── scripts/                   # 工程化工具脚本
├── docs/                      # 知识库
│   ├── api/                   # 自动生成的组件 API 接口说明
│   ├── guide/                 # 开发者上手指南
│   └── agent_memory/          # Agent 执行任务后的经验积累
│       ├── references/        # 引用文档：markdown格式存储经验
│       └── experience.json    # 语义索引：供 Agent 快速检索的经验元数据
├── examples/                  # 组件预览画廊 (Gallery)
├── src/
│   └── tyto_ui_lib/
│       ├── __init__.py
│       ├── core/              # 底层引擎（状态管理、DPI、主题）
│       ├── common/            # 行为混入（Mixins）与基类
│       │   ├── base.py        # 包含 Agent 友好的详细 Docstrings
│       │   └── traits/        # 组件特征定义（可拖拽、可缩放等）
│       ├── components/        # 原子化组件
│       │   ├── atoms/         # 基础控件
│       │   ├── molecules/     # 复合控件
│       │   └── organisms/     # 复杂机构
│       ├── styles/            # 动态样式工厂
│       └── utils/             # 辅助工具
├── dist/                      # 【发布期】打包后的 .whl 和 .tar.gz 文件
├── tests/                     # 单元测试与视觉回归测试
├── pyproject.toml             # uv/Poetry 配置
├── LICENSE                    # 开源协议
├── .gitignore                 # 忽略 .venv/, __pycache__/, build/, dist/ 等
├── .python-version            # 明确指定项目所需的 Python 版本（3.12）
├── MANIFEST.in                # 定义哪些非代码文件（如 QSS, JSON）需打包进 Wheel
├── AGENTS.md                  # 规范说明
└── README.md
3. 核心需求描述
   1. 维度定义与组件分级
      - 原子级（Atoms）：实现最小功能单元（如 PushButton, LineEdit, CheckBox）。要求零业务逻辑依赖，仅封装基础绘图逻辑（PaintEvent）与交互状态（State Machine）
      - 分子级（Molecules）：由原子组件组合而成的简单功能簇（如 SearchBar, FieldGroup）。负责原子间的局部信号转发与布局协调。
      - 有机体级（Organisms）：具备独立业务语境的复杂 UI 模块（如 NavigationSideBar, DataTable）。作为数据驱动的实体，对接核心业务逻辑与模型（QAbstractItemModel）。
   2. 样式与视觉一致性
      - Token 驱动：建立全局语义化颜色与尺寸体系（如 ColorPrimary, SpacingMedium, RadiusSmall）。严禁在组件内硬编码（Hard-coding）像素值。
      - 动态渲染引擎：基于 Python 字符串模板实现 运行时 QSS 注入。支持实时切换主题（Light/Dark Mode）且无界面闪烁，内存占用增量控制在 5% 以内。
   3. 交互行为抽象
      - 解耦交互逻辑：通过 Mixins（混入类）抽象通用行为（如 HoverEffect, ClickRipple, Draggable）。
      - 性能约束：高频交互组件（如滚动列表、动态图表）必须通过 QStyledItemDelegate 进行低开销绘制，确保在 4K 分辨率下保持 60 FPS 的渲染帧率。
4. 第一个版本（V1.0.0）实现目标
   - 基础控件及widget
     - Atoms (原子级控件)
       - Button (按钮)：支持 Primary, Default, Dashed, Text 四种类型；具备 Loading 状态与 Disabled 禁用态。
       - Checkbox (复选框)：支持选中、未选中及 Indeterminate（半选）状态；支持动画过渡。
       - Radio (单选框)：圆环平滑缩放动画；支持分组管理逻辑。
       - Input (输入框)：支持 Prefix/Suffix 图标插入；支持一键清空（Clearable）与密码可见性切换。
       - Switch (开关)：仿 iOS/NaiveUI 风格；支持丝滑的位移与缩放动画。
       - Tag (标签)：支持不同尺寸（Small, Medium, Large）与可关闭（Closable）属性。
     - Molecules (分子级/组合 Widget)
       - SearchBar (搜索栏)：集成 Input 与 Button，支持实时搜索回调。
       - Breadcrumb (面包屑)：支持自定义分隔符与点击跳转逻辑。
       - InputGroup (输入组合)：支持按钮与输入框的紧凑横向拼接。
     - Organisms (有机体/复杂 Widget)
       - Message (全局提示)：支持自上而下的悬浮弹出（Info, Success, Warning, Error），自动消失逻辑。
       - Modal (模态对话框)：支持遮罩层（Overlay）、标题栏自定义及平滑的缩放弹出效果。
   - 交互效果定义 (Interactive Effects)
     - Hover 状态：背景色平滑渐变（Transition Time: 200ms），光标变为 PointingHand
     - Pressed 状态：背景色加深，模拟轻微的“下陷”视觉位移（Scale: 0.98）。
     - Focus 状态：控件外围显示 2px 的半透明主色扩散光晕（Box-shadow 效果）。
     - Loading 状态：按钮文字旁显示 SVG 旋转动画，同时屏蔽所有鼠标点击事件。
     - Disabled 状态：整体透明度降至 0.5，光标变为 Forbidden（禁止点击）。
   - 样式风格（仿NaiveUI风格样式，需要支持light、dark两套样式）
     - 参考图 
       - [img.png](docs/image/img.png)
       - [img_1.png](docs/image/img_1.png)
       - [img_2.png](docs/image/img_2.png)
       - [img_3.png](docs/image/img_3.png)
       - [img_4.png](docs/image/img_4.png)
       - [img_5.png](docs/image/img_5.png)
       - [img_6.png](docs/image/img_6.png)
       - [img_7.png](docs/image/img_7.png)
       - [img_8.png](docs/image/img_8.png)
       - [img_9.png](docs/image/img_9.png)
       - [img_10.png](docs/image/img_10.png)
       - [img_11.png](docs/image/img_11.png)
5. kiro应该时刻遵循的规范
   - 当遇到不确定的事情且其置信度低于80%时，需要提供解决方案给用户进行决策
   - 在更新项目结构后，需要触发hook检查specs中的相关文档内容是否与项目最新状态保持一致，如果不一致，需要更新相关的specs文档内容
