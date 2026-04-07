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
