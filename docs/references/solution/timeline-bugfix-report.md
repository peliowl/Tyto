# TTimeline 组件缺陷修复报告

> 文档版本：1.0  
> 修复日期：2026-04-10  
> 涉及组件：`TTimeline`、`TTimelineItem`  
> 涉及文件：`timeline.py`、`timeline.qss.j2`

---

## 1. Horizontal 模式下节点和文本布局错误

### 1.1 问题描述

设置 `horizontal=True` 后，每个 TTimelineItem 内部仍使用垂直模式的布局结构（dot 在 title 左侧），导致水平模式下节点和文本位置错误。

预期效果（参考 NaiveUI）：
- 每个 item 内部垂直排列：dot 在上方，title / content / time 在下方
- items 之间水平排列，用水平线连接各 dot

### 1.2 根因分析

`_rebuild_full_layout` 仅将 TTimeline 的顶层布局从 `QVBoxLayout` 切换为 `QHBoxLayout`，但未重建 TTimelineItem 的内部布局。Item 内部始终保持初始化时的结构：

```
[root_layout: QHBoxLayout]
  └─ [text_column: QVBoxLayout]
       ├─ [title_row: QHBoxLayout] → dot + title 水平排列
       ├─ content_label
       └─ time_label
```

水平模式下需要的结构：

```
[root_layout: QHBoxLayout]
  └─ [column: QVBoxLayout]
       ├─ dot（左对齐）
       ├─ title
       ├─ content
       └─ time
```

### 1.3 修复方案

为 `TTimelineItem` 新增 `_set_horizontal(horizontal: bool)` 方法，根据模式重建内部布局：

- **水平模式**：创建垂直 QVBoxLayout，dot 左对齐在顶部，title / content / time 依次排列，content 和 time 的左侧缩进清零
- **垂直模式**：恢复原始布局（dot + title 水平行，content / time 缩进 16px）

在 `_apply_mode_to_item` 中调用 `item._set_horizontal(self._horizontal)`。

### 1.4 关键代码

```python
def _set_horizontal(self, horizontal: bool) -> None:
    # 分离所有 widget，清空子布局
    # ...
    if horizontal:
        col = QVBoxLayout()
        col.addWidget(dot_widget, 0, Qt.AlignmentFlag.AlignLeft)
        col.addWidget(title_widget)
        col.addWidget(self._content_label)  # contentsMargins(0,0,0,0)
        col.addWidget(self._time_label)     # contentsMargins(0,0,0,0)
    else:
        # 恢复垂直模式原始布局
        # ...
```

---

## 2. Horizontal 模式下文本未与 Dot 左对齐

### 2.1 问题描述

水平模式下 dot 居中显示，文本也跟着居中，未与 dot 左对齐。

### 2.2 根因分析

`_set_horizontal` 中 dot 使用了 `Qt.AlignmentFlag.AlignHCenter`。

### 2.3 修复方案

将 dot 的对齐方式改为 `Qt.AlignmentFlag.AlignLeft`：

```python
col.addWidget(dot_widget, 0, Qt.AlignmentFlag.AlignLeft)
```

---

## 3. Size 属性设置不生效

### 3.1 问题描述

设置 `TTimeline.size = TimelineSize.LARGE` 后，字体大小未发生变化。需要触发其他属性变更（如切换 horizontal）才能看到效果。

### 3.2 根因分析

QSS 使用后代选择器 `TTimeline[timelineSize="large"] TTimelineItem QLabel#timeline_title` 控制字体大小。`size` setter 仅 re-polish 了 TTimeline 自身和 TTimelineItem，但未 re-polish 目标 QLabel 子控件。

Qt QSS 的后代选择器要求目标控件本身被 re-polish 才能重新计算样式。仅 re-polish 祖先控件不会触发后代控件的样式更新。

### 3.3 修复方案

在 `size` setter 中显式 re-polish 每个 item 内部的 QLabel：

```python
@size.setter
def size(self, value: TimelineSize) -> None:
    self._size = value
    self.setProperty("timelineSize", value.value)
    self.style().unpolish(self)
    self.style().polish(self)
    for item in self._items:
        item.style().unpolish(item)
        item.style().polish(item)
        for label in (item._title_label, item._content_label, item._time_label):
            label.style().unpolish(label)
            label.style().polish(label)
    self.update()
```

同时在 `add_item` 中为新添加的 item 执行 re-polish，确保新 item 也能继承父级的 size 样式：

```python
def add_item(self, item: TTimelineItem) -> None:
    # ...
    self._apply_mode_to_item(item, idx)
    item.style().unpolish(item)
    item.style().polish(item)
    self.update()
```

### 3.4 通用规则

> 当父组件通过 QSS 动态属性（`setProperty`）控制子组件样式时，属性变更后必须对所有受影响的子控件（包括深层后代）执行 `unpolish` + `polish`，否则 QSS 后代选择器不会实时生效。
