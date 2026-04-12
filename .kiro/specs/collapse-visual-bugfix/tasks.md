# TCollapse 组件视觉缺陷修复 — 任务列表

## 任务

- [x] 1. 新增 _CollapseArrowWidget 自绘箭头组件
  - [x] 1.1 在 `collapse.py` 中新增 `_CollapseArrowWidget(QWidget)` 内部类，使用 QPainter 绘制 NaiveUI ChevronRight SVG path（viewBox 0 0 16 16），sizeHint 返回 `(component_sizes.medium.icon_size, component_sizes.medium.icon_size)` 即 (18, 18)，objectName 设为 `"collapse_arrow"`
  - [x] 1.2 实现 `set_expanded(bool)` 方法，展开时旋转 90°，收缩时 0°，调用 `update()` 触发重绘
  - [x] 1.3 `paintEvent` 中通过 `QPainterPath` 绘制 chevron path，颜色从 palette WindowText 获取，展开时应用 `QTransform.rotate(90)` 围绕中心旋转
- [x] 2. 替换箭头渲染逻辑
  - [x] 2.1 将 `TCollapseItem.__init__` 中的 `self._arrow_label = QLabel(...)` 替换为 `self._arrow_label = _CollapseArrowWidget(...)`，移除 `setAlignment` 和 `setText` 调用
  - [x] 2.2 修改 `_update_arrow` 方法：移除 `setText("▾"/"▸")` 和 `setFixedWidth(20)`，改为调用 `self._arrow_label.set_expanded(self._expanded)`
- [x] 3. 修复分割线逻辑
  - [x] 3.1 在 `TCollapse.add_item` 中，根据 item 在列表中的位置设置 `setProperty("firstItem", "true"/"false")`，并调用 `style().unpolish/polish` 刷新样式
  - [x] 3.2 在 `TCollapse.remove_item` 中，移除 item 后重新遍历 `_items` 更新所有 item 的 `firstItem` 属性
- [x] 4. 更新 QSS 模板
  - [x] 4.1 修改 `collapse.qss.j2`：将 `TCollapseItem` 的 `border-top` 移除，改为 `TCollapseItem[firstItem="false"]` 添加 `border-top: 1px solid {{ colors.divider }}`
  - [x] 4.2 修改箭头样式：将 `min-width/max-width: 20px` 改为 `min-width/max-width: {{ component_sizes.medium.icon_size }}px`，确保箭头容器尺寸与图标一致
- [x] 5. 更新单元测试
  - [x] 5.1 更新 `test_arrow_updates` 测试：验证箭头 widget 类型为 `_CollapseArrowWidget`，验证 `_expanded` 属性在 toggle 后正确变化
  - [x] 5.2 新增 `test_first_item_property` 测试：验证添加多个 item 后 firstItem 属性正确设置，验证 remove 后属性正确更新
  - [x] 5.3 新增 `test_first_item_single` 测试：验证只有一个 item 时 firstItem 为 "true"
- [x] 6. 属性基测试
  - [x] 6.1 Property 2: 箭头旋转状态一致性 — 使用 hypothesis 生成随机 toggle 操作序列，验证每次操作后 `_expanded` 状态与箭头 widget 的 `_expanded` 属性一致
  - [x] 6.2 Property 3: 分割线首项排除不变量 — 使用 hypothesis 生成随机 add/remove 操作序列，验证操作后第一个 item 的 firstItem 为 "true"，其余为 "false"
