# 实现计划：Tyto UI 组件库 V1.0.0

## 概述

基于原子设计方法论，自底向上实现 Tyto UI 组件库。从项目工程化配置和核心基础层开始，逐步构建原子组件、分子组件和有机体组件，最后完成组件预览画廊和包导出。每个阶段包含对应的属性基测试和单元测试任务。

## 任务

- [x] 1. 项目工程化配置
  - [x] 1.1 创建 pyproject.toml 配置文件
    - 配置 Setuptools 构建系统、项目元数据（name=tyto-ui-lib, version=1.0.0）
    - 配置 uv 依赖管理：PySide6、Jinja2 为核心依赖；pytest、pytest-qt、pytest-xdist、hypothesis、ruff、pyright 为开发依赖
    - 配置 Ruff（linting + formatting）、Pyright（类型检查）、pytest（testpaths、qt_api=pyside6）
    - _需求：14.1, 14.2, 14.3, 14.4_

  - [x] 1.2 创建项目目录结构和初始文件
    - 创建 src/tyto_ui_lib/ 及其子目录：core/、common/、common/traits/、components/atoms/、components/molecules/、components/organisms/、styles/、styles/templates/、styles/tokens/、utils/
    - 在每个包目录下创建 __init__.py
    - 创建 tests/ 目录及子目录：test_core/、test_common/、test_atoms/、test_molecules/、test_organisms/
    - 创建 tests/conftest.py，配置 QApplication fixture
    - _需求：14.1_

- [x] 2. Design Token 与主题引擎
  - [x] 2.1 实现 DesignTokenSet 数据模型和 Token 加载器
    - 在 src/tyto_ui_lib/core/tokens.py 中实现 DesignTokenSet dataclass
    - 实现 load_tokens_from_file(path) 函数，支持 JSON 文件加载
    - 实现 TokenFileError 自定义异常，包含错误位置描述
    - 实现 Token 验证逻辑：检查必需字段、类型校验
    - _需求：1.1, 1.6, 1.7_

  - [ ]* 2.2 编写 Token 加载的属性基测试
    - **属性 1：Token 完整性不变量**
    - **属性 2：Token 序列化 Round-Trip**
    - **属性 4：Token 文件错误处理**
    - **验证需求：1.1, 1.6, 1.7**

  - [x] 2.3 创建 Light 和 Dark 主题 Token 文件
    - 在 styles/tokens/light.json 中定义仿 NaiveUI 的 Light 主题 Token
    - 在 styles/tokens/dark.json 中定义仿 NaiveUI 的 Dark 主题 Token
    - 确保两套主题包含完全相同的 Token 键集合
    - _需求：1.1, 1.2_

  - [x] 2.4 实现 ThemeEngine 单例
    - 在 src/tyto_ui_lib/core/theme_engine.py 中实现 ThemeEngine
    - 实现 load_tokens()、switch_theme()、get_token()、current_theme()、render_qss() 方法
    - 集成 Jinja2 模板引擎，从 styles/templates/ 加载模板
    - 实现 theme_changed 信号
    - _需求：1.3, 1.4, 1.6_

  - [ ]* 2.5 编写 ThemeEngine 的属性基测试
    - **属性 3：QSS 渲染包含 Token 值**
    - **验证需求：1.4**

- [x] 3. 检查点 - 核心基础层验证
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 4. 组件基类与行为混入
  - [x] 4.1 实现 BaseWidget 基类
    - 在 src/tyto_ui_lib/common/base.py 中实现 BaseWidget
    - 实现 apply_theme()、_on_theme_changed()、cleanup() 方法
    - 在 __init__ 中自动连接 ThemeEngine.theme_changed 信号
    - 在 cleanup() 中断开信号连接
    - _需求：2.1, 2.2_

  - [ ]* 4.2 编写 BaseWidget 主题响应的属性基测试
    - **属性 5：主题切换自动更新组件样式**
    - **验证需求：2.2**

  - [x] 4.3 实现 Mixin 体系
    - 在 src/tyto_ui_lib/common/traits/ 下实现：
      - hover_effect.py：HoverEffectMixin（200ms 背景色渐变 + PointingHand 光标）
      - click_ripple.py：ClickRippleMixin（背景色加深 + Scale 0.98）
      - focus_glow.py：FocusGlowMixin（2px 半透明主色光晕）
      - disabled.py：DisabledMixin（0.5 透明度 + Forbidden 光标）
    - 确保各 Mixin 通过 super() 调用链支持多重继承
    - _需求：2.4, 2.5, 2.6, 2.7_

  - [ ]* 4.4 编写 Mixin 体系的属性基测试
    - **属性 6：HoverEffect 光标变化**
    - **属性 7：Disabled 状态属性**
    - **属性 8：多 Mixin 无冲突**
    - **验证需求：2.4, 2.7, 2.8**

- [x] 5. 原子组件 - Button 和 Checkbox
  - [x] 5.1 创建 Button QSS 模板并实现 TButton 组件
    - 在 styles/templates/button.qss.j2 中创建 Button 样式模板
    - 在 src/tyto_ui_lib/components/atoms/button.py 中实现 TButton
    - 支持 Primary/Default/Dashed/Text 四种类型
    - 实现 loading 状态（SVG 旋转动画 + 屏蔽点击）
    - 实现 disabled 状态（通过 DisabledMixin）
    - 混入 HoverEffectMixin、ClickRippleMixin、FocusGlowMixin
    - _需求：3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]* 5.2 编写 Button 的属性基测试
    - **属性 9：Button 类型正确性**
    - **属性 10：Loading 屏蔽点击**
    - **属性 11：Button 正常点击发射信号**
    - **验证需求：3.1, 3.2, 3.4, 3.5**

  - [x] 5.3 创建 Checkbox QSS 模板并实现 TCheckbox 组件
    - 在 styles/templates/checkbox.qss.j2 中创建 Checkbox 样式模板
    - 在 src/tyto_ui_lib/components/atoms/checkbox.py 中实现 TCheckbox
    - 支持 Checked/Unchecked/Indeterminate 三态
    - 实现状态切换动画
    - 实现 state_changed 信号
    - _需求：4.1, 4.2, 4.3, 4.4_

  - [ ]* 5.4 编写 Checkbox 的属性基测试
    - **属性 12：Checkbox 状态 Round-Trip**
    - **验证需求：4.1, 4.2**

