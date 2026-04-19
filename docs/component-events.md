# Tyto 组件事件手册

本文档整理了 Tyto UI 组件库中所有原子（Atom）、分子（Molecule）、有机体（Organism）组件能够触发的事件（Signal），并说明每个事件携带的信息。

> 信号命名遵循 `snake_case` 规范，基于 PySide6 的 `Signal` 机制。
> 所有公开组件的信号同时通过 EventBus 发布，事件名格式为 `{ClassName}:{signal_name}`。

---

## 一、原子组件（Atoms）

### 1. TButton

| 信号 | 参数 | 说明 |
|------|------|------|
| `clicked` | `object` — QMouseEvent | 鼠标释放时触发（非 loading、非 disabled 状态下） |

### 2. TInput

| 信号 | 参数 | 说明 |
|------|------|------|
| `text_changed` | `str` — 当前文本内容 | 文本内容发生变化时触发 |
| `cleared` | `object` — QMouseEvent | 点击清空按钮或调用 `clear()` 时触发 |
| `input` | `str` — 当前文本内容 | 每次输入时触发（含 IME 中间态） |
| `focus` | `object` — QFocusEvent | 输入框获得焦点时触发 |
| `blur` | `object` — QFocusEvent | 输入框失去焦点时触发 |
| `click` | `object` — QMouseEvent | 点击输入框区域时触发 |
| `mousedown` | `object` — QMouseEvent | 鼠标按下时触发 |
| `keydown` | `object` — QKeyEvent | 键盘按下时触发 |
| `keyup` | `object` — QKeyEvent | 键盘释放时触发 |

### 3. TCheckbox

| 信号 | 参数 | 说明 |
|------|------|------|
| `state_changed` | `int` — 新的 CheckState 值（0=未选中, 1=选中, 2=不确定） | 勾选状态变化时触发 |

### 4. TCheckboxGroup

| 信号 | 参数 | 说明 |
|------|------|------|
| `value_changed` | `list` — 当前所有已选中 checkbox 的 value 列表 | 组内任一 checkbox 状态变化且通过 min/max 约束校验后触发 |

### 5. TRadio

| 信号 | 参数 | 说明 |
|------|------|------|
| `toggled` | `bool` — 新的选中状态 | 选中状态变化时触发 |

### 6. TRadioButton

| 信号 | 参数 | 说明 |
|------|------|------|
| `toggled` | `bool` — 新的选中状态 | 选中状态变化时触发 |

### 7. TRadioGroup

| 信号 | 参数 | 说明 |
|------|------|------|
| `selection_changed` | `object` — 新选中 radio 的 value 值 | 互斥选择发生变化时触发 |

### 8. TSwitch

| 信号 | 参数 | 说明 |
|------|------|------|
| `toggled` | `bool` — 当前开关状态（True=开, False=关） | 每次切换状态后触发 |

### 9. TTag

| 信号 | 参数 | 说明 |
|------|------|------|
| `closed` | `object` — QMouseEvent | 点击关闭按钮时触发（closable=True 时可用） |
| `checked_changed` | `bool` — 新的选中状态 | checkable 模式下点击切换选中状态时触发 |
| `mouse_enter` | `object` — QEnterEvent | 鼠标进入标签区域时触发 |
| `mouse_leave` | `object` — QEvent | 鼠标离开标签区域时触发 |

### 10. TSlider

| 信号 | 参数 | 说明 |
|------|------|------|
| `value_changed` | `object` — 单滑块模式为 `int\|float`，双滑块模式为 `tuple[float, float]` | 滑块值发生变化时触发 |
| `drag_start` | 无 | 用户开始拖拽滑块时触发 |
| `drag_end` | 无 | 用户结束拖拽滑块时触发 |

### 11. TSpin

| 信号 | 参数 | 说明 |
|------|------|------|
| `spinning_changed` | `bool` — 新的旋转状态 | 旋转加载状态变化时触发 |

### 12. TInputNumber

| 信号 | 参数 | 说明 |
|------|------|------|
| `value_changed` | `object` — 当前数值（precision=0 时为 `int`，否则为 `float`） | 数值发生变化时触发 |
| `focused` | `object` — QFocusEvent | 输入框获得焦点时触发 |
| `blurred` | `object` — QFocusEvent | 输入框失去焦点时触发 |
| `cleared` | `object` — QMouseEvent | 清空数值时触发（clearable=True 时可用） |

### 13. TBackTop

| 信号 | 参数 | 说明 |
|------|------|------|
| `clicked` | 无 | 点击回到顶部按钮时触发 |
| `visibility_changed` | `bool` — 当前可见状态 | 按钮显示/隐藏状态变化时触发 |
| `shown` | 无 | 按钮变为可见时触发 |
| `hidden` | 无 | 按钮变为隐藏时触发 |

### 14. TEmpty

> TEmpty 为纯展示组件，不触发任何事件。

---

## 二、分子组件（Molecules）

### 1. TSearchBar

