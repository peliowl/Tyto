# 主题切换卡顿性能优化分析

| 属性 | 值 |
|------|-----|
| 版本 | V1.1.0 |
| 严重程度 | 中 |
| 影响范围 | 全局（所有组件在 light/dark 切换时均受影响） |
| 涉及文件 | `theme_engine.py`、`base.py`、所有组件的 `apply_theme()` |
| 分析日期 | 2026-04-19 |

---

## 1. 问题描述

在 Gallery / Playground 应用中，点击 Dark Mode 开关切换 light/dark 主题时，界面出现明显的卡顿（约 200-500ms 的冻结感），用户体验不佳。

---

## 2. 根因分析

经排查，卡顿由以下三个根因叠加导致：

### 根因 A：全局 QSS 渲染 + 每个组件实例重复渲染（双重渲染）

`ThemeEngine.switch_theme()` 的执行流程如下：

```
switch_theme("dark")
  ├── _render_all_templates()          # 渲染全部 24 个 .qss.j2 模板，拼接为全局 QSS
  │     └── render_qss() × 24         # 每个模板都执行 Jinja2 渲染
  ├── app.setStyleSheet(qss)           # 设置全局样式表 → Qt 遍历整棵 widget 树重新应用样式
  └── theme_changed.emit("dark")       # 触发所有 BaseWidget 子类的 apply_theme()
        ├── widget_1.apply_theme()
        │     └── render_qss("button.qss.j2")   # 再次渲染同一模板
        │     └── self.setStyleSheet(qss)        # 再次设置 per-widget 样式表
        ├── widget_2.apply_theme()
        │     └── render_qss("input.qss.j2")    # 再次渲染
        │     └── self.setStyleSheet(qss)        # 再次设置
        └── ... × N 个组件实例
```

**问题核心**：全局 `app.setStyleSheet()` 已经包含了所有组件的 QSS 规则，但绝大多数组件的 `apply_theme()` 又各自调用 `engine.render_qss()` 重新渲染模板并通过 `self.setStyleSheet()` 设置 per-widget 样式表。这导致：

1. **Jinja2 模板被重复渲染**：同一模板（如 `layout.qss.j2`）在全局渲染 1 次后，又被 TLayoutHeader、TLayoutFooter、TLayoutContent、TLayoutSider、TLayout 各渲染 1 次 = 共 6 次
2. **Qt 样式引擎被重复触发**：每次 `setStyleSheet()` 调用都会触发 Qt 对该 widget 及其子树的样式重新计算

**量化估算**（以 Gallery 为例）：
- 全局渲染：24 个模板 × 1 次 = 24 次 Jinja2 渲染
- 组件实例渲染：假设界面上有 50 个组件实例，每个调用 1 次 render_qss = 50 次 Jinja2 渲染
- 总计：~74 次 Jinja2 渲染 + 1 次全局 setStyleSheet + ~50 次 per-widget setStyleSheet

### 根因 B：Jinja2 模板未缓存

`render_qss()` 每次调用都执行完整的 Jinja2 模板渲染：

```python
def render_qss(self, template_name: str, **extra_context: Any) -> str:
    tokens = self._themes[self._current_theme]
    context = { "colors": tokens.colors, "spacing": tokens.spacing, ... }
    template = self._jinja_env.get_template(template_name)  # 模板对象有缓存
    return template.render(context)                          # 但渲染结果无缓存
```

虽然 Jinja2 的 `get_template()` 会缓存编译后的模板对象，但 `template.render(context)` 每次都会执行完整的字符串替换和拼接。对于 `button.qss.j2`（338 行）、`tag.qss.j2`（189 行）、`inputnumber.qss.j2`（170 行）等大模板，渲染开销不可忽略。

### 根因 C：theme_changed 信号同步触发所有组件

`theme_changed.emit()` 是同步调用，所有连接到该信号的 `apply_theme()` 槽函数在同一帧内依次执行。当组件数量较多时（Gallery 中可能有 50-100+ 个 BaseWidget 实例），所有 `apply_theme()` 的开销累加在一个事件循环迭代中，导致 UI 线程阻塞。

