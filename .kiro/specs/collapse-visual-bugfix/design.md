# TCollapse 组件视觉缺陷修复 — 设计文档

## 概述

修复 TCollapse 组件的 4 个视觉缺陷，使其与 NaiveUI Collapse 效果一致。涉及箭头图标渲染方式、间距、布局和分割线逻辑的调整。

---

## 修复方案

### Bug 1 & 3: 箭头间距与 right placement 位置（需求 1.1–1.3, 3.1–3.3）

**根因**：`_update_arrow` 中 `setFixedWidth(20)` 使箭头容器过宽，加上 QSS margin 导致总间距过大。

**方案**：
- 移除 `_arrow_label` 的 `setFixedWidth(20)` 调用
- 改用自绘 widget（见 Bug 2 方案），其 `sizeHint` 返回 `(icon_size, icon_size)` 即 `(18, 18)`
- QSS 中保持 `margin-right: 4px`（left placement）和 `margin-left: 4px`（right placement），通过 `spacing.small` token
- `_rebuild_header_layout` 逻辑不变，title stretch=1 已正确实现

### Bug 2: 箭头图标形状与大小（需求 2.1–2.4）

**根因**：使用 Unicode 字符 "▾"/"▸" 作为箭头，形状为实心三角形，与 NaiveUI 的 chevron-right 线条箭头不一致。

**方案**：
- 新建 `_CollapseArrowWidget(QWidget)` 内部类，使用 QPainter 绘制 NaiveUI ChevronRight SVG path
- SVG path data: `M5.64645 3.14645C5.45118 3.34171 5.45118 3.65829 5.64645 3.85355L9.79289 8L5.64645 12.1464C5.45118 12.3417 5.45118 12.6583 5.64645 12.8536C5.84171 13.0488 6.15829 13.0488 6.35355 12.8536L10.8536 8.35355C11.0488 8.15829 11.0488 7.84171 10.8536 7.64645L6.35355 3.14645C6.15829 2.95118 5.84171 2.95118 5.64645 3.14645Z`
- viewBox: 0 0 16 16，渲染尺寸通过 ThemeEngine 获取 `component_sizes.medium.icon_size`（18px）
- 展开状态通过 `QTransform.rotate(90)` 旋转绘制，收缩状态不旋转
- 颜色从 QSS 的 `color` 属性继承（通过 `self.palette().color(QPalette.ColorRole.WindowText)`）
- 替换原有的 `_arrow_label`（QLabel）为 `_CollapseArrowWidget` 实例
- `_update_arrow` 方法改为调用 arrow widget 的 `set_expanded(bool)` + `update()`
- objectName 保持 `"collapse_arrow"` 以兼容现有 QSS 选择器

**_CollapseArrowWidget 设计**：
```python
class _CollapseArrowWidget(QWidget):
    # Internal chevron-right arrow widget using QPainter
    # - sizeHint: (icon_size, icon_size) from theme token
    # - paintEvent: draw chevron-right path, rotate 90° when expanded
    # - set_expanded(bool): update rotation state
    # - objectName: "collapse_arrow"
```

### Bug 4: 分割线逻辑（需求 4.1–4.3）

**根因**：QSS 中所有 `TCollapseItem` 都有 `border-top`，包括第一个 item。

**方案**：
- 在 `TCollapse.add_item` 中，为每个 item 设置 Qt property `"firstItem"`
  - 第一个 item: `setProperty("firstItem", "true")`
  - 后续 item: `setProperty("firstItem", "false")`
- QSS 模板中：
  - `TCollapseItem` 默认无 border-top
  - `TCollapseItem[firstItem="false"]` 添加 `border-top: 1px solid {{ colors.divider }}`
- `remove_item` 时重新计算所有 item 的 `firstItem` 属性

---

## 涉及文件变更

| 文件 | 变更内容 |
|------|----------|
| `src/tyto_ui_lib/components/molecules/collapse.py` | 新增 `_CollapseArrowWidget`；修改 `_update_arrow`；修改 `add_item`/`remove_item` 设置 firstItem 属性 |
| `src/tyto_ui_lib/styles/templates/collapse.qss.j2` | 修改箭头尺寸样式；修改分割线选择器逻辑 |
| `tests/test_molecules/test_collapse.py` | 更新箭头相关测试；新增分割线测试 |

---

## 正确性属性

### Property 1: 箭头间距一致性（验证需求 1.1, 1.2, 3.2）

对于任意 `arrow_placement ∈ {"left", "right"}`，箭头 widget 与标题 widget 之间的 QSS margin 始终为 `spacing.small`（4px）。

### Property 2: 箭头旋转状态一致性（验证需求 2.1, 2.2）

对于任意 `TCollapseItem`，当 `expanded=True` 时箭头旋转角度为 90°，当 `expanded=False` 时旋转角度为 0°。在任意次 toggle 操作后，此不变量始终成立。

### Property 3: 分割线首项排除（验证需求 4.1, 4.2）

对于包含 N 个 item 的 `TCollapse`（N ≥ 1），第一个 item 的 `firstItem` 属性为 `"true"`，其余 item 的 `firstItem` 属性为 `"false"`。在任意 add/remove 操作后，此不变量始终成立。

---

## 测试策略

- 框架：pytest + pytest-qt + hypothesis
- 单元测试：验证箭头 widget 类型、旋转状态、firstItem 属性、布局顺序
- 属性基测试：Property 2（toggle 序列后旋转状态一致性）、Property 3（add/remove 序列后 firstItem 不变量）