- [x] 6. 原子组件 - Radio 和 Input
  - [x] 6.1 创建 Radio QSS 模板并实现 TRadio 和 TRadioGroup 组件
    - 在 styles/templates/radio.qss.j2 中创建 Radio 样式模板
    - 在 src/tyto_ui_lib/components/atoms/radio.py 中实现 TRadio 和 TRadioGroup
    - 实现圆环缩放动画
    - 实现 RadioGroup 互斥逻辑
    - 实现 toggled 和 selection_changed 信号
    - _需求：5.1, 5.2, 5.3, 5.4_

  - [ ]* 6.2 编写 Radio 的属性基测试
    - **属性 13：RadioGroup 互斥不变量**
    - **属性 14：RadioGroup 选择一致性**
    - **验证需求：5.2, 5.3, 5.4**

  - [x] 6.3 创建 Input QSS 模板并实现 TInput 组件
    - 在 styles/templates/input.qss.j2 中创建 Input 样式模板
    - 在 src/tyto_ui_lib/components/atoms/input.py 中实现 TInput
    - 实现前缀/后缀图标、clearable、password 模式
    - 实现 text_changed 和 cleared 信号
    - _需求：6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ]* 6.4 编写 Input 的属性基测试
    - **属性 15：Input 清空 Round-Trip**
    - **属性 16：Input 密码可见性 Toggle Round-Trip**
    - **属性 17：Input text_changed 信号**
    - **验证需求：6.2, 6.3, 6.5, 6.6**

- [x] 7. 原子组件 - Switch 和 Tag
  - [x] 7.1 创建 Switch QSS 模板并实现 TSwitch 组件
    - 在 styles/templates/switch.qss.j2 中创建 Switch 样式模板
    - 在 src/tyto_ui_lib/components/atoms/switch.py 中实现 TSwitch
    - 实现仿 iOS/NaiveUI 风格的滑块和轨道
    - 实现滑块位移与缩放动画
    - 实现 toggled 信号
    - _需求：7.1, 7.2, 7.3, 7.4_

  - [ ]* 7.2 编写 Switch 的属性基测试
    - **属性 18：Switch Toggle Round-Trip**
    - **验证需求：7.2, 7.3**

  - [x] 7.3 创建 Tag QSS 模板并实现 TTag 组件
    - 在 styles/templates/tag.qss.j2 中创建 Tag 样式模板
    - 在 src/tyto_ui_lib/components/atoms/tag.py 中实现 TTag
    - 支持 Small/Medium/Large 三种尺寸
    - 支持 Default/Primary/Success/Warning/Error 五种颜色类型
    - 实现 closable 和 closed 信号
    - _需求：8.1, 8.2, 8.3, 8.4_

  - [ ]* 7.4 编写 Tag 的属性基测试
    - **属性 19：Tag 属性正确性**
    - **属性 20：Tag closed 信号**
    - **验证需求：8.1, 8.3, 8.4**

- [x] 8. 检查点 - 原子组件验证
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 9. 分子组件
  - [x] 9.1 创建 SearchBar QSS 模板并实现 TSearchBar 组件
    - 在 styles/templates/searchbar.qss.j2 中创建 SearchBar 样式模板
    - 在 src/tyto_ui_lib/components/molecules/searchbar.py 中实现 TSearchBar
    - 组合 TInput + TButton
    - 实现 search_changed 和 search_submitted 信号
    - 支持 clearable 属性
    - _需求：9.1, 9.2, 9.3, 9.4_

  - [ ]* 9.2 编写 SearchBar 的属性基测试
    - **属性 21：SearchBar search_changed 信号**
    - **属性 22：SearchBar search_submitted 信号**
    - **验证需求：9.2, 9.3**

  - [x] 9.3 创建 Breadcrumb QSS 模板并实现 TBreadcrumb 组件
    - 在 styles/templates/breadcrumb.qss.j2 中创建 Breadcrumb 样式模板
    - 在 src/tyto_ui_lib/components/molecules/breadcrumb.py 中实现 TBreadcrumb 和 BreadcrumbItem
    - 实现路径项列表渲染、自定义分隔符
    - 实现 item_clicked 信号
    - 最后一项渲染为不可点击样式
    - _需求：10.1, 10.2, 10.3, 10.4_

  - [ ]* 9.4 编写 Breadcrumb 的属性基测试
    - **属性 23：Breadcrumb Items Round-Trip**
    - **属性 24：Breadcrumb item_clicked 信号**
    - **属性 25：Breadcrumb 最后一项不可点击**
    - **验证需求：10.1, 10.3, 10.4**

  - [x] 9.5 创建 InputGroup QSS 模板并实现 TInputGroup 组件
    - 在 styles/templates/inputgroup.qss.j2 中创建 InputGroup 样式模板
    - 在 src/tyto_ui_lib/components/molecules/inputgroup.py 中实现 TInputGroup
    - 实现子组件紧凑横向排列
    - 实现圆角自动合并逻辑（首尾保留外侧圆角，中间为零）
    - 实现动态重新计算（add/insert/remove 后自动更新）
    - _需求：11.1, 11.2, 11.3_

  - [ ]* 9.6 编写 InputGroup 的属性基测试
    - **属性 26：InputGroup 圆角合并不变量**
    - **验证需求：11.2, 11.3**

- [x] 10. 有机体组件
  - [x] 10.1 创建 Message QSS 模板并实现 TMessage 和 MessageManager
    - 在 styles/templates/message.qss.j2 中创建 Message 样式模板
    - 在 src/tyto_ui_lib/components/organisms/message.py 中实现 TMessage 和 MessageManager
    - 支持 Info/Success/Warning/Error 四种类型
    - 实现从顶部弹出动画和自动消失
    - 实现 MessageManager 单例管理消息堆叠
    - 实现 _update_positions() 堆叠位置计算
    - _需求：12.1, 12.2, 12.3, 12.4, 12.5_

  - [ ]* 10.2 编写 Message 的属性基测试
    - **属性 27：Message 类型正确性**
    - **属性 28：Message 堆叠不变量**
    - **验证需求：12.1, 12.4, 12.5**

  - [x] 10.3 创建 Modal QSS 模板并实现 TModal 组件
    - 在 styles/templates/modal.qss.j2 中创建 Modal 样式模板
    - 在 src/tyto_ui_lib/components/organisms/modal.py 中实现 TModal
    - 实现半透明遮罩层和缩放弹出动画
    - 支持自定义标题、内容和底部按钮区域
    - 实现 closable 和 mask_closable 属性控制
    - 实现 closed 信号
    - _需求：13.1, 13.2, 13.3, 13.4, 13.5_

  - [ ]* 10.4 编写 Modal 的属性基测试
    - **属性 29：Modal closed 信号**
    - **属性 30：Modal closable 属性控制**
    - **验证需求：13.4, 13.5**

- [x] 11. 检查点 - 全组件验证
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 12. 包导出与 Gallery
  - [x] 12.1 配置包导出
    - 在 src/tyto_ui_lib/__init__.py 中导出所有公开组件和核心 API
    - 导出列表：ThemeEngine、BaseWidget、所有 Mixin、所有组件类、所有枚举和数据类
    - 设置 __version__ = "1.0.0"
    - _需求：14.5_

  - [x] 12.2 实现组件预览 Gallery 应用
    - 在 examples/gallery.py 中创建独立的 PySide6 Gallery 应用
    - 实现主题切换按钮（Light/Dark）
    - 为每个组件创建独立展示区域，包含不同状态和配置的示例
    - _需求：15.1, 15.2, 15.3_

