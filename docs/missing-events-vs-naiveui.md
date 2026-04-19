# Tyto 控件欠缺事件对照表（vs NaiveUI）

本文档基于 NaiveUI 源码中各组件的事件回调（`on*` props）与 Tyto 当前已实现的 Signal 进行逐一比对，列出 Tyto 中尚未实现的事件。

> 比对原则：
> - NaiveUI 中 `onUpdate:value` / `onUpdateValue` 属于同一事件的两种绑定方式，在 PySide6 中对应一个 Signal，不重复计算
> - NaiveUI 中标记为 `deprecated` 的事件（如 `onChange`）不纳入缺失统计
> - NaiveUI 中标记为 `private` / `internal` 的事件不纳入缺失统计

---

## 一、原子组件（Atoms）

### 1. TButton

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onClick` | `(e: MouseEvent) => void` | ✅ `clicked(object)` — 携带 QMouseEvent | — |

### 2. TInput

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateValue` | `(value: string) => void` | ✅ `text_changed(str)` | — |
| `onClear` | `(e: MouseEvent) => void` | ✅ `cleared(object)` — 携带 QMouseEvent | — |
| `onInput` | `(value: string) => void` | ✅ `input(str)` | — |
| `onFocus` | `(e: FocusEvent) => void` | ✅ `focus(object)` — 携带 QFocusEvent | — |
| `onBlur` | `(e: FocusEvent) => void` | ✅ `blur(object)` — 携带 QFocusEvent | — |
| `onClick` | `(e: MouseEvent) => void` | ✅ `click(object)` — 携带 QMouseEvent | — |
| `onMousedown` | `(e: MouseEvent) => void` | ✅ `mousedown(object)` — 携带 QMouseEvent | — |
| `onKeydown` | `(e: KeyboardEvent) => void` | ✅ `keydown(object)` — 携带 QKeyEvent | — |
| `onKeyup` | `(e: KeyboardEvent) => void` | ✅ `keyup(object)` — 携带 QKeyEvent | — |

### 3. TCheckbox

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateChecked` | `(checked: boolean) => void` | ✅ `state_changed(int)` | — |

### 4. TCheckboxGroup

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateValue` | `(value: Array) => void` | ✅ `value_changed(list)` | — |

### 5. TRadio

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateChecked` | `(checked: boolean) => void` | ✅ `toggled(bool)` | — |

### 6. TRadioGroup

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateValue` | `(value: string \| number \| boolean) => void` | ✅ `selection_changed(object)` | — |

### 7. TSwitch

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateValue` | `(value: boolean) => void` | ✅ `toggled(bool)` | — |

### 8. TTag

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onClose` | `(e: MouseEvent) => void` | ✅ `closed(object)` — 携带 QMouseEvent | — |
| `onUpdateChecked` | `(checked: boolean) => void` | ✅ `checked_changed(bool)` | — |
| `onMouseenter` | `(e: MouseEvent) => void` | ✅ `mouse_enter(object)` — 携带 QEnterEvent | — |
| `onMouseleave` | `(e: MouseEvent) => void` | ✅ `mouse_leave(object)` — 携带 QEvent | — |

### 9. TSlider

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateValue` | `(value: number \| [number, number]) => void` | ✅ `value_changed(object)` | — |
| `onDragstart` | `() => void` | ✅ `drag_start` | — |
| `onDragend` | `() => void` | ✅ `drag_end` | — |

### 10. TSpin

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| — | — | ✅ `spinning_changed(bool)` | NaiveUI 无公开事件，Tyto 已超出 |

### 11. TInputNumber

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateValue` | `(value: number \| null) => void` | ✅ `value_changed(object)` | — |
| `onFocus` | `(e: FocusEvent) => void` | ✅ `focused(object)` — 携带 QFocusEvent | — |
| `onBlur` | `(e: FocusEvent) => void` | ✅ `blurred(object)` — 携带 QFocusEvent | — |
| `onClear` | `(e: MouseEvent) => void` | ✅ `cleared(object)` — 携带 QMouseEvent | — |

