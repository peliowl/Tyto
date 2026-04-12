# 实现计划：TMenu 组件重新实现

## 概述

基于设计文档重新实现 TMenu 菜单组件，替换现有 `organisms/menu.py`。采用增量开发方式：先实现核心数据结构（TMenuItem），再实现分组（TMenuItemGroup），最后实现顶层容器（TMenu）和水平弹出模式。每步完成后通过测试验证。

## Tasks

- [x] 1. 实现 TMenuItem 核心组件
  - [x] 1.1 重写 TMenuItem 类：继承 BaseWidget，实现 __init__、_build_ui、key/label/disabled 属性、set_active、is_active、set_indent_level、set_collapsed_mode、set_menu_disabled、mousePressEvent、apply_theme
    - 图标使用 QLabel + QIcon.pixmap，icon 为 None 时 setVisible(False)
    - 活跃状态通过 QSS dynamic property `active="true"/"false"` 控制
    - 缩进通过 row layout 的 left contentsMargins 实现，值从 Design Token menu.indent 获取
    - _Requirements: 1.4, 2.1, 2.3, 2.4, 6.3, 6.4_

  - [ ]* 1.2 编写 Property 2 属性基测试：key/label 数据完整性
    - **Property 2: key/label 数据完整性**
    - 使用 Hypothesis 生成随机非空字符串，验证 TMenuItem(key, label) 后 item.key == key, item.label == label
    - **Validates: Requirements 1.4**

  - [ ]* 1.3 编写单元测试：TMenuItem 基础行为
    - 测试 active 状态往返、disabled 阻断点击、icon 显示/隐藏、collapsed 模式隐藏文字
    - _Requirements: 2.1, 2.3, 2.4, 6.3, 6.4_

- [x] 2. 实现 TMenuItemGroup 垂直模式
  - [x] 2.1 重写 TMenuItemGroup 类：继承 BaseWidget，实现 __init__、_build_ui（header + children_wrapper）、key/label 属性、add_item、get_items、get_all_item_keys、set_indent_level、set_collapsed_mode、set_menu_disabled、apply_theme
    - 箭头指示符：展开时 ▲，收缩时 ▼
    - 子项缩进：child_level = parent_indent_level + 1
    - _Requirements: 1.2, 2.2, 4.2, 4.5, 4.6, 4.7_

  - [x] 2.2 实现 TMenuItemGroup 展开/收缩动画：set_expanded、_animate_toggle（QPropertyAnimation on maximumHeight，200ms ease-in-out）、mousePressEvent 切换展开状态
    - _Requirements: 4.3, 4.4_

  - [ ]* 2.3 编写 Property 5 属性基测试：箭头指示符与展开状态一致性
    - **Property 5: 箭头指示符与展开状态一致性**
    - 生成随机 expanded 状态，验证箭头文本匹配
    - **Validates: Requirements 4.5, 4.6**

  - [ ]* 2.4 编写 Property 6 属性基测试：展开/收缩切换往返一致性
    - **Property 6: 展开/收缩切换往返一致性**
    - 生成随机初始状态，toggle 两次验证恢复
    - **Validates: Requirements 4.3, 4.4**

  - [ ]* 2.5 编写 Property 7 属性基测试：缩进量与嵌套层级成正比
    - **Property 7: 缩进量与嵌套层级成正比**
    - 生成随机嵌套层级 0-5，验证左边距 = n × menu.indent
    - **Validates: Requirements 4.2, 4.7**

- [x] 3. Checkpoint - 确保 TMenuItem 和 TMenuItemGroup 测试通过
  - 运行 `uv run pytest tests/test_organisms/test_menu.py -v`，确保所有测试通过，如有问题请告知用户。

