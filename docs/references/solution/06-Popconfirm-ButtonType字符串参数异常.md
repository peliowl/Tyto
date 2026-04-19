# BUG-006：Popconfirm 弹窗中 TButton 创建时 button_type 参数类型异常

| 属性 | 值 |
|------|-----|
| 版本 | V1.1.0 |
| 严重程度 | 高 |
| 影响组件 | `TPopconfirm`、`TButton` |
| 涉及文件 | `src/tyto_ui_lib/components/atoms/button.py`、`examples/gallery/showcases/popconfirm_showcase.py` |
| 修复日期 | 2026-04-18 |

---

## 1. 问题描述

在 Gallery 的 Popconfirm 界面中，点击 Button Customization 区块的按钮后，弹出异常：

```
AttributeError: 'str' object has no attribute 'value'
```

**完整调用栈：**

```
File "popconfirm.py", line 555, in _build_popup
    cancel_btn = TButton(**cancel_kwargs)
File "button.py", line 266, in __init__
    self.setProperty("buttonType", button_type.value)
                                   ^^^^^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'value'
```

**复现步骤：**

1. 启动 Gallery 应用
2. 选择 **Popconfirm** 组件
3. 在 **Button Customization** 区块中点击任意按钮
4. 弹出 `AttributeError` 异常

## 2. 根因分析

`TPopconfirm._build_popup()` 构建弹窗按钮时，先创建默认 kwargs 字典（`button_type` 为 `ButtonType` 枚举），然后通过 `dict.update()` 合并用户自定义的 `positive_button_props` / `negative_button_props`：

```python
# _build_popup() 中的代码
cancel_kwargs = {
    "button_type": TButton.ButtonType.DEFAULT,  # 枚举类型
    "size": TButton.ButtonSize.TINY,
    ...
}
cancel_kwargs.update(self._negative_button_props)  # 用户 props 覆盖
cancel_btn = TButton(**cancel_kwargs)
```

而 `popconfirm_showcase.py` 中传入的 props 使用了字符串值：

```python
positive_button_props={"button_type": "primary"},   # 字符串，非枚举
negative_button_props={"button_type": "default"},    # 字符串，非枚举
```

`dict.update()` 将枚举值覆盖为字符串后，`TButton.__init__` 中执行 `button_type.value` 时，对字符串调用 `.value` 属性导致 `AttributeError`。

## 3. 解决方案

在 `TButton.__init__` 入口处增加类型防御，将字符串参数自动转换为对应枚举：

```python
# button.py __init__ 中新增
if isinstance(button_type, str):
    button_type = self.ButtonType(button_type)
if isinstance(size, str):
    size = self.ButtonSize(size)
```

### 修改汇总

| 文件 | 修改内容 |
|------|----------|
| `button.py` `__init__` | 在 mixin 初始化之后、属性赋值之前，增加 `button_type` 和 `size` 的字符串到枚举自动转换逻辑 |

## 4. 影响范围

- **TPopconfirm**：自定义按钮 props 中使用字符串类型的 `button_type` 不再抛出异常
- **TButton**：所有通过 dict kwargs 传入字符串类型参数的场景均自动兼容
- **Playground**：属性面板动态修改 `button_type` 时的字符串值也能正确处理

## 5. 验证

```bash
uv run pytest tests/test_atoms/test_button.py -v
# 20 passed
```

## 6. 经验总结

> **规则 1：** 当组件的构造参数接受枚举类型，且该参数可能通过 `dict` 动态传入时（如 `**kwargs` 展开），必须在入口处增加字符串到枚举的防御性转换。`str(Enum)` 的 `.value` 属性在字符串上不存在，是常见的运行时陷阱。

> **规则 2：** `dict.update()` 会静默覆盖已有键的值和类型，不会进行任何类型检查。在合并用户自定义 props 到默认 kwargs 时，应预期值类型可能与默认值不一致。