- [x] 13. 最终检查点 - 全部测试通过
  - 确保所有测试通过，如有问题请向用户确认。

## 备注

- 标记 `*` 的任务为可选任务，可跳过以加速 MVP 交付
- 每个任务引用了具体的需求编号以确保可追溯性
- 检查点任务确保增量验证
- 属性基测试使用 Hypothesis 框架，每个属性至少 100 次迭代
- 单元测试使用 pytest + pytest-qt 验证具体示例和边界情况


---

# 实现计划：Tyto UI 组件库 V1.0.1 - Gallery MVVM 重构

## 概述

将 Gallery 从单文件重构为 MVVM 架构的模块化结构。左侧导航菜单按原子/分子/有机体分类展示组件，右侧展示选中组件的所有特性。确保可扩展性：新增组件仅需添加 Showcase 并注册。

## 任务

- [x] 14. Gallery MVVM 基础架构
  - [x] 14.1 创建 Gallery 包目录结构
    - 创建 `examples/gallery/` 目录及子目录：models/、viewmodels/、views/、showcases/、styles/
    - 在每个子目录下创建 `__init__.py`
    - 创建 `examples/gallery/__main__.py` 支持模块化启动
    - _需求：16.1, 16.2, 16.3_

  - [x] 14.2 实现 Model 层 - ComponentInfo 和 ComponentRegistry
    - 在 `examples/gallery/models/component_info.py` 中实现 ComponentInfo dataclass
    - 在 `examples/gallery/models/component_registry.py` 中实现 ComponentRegistry
    - 实现 register()、get_by_key()、get_by_category()、categories()、all_components() 方法
    - _需求：16.4, 17.5_

  - [x] 14.3 实现 ViewModel 层 - GalleryViewModel
    - 在 `examples/gallery/viewmodels/gallery_viewmodel.py` 中实现 GalleryViewModel
    - 实现 select_component()、current_component_key()、toggle_theme() 方法
    - 实现 current_component_changed 和 theme_changed 信号
    - _需求：17.4, 18.1_

  - [x] 14.4 实现样式模块 - GalleryStyles
    - 在 `examples/gallery/styles/gallery_styles.py` 中实现 GalleryStyles
    - 提供 nav_menu_style()、top_bar_style()、showcase_section_title_style()、showcase_section_desc_style() 静态方法
    - 支持 light/dark 主题样式切换
    - _需求：19.2_

- [x] 15. Gallery View 层实现
  - [x] 15.1 实现 TopBar 视图
    - 在 `examples/gallery/views/top_bar.py` 中实现 TopBar
    - 包含标题 "Tyto UI Gallery" 和 TSwitch 主题切换开关
    - 连接 TSwitch.toggled 到 GalleryViewModel.toggle_theme()
    - _需求：19.1, 19.2_

  - [x] 15.2 实现 NavigationMenu 视图
    - 在 `examples/gallery/views/navigation_menu.py` 中实现 NavigationMenu
    - 从 ComponentRegistry 读取分类和组件列表，构建树形菜单
    - 显示三个一级分类：Atoms、Molecules、Organisms
    - 实现点击组件项时发射 component_selected 信号
    - 实现 set_active_item() 高亮当前选中项
    - _需求：17.1, 17.2, 17.3, 17.4, 17.5_

  - [x] 15.3 实现 ComponentShowcase 视图
    - 在 `examples/gallery/views/component_showcase.py` 中实现 ComponentShowcase
    - 继承 QScrollArea，支持垂直滚动
    - 实现 show_component(key) 方法，从 Registry 获取 showcase_factory 并创建展示面板
    - _需求：18.1, 18.5_

  - [x] 15.4 实现 GalleryWindow 主窗口
    - 在 `examples/gallery/views/gallery_window.py` 中实现 GalleryWindow
    - 组合 TopBar（顶部）、NavigationMenu（左侧）、ComponentShowcase（右侧）
    - 初始化 ComponentRegistry、GalleryViewModel，连接信号
    - _需求：16.1, 17.4, 18.1_

- [x] 16. Showcase 模块实现
  - [x] 16.1 实现 BaseShowcase 基类
    - 在 `examples/gallery/showcases/base_showcase.py` 中实现 BaseShowcase
    - 提供 add_section(title, description, content) 方法
    - 提供 hbox() 静态辅助方法
    - _需求：18.2, 18.4_

  - [x] 16.2 实现原子组件 Showcase
    - 实现 ButtonShowcase：基础用法、类型、加载状态、禁用状态
    - 实现 CheckboxShowcase：基础用法、三态展示
    - 实现 RadioShowcase：基础用法、分组互斥
    - 实现 InputShowcase：基础用法、可清空、密码模式
    - 实现 SwitchShowcase：基础用法、禁用状态
    - 实现 TagShowcase：基础用法、颜色类型、尺寸、可关闭
    - _需求：18.3_

  - [x] 16.3 实现分子和有机体组件 Showcase
    - 实现 SearchBarShowcase：基础用法、可清空
    - 实现 BreadcrumbShowcase：基础用法、自定义分隔符
    - 实现 InputGroupShowcase：基础用法
    - 实现 MessageShowcase：基础用法（触发各类型消息）
    - 实现 ModalShowcase：基础用法（打开/关闭对话框）
    - _需求：18.3_

  - [x] 16.4 实现组件注册和入口文件
    - 在 `examples/gallery/showcases/__init__.py` 中实现 register_all() 注册所有组件
    - 更新 `examples/gallery/__init__.py` 导出 main()
    - 更新 `examples/gallery.py` 入口文件委托给 gallery 包
    - _需求：16.3, 16.4_

- [x] 17. 检查点 - Gallery MVVM 验证
  - 手动运行 `uv run python examples/gallery.py` 验证 Gallery 功能
  - 验证左侧菜单分类展示、组件切换、右侧特性展示、主题切换

- [ ]* 18. Gallery 属性基测试
  - [ ]* 18.1 编写 ComponentRegistry 属性基测试
    - **属性 31：组件注册表完整性**
    - **属性 32：分类查询一致性**
    - **验证需求：16.4, 17.1, 17.2, 17.5**

  - [ ]* 18.2 编写 GalleryViewModel 属性基测试
    - **属性 33：ViewModel 组件切换信号**
    - **验证需求：17.4, 18.1**

## 备注

- 标记 `*` 的任务为可选任务
- V1.0.1 聚焦于 Gallery 重构，不涉及组件库核心代码变更
- 每个 Showcase 模块独立维护，新增组件仅需添加 Showcase 并在 register_all() 中注册


---

# 实现计划：Tyto UI 组件库 V1.0.1 - Bug 修复

## 概述

修复 V1.0.0 中发现的组件样式渲染和交互逻辑缺陷。按依赖关系排序：先修复基础组件（Button、Input、Tag），再验证依赖组件（SearchBar、Message）自动受益。

