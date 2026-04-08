# BUG-003：Gallery 滚动区域控件隐形与底部遮挡

| 属性 | 值 |
|------|-----|
| 版本 | V1.0.2 |
| 严重程度 | 高 |
| 影响组件 | `HoverEffectMixin`、`DisabledMixin`、`TTag`、`BaseShowcase`、`ComponentShowcase` |
| 涉及文件 | `src/tyto_ui_lib/common/traits/hover_effect.py`、`src/tyto_ui_lib/common/traits/disabled.py`、`src/tyto_ui_lib/components/atoms/tag.py`、`examples/gallery/showcases/base_showcase.py`、`examples/gallery/views/component_showcase.py` |
| 修复日期 | 2026-04-08 |

---

## 1. 问题描述

Gallery 右侧组件展示面板存在两个显示异常：

**现象 A：控件在滚动时隐形或固定在原处**

上下滚动展示面板时，如果鼠标划过控件（Button、Checkbox、Radio、Switch 等），控件会突然变为不可见，或者在滚动过程中固定显示在屏幕原始位置而不随页面滚动。

**现象 B：控件底部被遮挡**

在 Button 等内容较多的组件展示界面中，最后几个展示区块（如 Block、Icon Buttons、Loading、Disabled）的底部被截断，无法通过滚动查看完整内容。

**复现步骤：**

1. 启动 Gallery 应用（`uv run python examples/gallery.py`）
2. 选择左侧菜单中的 **Button** 组件
3. 上下滚动右侧展示面板，同时将鼠标移过按钮控件 → 观察到控件隐形（现象 A）
4. 滚动到页面底部 → 观察到 Disabled 区块的按钮底部被截断（现象 B）

## 2. 根因分析

此问题由两个独立的根因导致：

### 根因 A：QGraphicsEffect 与 QScrollArea 的渲染冲突

`HoverEffectMixin._init_hover_effect()` 在每个使用该 Mixin 的组件上调用了 `self.setGraphicsEffect(QGraphicsColorizeEffect)`：

```python
# 原始代码 - hover_effect.py
def _init_hover_effect(self):
    self._hover_effect = QGraphicsColorizeEffect(self)
    self._hover_effect.setColor(QColor(0, 0, 0, 0))
    self._hover_effect.setStrength(0.0)
    self.setGraphicsEffect(self._hover_effect)  # ← 问题所在
```

同样，`DisabledMixin.set_disabled_style()` 使用了 `QGraphicsOpacityEffect`：

```python
# 原始代码 - disabled.py
def set_disabled_style(self, disabled):
    if disabled:
        self._disabled_opacity_effect.setOpacity(0.5)
        widget.setGraphicsEffect(self._disabled_opacity_effect)  # ← 问题所在
```

`TTag._apply_disabled_visual()` 也直接创建了 `QGraphicsOpacityEffect`：

```python
# 原始代码 - tag.py
def _apply_disabled_visual(self):
    effect = QGraphicsOpacityEffect(self)
    effect.setOpacity(0.5)
    self.setGraphicsEffect(effect)  # ← 问题所在
```

**Qt 的 QGraphicsEffect 渲染机制：**

当 `QWidget` 设置了 `QGraphicsEffect` 后，Qt 会将该 widget 的绘制输出重定向到一个离屏像素缓冲区（offscreen pixmap），然后由 effect 对该缓冲区进行后处理（如着色、透明度变换），最后将处理后的结果合成到屏幕上。

这一机制在 `QScrollArea` 内部会产生严重冲突：

1. **位置不同步**：滚动时，viewport 通过移动内部 widget 的坐标来实现滚动效果。但 `QGraphicsEffect` 的离屏缓冲区的位置更新与 viewport 的滚动不同步，导致 widget 的渲染结果"粘"在屏幕上的旧位置
2. **缓冲区失效**：当 hover 事件触发 effect 的 `strength` 属性动画时，effect 需要重新渲染离屏缓冲区。在滚动过程中，这个重新渲染可能使用了过时的坐标信息，导致 widget 渲染为空白（隐形）
3. **尺寸计算干扰**：`QGraphicsEffect` 的 `boundingRect` 可能不被布局系统正确考虑，导致 `QScrollArea` 低估内容的实际高度