| 信号 | 参数 | 说明 |
|------|------|------|
| `search_changed` | `str` — 当前搜索文本 | 每次输入内容变化时触发 |
| `search_submitted` | `str` — 当前搜索文本 | 点击搜索按钮或按下 Enter 键时触发 |

### 2. TBreadcrumb

| 信号 | 参数 | 说明 |
|------|------|------|
| `item_clicked` | `int` — 被点击项的索引, `object` — 该项关联的 data 数据, `object` — QMouseEvent | 点击非末尾面包屑项时触发 |

### 3. TAlert

| 信号 | 参数 | 说明 |
|------|------|------|
| `closed` | 无 | 点击关闭按钮时触发 |
| `after_leave` | 无 | 关闭淡出动画完成后触发 |

### 4. TCollapse

| 信号 | 参数 | 说明 |
|------|------|------|
| `item_expanded` | `str` — 项的 name 标识, `bool` — 是否展开 | 任一折叠项展开/收起状态变化时触发 |
| `item_header_clicked` | `str` — 被点击项的 name 标识, `bool` — 当前展开状态, `object` — QMouseEvent | 任一折叠项的标题栏被点击时触发 |
| `expanded_names_changed` | `list` — 当前所有展开项的 name 列表 | 展开项集合发生变化时触发 |

### 5. TCollapseItem

| 信号 | 参数 | 说明 |
|------|------|------|
| `expanded_changed` | `bool` — 新的展开状态 | 展开/收起状态变化时触发 |

### 6. TPopconfirm

| 信号 | 参数 | 说明 |
|------|------|------|
| `confirmed` | 无 | 点击确认按钮时触发 |
| `cancelled` | 无 | 点击取消按钮时触发 |

### 7. TTimeline

| 信号 | 参数 | 说明 |
|------|------|------|
| `item_clicked` | `int` — 被点击项的索引 | 点击时间线节点时触发 |

### 8. TTimelineItem

| 信号 | 参数 | 说明 |
|------|------|------|
| `clicked` | 无 | 鼠标左键点击该节点时触发 |

### 9. TInputGroup

> TInputGroup 为纯布局组件，不触发任何事件。自动管理子组件的边框圆角合并。

---

## 三、有机体组件（Organisms）

### 1. TMessage

| 信号 | 参数 | 说明 |
|------|------|------|
| `leave` | 无 | 消息关闭动画开始时触发 |
| `closed` | 无 | 消息关闭动画完成后触发 |

### 2. TModal

| 信号 | 参数 | 说明 |
|------|------|------|
| `closed` | 无 | 模态框关闭时触发（通过关闭按钮或遮罩点击） |
| `esc_pressed` | 无 | 按下 Esc 键时触发 |
| `mask_clicked` | `object` — QMouseEvent | 点击遮罩层时触发 |
| `after_enter` | 无 | 打开动画完成后触发 |
| `before_leave` | 无 | 关闭动画开始前触发 |
| `after_leave` | 无 | 关闭动画完成后触发 |
| `positive_clicked` | 无 | 确认按钮点击时触发 |
| `negative_clicked` | 无 | 取消按钮点击时触发 |

### 3. TCard

| 信号 | 参数 | 说明 |
|------|------|------|
| `closed` | 无 | 点击关闭按钮时触发（closable=True 时可用） |

### 4. TLayout / TLayoutSider

| 组件 | 信号 | 参数 | 说明 |
|------|------|------|------|
| `TLayout` | `scrolled` | `object` — QEvent | 内容区域滚动时触发 |
| `TLayoutSider` | `collapsed_changed` | `bool` — 新的折叠状态 | 侧边栏折叠/展开状态变化时触发 |
| `TLayoutSider` | `after_enter` | 无 | 展开动画完成后触发 |
| `TLayoutSider` | `after_leave` | 无 | 折叠动画完成后触发 |
| `TLayoutSider` | `scrolled` | `object` — QEvent | 侧边栏内容滚动时触发 |

> TLayoutHeader、TLayoutFooter、TLayoutContent 为纯布局组件，不触发事件。

### 5. TMenu

| 信号 | 参数 | 说明 |
|------|------|------|
| `item_selected` | `str` — 被选中菜单项的 key 标识, `object` — MenuOption 对象 | 点击菜单项时触发 |
| `expanded_keys_changed` | `list` — 当前所有展开的菜单组 key 列表 | 展开的菜单组集合变化时触发 |

### 6. TMenuItem

| 信号 | 参数 | 说明 |
|------|------|------|
| `clicked` | `str` — 该菜单项的 key 标识 | 点击菜单项时触发（非 disabled 状态） |

### 7. TMenuItemGroup

| 信号 | 参数 | 说明 |
|------|------|------|
| `expanded_changed` | `bool` — 新的展开状态 | 子菜单组展开/收起时触发 |

---

## 四、事件汇总统计

| 分类 | 组件数量 | 含事件的组件 | 总事件数 |
|------|---------|-------------|---------|
| 原子组件 | 14 | 12 | 28 |
| 分子组件 | 9 | 7 | 12 |
| 有机体组件 | 8 | 6 | 16 |
| **合计** | **31** | **25** | **56** |