## 任务

- [x] 19. Bug 修复 - Button 类型样式
  - [x] 19.1 修复 TButton.apply_theme() 中 QSS 属性选择器未生效问题
    - 在 `src/tyto_ui_lib/components/atoms/button.py` 的 `apply_theme()` 方法中
    - 在 `self.setStyleSheet(qss)` 之后添加 `self.style().unpolish(self)` 和 `self.style().polish(self)`
    - 确保 `[buttonType="primary"]`、`[buttonType="dashed"]`、`[buttonType="text"]` 等 QSS 选择器立即生效
    - _需求：20.1, 20.2, 20.3, 20.4, 20.5_

  - [x] 19.2 编写 Button 类型样式修复的属性基测试
    - **属性 34：Button QSS 属性选择器生效**
    - 使用 Hypothesis 生成任意 ButtonType，验证创建 TButton 后 `property("buttonType")` 值正确
    - **验证需求：20.1, 20.2, 20.3, 20.4, 20.5**

- [x] 20. Bug 修复 - Input 清空按钮位置
  - [x] 20.1 重构 TInput 清空按钮为 QLineEdit 内部 action
    - 在 `src/tyto_ui_lib/components/atoms/input.py` 中
    - 将 `_clear_btn`（QToolButton）替换为 `QLineEdit.addAction(QAction, QLineEdit.ActionPosition.TrailingPosition)`
    - 当文本非空时显示清空 action，文本为空时隐藏
    - 点击清空 action 时调用 `_on_clear_clicked()` 清空文本并发射 `cleared` 信号
    - 同样将密码可见性切换按钮改为 QLineEdit 内部 action
    - 确保 `text_changed`、`cleared` 信号行为不变
    - _需求：21.1, 21.2, 21.3_

  - [x] 20.2 编写 Input 清空按钮位置修复的属性基测试
    - **属性 35：Input 清空按钮在 QLineEdit 内部**
    - 验证 clearable=True 的 TInput 的 QLineEdit 内部包含 trailing action
    - **验证需求：21.1, 21.2**

- [x] 21. Bug 修复 - Tag 样式与交互
  - [x] 21.1 修复 TTag.apply_theme() 中 QSS 属性选择器未生效问题
    - 在 `src/tyto_ui_lib/components/atoms/tag.py` 的 `apply_theme()` 方法中
    - 在 `self.setStyleSheet(qss)` 之后添加 `self.style().unpolish(self)` 和 `self.style().polish(self)`
    - 确保 `[tagType="primary"]`、`[tagType="success"]` 等 QSS 选择器立即生效
    - _需求：22.1, 22.2, 22.3, 22.4_

  - [x] 21.2 修复 TTag 关闭按钮无法隐藏标签的问题
    - 在 `src/tyto_ui_lib/components/atoms/tag.py` 中
    - 将关闭按钮的 `clicked` 连接改为先发射 `closed` 信号，再调用 `self.setVisible(False)`
    - _需求：22.5_

  - [x] 21.3 编写 Tag 修复的属性基测试
    - **属性 36：Tag QSS 属性选择器生效**
    - **属性 37：Tag 关闭按钮隐藏标签**
    - 使用 Hypothesis 生成任意 TagType，验证 QSS 属性选择器生效
    - 验证 closable=True 的 TTag 点击关闭按钮后 `isVisible()` 为 False
    - **验证需求：22.1, 22.2, 22.3, 22.4, 22.5**

- [x] 22. Bug 修复 - Message 组件综合修复
  - [x] 22.1 修复 TMessage 背景色和边框丢失问题
    - 在 `src/tyto_ui_lib/components/organisms/message.py` 中
    - 移除 `self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)` 或改用内部容器方案
    - 确保 QSS 中定义的 `background-color` 和 `border` 能正确渲染
    - 在 `apply_theme()` 中添加 `unpolish/polish` 确保 `[messageType="xxx"]` 选择器生效
    - _需求：24.2_

  - [x] 22.2 修复 MessageManager 消息弹出位置计算
    - 在 `src/tyto_ui_lib/components/organisms/message.py` 的 `_update_positions()` 方法中
    - 使用 `parent.mapToGlobal(QPoint(0, 0))` 获取 parent 窗口的全局坐标
    - 水平居中：`parent_global_x + (parent.width() - msg.width()) // 2`
    - 垂直位置：`parent_global_y + y_offset`
    - 确保消息始终相对于 parent 窗口顶部居中显示
    - _需求：24.1, 24.4_

  - [x] 22.3 编写 Message 修复的属性基测试
    - **属性 38：Message 窗口居中定位**
    - **属性 39：Message 背景色和边框可见**
    - **验证需求：24.1, 24.2, 24.4**

- [x] 23. Bug 修复验证 - SearchBar 和 Message 按钮
  - [x] 23.1 验证 SearchBar 清空按钮位置已修复
    - 确认 SearchBar 内部 TInput 的清空按钮已正确显示在输入框内部
    - 无需修改 `searchbar.py`，仅验证 TInput 修复后 SearchBar 自动受益
    - _需求：23.1, 23.2_

  - [x] 23.2 验证 Message 展示面板按钮样式已修复
    - 确认 MessageShowcase 中的 TButton 已正确显示对应的边框和背景颜色
    - 无需修改 `message_showcase.py`，仅验证 TButton 修复后自动受益
    - _需求：24.3_

- [x] 24. 检查点 - Bug 修复全部验证
  - 运行 `uv run pytest` 确保所有测试通过
  - 手动运行 `uv run python examples/gallery.py` 验证所有修复效果

## 备注

- Bug 5（SearchBar 清空按钮）和 Bug 6（Message 按钮样式）通过修复上游组件自动解决
- 任务 23 为验证性任务，不涉及代码修改
- 所有 QSS 模板文件无需修改，问题均在 Python 代码层


---

# 实现计划：Tyto UI 组件库 V1.0.1 - Dark 模式颜色修复

## 概述

修复 "dark" 模式下组件和 Gallery 界面元素的颜色显示异常。按依赖关系排序：先验证/修复 dark 主题 Token 值，再修复组件样式应用逻辑，最后修复 Gallery 界面元素。

## 任务

- [x] 25. Dark 模式修复 - Token 值验证与调整
  - [x] 25.1 对比参考图验证 dark.json Token 值
    - 对比参考图 `docs/image/reference/v1.0.1_1.png` 至 `v1.0.1_6.png`，验证 `styles/tokens/dark.json` 中的颜色值是否与 NaiveUI dark 主题一致
    - 如有偏差，调整 `dark.json` 中的 Token 值（如 `bg_default`、`bg_elevated`、`text_primary`、`border` 等）
    - 确保 dark 主题 Token 包含与 light 主题完全相同的键集合
    - _需求：25.1, 26.1, 27.1, 28.1_

