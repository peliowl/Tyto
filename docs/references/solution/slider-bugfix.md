# TSlider 组件问题修复记录

> 模块路径：`src/tyto_ui_lib/components/atoms/slider.py`
> 记录日期：2026-04-10

---

## 1. Reverse 模式下轨道填充颜色方向错误

**问题描述**

设置 `reverse=True` 后，轨道的绿色填充区域仍然从左侧开始绘制到滑块位置，而正确效果应为从滑块位置绘制到右侧边缘。

**根因分析**

`_SliderTrack.paintEvent` 中非 range 模式的水平填充区域绘制逻辑未区分 `reverse` 状态。`_frac_to_px` 已正确翻转了滑块的像素位置，但填充区域始终从左边缘画到滑块位置。

**修复方案**

在水平非 range 模式下增加 `self._reverse` 判断：

- 正常模式：从左边缘绘制到滑块位置
- 反转模式：从滑块位置绘制到右边缘

**涉及文件**

- `slider.py` — `_SliderTrack.paintEvent`
