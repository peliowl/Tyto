# 实现计划：Menu 子菜单弹出面板样式优化

## 概述

将 TMenu 的 popup 子菜单面板从纯 QSS 样式方案迁移为 `WA_TranslucentBackground` + `_MenuPopupContainer` 自绘 + `QGraphicsDropShadowEffect` 的组合方案，对齐 NaiveUI 视觉风格。

## 任务

- [x] 1. 新增 `_MenuPopupContainer` 类并重构 `_create_popup`
  - [x] 1.1 在 `menu.py` 中新增 `_MenuPopupContainer` 私有类
    - 继承 `QWidget`，重写 `paintEvent`
    - 使用 `QPainter` 自绘圆角矩形背景（`colors.popover_color`）和淡边框（`colors.divider`，1px）
    - 圆角半径从 ThemeEngine 读取 `radius.large`
    - 包含 fallback 值处理（bg=#ffffff, border=#efeff5, radius=8）
    - _Requirements: 1.1, 3.1, 3.2, 3.3_

  - [x] 1.2 重构 `TMenuItemGroup._create_popup` 方法
    - 添加 `WA_TranslucentBackground` 属性
    - 外层 layout 设置 shadow margin（8px）为阴影留出渲染空间
    - 插入 `_MenuPopupContainer` 作为内部容器（objectName: `menu_popup_container`）
    - 在容器上应用 `QGraphicsDropShadowEffect`，参数从 `shadows.medium` Token 解析
    - 容器内部 layout 设置 contentsMargins 为 `(0, spacing.small, 0, spacing.small)`
    - 子菜单项添加到容器内部而非直接添加到 popup
    - _Requirements: 2.1, 2.3, 3.1, 5.1, 5.2_

  - [ ]* 1.3 编写属性测试：Popup 结构完整性
    - **Property 1: Popup 结构完整性**
    - **Validates: Requirements 2.3, 3.1**

  - [ ]* 1.4 编写属性测试：容器布局边距正确性
    - **Property 5: 容器布局边距正确性**
    - **Validates: Requirements 5.1, 5.2**

- [x] 2. 修改 popup 定位逻辑，添加间距
  - [x] 2.1 修改 `TMenuItemGroup._show_popup` 方法
    - 水平模式下方弹出时，y 坐标增加 `spacing.small`（4px）的垂直间距
    - 侧边弹出时（嵌套子菜单或折叠模式），x 坐标增加 `spacing.small`（4px）的水平间距
    - 间距值从 ThemeEngine 读取 `spacing.small`，fallback 为 4
    - _Requirements: 4.1, 4.2_

  - [ ]* 2.2 编写属性测试：Popup 间距正确性
    - **Property 4: Popup 间距正确性**
    - **Validates: Requirements 4.1, 4.2**

- [x] 3. 主题切换支持
  - [x] 3.1 修改 `TMenuItemGroup.apply_theme` 方法
    - 当 `self._popup` 存在时，查找 `menu_popup_container` 子控件
    - 更新 `QGraphicsDropShadowEffect` 的阴影参数（从当前主题 Token 重新解析）
    - 调用 `container.update()` 触发 `_MenuPopupContainer` 重绘
    - _Requirements: 1.2, 2.2, 3.4, 6.3_

  - [x] 3.2 新增 `_apply_shadow_from_token` 辅助方法
    - 解析 `shadows.medium` Token 字符串为 offset、blur、color 参数
    - 应用到传入的 `QGraphicsDropShadowEffect` 实例
    - 包含解析失败的 fallback 处理
    - _Requirements: 2.1, 2.2_

  - [ ]* 3.3 编写属性测试：阴影参数与 Token 一致性
    - **Property 3: 阴影参数与 Token 一致性**
    - **Validates: Requirements 2.1, 2.2**

  - [ ]* 3.4 编写属性测试：主题切换传播
    - **Property 6: 主题切换传播**
    - **Validates: Requirements 6.3**

- [x] 4. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 5. 更新 QSS 模板
  - [x] 5.1 修改 `menu.qss.j2`
    - 移除旧的 `QWidget#menu_popup` 样式块
    - 新增 `QWidget#menu_popup_container` 内部菜单项的样式规则（hover 背景色等）
    - 确保 popup 内的 TMenuItem 和 TMenuItemGroup 样式正确继承
    - _Requirements: 1.1, 3.2, 3.3_

  - [ ]* 5.2 编写单元测试：Light/Dark 主题视觉验证
    - 验证 Light 主题下 popover_color 为 #ffffff
    - 验证 Dark 主题下 popover_color 为 rgb(72, 72, 78)
    - 验证 Token 缺失时 fallback 值正确
    - _Requirements: 6.1, 6.2_

- [x] 6. 集成验证与最终检查
  - [x] 6.1 确保 popup 的 eventFilter 在新结构下正常工作
    - 验证鼠标进入 popup 容器时取消隐藏定时器
    - 验证 `_do_hide_popup` 中的 `underMouse()` 检测在新层级结构下正确
    - _Requirements: 全部_

  - [ ]* 6.2 编写属性测试：容器自绘 Token 一致性
    - **Property 2: 容器自绘 Token 一致性**
    - **Validates: Requirements 1.1, 1.2, 3.2, 3.3, 3.4**

- [x] 7. 最终 Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请向用户确认。

## 备注

- 标记 `*` 的任务为可选任务，可跳过以加速 MVP
- 每个任务引用了具体的需求编号以确保可追溯性
- Checkpoint 任务确保增量验证
- 属性测试验证通用正确性属性，单元测试验证具体示例和边界情况
- 实现语言：Python 3.12（PySide6）
- 属性基测试库：hypothesis
