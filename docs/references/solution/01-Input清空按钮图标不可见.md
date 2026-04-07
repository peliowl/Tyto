# BUG-001：TInput 清空按钮图标不可见

| 属性 | 值 |
|------|-----|
| 版本 | V1.0.1 |
| 严重程度 | 中 |
| 影响组件 | `TInput`、`TSearchBar` |
| 涉及文件 | `src/tyto_ui_lib/components/atoms/input.py` |
| 修复日期 | 2026-04-07 |

---

## 1. 问题描述

在 Gallery 中，将 `TInput` 的 `clearable` 属性设置为 `True` 后，输入文本时右侧未显示清空图标（✕）。密码模式下的可见性切换图标同样不可见。

**复现步骤：**

1. 启动 Gallery 应用 (`uv run python examples/gallery.py`)
2. 在左侧导航中选择 **Input** 组件
3. 在 **Clearable** 区块的输入框中输入任意文本
4. 观察输入框右侧 —— 预期出现清空图标，实际无任何图标显示

## 2. 根因分析

`TInput` 使用 `QLineEdit.addAction()` 将清空按钮和密码切换按钮添加为 trailing action。代码中通过 `QAction.setText()` 设置了 Unicode 字符作为图标：

```python
# 原始代码
self._clear_action = QAction(self._line_edit)
self._clear_action.setText("\u2715")  # Unicode X mark
self._line_edit.addAction(self._clear_action, QLineEdit.ActionPosition.TrailingPosition)
```

**根本原因：** `QLineEdit` 的 trailing/leading action 仅渲染 `QAction` 的 `icon` 属性，不渲染 `text` 属性。使用 `setText()` 设置的文本在 action 位置上不会产生任何可见输出。这是 Qt 框架的设计行为，而非 bug。

## 3. 解决方案

引入 `_text_icon()` 辅助函数，将 Unicode 字符渲染为 `QPixmap` 并封装为 `QIcon`，替代原有的 `setText()` 调用。

### 3.1 新增辅助函数

```python
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPixmap, QPainter

def _text_icon(char: str, size: int = 16, color: QColor | None = None) -> QIcon:
    """Create a QIcon by rendering a single Unicode character onto a pixmap."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setPen(color if color is not None else QColor("#667085"))
    font = QFont()
    font.setPixelSize(int(size * 0.75))
    painter.setFont(font)
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, char)
    painter.end()
    return QIcon(px)
```

### 3.2 修改点

| 位置 | 修改前 | 修改后 |
|------|--------|--------|
| 清空按钮初始化 | `setText("\u2715")` | `setIcon(_text_icon("\u2715"))` |
| 密码切换按钮初始化 | `setText("\u25cf")` | `setIcon(_text_icon("\u25cf"))` |
| 密码可见时切换图标 | `setText("\u25cb")` | `setIcon(_text_icon("\u25cb"))` |
| 密码隐藏时切换图标 | `setText("\u25cf")` | `setIcon(_text_icon("\u25cf"))` |

## 4. 影响范围

- **TInput**：清空按钮和密码切换按钮均已修复
- **TSearchBar**：内部组合了 `TInput`，自动受益于此修复，无需额外改动

## 5. 验证

```bash
uv run pytest tests/test_atoms/test_input.py tests/test_molecules/test_searchbar.py -q
# 18 passed
```

## 6. 经验总结

> **规则：** 在 `QLineEdit` 中使用 `addAction()` 添加 trailing/leading action 时，必须通过 `setIcon()` 设置图标，`setText()` 仅用于菜单等上下文，不会在输入框内渲染。