---

## 3. 解决方案

### 方案 A：引入 QSS 渲染缓存（核心优化）

在 `ThemeEngine` 中为每个主题缓存已渲染的 QSS 结果。同一主题下，模板只需渲染一次：

```python
class ThemeEngine(QObject):
    def __init__(self):
        self._qss_cache: dict[str, dict[str, str]] = {}  # theme -> {template: qss}
        self._global_qss_cache: dict[str, str] = {}       # theme -> global_qss

    def render_qss(self, template_name: str, **extra_context: Any) -> str:
        if not extra_context:  # 仅缓存无额外上下文的标准渲染
            cache = self._qss_cache.setdefault(self._current_theme, {})
            if template_name in cache:
                return cache[template_name]
            result = self._do_render(template_name)
            cache[template_name] = result
            return result
        return self._do_render(template_name, **extra_context)

    def switch_theme(self, theme_name: str) -> None:
        self._current_theme = theme_name
        app = QApplication.instance()
        if app is not None:
            if theme_name not in self._global_qss_cache:
                self._global_qss_cache[theme_name] = self._render_all_templates()
            app.setStyleSheet(self._global_qss_cache[theme_name])
        self.theme_changed.emit(theme_name)
```

**效果**：首次切换到某主题时渲染一次，后续切换回该主题时直接使用缓存，渲染开销降为 0。

### 方案 B：移除组件中冗余的 per-widget setStyleSheet 调用

根据 BUG-002 的经验（见 `02-Button和Tag类型样式不生效.md`），per-widget `setStyleSheet()` 会覆盖全局样式表中的属性选择器规则。大多数组件应该只做 `unpolish/polish` 来触发样式重新评估，而不是重新渲染和设置 per-widget 样式表。

对于确实需要 per-widget 样式的组件（如需要动态计算的样式），应使用缓存后的 QSS 而非重新渲染。

### 方案 C：批量抑制 UI 更新

在主题切换期间，使用 `setUpdatesEnabled(False)` 暂时禁止 UI 重绘，所有样式变更完成后再统一刷新：

```python
def switch_theme(self, theme_name: str) -> None:
    self._current_theme = theme_name
    app = QApplication.instance()
    if app is not None:
        # 暂停 UI 更新
        for widget in app.topLevelWidgets():
            widget.setUpdatesEnabled(False)

        qss = self._get_cached_global_qss(theme_name)
        app.setStyleSheet(qss)
        self.theme_changed.emit(theme_name)

        # 恢复 UI 更新，触发一次性重绘
        for widget in app.topLevelWidgets():
            widget.setUpdatesEnabled(True)
```

**效果**：避免中间状态的多次重绘，将 N 次重绘合并为 1 次。

---

## 4. 实施计划

| 优先级 | 方案 | 预期收益 | 风险 |
|--------|------|----------|------|
| P0 | 方案 A：QSS 渲染缓存 | 消除重复 Jinja2 渲染，减少 ~70% 的渲染开销 | 低：缓存逻辑简单，切换主题时自动命中缓存 |
| P0 | 方案 B：移除冗余 per-widget setStyleSheet | 消除 ~50 次冗余的 setStyleSheet 调用 | 中：需逐组件验证样式是否仍正确 |
| P1 | 方案 C：批量抑制 UI 更新 | 合并多次重绘为 1 次 | 低：标准 Qt 优化手段 |

---

## 5. 经验总结

> **规则 1：** 当使用 `QApplication.setStyleSheet()` 设置全局样式表时，组件的 `apply_theme()` 不应再调用 `self.setStyleSheet(render_qss(...))`。全局样式表已包含所有规则，per-widget 调用是冗余的且会覆盖全局属性选择器。

> **规则 2：** Jinja2 模板渲染结果应按主题缓存。Design Token 在同一主题下是不变的，因此同一模板 + 同一主题的渲染结果可以安全缓存。

> **规则 3：** 批量样式变更时应使用 `setUpdatesEnabled(False/True)` 包裹，避免中间状态的多次重绘。
