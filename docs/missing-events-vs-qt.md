# Tyto 控件未发送到事件总线的 Qt 原生事件对照表

本文档比对 Tyto UI 组件与其底层 Qt（PySide6）控件已有的事件，列出 Qt 控件原生支持但 Tyto 组件未通过 `_emit_bus_event()` 发布到全局事件总线（EventBus）的事件。

> 比对原则：
> - 仅关注 Tyto 组件已定义的 Signal 但未调用 `_emit_bus_event()` 发布的事件
> - 同时列出 Qt 基类（QWidget / QAbstractButton / QLineEdit / QAbstractSlider 等）提供的常用事件中，Tyto 组件可能需要转发到事件总线的部分
> - 纯布局组件（TInputGroup、TLayoutHeader、TLayoutFooter、TLayoutContent）和纯展示组件（TEmpty）不纳入统计
> - Qt 内部低级事件（paintEvent、resizeEvent 等绘制/布局事件）不纳入统计

> **更新记录（V1.1.0 第二批事件总线集成）：**
> - 高优先级 23 个 Tyto Signal 已全部集成 `_emit_bus_event()` ✅
> - 中优先级 4 个未 emit 的 Signal 已实现并集成 ✅
> - 低优先级按需转发的 Qt 原生事件已完成 ✅

---

## 一、Tyto 已定义 Signal 但未发布到事件总线的事件

以下事件在 Tyto 组件中已通过 `Signal()` 定义并通过 `.emit()` 触发，但未调用 `_emit_bus_event()` 发布到全局事件总线。

> **状态说明：** ✅ = 已集成到事件总线，❌ = 仍未集成

### 1. 原子组件（Atoms）

#### TCheckbox

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `state_changed` | `int` — CheckState 值（0=未选中, 1=选中, 2=不确定） | `QCheckBox.stateChanged(int)` | 勾选状态变化 | ✅ 已集成 |

#### TCheckboxGroup

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `value_changed` | `list` — 已选中 checkbox 的 value 列表 | Tyto 自定义（Qt 无对应组件） | 组内选中值变化 | ✅ 已集成 |

#### TRadio

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `toggled` | `bool` — 新的选中状态 | `QRadioButton.toggled(bool)` | 选中状态变化 | ✅ 已集成 |

#### TRadioButton

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `toggled` | `bool` — 新的选中状态 | `QRadioButton.toggled(bool)` | 选中状态变化 | ✅ 已集成 |

#### TRadioGroup

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `selection_changed` | `object` — 新选中 radio 的 value 值 | Tyto 自定义（Qt 无对应组件） | 互斥选择变化 | ✅ 已集成 |

#### TSwitch

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `toggled` | `bool` — 当前开关状态 | Tyto 自定义（Qt 无原生 Switch） | 开关切换 | ✅ 已集成 |

#### TTag

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `checked_changed` | `bool` — 新的选中状态 | Tyto 自定义（checkable 模式） | 可选中标签状态变化 | ✅ 已集成 |

#### TSpin

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `spinning_changed` | `bool` — 新的旋转状态 | Tyto 自定义（Qt 无对应组件） | 加载旋转状态变化 | ✅ 已集成 |

#### TSlider

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `value_changed` | `object` — 单滑块为 `int\|float`，双滑块为 `tuple[float, float]` | `QAbstractSlider.valueChanged(int)` | 滑块值变化 | ✅ 已集成 |
| `drag_start` | 无 | `QAbstractSlider.sliderPressed()` | 开始拖拽 | ✅ 已集成 |
| `drag_end` | 无 | `QAbstractSlider.sliderReleased()` | 结束拖拽 | ✅ 已集成 |

#### TInputNumber

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|

| `value_changed` | `object` — 当前数值 | `QSpinBox.valueChanged(int)` | 所有路径（`set_value`、键盘增减、`_on_text_committed`、`_on_clear`）均已发布到总线 | ✅ 已集成 |

### 2. 分子组件（Molecules）

