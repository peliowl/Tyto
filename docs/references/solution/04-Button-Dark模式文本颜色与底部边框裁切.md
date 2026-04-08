# BUG-004：TButton Dark 模式文本颜色异常与 Gallery 按钮底部边框裁切

| 属性 | 值 |
|------|-----|
| 版本 | V1.0.2 |
| 严重程度 | 中 |
| 影响组件 | `TButton`、`TSearchBar`（间接）、`MessageShowcase`（间接）、`ModalShowcase`（间接） |
| 涉及文件 | `src/tyto_ui_lib/styles/templates/button.qss.j2`、`examples/gallery/views/component_showcase.py`、`examples/gallery/showcases/base_showcase.py`、`examples/gallery/showcases/button_showcase.py` |
| 修复日期 | 2026-04-08 |

---

## 1. 问题描述

在 Gallery 中发现 TButton 组件存在两个独立的显示异常：

### 异常 A：Dark 模式下按钮文本颜色未显示为白色

切换到 Dark 模式后，所有按钮的文本颜色仍然显示为深色（Light 模式的默认色），与 Checkbox、Radio、Input 等其他控件的 Dark 模式表现不一致。预期 Default/Dashed 类型按钮文本应为浅色（`rgba(255, 255, 255, 0.82)`），Primary/Info/Success/Warning/Error 类型按钮文本应为白色。

### 异常 B：Gallery 演示界面中部分按钮底部边框被裁切

在 Button Showcase 的多个区块中，部分按钮（Large 尺寸、Ghost 变体、Block Default）的底部 1px 边框被容器裁切，无法完整显示。

**复现步骤：**

1. 启动 Gallery 应用：`uv run python examples/gallery.py`
2. 选择 **Button** 组件
3. 切换到 **Dark Mode**，观察所有按钮文本颜色（异常 A）
4. 切换回 **Light Mode**，观察 Sizes 区块的 Large 按钮、Ghost 区块、Block 区块的底部边框（异常 B）

---

## 2. 根因分析

### 根因 A：QSS `color` 属性未级联到子 QLabel

TButton 内部使用 `QLabel`（`self._label`）渲染文本。全局 QSS 通过 `TButton { color: ... }` 设置了文本颜色，但 Qt QSS 的 `color` 属性不会自动从自定义父组件级联到子 QLabel。

`button.qss.j2` 中已有针对子 QLabel 的规则：

```css
TButton > QLabel {
    background: transparent;
    border: none;
}
```

该规则仅设置了 `background` 和 `border`，未设置 `color`。在 Light 模式下，QLabel 的默认文本颜色恰好为深色，视觉上无异常。但在 Dark 模式下，QLabel 仍使用默认的深色文本，导致文本在深色背景上不可见或对比度极低。

**对比验证：** 项目中其他组件（`TBreadcrumb`、`TMessage`、`TModal`）均在 QSS 模板中为子 QLabel 显式设置了 `color`：

```css
/* breadcrumb.qss.j2 */
TBreadcrumb QLabel { color: {{ colors.text_secondary }}; }

/* message.qss.j2 */
TMessage QLabel#message_text { color: {{ colors.text_primary }}; }
```

TButton 是唯一未为子 QLabel 设置 `color` 的组件。

### 根因 B：Gallery 容器布局零边距导致边框裁切

`BaseShowcase.hbox()` 静态方法创建的水平布局容器使用 `setContentsMargins(0, 0, 0, 0)`，即零底部边距。TButton 通过 `setFixedHeight(h)` 设置了精确高度（来自 Design Token），1px 边框绘制在该高度的最底部像素。

当容器的底部边距为 0 时，容器的绘制区域恰好等于按钮的 `fixedHeight`，导致底部 1px 边框位于容器绘制区域的边缘，被父级 `QScrollArea` 的视口裁切。

同时，`ComponentShowcase`（QScrollArea）使用 `setWidgetResizable(False)` 并通过 `resizeEvent` 手动同步宽度，但未正确处理内容高度计算，加剧了裁切问题。

**裁切链路：**

```
QScrollArea (viewport)
  └─ container (QWidget, fixedWidth)
       └─ BaseShowcase (QVBoxLayout, margins=0)
            └─ hbox container (QHBoxLayout, margins=0,0,0,0)
                 └─ TButton (fixedHeight=h, border=1px)
                      └─ 底部 1px 边框 → 被 hbox 容器边缘裁切
```

---

## 3. 解决方案

### 3.1 为所有按钮类型变体的子 QLabel 添加显式 `color` 规则

在 `button.qss.j2` 中，为每个按钮类型变体添加 `TButton[buttonType="xxx"] > QLabel { color: ... }` 规则，确保子 QLabel 在任何主题下都使用正确的文本颜色。

**基础规则：**

```css
TButton > QLabel {
    background: transparent;
    border: none;
    color: {{ colors.text_primary }};  /* 新增 */
}

TButton:hover > QLabel {
    color: {{ colors.primary }};  /* 新增 */
}

TButton:disabled > QLabel {
    color: {{ colors.text_disabled }};  /* 新增 */
}
```

**类型变体规则（以 Primary 为例）：**

```css
TButton[buttonType="primary"] > QLabel {
    color: {{ colors.white }};
}

TButton[buttonType="primary"]:hover > QLabel {
    color: {{ colors.white }};
}
```