### 12. TBackTop

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdate:show` | `(value: boolean) => void` | ✅ `visibility_changed(bool)` | — |
| `onShow` | `() => void` | ✅ `shown` | — |
| `onHide` | `() => void` | ✅ `hidden` | — |

### 13. TEmpty

NaiveUI 和 Tyto 均无事件，无缺失。

---

## 二、分子组件（Molecules）

### 1. TSearchBar

NaiveUI 无 SearchBar 组件，Tyto 自行设计。无缺失。

### 2. TBreadcrumb / TBreadcrumbItem

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| BreadcrumbItem `onClick` | `(e: MouseEvent) => void` | ✅ `item_clicked(int, object, object)` — 携带索引、data 和 QMouseEvent | — |

### 3. TAlert

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onClose` | `() => void` | ✅ `closed` | — |
| `onAfterLeave` | `() => void` | ✅ `after_leave` | — |

### 4. TCollapse

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateExpandedNames` | `(expandedNames: string[]) => void` | ✅ `expanded_names_changed(list)` | — |
| `onItemHeaderClick` | `(info: { name, expanded, event }) => void` | ✅ `item_header_clicked(str, bool, object)` — 携带 name、expanded 和 QMouseEvent | — |

### 5. TCollapseItem

NaiveUI CollapseItem 无公开事件 props。Tyto 的 `expanded_changed(bool)` 已超出。无缺失。

### 6. TPopconfirm

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onPositiveClick` | `() => Promise<boolean> \| boolean \| void` | ✅ `confirmed` + `on_positive_click` 回调 | — |
| `onNegativeClick` | `() => Promise<boolean> \| boolean \| void` | ✅ `cancelled` + `on_negative_click` 回调 | — |

### 7. TTimeline / TTimelineItem

NaiveUI Timeline 和 TimelineItem 均无公开事件 props。Tyto 的 `item_clicked(int)` 和 `clicked` 已超出。无缺失。

### 8. TInputGroup

NaiveUI 和 Tyto 均无事件。无缺失。

---

## 三、有机体组件（Organisms）

### 1. TMessage

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onAfterLeave` | `() => void` | ✅ `closed`（动画完成后触发） | — |
| `onLeave` | `() => void` | ✅ `leave`（动画开始时触发） | — |

### 2. TModal

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateShow` | `(value: boolean) => void` | ⚠️ 部分覆盖 | Tyto 有 `closed` + `after_enter`，但缺少统一的 `show_changed(bool)` 双向状态变更信号 |
| `onClose` | `() => Promise<boolean> \| boolean` | ✅ `closed` + `on_close` 回调（支持返回 False 阻止关闭） | — |
| `onEsc` | `() => void` | ✅ `esc_pressed` | — |
| `onMaskClick` | `(e: MouseEvent) => void` | ✅ `mask_clicked(object)` — 携带 QMouseEvent | — |
| `onAfterEnter` | `() => void` | ✅ `after_enter` | — |
| `onBeforeLeave` | `() => void` | ✅ `before_leave` | — |
| `onAfterLeave` | `() => void` | ✅ `after_leave` | — |
| `onPositiveClick` | `() => Promise<boolean> \| boolean` | ✅ `positive_clicked` | — |
| `onNegativeClick` | `() => Promise<boolean> \| boolean` | ✅ `negative_clicked` | — |

### 3. TCard

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onClose` | `() => void` | ✅ `closed` | — |

### 4. TLayout

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onScroll` | `(e: Event) => void` | ✅ `scrolled(object)` — 携带 QEvent | — |

### 5. TLayoutSider

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateCollapsed` | `(value: boolean) => void` | ✅ `collapsed_changed(bool)` | — |
| `onAfterEnter` | `() => void` | ✅ `after_enter` | — |
| `onAfterLeave` | `() => void` | ✅ `after_leave` | — |
| `onScroll` | `(e: Event) => void` | ✅ `scrolled(object)` — 携带 QEvent | — |

### 6. TMenu

| NaiveUI 事件 | 参数 | Tyto 现状 | 缺失 |
|--------------|------|-----------|------|
| `onUpdateValue` | `(key: string, item: MenuOption) => void` | ✅ `item_selected(str, object)` — 携带 key 和 MenuOption | — |
| `onUpdateExpandedKeys` | `(keys: string[]) => void` | ✅ `expanded_keys_changed(list)` | — |

---

## 四、缺失事件汇总

### 完全缺失的事件（共 0 个）

所有 NaiveUI 公开事件均已在 Tyto 中实现对应的 Signal。

### 参数不完整的事件（共 0 个）

所有事件参数已补齐。

### 语义不完整的事件（共 1 个）

| 组件 | 说明 |
|------|------|
| TModal | `closed` + `after_enter` 覆盖了 show/hide 生命周期，但缺少统一的 `show_changed(bool)` 双向状态变更信号（NaiveUI `onUpdateShow` 在 show 和 hide 时均触发） |