**受影响的组件（使用 HoverEffectMixin 的）：**

- `TButton`（HoverEffectMixin + ClickRippleMixin + FocusGlowMixin + DisabledMixin）
- `TCheckbox`（HoverEffectMixin + FocusGlowMixin + DisabledMixin）
- `TRadio` / `TRadioButton`（HoverEffectMixin + FocusGlowMixin + DisabledMixin）
- `TSwitch`（HoverEffectMixin）

### 根因 B：QWidget.sizeHint() 返回 layout.minimumSize() 而非 layout.sizeHint()

`ComponentShowcase`（QScrollArea）使用 `widgetResizable=True` 来管理内部 widget 的尺寸。当内容超出 viewport 时，scroll area 应该显示滚动条。但实际上内容被压缩了。

**诊断数据：**

```
Layout sizeHint:    QSize(448, 1620)   ← 布局需要的理想高度
Layout minimumSize: QSize(341, 1444)   ← 布局的最小高度
Showcase sizeHint:  QSize(448, 1444)   ← Widget 报告的理想高度（错误！）
```

`QWidget` 的默认 `sizeHint()` 实现返回的是其 layout 的 `minimumSize()`（1444px），而非 layout 的 `sizeHint()`（1620px）。差值 176px 来自 10 个描述文本 QLabel 的高度压缩（每个 QLabel 的 `sizeHint` 为 36px，但 `minimumSizeHint` 仅为 20px，差值 16px × 10 = 160px，加上 Ghost 描述标签的额外 16px）。

当 `QScrollArea` 使用 `widgetResizable=True` 时，它会将内部 widget 调整为 viewport 大小。如果 widget 的 `sizeHint` 小于实际需要的高度，scroll area 就不会为缺失的部分提供滚动空间，导致底部内容被截断。

## 3. 解决方案

### 3.1 移除 QGraphicsEffect，改用 QSS 动态属性（修复现象 A）

**HoverEffectMixin**：移除 `QGraphicsColorizeEffect` 和 `QPropertyAnimation`，改用 QSS 动态属性 `hovered` + QSS `:hover` 伪状态选择器驱动悬停样式：

```python
# 修复后 - hover_effect.py
class HoverEffectMixin:
    def _init_hover_effect(self):
        self._original_cursor = self.cursor().shape()
        # 不再创建 QGraphicsEffect

    def enterEvent(self, event):
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        widget.setProperty("hovered", True)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        super().enterEvent(event)

    def leaveEvent(self, event):
        widget.setCursor(original)
        widget.setProperty("hovered", False)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        super().leaveEvent(event)
```

**DisabledMixin**：移除 `QGraphicsOpacityEffect`，改用 QSS 动态属性 `disabledState` + QSS `:disabled` 伪状态选择器：

```python
# 修复后 - disabled.py
class DisabledMixin:
    def _init_disabled(self):
        self._disabled_original_cursor = self.cursor().shape()
        # 不再创建 QGraphicsOpacityEffect

    def set_disabled_style(self, disabled):
        widget.setProperty("disabledState", True if disabled else False)
        if disabled:
            widget.setCursor(Qt.CursorShape.ForbiddenCursor)
            widget.setEnabled(False)
        else:
            widget.setCursor(original)
            widget.setEnabled(True)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
```

**TTag**：删除 `_apply_disabled_visual()` 方法，在 `set_disabled()` 中直接使用 QSS 动态属性：

```python
# 修复后 - tag.py
def set_disabled(self, disabled):
    self._disabled = disabled
    self.setProperty("disabled", str(disabled).lower())
    if disabled:
        self.setCursor(Qt.CursorShape.ForbiddenCursor)
        self.setEnabled(False)
    else:
        self.setEnabled(True)
        # 恢复光标...
    self._repolish()
```

**可行性依据**：所有组件的 QSS 模板（`.qss.j2`）已定义了 `:hover`、`:pressed`、`:disabled` 伪状态选择器，无需新增 QSS 规则。

### 3.2 修复 QScrollArea 内容高度计算（修复现象 B）

**ComponentShowcase**：将 `widgetResizable` 设为 `False`，通过 `resizeEvent` 手动同步宽度，让内部 widget 的高度由其 layout 自然决定：

