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

- [ ] input控件：
  - type为textarea时，在playground中设置placeholder、clearable时，未实时显示效果


