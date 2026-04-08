# BUGFIX-001：TButton 尺寸变体、圆形/圆角形态及图标显示修复

| 属性 | 值 |
|------|-----|
| 文档编号 | BUGFIX-001 |
| 组件 | `TButton` (`src/tyto_ui_lib/components/atoms/button.py`) |
| 版本 | V1.0.2 |
| 严重程度 | 高 |
| 状态 | 已修复 |
| 关联需求 | 需求 31.1, 31.3, 31.4, 31.12, 31.13 |

---

## 1. 问题概述

在 Gallery 预览画廊中运行 Button 组件展示页面时，发现以下三类视觉缺陷：

| 编号 | 缺陷描述 | 影响范围 |
|------|---------|---------|
| BUG-1 | 不同 `size` 的按钮在界面上显示的尺寸完全相同 | 所有尺寸变体（tiny/small/medium/large） |
| BUG-2 | `circle` 和 `round` 属性不生效，按钮始终显示为方形 | circle 模式、round 模式 |
| BUG-3 | Icon Button 不生效，按钮中文本左侧或右侧没有显示出图标 | 带图标的按钮 |

---

## 2. 根因分析

### 2.1 BUG-1：尺寸变体不生效

**根因**：QSS 模板中使用 `min-height` 属性设置尺寸变体的高度，但 `TButton` 是一个包含内部 `QHBoxLayout` 的自定义 `QWidget`。Qt 的 QSS `min-height` 对带有内部布局的自定义 QWidget 不能可靠地强制执行高度约束——布局引擎会根据子控件的 `sizeHint` 计算最终尺寸，忽略 QSS 的 `min-height` 声明。

**验证**：创建不同 `size` 的 TButton 实例后，通过 `widget.height()` 检查，发现所有尺寸变体返回相同的高度值。

### 2.2 BUG-2：Circle/Round 形态不生效

**根因**：该问题由两个独立原因叠加导致。

**原因 A — QSS 模板缺少 circle 选择器**：`button.qss.j2` 模板中定义了 `TButton[round="true"]` 的 `border-radius` 规则，但完全缺少 `TButton[circle="true"]` 的选择器。Circle 模式下没有任何 QSS 规则设置圆形的 `border-radius`。

**原因 B — QSS `border-radius` 对自定义 QWidget 的局限性**：即使 QSS 中正确设置了 `border-radius`，Qt 的 QSS 引擎对 `QWidget` 子类的 `border-radius` 处理存在根本性限制：

1. QSS `border-radius` 仅影响 `QWidget` 自身的背景绘制（通过 `WA_StyledBackground`）
2. 子控件（如内部的 `QLabel`）独立绘制，不受父控件 `border-radius` 的裁剪
3. 控件的矩形区域在圆角外部仍然可见，显示为父容器的背景色

### 2.3 BUG-3：图标不显示

**根因**：`ButtonShowcase` 中创建图标按钮时，仅设置了 `icon_placement` 参数，但未传入实际的 `QIcon` 对象。`TButton.__init__` 的 `icon` 参数默认为 `None`，导致 `_update_icon_display()` 方法判断 `self._icon is None` 后直接跳过图标渲染。

```python
# 问题代码（ButtonShowcase）
TButton("Search", button_type=TButton.ButtonType.PRIMARY)  # 缺少 icon 参数
TButton("Next", icon_placement=TButton.IconPlacement.RIGHT)  # 缺少 icon 参数
```

---

## 3. 解决方案

### 3.1 BUG-1 修复：程序化强制尺寸

**策略**：从 Design Token 中读取 `component_sizes` 的高度值，通过 `setFixedHeight()` 程序化强制设置按钮高度，不再依赖 QSS `min-height`。

**修改文件**：`src/tyto_ui_lib/components/atoms/button.py`

**新增方法**：

```python
def _apply_size_from_tokens(self) -> None:
    """Enforce button height from design tokens so size variants are visible."""
    if not hasattr(self, "_size"):
        return
    try:
        engine = ThemeEngine.instance()
        tokens = engine.current_tokens()
        if tokens and tokens.component_sizes:
            size_data = tokens.component_sizes.get(self._size.value, {})
            h = size_data.get("height", 0)
            if h > 0:
                self.setFixedHeight(h)
    except Exception:
        pass
```

