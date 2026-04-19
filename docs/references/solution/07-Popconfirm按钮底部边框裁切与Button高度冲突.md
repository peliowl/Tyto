# BUG-007：Popconfirm 弹窗按钮底部边框裁切 / TButton setFixedHeight 与 QSS border 高度冲突

| 属性 | 值 |
|------|-----|
| 版本 | V1.1.0 |
| 严重程度 | 中 |
| 影响组件 | `TButton`、`TPopconfirm` |
| 涉及文件 | `src/tyto_ui_lib/components/atoms/button.py`、`src/tyto_ui_lib/styles/templates/popconfirm.qss.j2` |
| 修复日期 | 2026-04-18 |

---

## 1. 问题描述

在 Gallery 和 Playground 的 Popconfirm 弹窗中，取消按钮和确认按钮的底部边框被裁切，无法看到完整的底部边界线。

**复现步骤：**

1. 启动 Gallery 应用
2. 选择 **Popconfirm** 组件
3. 点击任意触发按钮弹出确认框
4. 观察弹窗中"取消"和"确认"按钮的底部边框被截断

## 2. 根因分析

### 2.1 核心矛盾：`setFixedHeight` 与 QSS `min-height` + `border` 的冲突

通过编写诊断脚本，获取运行时实际尺寸数据：

```
btn_row: h=24
Button[0]: h=24, geo=QRect(0, 1, 80, 24)   ← y=1，非 y=0
Button[1]: h=24, geo=QRect(88, 1, 80, 24)
maxH=22, minH=24                             ← min > max 冲突！
Button[0] bottom=25, btn_row h=24, clipped=True
```

**关键发现：** 按钮的 `minimumHeight=24` 大于 `maximumHeight=22`，这是一个 min > max 的矛盾状态。

**矛盾来源：**

| 约束来源 | 设置方式 | 值 |
|----------|----------|-----|
| Python 代码 | `setFixedHeight(22)` | maxHeight=22, minHeight=22 |
| QSS 模板 | `min-height: 22px` + `border: 1px solid` | 实际最小高度 = 22 + 1(top) + 1(bottom) = **24px** |

在 Qt 的盒模型中，QSS 的 `min-height` 指定的是**内容区域**的最小高度。当同时存在 `border: 1px solid` 时，Qt 会在 `min-height` 基础上叠加边框宽度，使得实际最小高度变为 `22 + 2 = 24px`。

而 Python 代码中的 `setFixedHeight(22)` 同时设置了 `minimumHeight=22` 和 `maximumHeight=22`。但 QSS 的 `min-height` 计算结果（24px）覆盖了 Python 设置的 `minimumHeight`，导致最终状态为：

- `minimumHeight = 24`（QSS 计算结果）
- `maximumHeight = 22`（Python setFixedHeight）

Qt 在 min > max 时取 min 值，按钮实际渲染为 24px。但布局系统基于 `maximumHeight=22` 分配空间，导致按钮溢出 2px，底部边框被父容器裁切。

### 2.2 附带问题：Popconfirm 容器 QSS 双重样式

`_PopconfirmContainer` 通过 `paintEvent()` 手动绘制背景和边框，但 QSS 模板中也定义了 `border` 和 `background-color`。QSS 的 `border` 会参与盒模型计算，进一步压缩容器内部可用空间。

## 3. 解决方案

### 3.1 修复 TButton 高度计算（核心修复）

在 `_apply_size_from_tokens()` 中，将 `setFixedHeight(h)` 改为 `setFixedHeight(h + 2)`，使 Python 设置的固定高度与 QSS 计算的最小高度一致：

```python
# 修复前
if h > 0:
    self.setFixedHeight(h)      # h=22，但 QSS 实际需要 24

# 修复后
if h > 0:
    self.setFixedHeight(h + 2)  # h=22 + 2(border) = 24，与 QSS 一致
```

同步修改 `sizeHint()` 返回值，确保布局系统获取正确的推荐尺寸：

```python
# 修复前
return QSize(80, h)             # h=22

# 修复后
border_extra = 2
return QSize(80, h + border_extra)  # h=22 + 2 = 24
```

### 3.2 修复 Popconfirm 容器 QSS 双重样式

移除 `popconfirm.qss.j2` 中 `#popconfirm_container` 的 `border` 和 `background-color`（由 `paintEvent` 负责绘制），避免 QSS border 参与盒模型计算：

```css
/* 修复前 */
QWidget#popconfirm_container {
    background-color: {{ colors.popover_color }};
    border: 1px solid {{ colors.border }};
    border-radius: {{ radius.medium }}px;
    padding: {{ spacing.large }}px;
    ...
}

/* 修复后 */
QWidget#popconfirm_container {
    background-color: transparent;
    border: none;
    ...
}
```

### 3.3 修改汇总

| 文件 | 修改内容 |
|------|----------|
| `button.py` `_apply_size_from_tokens()` | `setFixedHeight(h)` → `setFixedHeight(h + 2)` |
| `button.py` `sizeHint()` | 返回高度增加 `border_extra = 2` |
| `popconfirm.qss.j2` | 移除 `#popconfirm_container` 的 `border`、`background-color`、`padding`（由 `paintEvent` 和 Python layout margins 负责） |
| `popconfirm.py` `_build_popup()` | 容器底部 margin 从 12 调整为 14 |

## 4. 影响范围

- **TButton**：所有尺寸变体（Tiny/Small/Medium/Large）的高度均正确包含边框宽度
- **TPopconfirm**：弹窗中按钮的底部边框完整显示
- **Gallery/Playground**：所有使用 TButton 的场景均受益于高度修复

## 5. 验证

### 5.1 诊断脚本验证（修复后）

```
btn_row: h=24
Button[0]: h=24, geo=QRect(0, 0, 80, 24)   ← y=0，正确对齐
Button[1]: h=24, geo=QRect(88, 0, 80, 24)
maxH=16777215, minH=24                      ← 无冲突
Button[0] bottom=24, btn_row h=24, clipped=False
Button[1] bottom=24, btn_row h=24, clipped=False
```

### 5.2 单元测试

```bash
uv run pytest tests/test_atoms/test_button.py -v
# 20 passed
```

## 6. 经验总结

> **规则 1：** 在 Qt 的 QSS 盒模型中，`min-height` 指定的是内容区域高度，`border` 宽度会额外叠加。因此 Python 代码中的 `setFixedHeight(h)` 必须使用 `h + 2 * border_width` 才能与 QSS 的 `min-height: h` + `border: 1px solid` 保持一致。否则会出现 min > max 的矛盾，导致布局溢出裁切。

> **规则 2：** 当组件通过 `paintEvent()` 手动绘制背景和边框时，QSS 模板中不应再定义 `border` 和 `background-color`。`paintEvent` 的绘制是纯视觉的，不影响布局；而 QSS 的 `border` 会参与盒模型计算，压缩内容区域。两者同时存在会导致双重边框和空间不足。

> **规则 3：** 排查控件裁切问题时，应编写诊断脚本打印运行时的 `geometry()`、`minimumHeight()`、`maximumHeight()` 等数据，对比父容器与子控件的实际尺寸关系，定位 `clipped = (child_bottom > parent_height)` 的具体位置。
