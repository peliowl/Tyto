# Tyto UI Library

[![Python](https://img.shields.io/badge/Python-≥3.12-blue)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-≥6.7-green)](https://doc.qt.io/qtforpython/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.1.0-orange)](https://github.com/tyto-team/tyto-ui-lib)

基于 PySide6 的现代化桌面 UI 组件库，采用**原子设计方法论**（Atomic Design），提供从基础控件到复杂业务模块的分层组件体系。

视觉风格参考 [NaiveUI](https://www.naiveui.com/)，样式系统基于 **Design Token + Jinja2 + QSS** 动态渲染架构，支持 Light / Dark 主题实时无闪烁切换。

---

## 设计哲学

### 原子设计（Atomic Design）

Tyto 将 Brad Frost 的原子设计方法论引入桌面 UI 开发，组件按三层分级：

- **Atom（原子）**：最小粒度的 UI 元素，零业务逻辑依赖，仅封装绘图逻辑与交互状态机。如 Button、Checkbox、Input 等
- **Molecule（分子）**：由多个 Atom 组合而成，负责局部信号转发与布局协调。如 SearchBar = Input + Button
- **Organism（有机体）**：可对接业务逻辑与数据模型，承载完整的交互场景。如 Message、Modal

这种分层策略确保了组件的**高内聚、低耦合**，开发者可以自由组合原子级组件构建更复杂的界面。

### Design Token 驱动

所有视觉属性（颜色、间距、圆角、字号等）由 Design Token 统一管理，组件代码中**严禁硬编码**任何像素值或颜色值。Token 以 JSON 格式定义，通过 Jinja2 模板引擎渲染为 QSS 样式表，实现样式与逻辑的彻底分离。

### Mixin 行为注入

交互行为（Hover、Click Ripple、Focus Glow、Disabled）通过 Python Mixin 混入机制注入组件，避免在每个组件中重复实现相同的交互逻辑。这种模式使得行为可以灵活组合，同时保持组件代码的简洁。

### 主题热切换

基于 ThemeEngine 单例 + Qt 信号广播机制，所有继承 BaseWidget 的组件自动响应主题变更。切换过程无闪烁、无重建，用户体验流畅自然。

---

## 架构概览

```
tyto_ui_lib/
├── core/                       # 底层引擎
│   ├── theme_engine.py         #   ThemeEngine 单例：主题状态管理与信号广播
│   ├── tokens.py               #   DesignTokenSet 数据模型：Token 解析与访问
│   ├── easing_engine.py        #   EasingEngine：贝塞尔曲线缓动动画引擎
│   └── event_bus.py            #   EventBus：全局事件总线，组件间解耦通信
├── common/                     # 公共基础
│   ├── base.py                 #   BaseWidget 基类：自动主题响应、样式刷新
│   └── traits/                 #   行为 Mixin
│       ├── hover_effect.py     #     鼠标悬停平滑过渡
│       ├── click_ripple.py     #     点击涟漪扩散动画
│       ├── focus_glow.py       #     聚焦外发光效果
│       ├── disabled.py         #     禁用态透明度降低与交互屏蔽
│       └── container_query.py  #     容器查询响应式断点系统
├── components/                 # UI 组件（原子设计分层）
│   ├── atoms/                  #   原子级：Button, Checkbox, Radio, Input, Switch, Tag,
│   │                           #           InputNumber, Slider, Spin, BackTop, Empty
│   ├── molecules/              #   分子级：SearchBar, Breadcrumb, InputGroup,
│   │                           #           Alert, Collapse, Popconfirm, Timeline
│   └── organisms/              #   有机体：Message, Modal, Card, Layout, Menu
├── styles/                     # 样式工厂
│   ├── templates/              #   Jinja2 QSS 模板 (*.qss.j2)
│   └── tokens/                 #   主题 Token 文件 (light.json, dark.json)
└── utils/                      # 辅助工具
    └── color.py                #   颜色解析工具（hex / rgba / 命名色）
```

---

## 版本特性

### v1.1.0 — 组件大规模扩展 & 核心引擎增强

v1.1.0 新增 13 个组件（5 Atoms + 4 Molecules + 4 Organisms）、4 个核心模块，并对已有组件进行多项增强与修复。

#### 新增组件

- **原子级**：TBackTop（回到顶部）、TEmpty（空状态占位）、TInputNumber（数字输入框）、TSlider（滑块）、TSpin（加载旋转指示器）
- **分子级**：TAlert（警告提示）、TCollapse / TCollapseItem（折叠面板）、TPopconfirm（气泡确认框）、TTimeline / TTimelineItem（时间线）
- **有机体**：TCard（卡片容器）、TLayout 布局系统（Header / Footer / Sider / Content + 响应式断点）、TMenu 导航菜单（垂直/水平模式、多级子菜单弹出、折叠切换、MenuOption 数据载体）

#### 新增核心模块

- **EasingEngine**：贝塞尔曲线缓动动画引擎，提供标准缓动函数和自定义 cubic-bezier 支持
- **EventBus**：全局事件总线，支持 on / off / once / emit 发布订阅模式
- **ContainerQueryMixin**：容器查询 Mixin，实现类似 CSS Container Query 的响应式断点行为
- **parse_color**：颜色解析工具函数，统一处理 hex / rgba / 命名色等格式

#### 组件增强与修复

- **TButton**：新增 `set_button_type()` 运行时切换、圆形加载态 Spinner 居中与颜色跟随主题、SVG 模板化动态颜色注入
- **TTag**：新增 `set_tag_type()` / `set_size()` / `set_checkable()` 运行时切换方法、`sizeHint()` 基于 Token 动态计算
- **TCheckbox / TRadio / TSwitch**：`QColor()` 构造替换为 `parse_color()`，修复暗色模式下 rgba 颜色解析异常

#### 样式系统扩展

- 新增 12 个 QSS 模板文件
- Design Token 新增 `spin_sizes`、`slider`、`layout`、`card`、`menu` 等类别
- ThemeEngine 渲染上下文同步扩展

#### Gallery & Playground

- Gallery 新增 12 个组件展示用例
- Playground 新增 14 个组件属性定义，导航菜单增加滚动容器

### v1.0.2 — 原子组件特性增强 & Playground


V1.0.2 大幅增强了原子组件的功能覆盖度，并新增了交互式调试应用 Playground。

#### 组件增强亮点

- **TButton**：新增 9 种类型变体（tertiary / info / success / warning / error 等）、4 种尺寸（tiny / small / medium / large）、圆形/圆角/幽灵/块级/图标按钮、自定义颜色、secondary/tertiary/quaternary 层级样式
- **TInput**：新增 text / textarea / password 三种输入模式、4 种尺寸、圆角输入框、字数统计、验证状态（success / warning / error）、加载动画、只读模式、textarea 自适应高度
- **TCheckbox**：新增 3 种尺寸、禁用状态、value 属性、checked_value / unchecked_value 自定义返回值
- **TCheckboxGroup**：新增分组管理器，支持 min / max 可选数量限制、统一尺寸和禁用控制
- **TRadio**：新增 3 种尺寸、禁用状态、name 属性
- **TRadioButton**：新增按钮样式单选组件，在 RadioGroup 中呈现为按钮组布局
- **TSwitch**：新增 3 种尺寸、加载状态旋转动画、方形轨道模式、checked_value / unchecked_value 自定义值、轨道内文字显示、橡皮筋回弹效果
- **TTag**：新增 info 类型和 tiny 尺寸、圆角标签、禁用状态、bordered 控制、自定义颜色、checkable 可选中交互、strong 加粗文字

#### Playground 交互式调试应用

新增独立的 Playground 应用，支持实时修改控件属性并预览效果：
- 三栏布局：左侧导航菜单 + 中部组件预览 + 右侧属性面板
- 属性面板根据属性类型自动生成编辑控件（下拉框、复选框、输入框、数字框等）
- 支持 Light / Dark 主题实时切换

### v1.0.1 — Gallery 重构 & Bug 修复 & Dark 模式优化

- Gallery 采用 MVVM 架构重构，拆分为 models / viewmodels / views / showcases 模块化结构
- 左侧分类导航菜单 + 右侧组件特性展示面板
- 修复 Button / Tag QSS 动态属性选择器不生效问题
- 修复 Input / SearchBar 清空按钮位置溢出问题
- 修复 Message 弹出位置和样式异常
- 全面优化 Dark 模式下所有组件和 Gallery 界面的颜色显示

### v1.0.0 — 初始版本

首个正式版本，交付完整的组件库核心架构和 11 个 UI 组件。

---

## 组件一览

### 原子组件（Atoms）

| 组件 | 类名 | 说明 |
|------|------|------|
| 按钮 | `TButton` | 9 种类型、4 种尺寸、圆形/圆角/幽灵/块级/图标按钮，支持 Loading 和 Disabled |
| 复选框 | `TCheckbox` / `TCheckboxGroup` | 三态、3 种尺寸、分组管理（min/max 限制） |
| 单选按钮 | `TRadio` / `TRadioButton` / `TRadioGroup` | 3 种尺寸、按钮样式变体、RadioGroup 互斥管理 |
| 输入框 | `TInput` | text / textarea / password 模式、4 种尺寸、字数统计、验证状态、加载动画 |
| 数字输入框 | `TInputNumber` | 步进按钮、范围限制、精度控制、前缀/后缀插槽、加载/只读/验证状态 |
| 滑块 | `TSlider` | 单值/范围模式、步进/标记、垂直/水平方向、键盘操作、Tooltip |
| 开关 | `TSwitch` | 3 种尺寸、加载状态、方形/圆形轨道、轨道文字、橡皮筋回弹 |
| 标签 | `TTag` | 6 种颜色类型、4 种尺寸、可关闭/可选中、自定义颜色 |
| 加载指示器 | `TSpin` | 独立/嵌套模式、ring/dots/pulse 动画、3 种尺寸、自定义描述文字 |
| 回到顶部 | `TBackTop` | 滚动监听、可控显隐、淡入淡出动画、自定义内容 |
| 空状态 | `TEmpty` | 5 种尺寸、自定义图标/描述/操作区域 |

### 分子组件（Molecules）

| 组件 | 类名 | 说明 |
|------|------|------|
| 搜索栏 | `TSearchBar` | TInput + TButton 组合，支持 Enter 提交 |
| 面包屑 | `TBreadcrumb` | 导航路径，可点击跳转 |
| 输入组 | `TInputGroup` | 紧凑水平排列，自动合并边框圆角 |
| 警告提示 | `TAlert` | success / info / warning / error 四种类型、可关闭、自定义图标和操作区域 |
| 折叠面板 | `TCollapse` / `TCollapseItem` | 手风琴模式、箭头位置可配、展开/折叠动画 |
| 气泡确认框 | `TPopconfirm` | 多方向弹出、click/hover 触发、自定义按钮属性 |
| 时间线 | `TTimeline` / `TTimelineItem` | 垂直/水平模式、alternate 交替布局、自定义节点颜色和图标 |

### 有机体组件（Organisms）

| 组件 | 类名 | 说明 |
|------|------|------|
| 全局消息 | `TMessage` / `MessageManager` | Toast 风格顶部弹出，四种类型，自动堆叠与消失 |
| 模态对话框 | `TModal` | 遮罩层 + 居中对话框，缩放动画，可自定义内容 |
| 卡片 | `TCard` | 3 种尺寸、可关闭、悬停阴影效果、标题/内容/底部三区域 |
| 布局 | `TLayout` | Header / Footer / Sider / Content 四区域布局，Sider 折叠动画、响应式断点 |
| 导航菜单 | `TMenu` / `TMenuItem` / `TMenuItemGroup` / `MenuOption` | 垂直/水平模式、多级子菜单弹出、折叠切换、路由感知 |

### 样式系统

- **Jinja2 模板引擎**渲染 QSS，每个组件对应独立的 `.qss.j2` 模板
- **Light / Dark 双主题** Token 文件（`light.json` / `dark.json`）
- **ThemeEngine 单例**管理主题状态，通过信号驱动全局样式刷新
- **组件尺寸令牌**（`component_sizes` / `switch_sizes`）支持多尺寸变体的统一管理

### 交互行为 Mixin

| Mixin | 效果 |
|-------|------|
| `HoverEffectMixin` | 鼠标悬停时平滑过渡背景/边框颜色 |
| `ClickRippleMixin` | 点击时扩散涟漪动画 |
| `FocusGlowMixin` | 聚焦时外发光效果 |
| `DisabledMixin` | 禁用态统一降低透明度并屏蔽交互 |
| `ContainerQueryMixin` | 容器查询响应式断点系统，类似 CSS Container Query |

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 核心框架 | PySide6 (≥ 6.7) |
| 模板引擎 | Jinja2 (≥ 3.1) |
| 构建系统 | Setuptools |
| 包管理 | uv |
| 测试框架 | pytest, pytest-qt, pytest-xdist, hypothesis |
| 代码质量 | Ruff, Pyright |
| Python 版本 | ≥ 3.12 |

---

## 快速上手

### 安装

```bash
# 克隆项目
git clone https://github.com/tyto-team/tyto-ui-lib.git
cd tyto-ui-lib

# 安装依赖
uv sync

# 安装开发依赖
uv sync --extra dev
```

### 初始化主题引擎

```python
import sys
from PySide6.QtWidgets import QApplication
from tyto_ui_lib import ThemeEngine

app = QApplication(sys.argv)
app.setStyle("Fusion")

engine = ThemeEngine.instance()
engine.load_tokens()
engine.switch_theme("light")
```

### 使用组件

```python
from PySide6.QtWidgets import QVBoxLayout, QWidget
from tyto_ui_lib import TButton, TInput, TCheckbox, TInputNumber, TSlider

window = QWidget()
layout = QVBoxLayout(window)

layout.addWidget(TInput(placeholder="Enter your name", size=TInput.InputSize.MEDIUM))
layout.addWidget(TInputNumber(value=0, step=1, min_val=0, max_val=100))
layout.addWidget(TSlider(value=50, min_val=0, max_val=100))
layout.addWidget(TCheckbox("I agree to the terms", size=TCheckbox.CheckboxSize.MEDIUM))
layout.addWidget(TButton("Submit", button_type=TButton.ButtonType.PRIMARY, size=TButton.ButtonSize.MEDIUM))

window.show()
```

### 主题切换

```python
from tyto_ui_lib import TSwitch, ThemeEngine

switch = TSwitch(checked=False)
switch.toggled.connect(
    lambda dark: ThemeEngine.instance().switch_theme("dark" if dark else "light")
)
```

### 运行 Gallery 示例

Gallery 是一个交互式组件预览画廊，展示所有组件的各种状态和配置：

```bash
uv run python examples/gallery.py
```

### 运行 Playground 调试应用

Playground 支持实时修改控件属性并预览效果：

```bash
uv run python examples/playground.py
```

---

## 开发指南

### 项目结构

```
Tyto/
├── src/tyto_ui_lib/       # 源码
├── tests/                 # 测试（与源码目录结构对应）
├── examples/              # Gallery 预览画廊 & Playground 调试应用
│   ├── gallery/           #   Gallery MVVM 模块（models / viewmodels / views / showcases）
│   └── playground/        #   Playground MVVM 模块（definitions / models / viewmodels / views）
├── docs/                  # 技术参考文档 & 问题解决方案
│   ├── references/v1/     #   v1 版本技术参考文档
│   ├── references/release/#   版本更新日志
│   └── references/solution/#  问题排查与修复文档
├── pyproject.toml         # 项目配置
└── AGENTS.md              # AI Agent 开发规范
```

### 测试

```bash
# 运行全部测试
uv run pytest

# 并行运行
uv run pytest -n auto

# 运行特定组件测试
uv run pytest tests/test_atoms/test_button.py

# 类型检查
uv run pyright src/

# 代码检查
uv run ruff check src/ tests/
```

### 构建与发布

```bash
# 构建 wheel
uv build

# 发布到 PyPI
twine upload dist/*
```

### 编码规范

- 所有代码注释和 Docstrings 使用英文，文档和 commit message 使用中文
- 所有公开 API 必须有完整的类型标注（通过 Pyright strict 模式）
- 所有公开类和方法必须包含 Google 风格的 Docstrings
- 组件类名以 `T` 为前缀（如 `TButton`、`TInput`）
- 组件代码中严禁硬编码任何像素值、颜色值或字体大小

---

## 参考文档

详细的技术参考文档位于 `docs/references/v1/` 目录：

| 文档 | 内容 |
|------|------|
| [概览](docs/references/v1/00-概览.md) | 项目简介、架构总览、组件清单 |
| [核心引擎](docs/references/v1/01-核心引擎.md) | ThemeEngine、DesignTokenSet、EasingEngine、EventBus |
| [公共基础](docs/references/v1/02-公共基础.md) | BaseWidget、行为 Mixin（Hover / Click / Focus / Disabled / ContainerQuery） |
| [原子组件](docs/references/v1/03-原子组件.md) | Button, Checkbox, Radio, Input, Switch, Tag, InputNumber, Slider, Spin, BackTop, Empty |
| [分子组件](docs/references/v1/04-分子组件.md) | SearchBar, Breadcrumb, InputGroup, Alert, Collapse, Popconfirm, Timeline |
| [有机体组件](docs/references/v1/05-有机体组件.md) | Message, Modal, Card, Layout, Menu |
| [样式系统](docs/references/v1/06-样式系统.md) | Design Token、QSS 模板、主题配置 |
| [快速上手](docs/references/v1/07-快速上手.md) | 安装、初始化、Gallery / Playground 示例 |

---

## 许可证

MIT