- [x] 26. Dark 模式修复 - 组件样式应用
  - [x] 26.1 修复 TSwitch 主题切换时轨道未重绘问题
    - 在 `src/tyto_ui_lib/components/atoms/switch.py` 的 `apply_theme()` 方法中
    - 在现有 `setStyleSheet(qss)` 之后添加 `self._track.update()` 强制轨道重绘
    - 确保主题切换后轨道颜色立即更新为当前主题的 `colors.border`（未选中）或 `colors.primary`（已选中）
    - _需求：27.1, 27.2, 27.3_

  - [x] 26.2 验证 TInput dark 模式样式正确性
    - 确认 `src/tyto_ui_lib/components/atoms/input.py` 的 `apply_theme()` 在主题切换时被正确调用
    - 确认 `input.qss.j2` 模板中的 Token 变量在 dark 主题下渲染为正确的颜色值
    - 如需要，在 `input.qss.j2` 中添加占位符颜色规则（QLineEdit placeholder 使用 `colors.text_secondary`）
    - _需求：26.1, 26.2, 26.3, 26.4_

  - [x] 26.3 验证 TButton 和 TTag dark 模式样式正确性
    - 确认 TButton 和 TTag 使用全局 QSS + unpolish/polish 方式，dark 主题 Token 通过全局 QSS 自动生效
    - 如有问题，检查 `button.qss.j2` 和 `tag.qss.j2` 模板中的 Token 引用是否完整
    - _需求：25.1, 25.2, 25.3, 25.4, 25.5, 28.1, 28.2, 28.3_

  - [x] 26.4 验证 TSearchBar dark 模式样式正确性
    - 确认 SearchBar 内部的 TInput 和 TButton 在 dark 模式下自动受益于上游修复
    - 确认 `searchbar.qss.j2` 模板中无硬编码颜色值
    - _需求：29.1, 29.2_

- [x] 27. Dark 模式修复 - Gallery 界面
  - [x] 27.1 修复 GalleryWindow 主窗口 dark 模式背景色
    - 在 `examples/gallery/views/gallery_window.py` 中
    - 监听 `ThemeEngine.theme_changed` 信号，主题切换时更新主窗口背景色
    - 使用 `colors.bg_default` 作为主窗口背景色
    - _需求：30.6, 30.8_

  - [x] 27.2 修复 ComponentShowcase dark 模式背景色和硬编码颜色
    - 在 `examples/gallery/views/component_showcase.py` 中
    - 添加主题响应逻辑，监听 `ThemeEngine.theme_changed` 信号
    - 主题切换时更新 showcase 容器的背景色为 `colors.bg_default`
    - 移除 `_set_placeholder()` 中硬编码的 `color: #999`，改用 `colors.text_secondary` Token 值
    - _需求：30.6, 30.7_

  - [x] 27.3 添加 GalleryStyles 中 showcase 和主窗口的样式方法
    - 在 `examples/gallery/styles/gallery_styles.py` 中
    - 添加 `main_window_style(theme)` 静态方法，返回主窗口的 dark/light 主题 QSS
    - 添加 `showcase_panel_style(theme)` 静态方法，返回 showcase 面板的 dark/light 主题 QSS
    - 确保所有颜色值从 Token 获取，不硬编码
    - _需求：30.1, 30.5, 30.6_

  - [x] 27.4 验证 NavigationMenu 和 TopBar dark 模式样式
    - 确认 `GalleryStyles.nav_menu_style()` 和 `GalleryStyles.top_bar_style()` 在 dark 主题下返回正确的颜色值
    - 确认 NavigationMenu 的分类标题、列表项、选中项在 dark 模式下颜色正确
    - 确认 TopBar 的背景色和标题文本颜色在 dark 模式下正确
    - _需求：30.1, 30.2, 30.3, 30.4, 30.5_

- [x] 28. Dark 模式修复 - 属性基测试
  - [x] 28.1 编写组件 Dark 模式颜色一致性属性基测试
    - **属性 40：组件 Dark 模式颜色一致性**
    - 使用 Hypothesis 生成任意主题名称（light/dark），验证切换后 `ThemeEngine.get_token()` 返回值与 Token 文件一致
    - **验证需求：25.5, 26.4, 27.3, 28.3, 29.1**

  - [x] 28.2 编写 Switch 轨道重绘属性基测试
    - **属性 41：Switch 轨道重绘响应主题切换**
    - 验证 TSwitch 主题切换后 `_track.update()` 被调用
    - **验证需求：27.1, 27.2, 27.3**

  - [x] 28.3 编写 Gallery 界面 Dark 模式背景色属性基测试
    - **属性 42：Gallery 界面 Dark 模式背景色**
    - 验证 Gallery 界面元素在主题切换后的背景色与 Token 值一致
    - **验证需求：30.1, 30.5, 30.6, 30.8**

- [ ] 29. 检查点 - Dark 模式修复全部验证
  - 运行 `uv run pytest` 确保所有测试通过
  - 手动运行 `uv run python examples/gallery.py` 验证 dark 模式下所有组件和 Gallery 界面的颜色效果
  - 对比参考效果图确认修复结果

## 备注

- 任务 25 为前置验证任务，确保 Token 值正确后再修复代码
- TButton 和 TTag 已使用全局 QSS + unpolish/polish 方式，dark 模式下应自动生效，任务 26.3 为验证性任务
- TSearchBar 的 dark 模式修复自动受益于 TInput 和 TButton 的修复，任务 26.4 为验证性任务
- 所有修复以参考效果图为最终验收标准


---

# 实现计划：Tyto UI 组件库 V1.0.2 - 原子组件特性增强

## 概述

在现有原子组件基础上扩展属性和变体，新增 TCheckboxGroup 和 TRadioButton 子组件。按依赖关系排序：先扩展 Design Token，再逐个增强原子组件，最后更新 Gallery Showcase 和编写测试。

## 任务

- [x] 30. Token 扩展 - 尺寸变体和新增颜色
  - [x] 30.1 扩展 light.json 和 dark.json Token 文件
    - 在 `src/tyto_ui_lib/styles/tokens/light.json` 和 `dark.json` 中新增 `component_sizes` 节点（tiny/small/medium/large 的 height、padding_h、font_size、icon_size）
    - 新增 `switch_sizes` 节点（small/medium/large 的 width、height、thumb）
    - 新增 `colors.info`、`colors.info_hover`、`colors.info_pressed` 颜色值
    - 确保 light 和 dark 两套主题包含完全相同的新增键集合
    - _需求：31.1, 32.1, 33.1, 34.1, 35.1, 36.2_

  - [x] 30.2 更新 ThemeEngine 和 DesignTokenSet 以支持新增 Token 结构
    - 确保 `ThemeEngine.render_qss()` 能将 `component_sizes` 和 `switch_sizes` 传递给 Jinja2 模板上下文
    - 如需要，扩展 `DesignTokenSet` dataclass 以包含新增字段
    - _需求：31.1, 35.1_

