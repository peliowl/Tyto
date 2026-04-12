# TPopconfirm 组件问题修复记录

> 模块路径：`src/tyto_ui_lib/components/molecules/popconfirm.py`
> 记录日期：2026-04-10

---

## 1. 弹窗在任务栏生成独立窗口

**问题描述**

点击触发 TPopconfirm 弹窗后，Windows 任务栏中出现了一个新的窗口条目，而非仅在应用内部显示。

**根因分析**

弹窗使用 `Qt.WindowType.Window` 标志且 `parent=None` 创建，在 Windows 系统中被视为独立顶级窗口。

**修复方案**

将窗口类型从 `Window` 改为 `Tool`，并设置 `self.window()` 为父窗口。`Qt.WindowType.Tool` 不会在任务栏创建条目。

**涉及文件**

- `popconfirm.py` — `_build_popup`

---

## 2. 弹窗在切换应用后仍置顶显示

**问题描述**

弹出 TPopconfirm 后切换到其他应用程序，弹窗仍然显示在最顶层，遮挡其他软件。

**根因分析**

`Qt.WindowType.WindowStaysOnTopHint` 标志使弹窗在系统级别保持置顶，不受应用焦点影响。

**修复方案**

移除 `WindowStaysOnTopHint`，并将弹窗的 parent 设为 `self.window()`。`Tool` 类型的子窗口会自动在其父窗口之上显示，但不会遮挡其他应用：

```python
popup = QWidget(
    self.window(),
    Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
)
```

**涉及文件**

- `popconfirm.py` — `_build_popup`
