# Implementation Plan: TCollapse 箭头图标变形修复

## 概述

修复 TCollapse 箭头图标因非等比缩放导致的视觉变形。通过 QSS 高度约束和 paintEvent 等比缩放两层防御确保箭头在任何布局条件下正确渲染。

## Tasks

- [x] 1. 修复 QSS 模板高度约束
  - [x] 1.1 在 `collapse.qss.j2` 的 `TCollapseItem QWidget#collapse_arrow` 规则中添加 `min-height` 和 `max-height` 约束，值引用 `component_sizes.medium.icon_size` Token
    - 同时为 disabled 状态的箭头规则确认高度约束继承正确
    - _Requirements: 1.1, 1.2, 4.2_

- [x] 2. 修复 paintEvent 等比缩放逻辑
  - [x] 2.1 修改 `_CollapseArrowWidget.paintEvent`，将 `scale_x`/`scale_y` 替换为 `scale = min(w, h) / _CHEVRON_VIEWBOX`，并添加居中偏移 `offset_x`/`offset_y`
    - 旋转变换保持以控件中心为轴心，在缩放之前应用
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3_
  - [ ]* 2.2 编写 Property 1 属性基测试：等比缩放与居中不变量
    - **Property 1: 等比缩放与居中不变量**
    - 生成随机 (w, h) 对，验证缩放因子为 `min(w,h)/16` 且偏移量正确居中
    - **Validates: Requirements 2.1, 2.2, 2.3**
  - [ ]* 2.3 编写单元测试验证折叠/展开状态下的旋转行为
    - 验证折叠状态无旋转、展开状态 90 度旋转
    - _Requirements: 3.1, 3.2_

- [x] 3. Checkpoint - 确保所有测试通过
  - 运行 `uv run pytest tests/test_molecules/test_collapse.py -v`，确保所有测试通过，如有问题请告知用户。

- [ ] 4. 验证 QSS 模板渲染正确性
  - [ ]* 4.1 编写单元测试验证渲染后的 QSS 包含 min-height/max-height 约束
    - _Requirements: 1.1_
  - [ ]* 4.2 编写 Property 2 属性基测试：箭头控件正方形约束
    - **Property 2: 箭头控件正方形约束**
    - 创建不同配置的 TCollapseItem，验证箭头控件宽高相等
    - **Validates: Requirements 1.1, 1.2**

- [x] 5. Final checkpoint - 确保所有测试通过
  - 运行 `uv run pytest tests/test_molecules/test_collapse.py -v`，确保全部测试通过，如有问题请告知用户。

## Notes

- 标记 `*` 的任务为可选测试任务，可跳过以加速 MVP
- Property 3（箭头旋转状态一致性）已在现有测试中覆盖，无需新增
- 修改仅涉及 2 个文件：`collapse.qss.j2` 和 `collapse.py`