- [x] 31. TButton 特性增强
  - [x] 31.1 扩展 TButton 类 - 新增属性和枚举
    - 在 `src/tyto_ui_lib/components/atoms/button.py` 中
    - 扩展 `ButtonType` 枚举新增 TERTIARY / INFO / SUCCESS / WARNING / ERROR
    - 新增 `ButtonSize` 枚举（TINY / SMALL / MEDIUM / LARGE）
    - 新增 `IconPlacement` 枚举（LEFT / RIGHT）和 `AttrType` 枚举（BUTTON / SUBMIT / RESET）
    - 扩展 `__init__` 参数：size、circle、round、ghost、secondary、tertiary、quaternary、strong、block、color、text_color、bordered、icon、icon_placement、attr_type、focusable
    - 实现各属性的 setter 方法，每个 setter 更新 QSS 动态属性并调用 unpolish/polish
    - 实现 icon 布局逻辑（icon_placement 控制图标在文字左侧或右侧）
    - 实现 block 模式（设置 sizePolicy 水平策略为 Expanding）
    - 实现 circle 模式（设置固定宽高相等 + 圆形 border-radius）
    - _需求：31.1 - 31.15_

  - [x] 31.2 扩展 button.qss.j2 模板
    - 新增尺寸变体选择器（`[size="tiny"]`、`[size="small"]` 等）
    - 新增类型变体选择器（`[buttonType="info"]`、`[buttonType="success"]` 等）
    - 新增 ghost 变体选择器（`[ghost="true"]` 组合各 buttonType）
    - 新增 round 变体选择器（`[round="true"]`）
    - 新增 block 变体选择器（`[block="true"]`）
    - 新增 bordered=false 选择器（`[bordered="false"]`）
    - 新增 strong 选择器（`[strong="true"]`）
    - _需求：31.1 - 31.12_

  - [x] 31.3 编写 TButton 增强特性的属性基测试
    - **属性 43：Button 尺寸变体正确性**
    - **属性 44：Button 扩展类型正确性**
    - **属性 45：Button Ghost 样式不变量**
    - **属性 46：Button Block 宽度不变量**
    - **验证需求：31.1, 31.2, 31.5, 31.8**

- [x] 32. TInput 特性增强
  - [x] 32.1 扩展 TInput 类 - 新增属性和 Textarea 模式
    - 在 `src/tyto_ui_lib/components/atoms/input.py` 中
    - 新增 `InputType` 枚举（TEXT / TEXTAREA / PASSWORD）、`InputSize` 枚举、`InputStatus` 枚举
    - 扩展 `__init__` 参数：input_type、size、round、bordered、maxlength、minlength、show_count、readonly、autosize、rows、loading、status、resizable、show_password_on
    - 实现 Textarea 模式：当 input_type=TEXTAREA 时使用 QPlainTextEdit 替代 QLineEdit
    - 实现 maxlength 约束（QLineEdit.setMaxLength 或 QPlainTextEdit 文本过滤）
    - 实现 show_count 字数统计显示
    - 实现 autosize 自适应高度逻辑
    - 实现 status 验证状态边框颜色
    - 实现 loading 加载动画
    - _需求：32.1 - 32.15_

  - [x] 32.2 扩展 input.qss.j2 模板
    - 新增尺寸变体选择器
    - 新增 round 变体选择器
    - 新增 bordered=false 选择器
    - 新增 status 变体选择器（`[status="success"]`、`[status="warning"]`、`[status="error"]`）
    - 新增 textarea 模式样式规则
    - _需求：32.1, 32.4, 32.5, 32.13_

  - [x] 32.3 编写 TInput 增强特性的属性基测试
    - **属性 47：Input 尺寸变体正确性**
    - **属性 48：Input Textarea 模式切换**
    - **属性 49：Input Maxlength 约束**
    - **属性 50：Input Status 边框颜色**
    - **验证需求：32.1, 32.2, 32.3, 32.6, 32.13**

- [x] 33. TCheckbox 特性增强 + TCheckboxGroup
  - [x] 33.1 扩展 TCheckbox 类 - 新增属性
    - 在 `src/tyto_ui_lib/components/atoms/checkbox.py` 中
    - 新增 `CheckboxSize` 枚举（SMALL / MEDIUM / LARGE）
    - 扩展 `__init__` 参数：size、disabled、value、focusable、checked_value、unchecked_value、default_checked
    - 实现 disabled 状态（降低透明度 + Forbidden 光标 + 屏蔽交互）
    - 实现尺寸变体（调整 indicator 和 label 的大小）
    - 实现 value 属性用于 CheckboxGroup 标识
    - _需求：33.1 - 33.6_

  - [x] 33.2 实现 TCheckboxGroup 组件
    - 在 `src/tyto_ui_lib/components/atoms/checkbox.py` 中新增 TCheckboxGroup 类
    - 实现 add_checkbox()、get_value()、set_value() 方法
    - 实现 min/max 选中数量约束逻辑
    - 实现 size 统一设置和 disabled 统一禁用
    - 实现 value_changed 信号
    - _需求：33.7 - 33.10_

  - [x] 33.3 扩展 checkbox.qss.j2 模板
    - 新增尺寸变体选择器
    - 新增 disabled 样式规则
    - _需求：33.1, 33.2_

  - [x] 33.4 编写 TCheckbox/TCheckboxGroup 增强特性的属性基测试
    - **属性 51：Checkbox 尺寸变体正确性**
    - **属性 52：Checkbox Disabled 状态**
    - **属性 53：CheckboxGroup 选中数量约束**
    - **属性 54：CheckboxGroup value 一致性**
    - **验证需求：33.1, 33.2, 33.7, 33.8**

- [x] 34. TRadio 特性增强 + TRadioButton
  - [x] 34.1 扩展 TRadio 类 - 新增属性
    - 在 `src/tyto_ui_lib/components/atoms/radio.py` 中
    - 新增 `RadioSize` 枚举（SMALL / MEDIUM / LARGE）
    - 扩展 `__init__` 参数：size、disabled、name
    - 实现 disabled 状态
    - 实现尺寸变体
    - _需求：34.1 - 34.3_

  - [x] 34.2 实现 TRadioButton 组件
    - 在 `src/tyto_ui_lib/components/atoms/radio.py` 中新增 TRadioButton 类
    - 继承 BaseWidget，实现按钮样式的单选交互
    - 实现 toggled 信号、is_checked()、set_checked() 方法
    - 创建 `radiobutton.qss.j2` 模板
    - _需求：34.4_

  - [x] 34.3 扩展 TRadioGroup - 新增属性和按钮模式
    - 扩展 `__init__` 参数：name、size、disabled、default_value
    - 实现 `add_radio()` 支持 TRadio 和 TRadioButton 两种类型
    - 实现按钮模式检测（is_button_mode）和布局切换（水平紧凑排列）
    - 实现 set_disabled() 和 set_size() 统一控制
    - _需求：34.5 - 34.9_

  - [x] 34.4 扩展 radio.qss.j2 模板
    - 新增尺寸变体选择器
    - 新增 disabled 样式规则
    - _需求：34.1, 34.2_

  - [x] 34.5 编写 TRadio/TRadioButton 增强特性的属性基测试
    - **属性 55：Radio 尺寸变体正确性**
    - **属性 56：Radio Disabled 状态**
    - **属性 57：RadioButton 互斥不变量**
    - **验证需求：34.1, 34.2, 34.4, 34.9**

