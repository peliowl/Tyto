# 版本需求
## v1.0.1
- [x] 修改specs中的requirement、task、design文档及其它相关文档，增加/修改V1.0.1版本需求：
  - 参考图片[v1.0.1_1.png](../../docs/image/reference/v1.0.1_1.png)，优化Gallery界面及逻辑，要求：
    - 左侧菜单栏显示原子、分子、有机体菜单项，及列举出对应的所有控件
    - 左侧选择控件后，右侧展示该控件所有的特性如基础用法、形状、尺寸、禁用等
    - 使用MVVM的思想，分模块维护Gallery的样式、逻辑等内容，保证可扩展性

- [x] 修改specs中的requirement、task、design文档及其它相关文档，增加/修改V1.0.1版本需求：
  - 修复v1.0.0版本中的bug：
    - Button控件
      - 不同type的按钮未显示出对应的边框效果和背景颜色
    - Input控件
      - 当设置clearable时，清空按钮直接在输入框外的右侧显示了（错误），应该显示在输入框内靠右边界处（正确）
    - Tag控件
      - 不同type的标签未显示出对应的边框效果和背景颜色
      - 标签未显示边框及背景颜色，导致无法查看标签的尺寸效果
      - 当设置closable时，点击标签的关闭按钮，无法将标签删除
    - SearchBar控件
      - 输入框的清空按钮位置显示错误（同Input控件的问题）
    - Message控件
      - 按钮未显示出对应的边框效果和背景颜色（同Button控件的问题）
      - 弹出的提示消息的显示位置不正确，应该显示在软件窗口的顶部水平居中位置
      - 弹出的提示消息无背景色和边框

- [x] 修改specs中的requirement、task、design文档及其它相关文档，增加/修改V1.0.1版本需求：
  - 修复"dark"模式下控件颜色显示异常问题，参考正确的效果图进行修复：
    - 在"dark"模式下，Button、Input、Switch、Tag、SearchBar等控件的背景色、文本颜色、边框颜色等颜色显示效果与参考图中效果不一致
    - 在"dark"模式下，Gallery界面中列表、列表项的背景、边框、文本等元素的颜色显示不正确
  - 正确的效果图：
    - "dark"模式下的Button参考图：[v1.0.1_1.png](../../docs/image/reference/v1.0.1_1.png)
    - "dark"模式下的Input参考图：[v1.0.1_2.png](../../docs/image/reference/v1.0.1_2.png)
    - "dark"模式下的Switch参考图：[v1.0.1_3.png](../../docs/image/reference/v1.0.1_3.png)
    - "dark"模式下的Tag参考图：[v1.0.1_4.png](../../docs/image/reference/v1.0.1_4.png)
    - "dark"模式下的SearchBar参考图：[v1.0.1_5.png](../../docs/image/reference/v1.0.1_5.png)
    - "dark"模式下的列表及列表项参考图：[v1.0.1_6.png](../../docs/image/reference/v1.0.1_6.png)
