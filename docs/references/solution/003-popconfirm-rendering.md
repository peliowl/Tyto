# SOL-003: Popconfirm 弹窗背景/边框渲染异常

| 属性 | 值 |
|------|-----|
| 编号 | SOL-003 |
| 版本 | V1.1.0+ |
| 状态 | 已解决 |
| 影响范围 | TPopconfirm |
| 严重程度 | 高（弹窗在 light/dark 模式下均无法正常显示） |

---

## 1. 问题描述

TPopconfirm 组件的弹窗在 light 和 dark 模式下均存在渲染问题，经历了三个阶段的修复：

### 阶段一：弹窗背景为纯黑色（light 模式）

弹窗在 light 模式下显示为纯黑色背景，完全无法看清内容。

### 阶段二：弹窗背景/边框不可见（dark 模式）

修复阶段一后，弹窗在 dark 模式下背景和边框完全透明，与底层深色背景融为一体。

### 阶段三：背景色不正确 + 底部边框截断

修复阶段二后，dark 模式下弹窗背景色过深（与页面背景几乎相同），底部边框被截断。

## 2. 根因分析

### 2.1 阶段一：FramelessWindowHint 的默认黑色背景

TPopconfirm 的弹窗是一个独立的顶层窗口，使用了 `Qt.WindowType.FramelessWindowHint`。在 Windows 平台上，frameless 窗口的默认背景为黑色。

原始代码设置了 `WA_TranslucentBackground=False`，导致外层窗口渲染为黑色。内层 container 的 QSS 背景色被外层黑色覆盖。

### 2.2 阶段二：WA_TranslucentBackground 导致 QSS 背景失效

将 `WA_TranslucentBackground` 改为 `True` 后，外层窗口变为透明。但该属性会**传递给所有子 widget**，导致内层 container 的 QSS `background-color` 属性也不生效。

这是 Qt 的已知行为：`WA_TranslucentBackground` 会禁用子 widget 的 QSS 背景渲染。

### 2.3 阶段三：背景色 Token 选择错误 + Layout Margins 不足

- 背景色使用了 `bg_default`（dark: `#18181c`），与页面背景色相同，导致弹窗不可辨识。NaiveUI 的 Popover 类组件在 dark 模式下使用 `popoverColor`（`rgb(72,72,78)`），明显区别于页面背景。
- 外层 popup 的 root layout margins 为 `(2,2,2,2)`，不足以容纳 1px 边框 + 圆角渲染，导致底部边框被截断。

## 3. 解决方案

### 3.1 自定义 paintEvent 绘制背景（解决阶段一 + 二）

创建 `_PopconfirmContainer` 内部类，通过 `paintEvent` 使用 `QPainter` 直接绘制圆角矩形背景和边框，不依赖 QSS 的 `background-color`。

这种方式与项目中 InputNumber、Slider 等组件的 `paintEvent` 绘制模式一致，不受 `WA_TranslucentBackground` 影响。

### 3.2 使用 popover_color Token（解决阶段三背景色）

将背景色从 `bg_default` 改为 `popover_color`：

| 主题 | bg_default | popover_color |
|------|-----------|--------------|
| light | `#ffffff` | `#ffffff` |
| dark | `#18181c` | `rgb(72, 72, 78)` |

### 3.3 增大 Layout Margins（解决阶段三边框截断）

外层 popup 的 root layout margins 从 `(2,2,2,2)` 增大到 `(4,4,4,4)`，为边框和圆角渲染留出足够空间。

### 3.4 拆分 popover_color 和 indicator_color

Slider tooltip 和 Popconfirm 在 light 模式下需要不同的背景色：

| Token | light | dark | 用途 |
|-------|-------|------|------|
| `popover_color` | `#ffffff` | `rgb(72,72,78)` | Popconfirm 等弹出层 |
| `indicator_color` | `rgba(0,0,0,0.85)` | `rgb(72,72,78)` | Slider tooltip |

## 4. 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `components/molecules/popconfirm.py` | 修改 | 新增 `_PopconfirmContainer`；`WA_TranslucentBackground=True`；margins 4px |
| `styles/templates/popconfirm.qss.j2` | 重写 | 选择器改为 `QWidget#popconfirm_container` |
| `styles/tokens/light.json` | 修改 | `popover_color` 改为 `#ffffff`，新增 `indicator_color` |
| `styles/tokens/dark.json` | 修改 | 新增 `indicator_color` |
| `styles/templates/slider.qss.j2` | 修改 | tooltip 改用 `indicator_color` |
| `components/atoms/slider.py` | 修改 | tooltip 内联样式改用 `indicator_color` |

## 5. 经验总结

> **规则 1**：使用 `FramelessWindowHint` 的顶层弹窗必须设置 `WA_TranslucentBackground=True`，并通过内层 widget 的 `paintEvent` 绘制背景和边框。不要依赖 QSS 的 `background-color`。

> **规则 2**：弹出层（Popover 类）组件的背景色应使用 `popover_color` token，而非 `bg_default`。在 dark 模式下两者差异显著。

> **规则 3**：顶层弹窗的 root layout 需要留出足够的 margins（建议 4px），确保边框和圆角不被截断。

## 6. 验证

- 394 个单元测试全部通过
- Popconfirm 在 light 模式下显示白色背景、可见边框、底部边框完整
- Popconfirm 在 dark 模式下显示深灰色背景，与页面背景形成对比
- 主题切换时弹窗样式同步更新