- [x] 35. TSwitch 特性增强
  - [x] 35.1 扩展 TSwitch 类 - 新增属性
    - 在 `src/tyto_ui_lib/components/atoms/switch.py` 中
    - 新增 `SwitchSize` 枚举（SMALL / MEDIUM / LARGE）
    - 扩展 `__init__` 参数：size、loading、round、checked_value、unchecked_value、rubber_band、checked_text、unchecked_text
    - 实现尺寸变体（根据 switch_sizes Token 调整轨道和滑块尺寸）
    - 实现 loading 状态（滑块上显示旋转动画 + 屏蔽交互）
    - 实现 round=False 方形轨道模式
    - 实现 checked_value/unchecked_value 自定义值和 get_typed_value()
    - 实现 rubber_band 橡皮筋回弹效果
    - 实现 checked_text/unchecked_text 轨道内文字显示
    - _需求：35.1 - 35.6_

  - [x] 35.2 扩展 switch.qss.j2 模板
    - 新增尺寸变体样式规则
    - 新增 round=false 方形轨道样式
    - _需求：35.1, 35.3_

  - [x] 35.3 编写 TSwitch 增强特性的属性基测试
    - **属性 58：Switch 尺寸变体正确性**
    - **属性 59：Switch Loading 屏蔽交互**
    - **属性 60：Switch 自定义值 Round-Trip**
    - **验证需求：35.1, 35.2, 35.4**

- [x] 36. TTag 特性增强
  - [x] 36.1 扩展 TTag 类 - 新增属性和枚举
    - 在 `src/tyto_ui_lib/components/atoms/tag.py` 中
    - 扩展 `TagType` 枚举新增 INFO
    - 扩展 `TagSize` 枚举新增 TINY
    - 扩展 `__init__` 参数：round、disabled、bordered、color、checkable、checked、strong
    - 新增 `checked_changed` 信号
    - 实现 checkable 模式（点击切换选中/未选中状态）
    - 实现 disabled 状态
    - 实现自定义 color dict 覆盖类型预设
    - 实现 round、bordered、strong 样式变体
    - _需求：36.1 - 36.9_

  - [x] 36.2 扩展 tag.qss.j2 模板
    - 新增 info 类型选择器（`[tagType="info"]`）
    - 新增 tiny 尺寸选择器（`[tagSize="tiny"]`）
    - 新增 round 变体选择器
    - 新增 bordered=false 选择器
    - 新增 strong 选择器
    - 新增 checkable 选中/未选中样式
    - 新增 disabled 样式规则
    - _需求：36.1 - 36.9_

  - [x] 36.3 编写 TTag 增强特性的属性基测试
    - **属性 61：Tag Info 类型正确性**
    - **属性 62：Tag Tiny 尺寸正确性**
    - **属性 63：Tag Checkable Toggle Round-Trip**
    - **属性 64：Tag 自定义颜色覆盖**
    - **验证需求：36.1, 36.2, 36.6, 36.7, 36.8**

- [x] 37. Gallery Showcase 同步更新
  - [x] 37.1 更新 ButtonShowcase
    - 在 `examples/gallery/showcases/button_showcase.py` 中
    - 新增展示区块：尺寸变体、圆形/圆角按钮、幽灵按钮、块级按钮、图标按钮、新增类型变体
    - _需求：37.1_

  - [x] 37.2 更新 InputShowcase
    - 在 `examples/gallery/showcases/input_showcase.py` 中
    - 新增展示区块：尺寸变体、Textarea 模式、字数统计、验证状态、圆角输入框
    - _需求：37.2_

  - [x] 37.3 更新 CheckboxShowcase
    - 在 `examples/gallery/showcases/checkbox_showcase.py` 中
    - 新增展示区块：尺寸变体、禁用状态、CheckboxGroup 示例
    - _需求：37.3_

  - [x] 37.4 更新 RadioShowcase
    - 在 `examples/gallery/showcases/radio_showcase.py` 中
    - 新增展示区块：尺寸变体、禁用状态、RadioButton 按钮组示例
    - _需求：37.4_

  - [x] 37.5 更新 SwitchShowcase
    - 在 `examples/gallery/showcases/switch_showcase.py` 中
    - 新增展示区块：尺寸变体、加载状态、方形开关、轨道文字
    - _需求：37.5_

  - [x] 37.6 更新 TagShowcase
    - 在 `examples/gallery/showcases/tag_showcase.py` 中
    - 新增展示区块：Tiny 尺寸、Info 类型、圆角标签、可选中标签、自定义颜色
    - _需求：37.6_

  - [x] 37.7 更新组件注册表
    - 确保 `examples/gallery/showcases/__init__.py` 中的 `register_all()` 无需修改（现有注册已覆盖）
    - 如新增了独立组件（如 TCheckboxGroup 作为独立展示），在注册表中添加
    - _需求：37.3, 37.4_

- [x] 38. 检查点 - V1.0.2 全部验证
  - 运行 `uv run pytest` 确保所有测试通过
  - 手动运行 `uv run python examples/gallery.py` 验证所有新增特性的展示效果
  - 验证 light/dark 主题下新增特性的颜色正确性

## 备注

- 任务 30 为前置任务，所有组件增强依赖 Token 扩展
- 任务 31-36 可按任意顺序实现，彼此无依赖
- 任务 37（Gallery 更新）依赖对应组件增强任务完成
- 所有新增属性通过 QSS 动态属性选择器驱动样式，保持与 V1.0.0/V1.0.1 一致的架构模式
- 属性基测试使用 Hypothesis 框架，每个属性至少 100 次迭代


---

# 实现计划：Tyto UI 组件库 V1.0.2 - Playground 交互式调试应用

## 概述

新增 Playground 交互式调试应用，采用与 Gallery 一致的 MVVM 架构。三栏布局：左侧导航菜单、中部组件预览、右侧属性面板。通过声明式 PropertyDefinition 驱动属性面板生成，支持 Light/Dark 主题切换。

## 任务

