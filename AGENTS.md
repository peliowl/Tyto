# AGENTS.md - Tyto UI 组件库开发规范

## 项目概述

Tyto 是一个基于 PySide6 的现代化桌面 UI 组件库，采用原子设计方法论（Atomic Design），提供从基础控件（Atom）到复杂业务模块（Organism）的分层组件体系。样式系统基于 Design Token + Jinja2 + QSS 的动态渲染架构，支持 Light/Dark 主题实时无闪烁切换。视觉风格仿 NaiveUI。

## 技术栈

- **核心框架**：PySide6（Latest）
- **构建系统**：Setuptools
- **包管理**：uv
- **类型检查**：Pyright、Mypy
- **代码质量**：Ruff
- **样式引擎**：Jinja2 + QSS
- **测试**：pytest、pytest-qt、pytest-xdist、hypothesis
- **文档**：MkDocs-Material、mkdocstrings
- **Python 版本**：3.12

## 项目结构

```
Tyto/
├── assets/                    # 静态资源
│   ├── fonts/                 # 品牌字体
│   ├── icons/                 # SVG 矢量图标
│   └── themes/                # Design Tokens 定义文件
├── bin/                       # 可执行脚本
├── scripts/                   # 工程化工具脚本
├── docs/                      # 知识库
│   ├── api/                   # 自动生成的 API 文档
│   ├── guide/                 # 开发者指南
│   └── agent_memory/          # Agent 经验积累
│       ├── references/        # 引用文档
│       └── experience.json    # 语义索引
├── examples/                  # Gallery 预览画廊
├── src/tyto_ui_lib/           # 源码
│   ├── core/                  # 底层引擎（主题、DPI、状态管理）
│   ├── common/                # 基类与 Mixins
│   │   ├── base.py            # BaseWidget 基类
│   │   └── traits/            # 行为混入（HoverEffect, ClickRipple 等）
│   ├── components/            # UI 组件
│   │   ├── atoms/             # 原子级：Button, Checkbox, Radio, Input, Switch, Tag
│   │   ├── molecules/         # 分子级：SearchBar, Breadcrumb, InputGroup
│   │   └── organisms/         # 有机体：Message, Modal
│   ├── styles/                # 样式工厂
│   │   ├── templates/         # Jinja2 QSS 模板 (*.qss.j2)
│   │   └── tokens/            # 主题 Token 文件 (light.json, dark.json)
│   └── utils/                 # 辅助工具
├── tests/                     # 测试
├── pyproject.toml             # 项目配置
└── AGENTS.md                  # 本文件
```

## 编码规范

### 通用规则

1. **语言**：所有代码注释、Docstrings 使用英文；文档和 commit message 使用中文
2. **类型标注**：所有公开 API 必须有完整的类型标注，通过 Pyright strict 模式检查
3. **Docstrings**：所有公开类和方法必须包含 Google 风格的 Docstrings，描述用途、参数、返回值和使用示例
4. **代码格式**：遵循 Ruff 默认规则，行宽 120 字符
5. **导入排序**：使用 Ruff 的 isort 兼容模式

### 样式规范

1. **禁止硬编码**：组件代码中严禁硬编码任何像素值、颜色值或字体大小。所有视觉属性必须通过 Design Token 获取
2. **QSS 模板**：每个组件对应一个 `.qss.j2` 模板文件，存放在 `styles/templates/` 目录
3. **Token 引用**：在 Jinja2 模板中通过 `{{ colors.primary }}`、`{{ spacing.medium }}` 等方式引用 Token

### 组件开发规范

1. **继承 BaseWidget**：所有组件必须继承 `BaseWidget`，确保自动响应主题切换
2. **Mixin 使用**：通过 Mixin 注入交互行为，不在组件内重复实现 hover/click/focus 逻辑
3. **信号命名**：使用 snake_case，如 `clicked`、`state_changed`、`text_changed`
4. **枚举定义**：组件的类型/状态枚举定义为组件类的内部类
5. **组件前缀**：所有组件类名以 `T` 为前缀（如 `TButton`、`TInput`）

### 组件分级规则

- **Atoms**：零业务逻辑依赖，仅封装绘图逻辑与交互状态机
- **Molecules**：仅组合 Atoms，负责局部信号转发与布局协调
- **Organisms**：可对接业务逻辑与数据模型（QAbstractItemModel）

## 测试规范

### 双轨测试策略

1. **单元测试**（pytest + pytest-qt）：验证具体示例、边界情况和错误条件
2. **属性基测试**（Hypothesis）：验证跨所有输入的通用属性，每个属性至少 100 次迭代

### 测试文件组织

- 测试文件与源码目录结构对应，放在 `tests/` 下
- 属性基测试标注格式：`# Feature: tyto-ui-lib-v1, Property N: 属性名称`
- 使用 `**Validates: Requirements X.Y**` 标注验证的需求

### 测试运行

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

## Agent 决策规则

1. **置信度阈值**：当遇到不确定的事情且置信度低于 80% 时，必须提供解决方案给用户进行决策，不得自行假设
2. **项目结构变更**：在更新项目结构后，需要检查 `.kiro/specs/` 中的相关文档是否与项目最新状态一致，如不一致需更新
3. **经验记录**：完成重要任务后，将经验记录到 `docs/agent_memory/` 目录
4. **参考图片**：样式实现时参考 `docs/image/` 目录下的 NaiveUI 风格截图

## 构建与发布

```bash
# 安装依赖
uv sync

# 构建 wheel
uv build

# 发布到 PyPI
twine upload dist/*
```

## Spec 文档位置

- 需求文档：`.kiro/specs/tyto-ui-lib-v1/requirements.md`
- 设计文档：`.kiro/specs/tyto-ui-lib-v1/design.md`
- 任务列表：`.kiro/specs/tyto-ui-lib-v1/tasks.md`