#### TSearchBar

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `search_changed` | `str` — 当前搜索文本 | Tyto 自定义（组合 TInput） | 搜索文本变化 | ✅ 已集成 |
| `search_submitted` | `str` — 当前搜索文本 | Tyto 自定义（组合 TInput + TButton） | 搜索提交 | ✅ 已集成 |

#### TBreadcrumb

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `item_clicked` | `int` — 索引, `object` — 关联数据, `object` — QMouseEvent | Tyto 自定义（Qt 无对应组件） | 面包屑项点击（已扩展携带 QMouseEvent） | ✅ 已集成 |

#### TPopconfirm

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `confirmed` | 无 | Tyto 自定义（Qt 无对应组件） | 确认按钮点击 | ✅ 已集成 |
| `cancelled` | 无 | Tyto 自定义（Qt 无对应组件） | 取消按钮点击 | ✅ 已集成 |

#### TTimeline

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `item_clicked` | `int` — 被点击项的索引 | Tyto 自定义（Qt 无对应组件） | 时间线节点点击 | ✅ 已集成 |

#### TTimelineItem

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `clicked` | 无 | Tyto 自定义 | 节点点击 | ✅ 已集成 |

### 3. 有机体组件（Organisms）

#### TCard

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `closed` | 无 | Tyto 自定义（Qt 无对应组件） | 关闭按钮点击 | ✅ 已集成 |

#### TLayoutSider

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `collapsed_changed` | `bool` — 新的折叠状态 | Tyto 自定义 | 折叠/展开状态变化 | ✅ 已集成 |
| `scrolled` | `int` — 滚动条值 | `QScrollArea.verticalScrollBar().valueChanged(int)` | 已实现 emit 并集成到总线 | ✅ 已实现并集成 |

#### TLayout

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `scrolled` | `int` — 滚动条值 | `QScrollArea.verticalScrollBar().valueChanged(int)` | 已实现 emit 并集成到总线 | ✅ 已实现并集成 |

#### TModal

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `positive_clicked` | 无 | Tyto 自定义（Dialog 模式） | 已实现 emit 并集成到总线 | ✅ 已实现并集成 |
| `negative_clicked` | 无 | Tyto 自定义（Dialog 模式） | 已实现 emit 并集成到总线 | ✅ 已实现并集成 |

#### TMenu > TMenuItem

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `clicked` | `str` — 菜单项 key | Tyto 自定义 | 菜单项点击 | ✅ 已集成 |

#### TMenu > TMenuItemGroup

| Tyto Signal | 参数 | Qt 对应事件 | 说明 | 状态 |
|-------------|------|------------|------|------|
| `expanded_changed` | `bool` — 新的展开状态 | Tyto 自定义 | 子菜单组展开/收起 | ✅ 已集成 |

---

## 二、Qt 基类原生事件中 Tyto 组件未转发到事件总线的事件

以下事件由 Qt 基类（QWidget）原生提供，所有 Tyto 组件均可通过重写对应方法获取，但当前未通过 `_emit_bus_event()` 发布到全局事件总线。

> 说明：Tyto 所有组件均继承自 `BaseWidget(QWidget)`，因此 QWidget 的所有虚函数事件均可用。
> 以下仅列出对 UI 交互有实际意义的事件，排除绘制、布局等底层事件。
>
> **状态说明：** ✅ = 已转发到事件总线，❌ = 仍未转发

### QWidget 通用交互事件

以下事件适用于所有 Tyto 组件（继承自 QWidget），部分已按需转发到事件总线：

