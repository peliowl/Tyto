- [x] 执行命令`uv run python examples/gallery.py`抛出异常：uv : 无法将"uv"项识别为 cmdlet、函数、脚本文件或可运行程序的名称。请检查名称的拼写，如果包括路径，请确保路径正确，然后再试一次。
所在位置 行:1 字符: 1
+ uv run python examples/gallery.py
+ ~~
    + CategoryInfo          : ObjectNotFound: (uv:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

- [x] 修复bug：运行gallery程序，点击Tag菜单项时，抛出异常：
  AttributeError: 'TTag' object has no attribute '_color'. Did you mean: 'set_color'?
  Traceback (most recent call last):
    File "D:\Working\Me\Tyto\examples\gallery\views\component_showcase.py", line 63, in show_component
      showcase = info.showcase_factory(container)
    File "D:\Working\Me\Tyto\examples\gallery\showcases\__init__.py", line 50, in <lambda>
      showcase_factory=lambda parent: TagShowcase(parent)))
                                      ~~~~~~~~~~~^^^^^^^^
    File "D:\Working\Me\Tyto\examples\gallery\showcases\tag_showcase.py", line 28, in __init__
      self.hbox(TTag("Tag")),
                ~~~~^^^^^^^
    File "D:\Working\Me\Tyto\src\tyto_ui_lib\components\atoms\tag.py", line 84, in __init__
      super().__init__(parent)
      ~~~~~~~~~~~~~~~~^^^^^^^^
    File "D:\Working\Me\Tyto\src\tyto_ui_lib\common\base.py", line 40, in __init__
      self.apply_theme()
      ~~~~~~~~~~~~~~~~^^
    File "D:\Working\Me\Tyto\src\tyto_ui_lib\components\atoms\tag.py", line 343, in apply_theme
      if self._color:
         ^^^^^^^^^^^
    AttributeError: 'TTag' object has no attribute '_color'. Did you mean: 'set_color'?

- [x] 修复bug，在galler中，发现Button控件有以下异常：
  - 不同size的按钮，界面上显示的尺寸完全相同
  - circle和round不生效，按钮直接显示为方形按钮
  - Icon Button不生效，按钮中文本左侧或右侧没有显示出图标

- 修复bug，在gallery中，发现Button控件有以下异常：
  - circle和round的按钮，曲线边缘处显示有明显的锯齿
  - round按钮的文本左右侧没有留出适当的空间，导致文本接触到了按钮的左右边界

- [x] 修复bug：在gallery中，发现CheckBox控件有以下异常：
  - light模式下，checkbox无法看清文本前的图标，无法判断选中状态
  - dark模式下，checkbox的文本颜色几乎与背景色相同，导致无法看清文本

- [x] 修复bug：在gallery界面中，发现控件显示有以下异常：
  - 上下滚动界面时，如果被鼠标划过，控件会隐形或者固定显示在原处
  - 在不同控件演示界面中，都出现有部分控件的下边界被遮挡的现象

- [x] 修复bug：在gallery中，发现Radio控件有以下异常：
  - light模式下，Radio无法看清文本前的空状态
  - dark模式下，Radio的文本颜色几乎与背景色相同，导致无法看清文本

- [x] 修复bug：在gallery中，发现Input控件有以下异常：
  - textarea模式下，在textarea初始空文本状态时输入中文，输入字母过程中placeholder依然显示
  - 设置round的input控件，边框依然显示为方形，round效果未生效

- [x] 修复bug：在gallery中，发现Input控件有以下异常：
  - 在设置closable、checkable时，标签的文本（+按钮）左右侧没有留出适当的空间，导致文本（+按钮）接触到了标签的左右边界

- [x] 修复bug：在gallery中，发现Button控件有以下异常：
  - 在dark模式下，按钮的文本颜色没有显示为白色，与其它控件的dark模式表现不一致
  - 演示界面中，有部分按钮的下边框被遮挡，按钮未完全显示出来

- [x] 修复bug：在playground中，发现控件有以下异常：
  - switch控件：
    - 在属性设置面板中，有多余的属性设置项（如图红框中的内容）
  - tag控件：
    - 设置closable属性不生效
    - 设置round属性不生效
    - 设置size属性时，标签的高度未发生变化
    - 设置checkable属性不生效
    - 设置strong属性不生效

