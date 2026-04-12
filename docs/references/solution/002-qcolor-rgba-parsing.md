# SOL-002: QColor 无法解析 CSS rgba() 格式导致组件渲染为黑色

| 属性 | 值 |
|------|-----|
| 编号 | SOL-002 |
| 版本 | V1.1.0+ |
| 状态 | 已解决 |
| 影响范围 | Slider, InputNumber, Switch, Alert |
| 严重程度 | 高（组件在 light 模式下渲染为纯黑色） |

---

## 1. 问题描述

在 SOL-001 中更新 Design Token 值后，以下组件在 light 模式下出现严重的视觉异常：

- **Slider**：轨道未填充部分显示为纯黑色，应为浅灰色
- **InputNumber**：整个组件背景显示为纯黑色，应为白色/浅灰色
- **Switch**：dark 模式下未选中轨道颜色异常

## 2. 根因分析

### 2.1 Qt QColor 的格式限制

Qt 的 `QColor(str)` 构造函数仅支持以下格式：
- `#RGB`、`#RRGGBB`、`#AARRGGBB`
- 命名颜色（如 `red`、`blue`）

**不支持** CSS 标准的 `rgba(r, g, b, a)` 和 `rgb(r, g, b)` 格式。

### 2.2 Token 值与 QColor 的冲突

SOL-001 中新增的 token 使用了 CSS `rgba()` 格式（与 QSS 模板兼容）：

```json
"rail_color": "rgba(0, 0, 0, 0.14)",
"input_color": "rgba(255, 255, 255, 0.1)",
"border": "rgba(255, 255, 255, 0.24)"
```

这些值在 **QSS 模板**（Jinja2 渲染）中工作正常，因为 QSS 引擎支持 `rgba()` 语法。
但在组件的 **`paintEvent`** 中，代码通过 `QColor(str(engine.get_token(...)))` 直接构造颜色对象，`QColor` 无法解析 `rgba()` 字符串，返回无效颜色（默认为黑色）。

### 2.3 影响路径

```
Token 文件 (rgba 格式)
    ├── QSS 模板 (Jinja2) → QSS 引擎解析 → ✅ 正常
    └── paintEvent → QColor(str) → ❌ 解析失败 → 黑色
```

受影响的 `paintEvent` 调用点：

| 组件 | 文件 | 代码 |
|------|------|------|
| Slider | `slider.py` | `_get_color("colors", "rail_color", ...)` |
| InputNumber | `inputnumber.py` | `QColor(str(engine.get_token("colors", "input_color")))` |
| Switch | `switch.py` | `QColor(str(engine.get_token("colors", "border")))` |
| Alert | `alert.py` | `QColor(str(engine.get_token("colors", color_key)))` |

## 3. 解决方案

### 3.1 新增 parse_color 工具函数

在 `src/tyto_ui_lib/utils/color.py` 中新增颜色解析工具：

```python
def parse_color(value: str, fallback: str = "#000000") -> QColor:
    """Parse CSS color string into QColor.
    Supports: #hex, named, rgba(r,g,b,a), rgb(r,g,b)
    """
```

该函数通过正则表达式匹配 `rgba(r, g, b, a)` 和 `rgb(r, g, b)` 格式，手动构造 `QColor` 并设置 alpha 通道。对于 hex 和命名颜色，回退到 `QColor(str)` 原生解析。

### 3.2 替换所有 paintEvent 中的 QColor 调用

将所有 `QColor(str(engine.get_token(...)))` 替换为 `parse_color(str(engine.get_token(...)))`。

## 4. 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `utils/color.py` | 新增 | `parse_color()` 工具函数 |
| `components/atoms/slider.py` | 修改 | `_get_color` 改用 `parse_color` |
| `components/atoms/inputnumber.py` | 修改 | `paintEvent` 改用 `parse_color` |
| `components/atoms/switch.py` | 修改 | `paintEvent` 改用 `parse_color` |
| `components/molecules/alert.py` | 修改 | `paintEvent` 改用 `parse_color` |

## 5. 设计决策

### 为什么不将 Token 值改为 hex 格式？

- QSS 模板中 `rgba()` 格式是必需的，因为需要表达半透明颜色
- hex 格式的 `#AARRGGBB` alpha 在前不直观
- 统一使用 `parse_color` 对 token 格式无限制，更健壮

### 为什么不在 ThemeEngine 层统一处理？

- `get_token()` 返回原始字符串值，保持与 QSS 模板的兼容性
- 颜色解析仅在 `paintEvent` 中需要，不应影响 QSS 渲染路径

## 6. 经验总结

> **规则**：在 `paintEvent` 中使用 Design Token 颜色值时，必须通过 `parse_color()` 而非 `QColor()` 构造颜色对象。`QColor` 不支持 CSS `rgba()` 格式。

## 7. 验证

- 394 个单元测试全部通过
- Slider 轨道在 light 模式下正确显示为浅灰色
- InputNumber 背景在 light 模式下正确显示为白色
- Switch 轨道在 dark 模式下正确显示为半透明白色
