# Tyto UI Library

基于 PySide6 的现代化桌面 UI 组件库，采用原子设计方法论（Atomic Design），提供从基础控件到复杂业务模块的分层组件体系。

视觉风格参考 [NaiveUI](https://www.naiveui.com/)，样式系统基于 Design Token + Jinja2 + QSS 动态渲染架构，支持 Light / Dark 主题实时无闪烁切换。

---

## 设计哲学

- **原子设计（Atomic Design）**：组件按 Atom → Molecule → Organism 三层分级，职责清晰、组合灵活
- **Design Token 驱动**：所有视觉属性（颜色、间距、圆角、字号等）由 Token 统一管理，组件代码零硬编码
- **Mixin 行为注入**：Hover、Click Ripple、Focus Glow、Disabled 等交互行为通过 Mixin 混入，避免重复实现
- **主题热切换**：基于 ThemeEngine 单例 + 信号广播机制，所有组件实时响应主题变更，无闪烁

## 架构概览

```
tyto_ui_lib/
├── core/               # 底层引擎：ThemeEngine 主题引擎、DesignTokenSet 数据模型
├── common/             # 公共基础：BaseWidget 基类、行为 Mixin
│   └── traits/         # 交互行为混入（Hover / Click / Focus / Disabled）
├── components/         # UI 组件（按原子设计分层）
│   ├── atoms/          # 原子级：Button, Checkbox, Radio, Input, Switch, Tag
│   ├── molecules/      # 分子级：SearchBar, Breadcrumb, InputGroup
│   └── organisms/      # 有机体：Message, Modal
├── styles/             # 样式工厂
│   ├── templates/      # Jinja2 QSS 模板 (*.qss.j2)
│   └── tokens/         # 主题 Token 文件 (light.json, dark.json)
└── utils/              # 辅助工具
```

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

- Jinja2 模板引擎渲染 QSS，每个组件对应独立的 `.qss.j2` 模板
- Light / Dark 双主题 Token 文件（`light.json` / `dark.json`）
- ThemeEngine 单例管理主题状态，通过信号驱动全局样式刷新

### 交互行为 Mixin

| Mixin | 效果 |
|-------|------|
| `HoverEffectMixin` | 鼠标悬停时平滑过渡背景/边框颜色 |
| `ClickRippleMixin` | 点击时扩散涟漪动画 |
| `FocusGlowMixin` | 聚焦时外发光效果 |
| `DisabledMixin` | 禁用态统一降低透明度并屏蔽交互 |

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

## 快速上手

### 安装

```bash
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

```bash
uv run python examples/gallery.py
```

## 测试

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

## 许可证

MIT
