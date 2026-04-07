# Tyto UI Library

[![Python](https://img.shields.io/badge/Python-≥3.12-blue)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-≥6.7-green)](https://doc.qt.io/qtforpython/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)](https://github.com/tyto-team/tyto-ui-lib)

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
├── core/                   # 底层引擎
│   ├── theme_engine.py     #   ThemeEngine 单例：主题状态管理与信号广播
│   └── tokens.py           #   DesignTokenSet 数据模型：Token 解析与访问
├── common/                 # 公共基础
│   ├── base.py             #   BaseWidget 基类：自动主题响应、样式刷新
│   └── traits/             #   行为 Mixin
│       ├── hover_effect.py #     鼠标悬停平滑过渡
│       ├── click_ripple.py #     点击涟漪扩散动画
│       ├── focus_glow.py   #     聚焦外发光效果
│       └── disabled.py     #     禁用态透明度降低与交互屏蔽
├── components/             # UI 组件（原子设计分层）
│   ├── atoms/              #   原子级：Button, Checkbox, Radio, Input, Switch, Tag
│   ├── molecules/          #   分子级：SearchBar, Breadcrumb, InputGroup
│   └── organisms/          #   有机体：Message, Modal
├── styles/                 # 样式工厂
│   ├── templates/          #   Jinja2 QSS 模板 (*.qss.j2)
│   └── tokens/             #   主题 Token 文件 (light.json, dark.json)
└── utils/                  # 辅助工具
```

---

## v1.0.0 版本特性

### 原子组件（Atoms）

| 组件 | 类名 | 说明 |
|------|------|------|
| 按钮 | `TButton` | Primary / Default / Dashed / Text 四种类型，支持 Loading 和 Disabled |
| 复选框 | `TCheckbox` | 三态（Unchecked / Checked / Indeterminate），带勾选动画 |
| 单选按钮 | `TRadio` / `TRadioGroup` | 环形缩放动画，RadioGroup 管理互斥逻辑 |
| 输入框 | `TInput` | 前缀/后缀图标、可清除、密码模式 |
| 开关 | `TSwitch` | iOS / NaiveUI 风格滑动开关，带缩放动画 |
| 标签 | `TTag` | 五种颜色类型、三种尺寸、可关闭 |

### 分子组件（Molecules）

| 组件 | 类名 | 说明 |
|------|------|------|
| 搜索栏 | `TSearchBar` | TInput + TButton 组合，支持 Enter 提交 |
| 面包屑 | `TBreadcrumb` | 导航路径，可点击跳转 |
| 输入组 | `TInputGroup` | 紧凑水平排列，自动合并边框圆角 |

### 有机体组件（Organisms）

| 组件 | 类名 | 说明 |
|------|------|------|
| 全局消息 | `TMessage` / `MessageManager` | Toast 风格顶部弹出，四种类型，自动堆叠与消失 |
| 模态对话框 | `TModal` | 遮罩层 + 居中对话框，缩放动画，可自定义内容 |

### 样式系统

- **Jinja2 模板引擎**渲染 QSS，每个组件对应独立的 `.qss.j2` 模板
- **Light / Dark 双主题** Token 文件（`light.json` / `dark.json`）
- **ThemeEngine 单例**管理主题状态，通过信号驱动全局样式刷新

### 交互行为 Mixin

| Mixin | 效果 |
|-------|------|
| `HoverEffectMixin` | 鼠标悬停时平滑过渡背景/边框颜色 |
| `ClickRippleMixin` | 点击时扩散涟漪动画 |
| `FocusGlowMixin` | 聚焦时外发光效果 |
| `DisabledMixin` | 禁用态统一降低透明度并屏蔽交互 |

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
from tyto_ui_lib import TButton, TInput, TCheckbox

window = QWidget()
layout = QVBoxLayout(window)

layout.addWidget(TInput(placeholder="Enter your name"))
layout.addWidget(TCheckbox("I agree to the terms"))
layout.addWidget(TButton("Submit", button_type=TButton.ButtonType.PRIMARY))

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

---

## 开发指南

### 项目结构

```
Tyto/
├── src/tyto_ui_lib/       # 源码
├── tests/                 # 测试（与源码目录结构对应）
├── examples/              # Gallery 预览画廊
├── docs/                  # 技术参考文档
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
| [核心引擎](docs/references/v1/01-核心引擎.md) | ThemeEngine、DesignTokenSet |
| [公共基础](docs/references/v1/02-公共基础.md) | BaseWidget、行为 Mixin |
| [原子组件](docs/references/v1/03-原子组件.md) | Button, Checkbox, Radio, Input, Switch, Tag |
| [分子组件](docs/references/v1/04-分子组件.md) | SearchBar, Breadcrumb, InputGroup |
| [有机体组件](docs/references/v1/05-有机体组件.md) | Message, Modal |
| [样式系统](docs/references/v1/06-样式系统.md) | Design Token、QSS 模板、主题配置 |
| [快速上手](docs/references/v1/07-快速上手.md) | 安装、初始化、Gallery 示例 |

---

## 许可证

MIT