```python
# 修复后 - component_showcase.py
class ComponentShowcase(QScrollArea):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(False)  # ← 关键：不让 scroll area 控制高度
        # ...

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.widget()
        if w is not None:
            w.setFixedWidth(self.viewport().width())  # 仅同步宽度
```

**BaseShowcase**：重写 `sizeHint()` 返回 layout 的 `sizeHint()`（而非默认的 `minimumSize()`）：

```python
# 修复后 - base_showcase.py
class BaseShowcase(QWidget):
    def sizeHint(self) -> QSize:
        return self._layout.sizeHint()  # ← 返回布局的理想尺寸
```

**修复效果验证：**

```
修复前：Showcase sizeHint = QSize(448, 1444)  → 底部 176px 被截断
修复后：Showcase sizeHint = QSize(448, 1620)  → 完整显示所有内容
```

### 3.3 修改汇总

| 文件 | 修改内容 | 修复现象 |
|------|----------|----------|
| `common/traits/hover_effect.py` | 移除 `QGraphicsColorizeEffect` 和 `QPropertyAnimation`，改用 QSS 动态属性 `hovered` | A |
| `common/traits/disabled.py` | 移除 `QGraphicsOpacityEffect`，改用 QSS 动态属性 `disabledState` | A |
| `components/atoms/tag.py` | 删除 `_apply_disabled_visual()` 方法，`set_disabled()` 改用 QSS 动态属性 | A |
| `gallery/showcases/base_showcase.py` | 重写 `sizeHint()` 返回 `self._layout.sizeHint()` | B |
| `gallery/views/component_showcase.py` | `widgetResizable=False` + `resizeEvent` 手动同步宽度 | B |

## 4. 影响范围

- **HoverEffectMixin**：所有使用该 Mixin 的组件（TButton、TCheckbox、TRadio、TRadioButton、TSwitch）在 QScrollArea 内不再出现渲染异常
- **DisabledMixin**：所有使用该 Mixin 的组件的禁用状态改为 QSS 驱动，视觉效果不变
- **TTag**：禁用状态的透明度效果由 QSS `opacity: 0.5` 规则实现（`tag.qss.j2` 中已有 `TTag[disabled="true"] { opacity: 0.5; }` 规则）
- **Gallery 所有 Showcase**：底部内容不再被截断，滚动范围正确覆盖全部内容

## 5. 验证

```bash
uv run pytest --tb=short -q
# 174 passed
```

手动验证：

1. 启动 Gallery，选择 Button 组件
2. 上下滚动 → 控件不再隐形或固定在原处 ✓
3. 滚动到底部 → Disabled 区块完整可见 ✓
4. 切换到其他组件（Checkbox、Radio、Tag 等）→ 底部内容完整可见 ✓
5. 切换 Light/Dark 主题 → 所有控件样式正确更新 ✓

## 6. 经验总结

> **规则 1：** 在 `QScrollArea` 内部的 widget 上禁止使用 `QGraphicsEffect`（包括 `QGraphicsColorizeEffect`、`QGraphicsOpacityEffect`、`QGraphicsDropShadowEffect` 等）。`QGraphicsEffect` 的离屏渲染机制与 `QScrollArea` 的 viewport 裁剪/滚动机制存在根本性冲突，会导致 widget 在滚动时渲染位置不同步或变为不可见。应使用 QSS 伪状态选择器（`:hover`、`:disabled`）或 QSS 动态属性（`[hovered="true"]`）替代。

> **规则 2：** `QWidget` 的默认 `sizeHint()` 返回其 layout 的 `minimumSize()` 而非 `sizeHint()`。当 widget 作为 `QScrollArea` 的内容时，这会导致 scroll area 低估内容高度，截断底部内容。对于内容高度可能超出 viewport 的容器 widget，应重写 `sizeHint()` 返回 `self.layout().sizeHint()`。

> **规则 3：** `QScrollArea.setWidgetResizable(True)` 会同时控制内部 widget 的宽度和高度。当内容高度应由 layout 自然决定时，应设置 `widgetResizable=False` 并通过 `resizeEvent` 手动同步宽度，避免 scroll area 压缩内容高度。