| Qt 事件方法 | Qt 事件类型 | 参数 | 说明 | 已转发的 Tyto 组件 | 未转发的 Tyto 组件 |
|-------------|------------|------|------|-------------------|-------------------|
| `enterEvent` | `QEnterEvent` | `QEnterEvent` | 鼠标进入控件区域 | TTag、TInput（已处理） | TButton、TCheckbox、TRadio、TSwitch、TSpin、TSlider、TInputNumber、TBackTop |
| `leaveEvent` | `QEvent` | `QEvent` | 鼠标离开控件区域 | TTag、TInput（已处理） | TButton、TCheckbox、TRadio、TSwitch、TSpin、TSlider、TInputNumber、TBackTop |
| `mousePressEvent` | `QMouseEvent` | `QMouseEvent` | 鼠标按下 | TButton、TInput（已处理） | TCheckbox、TRadio、TSwitch、TSpin、TSlider、TInputNumber |
| `mouseReleaseEvent` | `QMouseEvent` | `QMouseEvent` | 鼠标释放 | TButton（已处理） | TCheckbox、TRadio、TSwitch、TSpin、TSlider、TInputNumber |
| `mouseDoubleClickEvent` | `QMouseEvent` | `QMouseEvent` | 鼠标双击 | — | 所有组件 |
| `mouseMoveEvent` | `QMouseEvent` | `QMouseEvent` | 鼠标移动（需 setMouseTracking） | — | 所有组件 |
| `wheelEvent` | `QWheelEvent` | `QWheelEvent` | 鼠标滚轮 | ✅ TSlider、TInputNumber | TLayout、TLayoutSider |
| `keyPressEvent` | `QKeyEvent` | `QKeyEvent` | 键盘按下 | TInput、TModal（已处理） | TCheckbox、TRadio、TSwitch、TSlider、TInputNumber |
| `keyReleaseEvent` | `QKeyEvent` | `QKeyEvent` | 键盘释放 | TInput（已处理） | TCheckbox、TRadio、TSwitch、TSlider、TInputNumber |
| `focusInEvent` | `QFocusEvent` | `QFocusEvent` | 获得焦点 | ✅ TButton、TCheckbox、TRadio、TSwitch、TSlider；TInput、TInputNumber（已处理） | — |
| `focusOutEvent` | `QFocusEvent` | `QFocusEvent` | 失去焦点 | ✅ TButton、TCheckbox、TRadio、TSwitch、TSlider；TInput、TInputNumber（已处理） | — |
| `contextMenuEvent` | `QContextMenuEvent` | `QContextMenuEvent` | 右键菜单请求 | — | 所有组件 |
| `dragEnterEvent` | `QDragEnterEvent` | `QDragEnterEvent` | 拖拽进入 | — | 所有组件（需 setAcceptDrops） |
| `dragLeaveEvent` | `QDragLeaveEvent` | `QDragLeaveEvent` | 拖拽离开 | — | 所有组件（需 setAcceptDrops） |
| `dropEvent` | `QDropEvent` | `QDropEvent` | 拖拽释放 | — | 所有组件（需 setAcceptDrops） |
| `showEvent` | `QShowEvent` | `QShowEvent` | 控件显示 | ✅ TModal、TMessage | 其他组件 |
| `hideEvent` | `QHideEvent` | `QHideEvent` | 控件隐藏 | ✅ TModal、TMessage | 其他组件 |
| `closeEvent` | `QCloseEvent` | `QCloseEvent` | 控件关闭 | — | TModal、TMessage |

### TMenuItem 特有事件转发

| Qt 事件方法 | 说明 | 状态 |
|-------------|------|------|
| `enterEvent` | 鼠标进入菜单项 | ✅ 已转发（`mouse_enter`） |
| `leaveEvent` | 鼠标离开菜单项 | ✅ 已转发（`mouse_leave`） |

---

## 三、按组件汇总：未发布到事件总线的事件清单

### 原子组件