**调用时机**：在 `_apply_circle_geometry()` 和 `apply_theme()` 中调用，确保初始化和主题切换时都能正确应用尺寸。

**同步更新 `sizeHint()`**：使其也从 Token 读取高度，保持一致性。

### 3.2 BUG-2 修复：自定义 paintEvent + WA_TranslucentBackground

**策略**：放弃依赖 QSS `border-radius` 渲染圆角，改为在 `paintEvent` 中使用 `QPainter` 手动绘制圆角背景和边框。

**修改文件**：
- `src/tyto_ui_lib/components/atoms/button.py`
- `src/tyto_ui_lib/styles/templates/button.qss.j2`

#### 3.2.1 QSS 模板补充

在 `button.qss.j2` 中新增 circle 选择器和子控件透明规则：

```css
/* 子控件透明，防止覆盖父控件圆角背景 */
TButton > QLabel {
    background: transparent;
    border: none;
}

/* Circle 变体 */
TButton[circle="true"] {
    border-radius: {{ (component_sizes.medium.height / 2)|int }}px;
}
/* ... 各尺寸变体的 circle 选择器 */
```

#### 3.2.2 自定义 paintEvent

对 circle/round 模式的按钮，完全绕过 QSS 的 `PE_Widget` 绘制，改为手动绘制：

```python
def paintEvent(self, _event: object) -> None:
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if self._circle or self._round:
        # 计算圆角半径
        radius = h / 2.0 if self._round else min(w, h) / 2.0

        # 从 ThemeEngine 读取当前主题颜色
        # 根据 button_type、ghost、hover 状态确定 bg 和 border_color

        # 使用 QPainterPath 绘制圆角背景
        path = QPainterPath()
        path.addRoundedRect(0.5, 0.5, w - 1, h - 1, radius, radius)
        painter.fillPath(path, bg)

        # 绘制圆角边框（支持 dashed 虚线）
        painter.strokePath(path, pen)
    else:
        # 普通按钮使用标准 QSS 渲染
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(PE_Widget, opt, painter, self)
```

**关键设计决策**：

| 方案 | 优点 | 缺点 | 采用 |
|------|------|------|------|
| QSS `border-radius` + `QRegion` mask | 简单 | 锯齿严重，无抗锯齿 | ✗ |
| QSS `border-radius` + `QPainter.setClipPath` | 抗锯齿 | 边框在圆角处被裁剪不完整 | ✗ |
| 手动 `QPainter` 绘制 | 完全控制，抗锯齿，边框完整 | 需要手动管理颜色状态 | ✓ |

#### 3.2.3 WA_TranslucentBackground

对 circle/round 按钮设置 `WA_TranslucentBackground`，使控件矩形区域中圆角外部的区域透明：

```python
def _apply_circle_geometry(self) -> None:
    if self._circle or self._round:
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    else:
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
```

#### 3.2.4 Round 按钮内边距

Round 按钮的大圆角会侵入内容区域，导致文本触碰边缘。通过 `setContentsMargins` 添加额外水平内边距：

```python
def _apply_round_padding(self) -> None:
    """Add extra horizontal padding equal to height/2 for capsule buttons."""
    size_data = tokens.component_sizes.get(self._size.value, {})
    h = size_data.get("height", 34)
    extra = h // 2
    self._layout.setContentsMargins(extra, 0, extra, 0)
```

### 3.3 BUG-3 修复：Showcase 传入实际 QIcon

**修改文件**：`examples/gallery/showcases/button_showcase.py`

新增 `_make_icon()` 辅助函数（复用 `input.py` 中 `_text_icon` 的模式），通过 Unicode 字符渲染为 `QPixmap` 创建图标：