**覆盖范围：** base、hover、pressed、disabled 状态 × default、primary、dashed、text、tertiary、info、success、warning、error 类型 × ghost 变体，共计约 30 条 `> QLabel` 规则。

### 3.2 修复 ComponentShowcase 滚动区域内容高度计算

将 `ComponentShowcase` 的 `setWidgetResizable` 从 `False` 改为 `True`，让 QScrollArea 自动管理内容 widget 的尺寸，正确计算内容高度：

```python
# 修复前
self.setWidgetResizable(False)

# 修复后
self.setWidgetResizable(True)
```

同时移除不再需要的 `resizeEvent` 覆写和 `show_component` 中的 `setFixedWidth` 调用，因为 `setWidgetResizable(True)` 已自动处理宽度同步。

### 3.3 为 Gallery 容器添加底部边距防止边框裁切

在 `BaseShowcase.hbox()` 和 `ButtonShowcase` 的 Block 容器中，将底部边距从 `0` 改为 `2`，为按钮的 1px 边框提供渲染空间：

```python
# BaseShowcase.hbox() 修复
layout.setContentsMargins(0, 0, 0, 2)  # 原为 (0, 0, 0, 0)

# ButtonShowcase Block 容器修复
block_layout.setContentsMargins(0, 0, 0, 2)  # 原为 (0, 0, 0, 0)
```

### 3.4 修改汇总

| 文件 | 修改内容 |
|------|----------|
| `styles/templates/button.qss.j2` | 为所有按钮类型变体的 `> QLabel` 添加显式 `color` 规则 |
| `examples/gallery/views/component_showcase.py` | `setWidgetResizable(False)` → `True`；移除 `resizeEvent` 覆写和 `setFixedWidth` 调用 |
| `examples/gallery/showcases/base_showcase.py` | `hbox()` 底部边距 `0` → `2` |
| `examples/gallery/showcases/button_showcase.py` | Block 容器底部边距 `0` → `2` |

---

## 4. 排除的方案

### 4.1 使用 `color: inherit`（已排除）

Qt QSS 不支持 CSS 的 `inherit` 关键字。尝试在 `TButton > QLabel` 中使用 `color: inherit` 会被 Qt 样式引擎忽略，QLabel 仍使用默认颜色。

### 4.2 在 `apply_theme()` 中程序化设置 QLabel 颜色（已排除）

虽然可以在 `apply_theme()` 中通过 `self._label.setStyleSheet(f"color: {color}")` 设置颜色，但这违反了项目的样式架构原则：所有样式应通过 QSS 模板 + Design Token 驱动，不在组件代码中硬编码样式逻辑。

### 4.3 使用 `setMinimumHeight` 替代 `setFixedHeight`（已排除）

尝试将 `_apply_size_from_tokens()` 中的 `setFixedHeight(h)` 改为 `setMinimumHeight(h)`，虽然解决了边框裁切，但在 `setWidgetResizable(True)` 的 QScrollArea 中，按钮会无限制地纵向拉伸填满可用空间，导致所有尺寸变体高度相同，分子组件和有机体组件中的按钮也严重变形。

---

## 5. 影响范围

- **TButton**：Dark 模式下所有类型变体的文本颜色正确显示
- **Gallery Button Showcase**：所有区块（Sizes、Ghost、Block 等）的按钮底部边框完整显示
- **TSearchBar**：内部 TButton 的 Dark 模式文本颜色自动受益
- **MessageShowcase / ModalShowcase**：触发按钮的 Dark 模式文本颜色自动受益
- **其他 Showcase**：`hbox()` 底部边距变更影响所有使用 `hbox()` 的 Showcase，但 2px 的增量在视觉上不可感知

---

## 6. 验证

```bash
uv run pytest -v
# 174 passed in 14.84s
```

**手动验证：**

1. 启动 Gallery，切换到 Dark Mode，确认所有按钮文本颜色正确
2. 切换回 Light Mode，确认 Sizes/Ghost/Block 区块按钮底部边框完整
3. 检查 SearchBar、Message、Modal 页面中的按钮在 Dark 模式下文本颜色正确

---

## 7. 经验总结

> **规则 1：** Qt QSS 的 `color` 属性不会从自定义父组件（`QWidget` 子类）自动级联到子 `QLabel`。当组件内部使用 `QLabel` 渲染文本时，必须在 QSS 模板中为 `ParentWidget > QLabel` 显式设置 `color`，并为每个类型变体和交互状态（hover、disabled 等）提供对应的颜色规则。

> **规则 2：** `QScrollArea` 使用 `setWidgetResizable(False)` 时需要手动管理内容 widget 的宽高，容易导致高度计算不准确。优先使用 `setWidgetResizable(True)` 让 QScrollArea 自动管理内容尺寸。

> **规则 3：** 当组件使用 `setFixedHeight` 且具有 1px 边框时，父容器的布局边距（`contentsMargins`）必须为边框预留至少 1-2px 的底部空间，否则边框会被容器边缘裁切。这是 Gallery 展示层的布局问题，不应通过修改组件的 `setFixedHeight` 逻辑来解决。

> **规则 4：** 不要用 `setMinimumHeight` 替代 `setFixedHeight` 来解决边框裁切问题。在 `setWidgetResizable(True)` 的 QScrollArea 中，仅设置 `minimumHeight` 的 widget 会被拉伸填满可用空间，破坏尺寸变体的视觉区分。