- [x] 39. Playground 基础架构
  - [x] 39.1 创建 Playground 包目录结构
    - 创建 `examples/playground/` 目录及子目录：models/、viewmodels/、views/、definitions/、styles/
    - 在每个子目录下创建 `__init__.py`
    - 创建 `examples/playground/__main__.py` 支持模块化启动
    - 创建 `examples/playground.py` 入口文件
    - _需求：38.1_

  - [x] 39.2 实现 Model 层 - PropertyDefinition 和 PropertyRegistry
    - 在 `examples/playground/models/property_definition.py` 中实现 PropertyDefinition dataclass
    - 在 `examples/playground/models/property_registry.py` 中实现 PropertyRegistry
    - 实现 register()、get_definitions()、register_factory()、get_factory() 方法
    - _需求：42.1, 42.4_

  - [x] 39.3 实现 ViewModel 层 - PlaygroundViewModel
    - 在 `examples/playground/viewmodels/playground_viewmodel.py` 中实现 PlaygroundViewModel
    - 实现 select_component()、current_component_key()、update_property()、toggle_theme() 方法
    - 实现 current_component_changed、property_changed、theme_changed 信号
    - _需求：38.2, 39.3, 40.3_

  - [x] 39.4 实现样式模块 - PlaygroundStyles
    - 在 `examples/playground/styles/playground_styles.py` 中实现 PlaygroundStyles
    - 提供 nav_menu_style()、top_bar_style()、main_window_style()、property_panel_style()、preview_panel_style()、property_row_style() 静态方法
    - 复用 GalleryStyles 的 Token 读取模式，支持 light/dark 主题
    - _需求：43.2_

- [x] 40. Playground View 层实现
  - [x] 40.1 实现 TopBar 视图
    - 在 `examples/playground/views/top_bar.py` 中实现 TopBar
    - 包含标题 "Tyto UI Playground" 和 TSwitch 主题切换开关
    - 连接 TSwitch.toggled 到 PlaygroundViewModel.toggle_theme()
    - _需求：38.4, 43.1_

  - [x] 40.2 实现 NavigationMenu 视图
    - 在 `examples/playground/views/navigation_menu.py` 中实现 NavigationMenu
    - 从 ComponentRegistry 读取分类和组件列表，构建树形菜单
    - 显示三个一级分类：Atoms、Molecules、Organisms
    - 实现点击组件项时发射 component_selected 信号
    - 实现 set_active_item() 高亮当前选中项
    - _需求：39.1, 39.2, 39.3, 39.4_

  - [x] 40.3 实现 ComponentPreview 视图
    - 在 `examples/playground/views/component_preview.py` 中实现 ComponentPreview
    - 继承 QScrollArea，支持垂直滚动
    - 实现 show_component(key) 方法，从 PropertyRegistry 获取工厂创建默认组件实例
    - 实现 update_property(name, value) 方法，查找对应 PropertyDefinition 的 apply 回调并执行
    - _需求：40.1, 40.2, 40.3, 40.4_

  - [x] 40.4 实现 PropertyPanel 视图
    - 在 `examples/playground/views/property_panel.py` 中实现 PropertyPanel
    - 继承 QScrollArea，支持垂直滚动
    - 实现 load_properties(key) 方法，从 PropertyRegistry 获取属性定义并动态生成编辑控件
    - 实现 _create_editor(prop_def) 方法：
      - enum → QComboBox（填充 options）
      - bool → QCheckBox
      - str → QLineEdit
      - int → QSpinBox
      - color → QLineEdit（支持 hex 格式）
    - 编辑控件值变化时发射 property_value_changed 信号
    - _需求：41.1, 41.2, 41.3, 41.4, 41.5, 41.6_

  - [x] 40.5 实现 PlaygroundWindow 主窗口
    - 在 `examples/playground/views/playground_window.py` 中实现 PlaygroundWindow
    - 组合 TopBar（顶部）、NavigationMenu（左侧）、ComponentPreview（中部）、PropertyPanel（右侧）
    - 初始化 ComponentRegistry、PropertyRegistry、PlaygroundViewModel，连接信号
    - 信号连接：Nav → VM → Preview + Nav + Props；Props → VM → Preview
    - _需求：38.3, 38.5_

- [x] 41. Playground 属性定义注册
  - [x] 41.1 实现原子组件属性定义
    - 在 `examples/playground/definitions/button_props.py` 中定义 TButton 属性：text、button_type、size、loading、disabled、circle、round、ghost、strong、block、bordered、color、text_color
    - 在 `examples/playground/definitions/input_props.py` 中定义 TInput 属性：placeholder、input_type、size、clearable、password、round、bordered、maxlength、show_count、readonly、loading、status
    - 在 `examples/playground/definitions/checkbox_props.py` 中定义 TCheckbox 属性：label、size、disabled、default_checked
    - 在 `examples/playground/definitions/radio_props.py` 中定义 TRadio 属性：label、size、disabled
    - 在 `examples/playground/definitions/switch_props.py` 中定义 TSwitch 属性：size、disabled、loading、round、checked_text、unchecked_text
    - 在 `examples/playground/definitions/tag_props.py` 中定义 TTag 属性：text、tag_type、size、closable、round、disabled、bordered、checkable、strong
    - _需求：42.2_

  - [x] 41.2 实现分子组件属性定义
    - 在 `examples/playground/definitions/searchbar_props.py` 中定义 TSearchBar 属性：placeholder、clearable
    - 在 `examples/playground/definitions/breadcrumb_props.py` 中定义 TBreadcrumb 属性：separator
    - _需求：42.3_

  - [x] 41.3 实现组件注册和入口文件
    - 在 `examples/playground/definitions/__init__.py` 中实现 register_all_properties() 注册所有属性定义
    - 在 `examples/playground/__init__.py` 中实现 main() 函数，复用 Gallery 的 ComponentRegistry 注册逻辑
    - 更新 `examples/playground.py` 入口文件委托给 playground 包
    - _需求：38.1, 38.5_

- [x] 42. 检查点 - Playground 功能验证
  - 手动运行 `uv run python examples/playground.py` 验证 Playground 功能
  - 验证左侧菜单分类展示、组件切换、中部预览、右侧属性面板、属性实时更新、主题切换

- [ ]* 43. Playground 属性基测试
  - [ ]* 43.1 编写 PropertyRegistry 属性基测试
    - **属性 65：PropertyRegistry 注册与查询一致性**
    - **验证需求：42.1**

  - [ ]* 43.2 编写 PropertyPanel 编辑器类型匹配单元测试
    - **属性 66：PropertyPanel 编辑器类型匹配**
    - **验证需求：41.2**

  - [ ]* 43.3 编写属性变更信号传播单元测试
    - **属性 67：属性变更信号传播**
    - **验证需求：40.3, 41.3**

## 备注

- 标记 `*` 的任务为可选任务
- Playground 复用 Gallery 的 ComponentRegistry 和 ComponentInfo 模型，不重复实现
- 每个组件的属性定义独立维护，新增组件仅需添加 `xxx_props.py` 并在 `register_all_properties()` 中注册
- View 层的视觉效果通过手动运行验证
- Playground 的样式模块复用 GalleryStyles 的 Token 读取模式