```python
def _make_icon(char: str, size: int = 16, color: QColor | None = None) -> QIcon:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setPen(color or QColor("#ffffff"))
    font = QFont()
    font.setPixelSize(int(size * 0.75))
    painter.setFont(font)
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, char)
    painter.end()
    return QIcon(px)

# 使用
TButton("Search", button_type=TButton.ButtonType.PRIMARY, icon=_make_icon("🔍"))
TButton("Next", icon=_make_icon("→", color=QColor("#333639")),
        icon_placement=TButton.IconPlacement.RIGHT)
```

---

## 4. BaseWidget 初始化顺序问题

### 4.1 问题

`BaseWidget.__init__` 在 `super().__init__()` 中调用 `apply_theme()`，而此时 `TButton.__init__` 尚未完成实例属性（如 `_circle`、`_round`、`_size`）的初始化。新增的 `_apply_circle_geometry()` 和 `_apply_size_from_tokens()` 方法访问这些属性时会抛出 `AttributeError`。

### 4.2 解决

在所有访问实例属性的方法入口处添加 `hasattr` 防御性检查：

```python
def _apply_size_from_tokens(self) -> None:
    if not hasattr(self, "_size"):
        return
    # ...

def _apply_circle_geometry(self) -> None:
    if not hasattr(self, "_circle"):
        return
    # ...
```

这是 Python 多重继承中 MRO（Method Resolution Order）导致的经典问题，`hasattr` 是标准的防御模式。

---

## 5. 修改文件清单

| 文件路径 | 修改类型 | 说明 |
|---------|---------|------|
| `src/tyto_ui_lib/components/atoms/button.py` | 修改 | 新增 `_apply_size_from_tokens()`、`_apply_round_padding()`；重写 `paintEvent()`、`_apply_circle_geometry()`；更新 `apply_theme()`、`sizeHint()` |
| `src/tyto_ui_lib/styles/templates/button.qss.j2` | 修改 | 新增 `TButton > QLabel` 透明规则、`TButton[circle="true"]` 选择器 |
| `examples/gallery/showcases/button_showcase.py` | 修改 | 新增 `_make_icon()` 辅助函数，Icon Buttons 区块传入实际 QIcon |

---

## 6. 测试验证

### 6.1 自动化测试

全部 174 项测试通过，其中 TButton 相关 20 项测试全部通过：

```
tests/test_atoms/test_button.py  20 passed
```

### 6.2 手动验证

通过 `uv run python examples/gallery.py` 启动 Gallery，验证以下场景：

| 验证项 | 预期结果 | 状态 |
|-------|---------|------|
| Sizes 区块：Tiny/Small/Medium/Large | 四个按钮高度依次递增 | ✓ |
| Circle & Round 区块：Circle 按钮 | 显示为正圆形，边缘平滑无锯齿 | ✓ |
| Circle & Round 区块：Round 按钮 | 显示为胶囊形，边缘平滑无锯齿 | ✓ |
| Round 按钮文本 | 文本左右有充足间距，不触碰边缘 | ✓ |
| Round 按钮 hover | 鼠标悬停时边框颜色在圆角处完整显示 | ✓ |
| Icon Buttons 区块 | 图标在文本左侧/右侧正确显示 | ✓ |
| Light/Dark 主题切换 | 所有修复在两套主题下均正常 | ✓ |

---

## 7. 经验总结

### 7.1 Qt QSS `border-radius` 的局限性

在基于 `QWidget` 的自定义组件中，QSS `border-radius` 存在以下已知限制：

1. **仅影响背景绘制**：不裁剪子控件的绘制区域
2. **不支持抗锯齿裁剪**：`QRegion` mask 是像素级的，无法实现平滑边缘
3. **`PE_Widget` 绘制的边框与自定义 clip path 可能不匹配**：导致边框在圆角处被截断

**最佳实践**：对需要圆角/圆形的自定义 QWidget，使用 `QPainter` 手动绘制背景和边框，配合 `WA_TranslucentBackground` 实现透明外部区域。

### 7.2 BaseWidget 初始化顺序

当基类的 `__init__` 调用虚方法（如 `apply_theme()`）时，子类的实例属性可能尚未初始化。应在所有被虚方法调用的辅助方法中添加 `hasattr` 防御检查。