- [x] 4. 实现 TMenu 容器（垂直模式）
  - [x] 4.1 重写 TMenu 类：继承 BaseWidget，实现 MenuMode 枚举、__init__、_build_ui（根据 mode 选择 QHBoxLayout/QVBoxLayout）、add_item（插入布局 + 连接信号 + 传播 mode）、set_active_key、get_active_key、apply_theme
    - 垂直模式末尾添加 stretch
    - add_item 时调用 item.set_menu_mode(self._mode)（对 TMenuItemGroup）
    - _Requirements: 1.1, 1.3, 3.1, 4.1, 6.1, 6.2_

  - [x] 4.2 实现 TMenu 折叠模式：set_collapsed、_animate_collapse（QPropertyAnimation on minimumWidth + maximumWidth）
    - collapsed_width 从 Design Token menu.collapsed_width 获取
    - 递归调用所有子项的 set_collapsed_mode
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 4.3 实现 TMenu 禁用状态：set_disabled，递归调用子项 set_menu_disabled
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 4.4 实现 TMenu 路由感知：set_route、_find_matching_key（最长前缀匹配）、_collect_all_keys
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ]* 4.5 编写 Property 1 属性基测试：添加子项保持结构完整性并连接信号
    - **Property 1: 添加子项保持结构完整性并连接信号**
    - 生成随机菜单项列表，验证 items 列表完整且信号连接
    - **Validates: Requirements 1.1, 1.2, 1.3**

  - [ ]* 4.6 编写 Property 3 属性基测试：布局类型与 MenuMode 一致性
    - **Property 3: 布局类型与 MenuMode 一致性**
    - 生成随机 MenuMode，验证根布局类型匹配
    - **Validates: Requirements 3.1, 4.1**

  - [ ]* 4.7 编写 Property 8 属性基测试：set_active_key 精确激活唯一项
    - **Property 8: set_active_key 精确激活唯一项**
    - 生成随机菜单树和有效 key，验证仅该项 active
    - **Validates: Requirements 6.1, 6.2, 6.3**

  - [ ]* 4.8 编写 Property 4 属性基测试：折叠模式隐藏文字标签的往返一致性
    - **Property 4: 折叠模式隐藏文字标签的往返一致性**
    - 生成随机菜单树，collapse/uncollapse 验证文字标签可见性恢复
    - **Validates: Requirements 2.4, 5.2, 5.3, 5.4**

  - [ ]* 4.9 编写 Property 9-11 属性基测试：禁用状态相关
    - **Property 9: 禁用状态阻断交互**
    - **Property 10: disabled 状态递归传播**
    - **Property 11: disabled 往返保留项自身 disabled 状态**
    - **Validates: Requirements 6.4, 7.1, 7.2, 7.3, 7.4**

  - [ ]* 4.10 编写 Property 12-13 属性基测试：路由感知
    - **Property 12: 路由匹配使用最长前缀**
    - **Property 13: route_awareness 关闭时忽略 set_route**
    - **Validates: Requirements 8.1, 8.2, 8.3**

- [x] 5. Checkpoint - 确保垂直模式全部测试通过
  - 运行 `uv run pytest tests/test_organisms/test_menu.py -v`，确保所有测试通过，如有问题请告知用户。

- [x] 6. 实现水平模式弹出子菜单
  - [x] 6.1 在 TMenuItemGroup 中实现 set_menu_mode 方法和水平模式弹出逻辑
    - 添加 _menu_mode 字段，set_menu_mode 递归传播到子 TMenuItemGroup
    - 水平模式下：enterEvent 创建/显示 _popup QWidget，leaveEvent 启动 QTimer 延迟隐藏
    - 顶层 Group popup 定位在 Group 下方，嵌套 Group popup 定位在父 popup 右侧
    - 使用 Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
    - _Requirements: 3.2, 3.3, 3.4, 3.5_

  - [x] 6.2 在 TMenu.add_item 中添加 mode 传播逻辑：对 TMenuItemGroup 调用 set_menu_mode
    - _Requirements: 3.2_

  - [ ]* 6.3 编写单元测试：水平模式弹出窗口创建
    - 验证水平模式下 TMenuItemGroup 的 _popup 在 enterEvent 后被创建
    - _Requirements: 3.2, 3.3_

- [x] 7. 更新 QSS 模板
  - [x] 7.1 更新 menu.qss.j2 模板：确保包含水平模式 border-bottom 活跃指示、垂直模式 border-left 活跃指示、disabled 状态样式、popup 窗口样式
    - 所有颜色、间距、字号引用 Design Token
    - _Requirements: 9.1, 9.3, 9.4_

  - [ ]* 7.2 编写单元测试：验证 QSS 模板渲染正确性
    - 验证渲染后包含 border-bottom 和 border-left 规则
    - 验证包含 text_disabled 颜色引用
    - _Requirements: 9.1, 9.3, 9.4_

- [x] 8. 更新模块导出和集成
  - [x] 8.1 更新 organisms/__init__.py 导出 TMenu、TMenuItem、TMenuItemGroup
    - 确保现有导入路径兼容
    - _Requirements: 1.1_

- [x] 9. Final checkpoint - 确保所有测试通过
  - 运行 `uv run pytest tests/test_organisms/test_menu.py -v`，确保全部测试通过，如有问题请告知用户。

## Notes

- 标记 `*` 的任务为可选测试任务，可跳过以加速 MVP
- 组件文件：`src/tyto_ui_lib/components/organisms/menu.py`（替换现有文件）
- QSS 模板：`src/tyto_ui_lib/styles/templates/menu.qss.j2`（更新现有文件）
- 测试文件：`tests/test_organisms/test_menu.py`（替换现有文件）
- Property 测试使用 Hypothesis 库，每个属性至少 100 次迭代
- 所有代码注释和 Docstrings 使用英文