- [x] 运行playground，点击菜单项'timeline'抛出异常：
  Failed to create component instance for 'timeline'
  Traceback (most recent call last):

  File "D:\Working\Me\Tyto\examples\playground\views\component_preview.py", line 67, in show_component

    widget = factory()

  File "D:\Working\Me\Tyto\examples\playground\definitions\timeline_props.py", line 18, in _make_timeline

    tl.add_item(TTimelineItem(title="Step 1", content="First step"))

                ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "D:\Working\Me\Tyto\src\tyto_ui_lib\components\molecules\timeline.py", line 86, in __init__

    super().__init__(parent)

    ~~~~~~~~~~~~~~~~^^^^^^^^

  File "D:\Working\Me\Tyto\src\tyto_ui_lib\common\base.py", line 40, in __init__

    self.apply_theme()

    ~~~~~~~~~~~~~~~~^^

  File "D:\Working\Me\Tyto\src\tyto_ui_lib\components\molecules\timeline.py", line 296, in apply_theme

    self._apply_dot_color()

    ~~~~~~~~~~~~~~~~~~~~~^^

  File "D:\Working\Me\Tyto\src\tyto_ui_lib\components\molecules\timeline.py", line 313, in _apply_dot_color

    self._dot_label.setStyleSheet(

    ^^^^^^^^^^^^^^^

  AttributeError: 'TTimelineItem' object has no attribute '_dot_label'

- [x] 修复bug：在playground中，发现控件有以下异常：
  - inputNumber控件：
    - 设置size属性不生效；高度显示过大
    - 样式显示错误1：数字输入框与'+'按钮、'-'按钮之间显示了边框，正确效果是边界交接处不显示边框
    - 样式显示错误2：在鼠标hover或者获得焦点时，数字输入框、'+'按钮、'-'按钮分别显示了边框颜色，正确效果是只变化整个控件的外侧边框颜色
  - Slider控件：
    - 数字没有固定显示在滑块上方的位置：数字显示的位置随着鼠标在y轴上变化而变化了（错误）
    - dark模式下，数字颜色显示不正确：数字颜色错误显示为黑色
    - 设置tooltip、step属性不生效
  - Spin控件：
    - 设置size属性不生效
    - 设置Animation Type属性不生效
    - 设置description属性不生效    
  - BackTop控件
    - 在界面上未显示出来
  - Alert控件
    - 设置Type属性不生效
    - 设置Title、Description、closable、bordered属性不生效
  - Collapse控件
    - 设置Accordion属性不生效
    - 点击折叠项展开面板，只有折叠项右侧的图标发生变化，未展开显示面板
    - 处于展开状态的折叠项的图标与未展开状态的图标，大小不一致
  - PopConfirm控件
    - 点击按钮后，弹出一个内容框并快速消失，无法查看效果
  - 点击Layout菜单项后抛出异常：
    `Failed to create component instance for 'layout'
     Traceback (most recent call last):
      File "D:\Working\Me\Tyto\examples\playground\views\component_preview.py", line 67, in show_component
        widget = factory()
         File "D:\Working\Me\Tyto\examples\playground\definitions\layout_props.py", line 16, in _make_layout
         header = TLayoutHeader(height=50)
       File "D:\Working\Me\Tyto\src\tyto_ui_lib\components\organisms\layout.py", line 91, in __init__
        super().__init__(parent)
          ~~~~~~~~~~~~~~~~^^^^^^^^
         File "D:\Working\Me\Tyto\src\tyto_ui_lib\common\base.py", line 40, in __init__
        self.apply_theme()
          ~~~~~~~~~~~~~~~~^^
        File "D:\Working\Me\Tyto\src\tyto_ui_lib\components\organisms\layout.py", line 143, in apply_theme
         self._apply_height()
         ~~~~~~~~~~~~~~~~~~^^
        File "D:\Working\Me\Tyto\src\tyto_ui_lib\components\organisms\layout.py", line 149, in _apply_height
        h = self._custom_height
            ^^^^^^^^^^^^^^^^^^^
        AttributeError: 'TLayoutHeader' object has no attribute '_custom_height'`

- 以下缺陷未成功修复：
  - inputNumber控件的样式显示错误
  - Slider控件在dark模式下的tooltip颜色样式显示错误
  - BackTop控件的样式显示错误
  - Alert控件的Bordered属性未生效（可能是边框颜色及形状显示有误）
  - Collapse控件的样式显示错误
  - Popconfirm演示界面中，点击按钮无反应

- [x] v1.1.0版本发现的控件缺陷：
  - [x] 在playground中，popconfirm控件的两个按钮的底部边框处都被遮挡，没有显示出来
  - [x] popconfirm控件未固定显示在触发按钮周围，正确效果是popconfirm弹窗需固定显示在触发按钮周围（即使界面被拖动）
  - [x] backtop控件设置visibility height属性不生效
  - [x] timeline控件中事件的节点未与标题文本中位线水平对齐

- [x] collapse控件，发现以下问题：
  - 展开/收缩图标与标题文本的间距过大，未与naiveUI的collapse效果保持一致
  - 展开/收缩图标的形状、大小显示有误，未与naiveUI的collapse效果保持一致
  - 设置arrow placement属性为right时，展开/收缩图标显示的位置不正确
  - collapse中内容项交界处，未显示出来分割线

- [x] timeline控件，发现以下缺陷：
  -设置Horizontal属性后，节点和文本等内容显示位置错误
  - 设置Size属性不生效

- [x] 修复bug：在playground中点击message菜单项，提示"No preview factory for 'message'"；点击Modal菜单项，提示"No preview factory for 'modal'"

- [ ] menu控件，发现以下缺陷：
  - 设置mode、disabled属性不生效
  - 样式错误

- [ ] 修复控件样式及功能逻辑缺陷：
  - [ ] 点击弹出TConfirm弹窗后，在任务栏中生成了一个新的会话窗口（错误），正确做法是始终保持任务栏只有一个顶级父窗口
  - [ ] inputNumber控件，清空按钮与'-'按钮、'+'按钮的间距过大，清空按钮图标显示模糊且有锯齿
  - [ ] collapse控件，在展开/收缩时，会抖动重刷
  - [ ] input控件，当type为textarea时，在playground中设置placeholder、clearable属性，未实时显示效果

- [x] menu控件，边栏收缩按钮的圆形边框和背景颜色不正确。正确效果为：当light模式时，边框颜色为#efeff5，当dark模式时，无边框颜色，并且背景色为#48484e

- [x] menu控件，垂直菜单的高度应该自适应为父容器的高度，垂直菜单的高度应该固定为菜单项的高度

- [x] menu控件，垂直菜单在边栏收缩并恢复后，父级菜单项右侧的展开/收缩图标与右边界间距过小

- [x] tag控件，设置属性size、round、Strong不生效

- [x] tag控件，设置checkable，点击选中tag后，设置type属性，背景色未实时切换显示

- [x] tag控件，在dark模式下，文本颜色显示错误，正确效果是显示白色（与其它控件的效果保持一致）

- [x] button控件，不同尺寸的按钮，当设置loading和circle属性时，加载图标未居中显示


