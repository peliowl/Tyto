# TCollapse 组件问题修复记录

> 模块路径：`src/tyto_ui_lib/components/molecules/collapse.py`
> Playground 定义：`examples/playground/definitions/collapse_props.py`
> 记录日期：2026-04-10

---

## 1. 展开/收缩面板时界面抖动

**问题描述**

点击面板标题展开或收缩内容区域时，整个 Collapse 控件及其父容器出现明显的抖动/闪烁。

**根因分析**

1. 展开动画开始时，`_content_wrapper` 先被设为 `setVisible(True)` 再设为 `setMaximumHeight(16777215)` 获取 `sizeHint`，导致内容区域在一帧内以全尺寸闪现。
2. 动画过程中 `maximumHeight` 逐帧变化，父布局（Playground 的 `AlignCenter` 容器）每帧重新计算位置，导致整个控件上下跳动。

**修复方案**

1. 展开时先设 `setMaximumHeight(0)` 再 `setVisible(True)`，防止全尺寸闪现。
2. 动画开始前锁定父 TCollapse 的 `minimumHeight`，动画结束后释放。

**涉及文件**

- `collapse.py` — `_animate_toggle`、`_on_expand_finished`、`_on_collapse_finished`

---

## 2. Playground 演示界面缺少属性控制

**问题描述**

Collapse 的 Playground 属性面板仅有 Accordion 和 Arrow Placement 两个属性，缺少触发区域、自定义标题、标题栏额外内容、自定义箭头图标的设置。

**修复方案**

在 `collapse_props.py` 中新增以下属性定义：

| 属性名 | 类型 | 说明 |
|--------|------|------|
| `trigger_areas` | enum | 触发区域预设（main / arrow / extra / 组合） |
| `custom_title` | str | 自定义标题文本输入（Panel 1） |
| `header_extra` | bool | 标题栏右侧额外按钮开关（Panel 1） |
| `arrow_preset` | enum | 预设箭头图标（▶ ★ ✕ ✔ ● ◆） |
| `arrow_file` | file | 自定义箭头图标文件选择（Panel 1） |

**涉及文件**

- `examples/playground/definitions/collapse_props.py`
