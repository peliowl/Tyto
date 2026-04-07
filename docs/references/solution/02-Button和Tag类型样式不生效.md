# BUG-002：TButton / TTag 类型样式不生效

| 属性 | 值 |
|------|-----|
| 版本 | V1.0.1 |
| 严重程度 | 高 |
| 影响组件 | `TButton`、`TTag`、`TSearchBar`（间接）、`MessageShowcase`（间接） |
| 涉及文件 | `src/tyto_ui_lib/components/atoms/button.py`、`src/tyto_ui_lib/components/atoms/tag.py` |
| 修复日期 | 2026-04-07 |

---

## 1. 问题描述

在 Gallery 中，不同 `button_type`（Primary / Default / Dashed / Text）的 `TButton` 均显示为相同的默认白色背景和实线边框，无法区分类型。`TTag` 的不同 `tag_type` 同样无法显示对应的背景色和边框色。

**复现步骤：**

1. 启动 Gallery 应用
2. 选择 **Button** 组件，查看 **Types** 区块
3. 四个按钮（Primary / Default / Dashed / Text）外观完全一致

## 2. 根因分析

此问题由两个独立的根因叠加导致：

### 根因 A：per-widget `setStyleSheet()` 覆盖全局样式表

`ThemeEngine.switch_theme()` 已将所有组件的 QSS 规则（包含 `TButton[buttonType="primary"]` 等属性选择器）设置为全局样式表（`QApplication.setStyleSheet()`）。但 `TButton.apply_theme()` 又在组件实例上调用了 `self.setStyleSheet(qss)`：

```python
# 原始代码
def apply_theme(self) -> None:
    qss = engine.render_qss("button.qss.j2")
    self.setStyleSheet(qss)  # ← 问题所在
```

在 Qt 的样式表优先级模型中，per-widget stylesheet 的优先级高于 application-level stylesheet。当 per-widget stylesheet 中包含 `TButton { ... }` 基础规则时，它会覆盖全局样式表中更具体的 `TButton[buttonType="primary"]` 选择器，因为 Qt 在 per-widget 上下文中对类名选择器的解析行为与全局上下文不同。

### 根因 B：缺少 `WA_StyledBackground` 属性

`TButton` 和 `TTag` 继承自 `QWidget`（而非 `QPushButton`）。Qt 中，纯 `QWidget` 子类默认不绘制 QSS 定义的 `background-color` 和 `border`。必须显式启用 `WA_StyledBackground` 属性，Qt 的样式引擎才会为该 widget 绘制背景和边框。

**诊断验证：**

```python
btn = TButton("Primary", button_type=TButton.ButtonType.PRIMARY)
print(btn.testAttribute(Qt.WidgetAttribute.WA_StyledBackground))  # False
print(btn.palette().color(btn.palette().ColorRole.Window).name())  # #18a058 ← QSS 已匹配
```

palette 数据证明 QSS 属性选择器已正确匹配（颜色值正确），但由于 `WA_StyledBackground=False`，Qt 不会将这些样式绘制到屏幕上。

## 3. 解决方案

### 3.1 移除 per-widget `setStyleSheet()` 调用

将 `apply_theme()` 改为仅执行 `unpolish/polish` 强制 Qt 重新评估全局样式表：

```python
# 修复后
def apply_theme(self) -> None:
    engine = ThemeEngine.instance()
    if not engine.current_theme():
        return
    self.style().unpolish(self)
    self.style().polish(self)
    self.update()
```

### 3.2 启用 `WA_StyledBackground`

在组件 `__init__` 中添加：

```python
self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
```

### 3.3 修改汇总

| 文件 | 修改内容 |
|------|----------|
| `button.py` `__init__` | 添加 `setAttribute(WA_StyledBackground, True)` |
| `button.py` `apply_theme()` | 移除 `setStyleSheet()`，保留 `unpolish/polish` |
| `tag.py` `__init__` | 添加 `setAttribute(WA_StyledBackground, True)` |
| `tag.py` `apply_theme()` | 移除 `setStyleSheet()`，保留 `unpolish/polish` |
| `test_button.py` | 更新测试断言：从检查 per-widget stylesheet 改为检查 global stylesheet |

## 4. 影响范围

- **TButton**：所有四种类型（Primary / Default / Dashed / Text）现在正确显示对应样式
- **TTag**：所有五种颜色类型（Default / Primary / Success / Warning / Error）现在正确显示
- **TSearchBar**：内部的 TButton 自动受益
- **MessageShowcase**：触发按钮样式自动修复

## 5. 验证

```bash
uv run pytest --tb=short -q
# 147 passed
```

## 6. 经验总结

> **规则 1：** 继承自 `QWidget` 的自定义组件若需要 QSS 绘制背景和边框，必须设置 `WA_StyledBackground = True`。`QPushButton`、`QFrame` 等内置控件已默认启用此行为，但纯 `QWidget` 子类不会。

> **规则 2：** 当使用 `QApplication.setStyleSheet()` 设置全局样式表时，组件的 `apply_theme()` 不应再调用 `self.setStyleSheet()`。per-widget stylesheet 会覆盖全局样式表中的属性选择器规则，导致类型区分失效。正确做法是仅调用 `unpolish/polish` 触发样式重新评估。

> **规则 3：** 诊断 QSS 样式问题时，应区分"选择器是否匹配"和"样式是否被绘制"两个层面。通过 `palette()` 可验证选择器匹配情况，通过 `WA_StyledBackground` 可验证绘制行为。
