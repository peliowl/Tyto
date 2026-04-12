# TCollapse 组件缺陷修复报告

> 文档版本：1.0  
> 修复日期：2026-04-10  
> 涉及组件：`TCollapse`、`TCollapseItem`、`_CollapseArrowWidget`  
> 涉及文件：`collapse.py`、`collapse.qss.j2`、`test_collapse.py`

---

## 1. Arrow Placement Right 布局错误

### 1.1 问题描述

设置 `arrow_placement="right"` 时，箭头被推到 header 最右侧，与标题之间产生大量空白。预期行为是箭头紧贴标题文字右侧。

### 1.2 根因分析

`_rebuild_header_layout` 方法在 `"right"` 分支中为 `title_widget` 设置了 `stretch=1`：

```python
# 错误代码
self._header_layout.addWidget(title_widget, 1)  # stretch=1 导致 title 占满剩余空间
```

`stretch=1` 使 title 扩展填满所有可用空间，将 arrow 推到了 header 最右端。

### 1.3 修复方案

- `"right"` 分支：title 和 arrow 均不设置 stretch，在 arrow 之后添加 `addStretch(1)` 填充剩余空间
- `"left"` 分支：保持 title 的 `stretch=1`，确保内容左对齐

```python
if self._arrow_placement == "right":
    self._header_layout.addWidget(title_widget)
    self._header_layout.addWidget(arrow_widget)
    self._header_layout.addStretch(1)
    # header_extra 放在 stretch 之后
else:
    self._header_layout.addWidget(arrow_widget)
    self._header_layout.addWidget(title_widget, 1)
```

### 1.4 关联测试变更

- `test_arrow_right_layout_order`：更新断言匹配新布局顺序 `[title, arrow]`
- `test_header_extra_in_right_arrow_layout`：extra widget 位于 stretch spacer 之后（index 3）

---

## 2. 自定义标题字体大小不一致

### 2.1 问题描述

通过 `set_title(widget)` 设置自定义标题后，自定义标题的字体大小与默认标题不一致（偏小）。

### 2.2 根因分析

QSS 选择器 `TCollapseItem QLabel#collapse_title` 通过 `objectName` 匹配目标控件。`set_title` 方法未给自定义 widget 设置 `collapse_title` 的 objectName，导致 QSS 中的 `font-size`、`color` 等规则无法应用。

### 2.3 修复方案

在 `set_title` 中添加 `widget.setObjectName("collapse_title")`：

```python
def set_title(self, widget: QWidget) -> None:
    # ...
    self._custom_title_widget = widget
    widget.setObjectName("collapse_title")  # 新增
    # ...
```

---

## 3. 自定义箭头图标间距缺失

### 3.1 问题描述

通过 `set_arrow(widget)` 设置自定义箭头图标后，图标与标题之间没有间距。

### 3.2 根因分析

与问题 2 同类。QSS 中 `collapse_arrow` 的 `margin-left` / `margin-right` 规则未能匹配到自定义 arrow widget，因为缺少 objectName。

### 3.3 修复方案

在 `set_arrow` 中添加 `widget.setObjectName("collapse_arrow")`：

```python
def set_arrow(self, widget: QWidget) -> None:
    # ...
    self._custom_arrow_widget = widget
    widget.setObjectName("collapse_arrow")  # 新增
    # ...
```

---

## 4. 自定义系统图标尺寸不一致

### 4.1 问题描述

使用 QLabel 文字图标（如 "✔"）作为自定义箭头时，图标视觉尺寸与默认箭头不一致。

### 4.2 根因分析

QSS 中 `collapse_arrow` 规则设置了 `min-width`/`max-width`/`min-height`/`max-height` 约束控件尺寸，但未设置 `font-size`。默认的 `_CollapseArrowWidget` 通过 `paintEvent` 自绘不受 font-size 影响，但 QLabel 文字图标的渲染大小取决于 font-size。

### 4.3 修复方案

在 `collapse.qss.j2` 的 `collapse_arrow` 规则中添加 `font-size`：

```css
TCollapseItem QWidget#collapse_arrow {
    color: {{ colors.text_primary }};
    font-size: {{ component_sizes.medium.icon_size }}px;  /* 新增 */
    min-width: {{ component_sizes.medium.icon_size }}px;
    max-width: {{ component_sizes.medium.icon_size }}px;
    min-height: {{ component_sizes.medium.icon_size }}px;
    max-height: {{ component_sizes.medium.icon_size }}px;
}
```

---

## 5. Dark 模式下展开面板文字颜色错误

### 5.1 问题描述

Dark 模式下，展开面板中的内容文字颜色偏暗，几乎不可见。

### 5.2 根因分析

`collapse_content_wrapper` 的 QSS 规则未设置 `color` 属性。QSS 中 `QWidget` 的 `color` 不会自动传递给子 `QLabel`，导致 QLabel 使用系统默认的深色文字。

### 5.3 修复方案

在 `collapse.qss.j2` 中为内容区域添加文字颜色，同时为子 QLabel 显式设置：

```css
TCollapseItem QWidget#collapse_content_wrapper {
    color: {{ colors.text_primary }};
    /* ... 其他属性 ... */
}

TCollapseItem QWidget#collapse_content_wrapper QLabel {
    color: {{ colors.text_primary }};
}
```

---

## 6. 跨组件同类问题排查与修复

### 6.1 问题描述

问题 2、3 的模式（自定义 widget 未传播 objectName）在其他组件中同样存在。

### 6.2 影响范围

| 组件 | 方法 | 缺失的 objectName | QSS 影响 |
|------|------|--------------------|----------|
| `TAlert` | `set_icon` | `alert_icon` | font-size、padding、color |
| `TTimelineItem` | `set_dot` | `timeline_dot` | size、border-radius、color |
| `TTimelineItem` | `set_title` | `timeline_title` | font-size、color、font-weight |

### 6.3 修复方案

在每个 `set_*` 方法中添加对应的 `setObjectName` 调用：

```python
# TAlert.set_icon
widget.setObjectName("alert_icon")

# TTimelineItem.set_dot
widget.setObjectName("timeline_dot")

# TTimelineItem.set_title
widget.setObjectName("timeline_title")
```

### 6.4 通用规则

> 当组件提供 `set_*(widget)` 方法替换默认子控件时，必须为自定义 widget 设置与默认控件相同的 `objectName`，以确保 QSS 规则正确匹配。