| 组件 | 未发布的 Tyto Signal | 未转发的 Qt 原生事件 | 合计 |
|------|---------------------|---------------------|------|
| TButton | — | `enterEvent`、`leaveEvent`、`mouseDoubleClickEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 6 |
| TInput | — | `mouseDoubleClickEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 4 |
| TCheckbox | ~~`state_changed`~~ ✅ | `enterEvent`、`leaveEvent`、`mousePressEvent`、`mouseReleaseEvent`、`mouseDoubleClickEvent`、`keyPressEvent`、`keyReleaseEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 10 |
| TCheckboxGroup | ~~`value_changed`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TRadio | ~~`toggled`~~ ✅ | `enterEvent`、`leaveEvent`、`mousePressEvent`、`mouseReleaseEvent`、`mouseDoubleClickEvent`、`keyPressEvent`、`keyReleaseEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 10 |
| TRadioButton | ~~`toggled`~~ ✅ | 同 TRadio | 10 |
| TRadioGroup | ~~`selection_changed`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TSwitch | ~~`toggled`~~ ✅ | `enterEvent`、`leaveEvent`、`mousePressEvent`、`mouseReleaseEvent`、`mouseDoubleClickEvent`、`keyPressEvent`、`keyReleaseEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 10 |
| TTag | ~~`checked_changed`~~ ✅ | `mouseDoubleClickEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 4 |
| TSpin | ~~`spinning_changed`~~ ✅ | `enterEvent`、`leaveEvent`、`mousePressEvent`、`mouseReleaseEvent`、`mouseDoubleClickEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 8 |
| TSlider | ~~`value_changed`~~ ✅、~~`drag_start`~~ ✅、~~`drag_end`~~ ✅ | `enterEvent`、`leaveEvent`、`mouseDoubleClickEvent`、`keyPressEvent`、`keyReleaseEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 8 |
| TInputNumber | ~~`value_changed`~~ ✅ | `enterEvent`、`leaveEvent`、`mouseDoubleClickEvent`、`keyPressEvent`、`keyReleaseEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 8 |
| TBackTop | — | `enterEvent`、`leaveEvent`、`mouseDoubleClickEvent`、`contextMenuEvent`、`showEvent`、`hideEvent` | 6 |
| TEmpty | — | — | 0 |

### 分子组件

| 组件 | 未发布的 Tyto Signal | 未转发的 Qt 原生事件 | 合计 |
|------|---------------------|---------------------|------|
| TSearchBar | ~~`search_changed`~~ ✅、~~`search_submitted`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TBreadcrumb | ~~`item_clicked`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TAlert | — | `showEvent`、`hideEvent` | 2 |
| TCollapse | — | `showEvent`、`hideEvent` | 2 |
| TCollapseItem | — | `showEvent`、`hideEvent` | 2 |
| TPopconfirm | ~~`confirmed`~~ ✅、~~`cancelled`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TTimeline | ~~`item_clicked`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TTimelineItem | ~~`clicked`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TInputGroup | — | — | 0 |

### 有机体组件

| 组件 | 未发布的 Tyto Signal | 未转发的 Qt 原生事件 | 合计 |
|------|---------------------|---------------------|------|
| TMessage | — | `closeEvent` | 1 |
| TModal | ~~`positive_clicked`~~ ✅、~~`negative_clicked`~~ ✅ | `closeEvent` | 1 |
| TCard | ~~`closed`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TLayout | ~~`scrolled`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TLayoutSider | ~~`collapsed_changed`~~ ✅、~~`scrolled`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TMenu | — | `showEvent`、`hideEvent` | 2 |
| TMenuItem | ~~`clicked`~~ ✅ | `showEvent`、`hideEvent` | 2 |
| TMenuItemGroup | ~~`expanded_changed`~~ ✅ | `showEvent`、`hideEvent` | 2 |

---

## 四、优先级建议

### 高优先级（Tyto 已定义 Signal 但未发布到总线）— ✅ 全部完成

这些事件已经在 Tyto 组件中通过 `Signal().emit()` 触发，只需在 emit 后追加一行 `self._emit_bus_event(...)` 即可完成集成。

| 组件 | Signal | 建议总线事件名 | 状态 |
|------|--------|---------------|------|
| TCheckbox | `state_changed(int)` | `TCheckbox:state_changed` | ✅ |
| TCheckboxGroup | `value_changed(list)` | `TCheckboxGroup:value_changed` | ✅ |
| TRadio | `toggled(bool)` | `TRadio:toggled` | ✅ |
| TRadioButton | `toggled(bool)` | `TRadioButton:toggled` | ✅ |
| TRadioGroup | `selection_changed(object)` | `TRadioGroup:selection_changed` | ✅ |
| TSwitch | `toggled(bool)` | `TSwitch:toggled` | ✅ |
| TTag | `checked_changed(bool)` | `TTag:checked_changed` | ✅ |
| TSpin | `spinning_changed(bool)` | `TSpin:spinning_changed` | ✅ |
| TSlider | `value_changed(object)` | `TSlider:value_changed` | ✅ |
| TSlider | `drag_start()` | `TSlider:drag_start` | ✅ |
| TSlider | `drag_end()` | `TSlider:drag_end` | ✅ |
| TInputNumber | `value_changed(object)` | `TInputNumber:value_changed` | ✅ |
| TSearchBar | `search_changed(str)` | `TSearchBar:search_changed` | ✅ |
| TSearchBar | `search_submitted(str)` | `TSearchBar:search_submitted` | ✅ |
| TBreadcrumb | `item_clicked(int, object, object)` | `TBreadcrumb:item_clicked` | ✅ |
| TPopconfirm | `confirmed()` | `TPopconfirm:confirmed` | ✅ |
| TPopconfirm | `cancelled()` | `TPopconfirm:cancelled` | ✅ |
| TTimeline | `item_clicked(int)` | `TTimeline:item_clicked` | ✅ |
| TTimelineItem | `clicked()` | `TTimelineItem:clicked` | ✅ |
| TCard | `closed()` | `TCard:closed` | ✅ |
| TLayoutSider | `collapsed_changed(bool)` | `TLayoutSider:collapsed_changed` | ✅ |
| TMenuItem | `clicked(str)` | `TMenuItem:clicked` | ✅ |
| TMenuItemGroup | `expanded_changed(bool)` | `TMenuItemGroup:expanded_changed` | ✅ |

### 中优先级（Signal 已定义但从未 emit，需先实现再发布）— ✅ 全部完成

| 组件 | Signal | 说明 | 状态 |
|------|--------|------|------|
| TLayout | `scrolled(object)` | 已实现：转发 TLayoutContent 内部滚动区域的 `verticalScrollBar().valueChanged` | ✅ |
| TLayoutSider | `scrolled(object)` | 已实现：监听内部 QScrollArea 的 `verticalScrollBar().valueChanged` | ✅ |
| TModal | `positive_clicked()` | 已实现：Dialog 模式下确认按钮点击触发 | ✅ |
| TModal | `negative_clicked()` | 已实现：Dialog 模式下取消按钮点击触发 | ✅ |

### 低优先级（Qt 原生事件，按需转发）— ✅ 推荐项已完成

Qt 基类的通用交互事件（如 `enterEvent`、`leaveEvent`、`focusInEvent`、`focusOutEvent`、`showEvent`、`hideEvent` 等）数量庞大，建议按实际业务需求选择性转发，而非全量接入事件总线。

推荐优先转发的 Qt 原生事件：

| Qt 事件 | 推荐转发的组件 | 理由 | 状态 |
|---------|---------------|------|------|
| `focusInEvent` / `focusOutEvent` | TButton、TCheckbox、TRadio、TSwitch、TSlider | 表单控件的焦点状态对表单验证和无障碍访问有重要意义 | ✅ 已转发 |
| `enterEvent` / `leaveEvent` | TMenuItem | 菜单项的 hover 状态对交互反馈有意义 | ✅ 已转发 |
| `wheelEvent` | TSlider、TInputNumber | 滚轮操作是这两个控件的核心交互方式之一 | ✅ 已转发 |
| `showEvent` / `hideEvent` | TModal、TMessage | 弹窗类组件的显示/隐藏状态对业务逻辑有重要意义 | ✅ 已转发 |

---

## 五、统计

| 分类 | 总数 | 已完成 | 剩余 |
|------|------|--------|------|
| 高优先级（已有 Signal 未发布） | 23 | ✅ 23 | 0 |
| 中优先级（Signal 未 emit） | 4 | ✅ 4 | 0 |
| 低优先级（Qt 原生事件 - 推荐项） | 10 | ✅ 10 | 0 |
| 低优先级（Qt 原生事件 - 其他） | — | — | 按需选择 |