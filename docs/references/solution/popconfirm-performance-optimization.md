# TPopconfirm 弹窗卡顿性能优化

> 模块路径：`src/tyto_ui_lib/components/molecules/popconfirm.py`
> 记录日期：2026-04-18

---

## 问题描述

在点击触发按钮弹出 TPopconfirm 弹窗时，存在明显的卡顿延迟，用户体验不流畅。

---

## 根因分析

通过对 `show_popup()` → `_build_popup()` → `_fade_in()` 调用链的逐层分析，识别出以下 5 个性能瓶颈：

### 原因 1：每次弹出都重建整个 popup widget 树

**严重程度：高**

`show_popup()` 每次调用时都会先 `hide_popup()`（销毁旧 popup），然后调用 `_build_popup()` 从零构建整个 widget 树。`_build_popup()` 内部创建了：

- 1 个 `QWidget`（popup 顶层窗口）
- 1 个 `_PopconfirmContainer`（自绘背景容器）
- 2 个 `QLabel`（icon + title）
- 1 个 `QWidget`（按钮行容器）
- 2 个 `TButton`（确认 + 取消按钮）

每个 `TButton` 的构造函数开销极大（见原因 2），且每次都要重新创建和销毁这些对象。

**解决方案：** 缓存 popup widget，首次构建后复用。仅在属性（title、按钮文本等）变化时更新内部控件的文本/属性，而非重建。

### 原因 2：TButton 构造函数开销过大

**严重程度：高**

每个 `TButton` 在构造时执行以下操作：

1. `BaseWidget.__init__` → 连接 `ThemeEngine.theme_changed` 信号
2. 初始化 4 个 Mixin（`_init_hover_effect`、`_init_click_ripple`、`_init_focus_glow`、`_init_disabled`）
3. 创建 `_SpinnerWidget`（内部加载 SVG、创建 `QPropertyAnimation`、创建 `QSvgRenderer`）
4. 创建 4 个 `QLabel`（icon_left、icon_right、spinner、text label）
5. 设置 12+ 个 QSS 动态属性（`setProperty` 调用）
6. 调用 `_update_icon_display()`（访问 ThemeEngine 获取 token）
7. 调用 `_apply_circle_geometry()`（访问 ThemeEngine 获取 token、计算尺寸）
8. 调用 `apply_theme()`（再次访问 ThemeEngine、执行 `unpolish/polish`）

两个按钮的构造总共涉及约 30+ 次 ThemeEngine 访问、2 次 SVG 解析、2 次 QPropertyAnimation 创建。

**解决方案：** 通过缓存 popup 避免重复创建 TButton。

### 原因 3：Jinja2 模板渲染开销

**严重程度：中**

`_build_popup()` 末尾调用 `engine.render_qss("popconfirm.qss.j2")` 渲染 QSS 模板。虽然 popconfirm 模板本身较小，但 Jinja2 的模板加载、编译、渲染流程仍有一定开销。加上每个 TButton 在 `apply_theme()` 中也可能触发模板渲染，总渲染次数较多。

**解决方案：** 缓存 popup 后，仅在主题切换时重新渲染 QSS，而非每次弹出都渲染。

### 原因 4：QGraphicsOpacityEffect 创建开销

**严重程度：低**

`_fade_in()` 每次都创建新的 `QGraphicsOpacityEffect` 和 `QPropertyAnimation`。`QGraphicsOpacityEffect` 会触发 Qt 的渲染管线变更，导致额外的 GPU 上下文切换。

**解决方案：** 缓存 popup 后，opacity effect 和 animation 也一并缓存复用。

### 原因 5：16ms 定时器重定位开销

**严重程度：低**

`show_popup()` 启动了一个 16ms 间隔的 `QTimer`（`_reposition_timer`），每帧调用 `_position_popup()` 重新计算弹窗位置。虽然单次计算开销不大，但 60fps 的定时器在弹窗显示期间持续运行，可能与其他渲染操作竞争 CPU 时间。

**解决方案：** 保留定时器（用于跟随触发按钮位置），但可适当降低频率（如 32ms）或改用事件驱动方式。此项优先级较低。

---

## 综合解决方案

采用 **popup 缓存复用** 策略，核心思路：

1. 首次 `show_popup()` 时构建 popup 并缓存
2. 后续 `show_popup()` 时直接复用已缓存的 popup，仅更新文本属性
3. `hide_popup()` 时隐藏 popup 而非销毁
4. 缓存 `QGraphicsOpacityEffect` 和 `QPropertyAnimation`，避免重复创建
5. 在属性 setter 中标记 dirty flag，下次 show 时按需更新

### 预期效果

- 首次弹出：与优化前相当（需要构建 widget 树）
- 后续弹出：消除 widget 构建开销，预计延迟降低 80%+
- 内存：popup 常驻内存，但仅为一个轻量 widget 树，影响可忽略

---

## 涉及文件

- `src/tyto_ui_lib/components/molecules/popconfirm.py` — `show_popup`、`hide_popup`、`_build_popup`、`_fade_in`、`_fade_out`
