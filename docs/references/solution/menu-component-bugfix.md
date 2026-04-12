# TMenu 组件问题修复记录

> 组件：`TMenu` / `TMenuItem` / `TMenuItemGroup`
> 文件：`src/tyto_ui_lib/components/organisms/menu.py`
> 日期：2026-04-11
> 状态：已修复（popup 样式优化待后续迭代）

---

## 目录

1. [mode 属性设置不生效](#1-mode-属性设置不生效)
2. [缺少图标属性设置](#2-缺少图标属性设置)
3. [水平模式文本被裁剪](#3-水平模式文本被裁剪)
4. [选中/hover 状态下多余边框](#4-选中hover-状态下多余边框)
5. [collapsed 属性导致界面空白](#5-collapsed-属性导致界面空白)
6. [所有菜单项显示为选中状态](#6-所有菜单项显示为选中状态)
7. [hover 效果失效](#7-hover-效果失效)
8. [菜单项宽度不一致](#8-菜单项宽度不一致)
9. [水平模式弹出子菜单闪烁](#9-水平模式弹出子菜单闪烁)
10. [展开收缩图标与 NaiveUI 不一致](#10-展开收缩图标与-naiveui-不一致)
11. [禁用状态样式显示错误](#11-禁用状态样式显示错误)
12. [父级菜单项未显示图标](#12-父级菜单项未显示图标)

---

## 1. mode 属性设置不生效

**现象**：在 Playground 中切换 mode 属性（vertical ↔ horizontal）无任何效果。

**根因**：三个独立问题叠加。

| 子问题 | 原因 | 涉及文件 |
|--------|------|----------|
| `str(Enum)` 比较失败 | `set_menu_mode` 中使用 `str(self._menu_mode) == "horizontal"` 判断，但 `str(MenuMode.HORIZONTAL)` 返回 `"MenuMode.HORIZONTAL"` | `menu.py` L434, L449 |
| 缺少 `set_mode` 方法 | `TMenu` 只在构造时接受 mode，无法运行时切换 | `menu.py` |
| Playground apply 为空操作 | `apply=lambda w, v: None` | `menu_props.py` |

**修复方案**：

```python
# 1. 枚举比较：str() → .value
self._menu_mode.value == "horizontal"

# 2. 新增 TMenu.set_mode()：清除旧布局 → 重建 → 重新添加子项 → 传播 mode

# 3. Playground 回调
apply=lambda w, v: w.set_mode(TMenu.MenuMode(v))
```

---

## 2. 缺少图标属性设置

**现象**：Playground 中无法为菜单项设置图标。

**根因**：`TMenuItem` 和 `TMenuItemGroup` 缺少运行时图标设置方法；Playground 未注册 icon 属性。

**修复方案**：

- 新增 `TMenuItem.set_icon(icon: QIcon | None)` 和 `TMenuItemGroup.set_icon(icon: QIcon | None)`
- `menu_props.py` 新增 `icon` 属性（`prop_type="file"`）

---

## 3. 水平模式文本被裁剪

**现象**：水平模式下菜单项文本右侧被截断（"Home" → "Ho"）。

**根因**：多个 Qt 布局机制问题叠加。

| 子问题 | 原因 |
|--------|------|
| QSS padding/margin 不影响 sizeHint | Qt QSS 的 `padding`、`margin` 是纯视觉属性，不参与 `sizeHint()` 计算 |
| text label stretch=1 | `addWidget(label, 1)` 允许 label 被压缩到接近 0 宽度 |
| fixedWidth(200) 约束残留 | `_make_menu` 的 `setFixedWidth(200)` 在切换水平模式后仍生效 |

**修复方案**：

```python
# 1. padding/margin 改为代码层 contentsMargins
row_layout.setContentsMargins(h_pad, 0, h_pad, 0)

# 2. 移除 stretch 因子
row_layout.addWidget(self._text_label)  # 无 stretch
row_layout.addStretch()

# 3. set_mode 切换水平时清除宽度约束
self.setMinimumWidth(0)
self.setMaximumWidth(16777215)
```

**经验总结**：Qt QSS 的 `padding`、`margin`、`min-height`、`max-height` 均不影响 `sizeHint()` 计算，必须通过代码层 API 控制。

---

## 4. 选中/hover 状态下多余边框

**现象**：水平模式下选中和 hover 的菜单项底部出现多余边框线。

**根因**：`border-bottom` 设置在内部 `#menu_item_row` 上，与 `max-height` 约束冲突导致溢出。

**修复方案**：将 `border-bottom` 从内部 row 移到 `TMenuItem` 本身。

```css
/* 修复后 */
TMenu[mode="horizontal"] TMenuItem {
    border-bottom: 2px solid transparent;
}
```

---

## 5. collapsed 属性导致界面空白

**现象**：水平模式下勾选 Collapsed 后整个菜单消失。

**根因**：collapsed 的宽度动画将菜单压缩到 48px，水平模式下所有内容被挤压。

**修复方案**：collapsed 仅适用于垂直菜单（与 NaiveUI 一致）。

```python
def set_collapsed(self, collapsed: bool) -> None:
    if self._mode == self.MenuMode.HORIZONTAL:
        self._collapsed = False
        return
```

---

## 6. 所有菜单项显示为选中状态

**现象**：垂直和水平模式下，所有菜单项文本均显示为绿色（选中色）。

**根因**：Qt QSS 祖先属性选择器在多层 stylesheet 叠加时行为不可靠。

| 阶段 | 尝试方案 | 结果 |
|------|---------|------|
| 第一次 | `unpolish/polish` 子 widget | 初始加载时仍全绿 |
| 第二次 | `set_mode` 末尾调用 `apply_theme()` | 水平模式修复，垂直仍有问题 |
| 第三次 | 移除 TMenuItem/TMenuItemGroup 的 `setStyleSheet` | 减少冲突但仍不稳定 |
| **最终方案** | 放弃 QSS 属性选择器，改为代码直接设置颜色 | 彻底解决 |

**最终修复**：新增 `_apply_active_colors()` 方法，通过 `setStyleSheet` 直接在 `_text_label` 和 `_icon_label` 上设置颜色。

```python
def _apply_active_colors(self) -> None:
    if effectively_disabled:
        color = engine.get_token("colors", "text_disabled")
    elif self._active:
        color = engine.get_token("colors", "primary")
    else:
        color = engine.get_token("colors", "text_primary")
    self._text_label.setStyleSheet(f"color: {color}; ...")
    self._icon_label.setStyleSheet(f"color: {icon_color}; ...")
```

**经验总结**：Qt QSS 的祖先属性选择器（`Parent[prop="val"] Child`）对后代 widget 的匹配行为不可靠，尤其在多层 `setStyleSheet` 叠加时。对于需要动态切换的样式属性，应通过代码直接设置，仅将静态样式交给 QSS。

---

## 7. hover 效果失效

**现象**：菜单项鼠标悬停无背景色变化。

**根因**：`_apply_active_colors` 在 `_row` 上设置了 inline `setStyleSheet`，覆盖了 TMenu QSS 中的 `:hover` 伪类规则。

**修复方案**：放弃 QSS `:hover`，改用 `enterEvent`/`leaveEvent` 在代码中控制 hover 背景。

```python
def enterEvent(self, event):
    hover_color = engine.get_token("colors", "hover_color")
    self.setStyleSheet(f"background-color: {hover_color}; ...")

def leaveEvent(self, event):
    self.setStyleSheet("")
```

**设计决策**：hover 背景设置在 `TMenuItem` 自身（而非内部 `_row`），确保 hover 背景覆盖整个菜单项宽度，不受子项缩进影响。

---

## 8. 菜单项宽度不一致

**现象**：同级菜单项中，`TMenuItemGroup` 比 `TMenuItem` 更宽。

**根因**：`TMenuItem._build_ui` 的外层 layout 有 `contentsMargins(8, 0, 8, 0)`，而 `TMenuItemGroup` 的外层 layout 是 `contentsMargins(0, 0, 0, 0)`，导致 TMenuItem 有效宽度少 16px。

**修复方案**：

- 移除 TMenuItem 外层 layout 的 margin，统一为 `contentsMargins(0, 0, 0, 0)`
- 内边距完全由 `_row` 的 `contentsMargins` 控制
- 为所有组件设置 `QSizePolicy.Expanding` 水平策略

---

## 9. 水平模式弹出子菜单闪烁

**现象**：水平模式下鼠标悬停在父级菜单项时，弹出子菜单反复出现/消失。

**根因**：popup 使用 `Qt.WindowType.Popup`，该类型抢占鼠标焦点，触发父 widget `leaveEvent`，形成 show→leave→hide→enter→show 无限循环。

**修复方案**：

```python
# 1. 窗口类型改为 Tool（不抢占焦点）
popup = QWidget(None,
    Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
    | Qt.WindowType.WindowStaysOnTopHint)
popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

# 2. eventFilter 监听 popup Enter/Leave
def eventFilter(self, obj, event):
    if obj is self._popup:
        if event.type() == QEvent.Type.Enter:
            self._hide_timer.stop()
        elif event.type() == QEvent.Type.Leave:
            self._hide_popup()
```

---

## 10. 展开收缩图标与 NaiveUI 不一致

**现象**：展开/收缩使用 Unicode 文本字符，与 NaiveUI 的 SVG chevron 风格不一致。

**修复方案**：参考 `TCollapse` 的 `_CollapseArrowWidget`，新增 `_MenuArrowWidget`，复用 NaiveUI ChevronRight SVG 路径，使用 `QPainter` + `QTransform` 绘制，展开时旋转 90°。

---

## 11. 禁用状态样式显示错误

**现象**：禁用菜单后文本和图标颜色未变为浅灰色。

**根因**：`_apply_active_colors` 未处理 disabled 状态，inline stylesheet 覆盖了 QSS 的 disabled 规则。

**修复方案**：`_apply_active_colors` 优先检查 disabled 状态，使用 `text_disabled` 颜色。`set_menu_disabled` 改为调用 `_apply_active_colors()` 刷新。

---

## 12. 父级菜单项未显示图标

**现象**：Playground 设置图标后，`TMenuItemGroup` 不显示图标。

**根因**：`_apply_icon` 只对 `TMenuItem` 调用 `set_icon`，遗漏了 `TMenuItemGroup`。

**修复方案**：`_apply_icon` 增加对 `TMenuItemGroup` 的 `set_icon` 调用。

---

## 待优化项

| 项目 | 描述 | 优先级 |
|------|------|--------|
| popup 子菜单样式 | hover 背景需左右内边距圆角、子分组显示右箭头、添加阴影 | P2 |
| 主题切换验证 | Dark 主题下菜单颜色需验证 | P2 |

---

## 关键技术经验

### Qt QSS 的局限性

1. **`padding`/`margin`/`min-height`/`max-height` 不影响 `sizeHint()`**：必须通过代码层 API 控制
2. **祖先属性选择器不可靠**：`Parent[prop="val"] Child` 在多层 stylesheet 叠加时匹配不确定
3. **inline `setStyleSheet` 覆盖 `:hover`**：widget 上设置 inline stylesheet 后，父级 QSS 的 `:hover` 失效
4. **`Qt.WindowType.Popup` 抢占鼠标**：触发父 widget `leaveEvent`，导致弹出菜单闪烁

### 推荐实践

- 动态样式（active/disabled/hover）通过代码直接设置
- 静态样式（字体大小、背景色基础值）通过 QSS 模板
- 弹出窗口使用 `Tool | FramelessWindowHint | WindowStaysOnTopHint` + `WA_ShowWithoutActivating`
- 布局尺寸控制使用代码层 API，不依赖 QSS
