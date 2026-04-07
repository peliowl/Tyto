# 设计文档：Tyto UI 组件库 V1.0.0

## 概述

Tyto 是一个基于 PySide6 的现代化桌面 UI 组件库，采用原子设计方法论（Atomic Design），提供从基础控件（Atom）到复杂业务模块（Organism）的分层组件体系。样式系统基于 Design Token + Jinja2 + QSS 的动态渲染架构，支持 Light/Dark 主题实时无闪烁切换。视觉风格仿 NaiveUI。

本设计文档覆盖 V1.0.0 的全部交付内容：主题引擎、组件基类与行为混入、11 个 UI 组件、工程化配置和组件预览画廊。

## 架构

### 整体分层架构

```mermaid
graph TB
    subgraph Application["应用层"]
        Gallery["Gallery 预览画廊"]
    end

    subgraph Components["组件层"]
        Organisms["Organisms<br/>Message, Modal"]
        Molecules["Molecules<br/>SearchBar, Breadcrumb, InputGroup"]
        Atoms["Atoms<br/>Button, Checkbox, Radio,<br/>Input, Switch, Tag"]
    end

    subgraph Foundation["基础层"]
        BaseWidget["Base Widget"]
        Mixins["Mixins<br/>HoverEffect, ClickRipple,<br/>FocusGlow, Draggable"]
        ThemeEngine["Theme Engine"]
        Tokens["Design Tokens<br/>JSON/TOML"]
        Templates["Jinja2 QSS Templates"]
    end

    Gallery --> Organisms
    Gallery --> Molecules
    Gallery --> Atoms
    Organisms --> Molecules
    Organisms --> Atoms
    Molecules --> Atoms
    Atoms --> BaseWidget
    BaseWidget --> Mixins
    BaseWidget --> ThemeEngine
    ThemeEngine --> Tokens
    ThemeEngine --> Templates
```

### 主题引擎渲染流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant TE as ThemeEngine
    participant TF as Token 文件 (JSON/TOML)
    participant J2 as Jinja2 引擎
    participant QApp as QApplication

    User->>TE: switch_theme("dark")
    TE->>TF: 加载 dark 主题 Token
    TF-->>TE: Token 字典
    TE->>J2: render(template, tokens)
    J2-->>TE: QSS 字符串
    TE->>QApp: setStyleSheet(qss)
    TE-->>TE: 发射 theme_changed 信号
    Note over QApp: 所有 BaseWidget 子类<br/>自动响应信号更新样式
```

### 组件状态机

```mermaid
stateDiagram-v2
    [*] --> Normal
    Normal --> Hovered : mouseEnter
    Hovered --> Normal : mouseLeave
    Hovered --> Pressed : mousePress
    Pressed --> Hovered : mouseRelease
    Normal --> Focused : focusIn
    Focused --> Normal : focusOut
    Focused --> Hovered : mouseEnter
    Normal --> Disabled : setDisabled(True)
    Disabled --> Normal : setDisabled(False)
    Normal --> Loading : setLoading(True)
    Loading --> Normal : setLoading(False)
```

## 组件与接口

### 1. 核心模块 (`core/`)

#### ThemeEngine（单例）

```python
class ThemeEngine(QObject):
    """主题引擎，管理 Design Token 并动态渲染 QSS。"""

    # 信号
    theme_changed = Signal(str)  # 参数: 主题名称 ("light" | "dark")

    # 公开方法
    def load_tokens(self, path: str | Path) -> None:
        """从 JSON/TOML 文件加载 Design Token 定义。
        Raises: TokenFileError 当文件格式错误时。
        """

    def switch_theme(self, theme_name: str) -> None:
        """切换主题并重新渲染所有样式。"""

    def get_token(self, key: str) -> str:
        """获取当前主题下指定 Token 的值。"""

    def current_theme(self) -> str:
        """返回当前主题名称。"""

    def render_qss(self, template_name: str, **extra_context) -> str:
        """使用 Jinja2 渲染指定模板为 QSS 字符串。"""
```

#### DesignToken 数据结构

```python
@dataclass
class DesignTokenSet:
    """一套完整的 Design Token 定义。"""
    colors: dict[str, str]       # 如 {"primary": "#18a058", ...}
    spacing: dict[str, int]      # 如 {"small": 4, "medium": 8, ...}
    radius: dict[str, int]       # 如 {"small": 2, "medium": 4, ...}
    font_sizes: dict[str, int]   # 如 {"small": 12, "medium": 14, ...}
    shadows: dict[str, str]      # 如 {"small": "0 2px 8px ...", ...}
```

### 2. 通用模块 (`common/`)

#### BaseWidget

```python
class BaseWidget(QWidget):
    """所有 Tyto 组件的基类。"""

    def __init__(self, parent: QWidget | None = None) -> None: ...

    def apply_theme(self) -> None:
        """从 ThemeEngine 获取当前 Token 并更新自身样式。"""

    def _on_theme_changed(self, theme_name: str) -> None:
        """主题变更信号的槽函数。"""

    def cleanup(self) -> None:
        """销毁前的清理逻辑，断开信号连接。"""
```

#### Mixin 体系 (`common/traits/`)

```python
class HoverEffectMixin:
    """鼠标悬停效果混入：200ms 背景色渐变 + PointingHand 光标。"""
    def enterEvent(self, event: QEnterEvent) -> None: ...
    def leaveEvent(self, event: QEvent) -> None: ...

class ClickRippleMixin:
    """点击效果混入：背景色加深 + Scale 0.98 下陷。"""
    def mousePressEvent(self, event: QMouseEvent) -> None: ...
    def mouseReleaseEvent(self, event: QMouseEvent) -> None: ...

class FocusGlowMixin:
    """焦点光晕混入：2px 半透明主色扩散光晕。"""
    def focusInEvent(self, event: QFocusEvent) -> None: ...
    def focusOutEvent(self, event: QFocusEvent) -> None: ...

class DisabledMixin:
    """禁用状态混入：0.5 透明度 + Forbidden 光标。"""
    def set_disabled_style(self, disabled: bool) -> None: ...
```

### 3. 原子组件 (`components/atoms/`)

#### Button

```python
class TButton(BaseWidget, HoverEffectMixin, ClickRippleMixin, FocusGlowMixin):
    """按钮组件，支持 Primary/Default/Dashed/Text 四种类型。"""

    class ButtonType(str, Enum):
        PRIMARY = "primary"
        DEFAULT = "default"
        DASHED = "dashed"
        TEXT = "text"

    # 信号
    clicked = Signal()

    def __init__(
        self,
        text: str = "",
        button_type: ButtonType = ButtonType.DEFAULT,
        loading: bool = False,
        disabled: bool = False,
        parent: QWidget | None = None,
    ) -> None: ...

    def set_loading(self, loading: bool) -> None: ...
    def set_disabled(self, disabled: bool) -> None: ...
```

#### Checkbox

```python
class TCheckbox(BaseWidget, HoverEffectMixin, FocusGlowMixin):
    """复选框组件，支持三态。"""

    class CheckState(IntEnum):
        UNCHECKED = 0
        CHECKED = 1
        INDETERMINATE = 2

    # 信号
    state_changed = Signal(int)  # CheckState 值

    def __init__(
        self,
        label: str = "",
        state: CheckState = CheckState.UNCHECKED,
        parent: QWidget | None = None,
    ) -> None: ...

    def set_state(self, state: CheckState) -> None: ...
    def get_state(self) -> CheckState: ...
    def toggle(self) -> None: ...
```

#### Radio / RadioGroup

```python
class TRadio(BaseWidget, HoverEffectMixin, FocusGlowMixin):
    """单选框组件。"""
    toggled = Signal(bool)

    def __init__(
        self,
        label: str = "",
        value: Any = None,
        checked: bool = False,
        parent: QWidget | None = None,
    ) -> None: ...

    def set_checked(self, checked: bool) -> None: ...
    def is_checked(self) -> bool: ...

class TRadioGroup(BaseWidget):
    """单选框分组管理器。"""
    selection_changed = Signal(object)  # 选中项的 value

    def add_radio(self, radio: TRadio) -> None: ...
    def get_selected_value(self) -> Any: ...
```

#### Input

```python
class TInput(BaseWidget, FocusGlowMixin):
    """输入框组件，支持前后缀图标、清空、密码模式。"""

    # 信号
    text_changed = Signal(str)
    cleared = Signal()

    def __init__(
        self,
        placeholder: str = "",
        clearable: bool = False,
        password: bool = False,
        prefix_icon: QIcon | None = None,
        suffix_icon: QIcon | None = None,
        parent: QWidget | None = None,
    ) -> None: ...

    def get_text(self) -> str: ...
    def set_text(self, text: str) -> None: ...
    def clear(self) -> None: ...
    def toggle_password_visibility(self) -> None: ...
```

#### Switch

```python
class TSwitch(BaseWidget, HoverEffectMixin):
    """开关组件，仿 iOS/NaiveUI 风格。"""

    toggled = Signal(bool)

    def __init__(
        self,
        checked: bool = False,
        disabled: bool = False,
        parent: QWidget | None = None,
    ) -> None: ...

    def is_checked(self) -> bool: ...
    def set_checked(self, checked: bool) -> None: ...
    def toggle(self) -> None: ...
```

#### Tag

```python
class TTag(BaseWidget):
    """标签组件，支持多尺寸和可关闭。"""

    class TagSize(str, Enum):
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class TagType(str, Enum):
        DEFAULT = "default"
        PRIMARY = "primary"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    closed = Signal()

    def __init__(
        self,
        text: str = "",
        tag_type: TagType = TagType.DEFAULT,
        size: TagSize = TagSize.MEDIUM,
        closable: bool = False,
        parent: QWidget | None = None,
    ) -> None: ...
```

### 4. 分子组件 (`components/molecules/`)

#### SearchBar

```python
class TSearchBar(BaseWidget):
    """搜索栏组件，由 TInput + TButton 组合。"""

    search_changed = Signal(str)
    search_submitted = Signal(str)

    def __init__(
        self,
        placeholder: str = "搜索...",
        clearable: bool = True,
        parent: QWidget | None = None,
    ) -> None: ...

    def get_text(self) -> str: ...
    def clear(self) -> None: ...
```

#### Breadcrumb

```python
@dataclass
class BreadcrumbItem:
    label: str
    data: Any = None

class TBreadcrumb(BaseWidget):
    """面包屑导航组件。"""

    item_clicked = Signal(int, object)  # (index, data)

    def __init__(
        self,
        items: list[BreadcrumbItem] | None = None,
        separator: str = "/",
        parent: QWidget | None = None,
    ) -> None: ...

    def set_items(self, items: list[BreadcrumbItem]) -> None: ...
    def get_items(self) -> list[BreadcrumbItem]: ...
```

#### InputGroup

```python
class TInputGroup(BaseWidget):
    """输入组合组件，紧凑横向排列子组件并自动合并圆角。"""

    def __init__(self, parent: QWidget | None = None) -> None: ...

    def add_widget(self, widget: QWidget) -> None: ...
    def insert_widget(self, index: int, widget: QWidget) -> None: ...
    def remove_widget(self, widget: QWidget) -> None: ...
    def _recalculate_radius(self) -> None:
        """重新计算所有子组件的圆角合并规则。"""
```

### 5. 有机体组件 (`components/organisms/`)

#### Message

```python
class MessageType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class TMessage(BaseWidget):
    """单条消息气泡。"""
    closed = Signal()

    def __init__(
        self,
        text: str,
        msg_type: MessageType = MessageType.INFO,
        duration: int = 3000,
        parent: QWidget | None = None,
    ) -> None: ...

    def show_message(self) -> None: ...
    def close_message(self) -> None: ...

class MessageManager(QObject):
    """全局消息管理器（单例），管理消息堆叠。"""

    @classmethod
    def info(cls, text: str, duration: int = 3000) -> None: ...
    @classmethod
    def success(cls, text: str, duration: int = 3000) -> None: ...
    @classmethod
    def warning(cls, text: str, duration: int = 3000) -> None: ...
    @classmethod
    def error(cls, text: str, duration: int = 3000) -> None: ...

    def _update_positions(self) -> None:
        """重新计算所有可见消息的堆叠位置。"""
```

#### Modal

```python
class TModal(BaseWidget):
    """模态对话框组件。"""

    closed = Signal()

    def __init__(
        self,
        title: str = "",
        closable: bool = True,
        mask_closable: bool = True,
        parent: QWidget | None = None,
    ) -> None: ...

    def set_content(self, widget: QWidget) -> None: ...
    def set_footer(self, widget: QWidget) -> None: ...
    def open(self) -> None: ...
    def close(self) -> None: ...
```

### 6. 样式模块 (`styles/`)

```
styles/
├── templates/
│   ├── base.qss.j2          # 基础样式模板
│   ├── button.qss.j2        # Button 专用模板
│   ├── checkbox.qss.j2
│   ├── radio.qss.j2
│   ├── input.qss.j2
│   ├── switch.qss.j2
│   ├── tag.qss.j2
│   ├── searchbar.qss.j2
│   ├── breadcrumb.qss.j2
│   ├── inputgroup.qss.j2
│   ├── message.qss.j2
│   └── modal.qss.j2
└── tokens/
    ├── light.json            # Light 主题 Token
    └── dark.json             # Dark 主题 Token
```

Jinja2 QSS 模板示例：

```jinja2
{# button.qss.j2 #}
TButton {
    background-color: {{ colors.bg_default }};
    color: {{ colors.text_primary }};
    border: 1px solid {{ colors.border }};
    border-radius: {{ radius.medium }}px;
    padding: {{ spacing.small }}px {{ spacing.medium }}px;
    font-size: {{ font_sizes.medium }}px;
}

TButton[buttonType="primary"] {
    background-color: {{ colors.primary }};
    color: {{ colors.white }};
    border: none;
}

TButton:hover {
    background-color: {{ colors.primary_hover }};
}

TButton:disabled {
    opacity: 0.5;
}
```

## 数据模型

### Design Token JSON 结构

```json
{
  "name": "light",
  "colors": {
    "primary": "#18a058",
    "primary_hover": "#36ad6a",
    "primary_pressed": "#0c7a43",
    "success": "#18a058",
    "warning": "#f0a020",
    "error": "#d03050",
    "info": "#2080f0",
    "bg_default": "#ffffff",
    "bg_elevated": "#f8f8fa",
    "text_primary": "#333639",
    "text_secondary": "#667085",
    "text_disabled": "#c2c2c2",
    "border": "#e0e0e6",
    "border_focus": "#18a058",
    "white": "#ffffff",
    "mask": "rgba(0, 0, 0, 0.4)"
  },
  "spacing": {
    "small": 4,
    "medium": 8,
    "large": 16,
    "xlarge": 24
  },
  "radius": {
    "small": 2,
    "medium": 4,
    "large": 8
  },
  "font_sizes": {
    "small": 12,
    "medium": 14,
    "large": 16,
    "xlarge": 20
  },
  "shadows": {
    "small": "0 2px 8px rgba(0, 0, 0, 0.08)",
    "medium": "0 4px 16px rgba(0, 0, 0, 0.12)",
    "large": "0 8px 32px rgba(0, 0, 0, 0.16)"
  }
}
```

### 组件状态枚举

```python
class WidgetState(str, Enum):
    """组件交互状态。"""
    NORMAL = "normal"
    HOVERED = "hovered"
    PRESSED = "pressed"
    FOCUSED = "focused"
    DISABLED = "disabled"
    LOADING = "loading"
```

### 消息堆叠模型

```python
@dataclass
class MessageSlot:
    """消息在堆叠中的位置信息。"""
    message: TMessage
    y_offset: int        # 距离屏幕顶部的偏移量
    created_at: float    # 创建时间戳
```

## 正确性属性

*属性（Property）是一种在系统所有有效执行中都应成立的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性是人类可读规范与机器可验证正确性保证之间的桥梁。*

以下属性基于需求文档中的验收标准推导而来，每个属性都包含明确的"对于任意"全称量化声明，可直接转化为 Hypothesis 属性基测试。

### 属性 1：Token 完整性不变量

*对于任意*有效的主题配置（light 或 dark），加载后的 DesignTokenSet 应包含所有必需的 Token 类别（colors、spacing、radius、font_sizes），且每个类别中包含所有必需的键。

**验证需求：1.1**

### 属性 2：Token 序列化 Round-Trip

*对于任意*有效的 DesignTokenSet 对象，将其序列化为 JSON 后再反序列化加载，应得到与原始对象等价的 DesignTokenSet。

**验证需求：1.6**

### 属性 3：QSS 渲染包含 Token 值

*对于任意*有效的 Token 字典和 Jinja2 QSS 模板，渲染后的 QSS 字符串应包含 Token 字典中所有被模板引用的值，且不包含未解析的 Jinja2 模板变量。

**验证需求：1.4**

### 属性 4：Token 文件错误处理

*对于任意*格式错误的 Token 文件内容（缺少必需字段、类型错误、JSON 语法错误），ThemeEngine 的 load_tokens 方法应抛出 TokenFileError 异常，且异常消息包含具体的错误描述。

**验证需求：1.7**

### 属性 5：主题切换自动更新组件样式

*对于任意* BaseWidget 子类实例，当 ThemeEngine 发射 theme_changed 信号时，该组件的 apply_theme 方法应被调用。

**验证需求：2.2**

### 属性 6：HoverEffect 光标变化

*对于任意*应用了 HoverEffectMixin 的组件，模拟 enterEvent 后组件的光标应变为 PointingHandCursor，模拟 leaveEvent 后应恢复为默认光标。

**验证需求：2.4**

### 属性 7：Disabled 状态属性

*对于任意*组件，设置 disabled=True 后，组件的 windowOpacity 应为 0.5，光标应为 ForbiddenCursor，且所有交互事件应被屏蔽。

**验证需求：2.7, 3.3**

### 属性 8：多 Mixin 无冲突

*对于任意*同时应用了 HoverEffectMixin、ClickRippleMixin 和 FocusGlowMixin 的组件，依次触发 enterEvent、mousePressEvent、focusInEvent 后，各 Mixin 的效果应独立生效且不互相覆盖。

**验证需求：2.8**

### 属性 9：Button 类型正确性

*对于任意* ButtonType 枚举值，创建 TButton 时传入该类型后，Button 的 buttonType 属性应等于传入值。

**验证需求：3.1**

### 属性 10：Loading 屏蔽点击

*对于任意* TButton，设置 loading=True 后，模拟鼠标点击不应发射 clicked 信号。

**验证需求：3.2, 3.5**

### 属性 11：Button 正常点击发射信号

*对于任意*非 loading 且非 disabled 的 TButton，模拟鼠标点击后应发射恰好一次 clicked 信号。

**验证需求：3.4**

### 属性 12：Checkbox 状态 Round-Trip

*对于任意* CheckState 枚举值，对 TCheckbox 调用 set_state(state) 后，get_state() 应返回相同的 state 值，且 state_changed 信号应携带该 state 值。

**验证需求：4.1, 4.2**

### 属性 13：RadioGroup 互斥不变量

*对于任意* TRadioGroup 和其中任意数量（≥2）的 TRadio，选中其中一个 Radio 后，该组内有且仅有一个 Radio 处于选中状态。

**验证需求：5.2**

### 属性 14：RadioGroup 选择一致性

*对于任意* TRadioGroup，选中某个 TRadio 后，get_selected_value() 应返回该 Radio 的 value 值，且 selection_changed 信号应携带该 value。

**验证需求：5.3, 5.4**

### 属性 15：Input 清空 Round-Trip

*对于任意*非空文本字符串和 clearable=True 的 TInput，设置文本后调用 clear()，get_text() 应返回空字符串，且 cleared 信号应被发射。

**验证需求：6.2, 6.3**

### 属性 16：Input 密码可见性 Toggle Round-Trip

*对于任意* password=True 的 TInput，调用 toggle_password_visibility() 两次后，输入框的显示模式应回到初始的掩码模式（幂等性：f(f(x)) = x）。

**验证需求：6.5**

### 属性 17：Input text_changed 信号

*对于任意*文本字符串，对 TInput 调用 set_text(text) 后，text_changed 信号应携带该 text 值。

**验证需求：6.6**

### 属性 18：Switch Toggle Round-Trip

*对于任意* TSwitch 和初始布尔状态，调用 toggle() 后 is_checked() 应返回相反值，再次调用 toggle() 后应回到初始值。toggled 信号应携带正确的布尔值。

**验证需求：7.2, 7.3**

### 属性 19：Tag 属性正确性

*对于任意* TagSize 和 TagType 枚举值组合，创建 TTag 后其 size 和 tag_type 属性应等于传入值。

**验证需求：8.1, 8.4**

### 属性 20：Tag closed 信号

*对于任意* closable=True 的 TTag，模拟点击关闭按钮后应发射恰好一次 closed 信号。

**验证需求：8.3**

### 属性 21：SearchBar search_changed 信号

*对于任意*文本字符串，在 TSearchBar 的输入框中输入文本后，search_changed 信号应携带该文本值。

**验证需求：9.2**

### 属性 22：SearchBar search_submitted 信号

*对于任意*文本字符串，在 TSearchBar 中输入文本后触发提交（点击按钮或 Enter），search_submitted 信号应携带该文本值。

**验证需求：9.3**

### 属性 23：Breadcrumb Items Round-Trip

*对于任意* BreadcrumbItem 列表，对 TBreadcrumb 调用 set_items(items) 后，get_items() 应返回与原始列表等价的列表。

**验证需求：10.1**

### 属性 24：Breadcrumb item_clicked 信号

*对于任意*非空 BreadcrumbItem 列表和任意有效索引（非最后一项），点击该路径项后 item_clicked 信号应携带正确的索引和数据。

**验证需求：10.3**

### 属性 25：Breadcrumb 最后一项不可点击

*对于任意*非空 BreadcrumbItem 列表，最后一个路径项应处于不可点击状态（点击不发射 item_clicked 信号）。

**验证需求：10.4**

### 属性 26：InputGroup 圆角合并不变量

*对于任意*数量（≥2）的子组件序列，InputGroup 中第一个组件应仅保留左侧圆角，最后一个组件应仅保留右侧圆角，中间所有组件的圆角应为零。此不变量在添加或删除子组件后仍应成立。

**验证需求：11.2, 11.3**

### 属性 27：Message 类型正确性

*对于任意* MessageType 枚举值，创建 TMessage 后其消息类型属性应等于传入值。

**验证需求：12.1**

### 属性 28：Message 堆叠不变量

*对于任意*数量的同时可见消息，它们的 y_offset 应按创建时间严格递增，且相邻消息之间的间距应为固定值。

**验证需求：12.4, 12.5**

### 属性 29：Modal closed 信号

*对于任意* closable=True 的 TModal，点击关闭按钮或遮罩层后应发射 closed 信号。

**验证需求：13.4**

### 属性 30：Modal closable 属性控制

*对于任意* TModal，当 closable=False 时，点击遮罩层不应关闭 Modal 且不应发射 closed 信号；当 mask_closable=False 时，点击遮罩层同样不应关闭 Modal。

**验证需求：13.5**

## 错误处理

### Token 文件加载错误

| 错误场景 | 异常类型 | 处理方式 |
|---------|---------|---------|
| 文件不存在 | `FileNotFoundError` | 抛出异常，包含文件路径 |
| JSON/TOML 语法错误 | `TokenFileError` | 抛出异常，包含行号和错误描述 |
| 缺少必需 Token 键 | `TokenFileError` | 抛出异常，列出缺失的键名 |
| Token 值类型错误 | `TokenFileError` | 抛出异常，包含键名和期望类型 |

### Jinja2 模板渲染错误

| 错误场景 | 异常类型 | 处理方式 |
|---------|---------|---------|
| 模板文件不存在 | `TemplateNotFoundError` | 抛出异常，包含模板名称 |
| 模板语法错误 | `TemplateSyntaxError` | 抛出异常，包含行号 |
| 未定义的 Token 变量 | `UndefinedError` | 抛出异常，包含变量名 |

### 组件运行时错误

| 错误场景 | 处理方式 |
|---------|---------|
| 组件在 ThemeEngine 初始化前创建 | 使用默认样式，在 ThemeEngine 就绪后自动更新 |
| Mixin 事件处理异常 | 捕获异常并记录日志，不影响组件基本功能 |
| Message 定时器异常 | 强制关闭消息并释放资源 |
| Modal 遮罩层创建失败 | 回退到无遮罩模式并记录警告 |

## 测试策略

### 双轨测试方法

本项目采用单元测试与属性基测试互补的双轨策略：

- **单元测试（pytest + pytest-qt）**：验证具体示例、边界情况和错误条件
- **属性基测试（Hypothesis）**：验证跨所有输入的通用属性

### 属性基测试配置

- **测试库**：Hypothesis（Python 生态最成熟的属性基测试框架）
- **最小迭代次数**：每个属性测试至少 100 次迭代
- **标注格式**：每个测试用注释引用设计文档中的属性编号
  ```python
  # Feature: tyto-ui-lib-v1, Property 1: Token 完整性不变量
  @given(theme_name=st.sampled_from(["light", "dark"]))
  def test_token_completeness(theme_name: str) -> None:
      ...
  ```
- **每个正确性属性对应一个独立的属性基测试函数**

### Hypothesis 自定义策略

为组件测试定义以下自定义生成策略：

```python
# 生成任意 ButtonType
button_types = st.sampled_from(list(TButton.ButtonType))

# 生成任意 CheckState
check_states = st.sampled_from(list(TCheckbox.CheckState))

# 生成任意 TagSize 和 TagType 组合
tag_configs = st.tuples(
    st.sampled_from(list(TTag.TagSize)),
    st.sampled_from(list(TTag.TagType)),
)

# 生成任意非空文本
non_empty_text = st.text(min_size=1, max_size=100)

# 生成任意 BreadcrumbItem 列表
breadcrumb_items = st.lists(
    st.builds(BreadcrumbItem, label=st.text(min_size=1, max_size=50)),
    min_size=1,
    max_size=20,
)

# 生成任意有效 Token 字典
valid_token_colors = st.fixed_dictionaries({
    "primary": st.from_regex(r"#[0-9a-f]{6}", fullmatch=True),
    # ... 其他必需颜色键
})
```

### 测试目录结构

```
tests/
├── conftest.py                    # pytest-qt fixtures, QApplication 初始化
├── test_core/
│   ├── test_theme_engine.py       # 属性 1-4 的属性基测试 + 单元测试
│   └── test_design_tokens.py      # Token 加载和验证测试
├── test_common/
│   ├── test_base_widget.py        # 属性 5 的属性基测试
│   └── test_mixins.py             # 属性 6-8 的属性基测试
├── test_atoms/
│   ├── test_button.py             # 属性 9-11 的属性基测试
│   ├── test_checkbox.py           # 属性 12 的属性基测试
│   ├── test_radio.py              # 属性 13-14 的属性基测试
│   ├── test_input.py              # 属性 15-17 的属性基测试
│   ├── test_switch.py             # 属性 18 的属性基测试
│   └── test_tag.py                # 属性 19-20 的属性基测试
├── test_molecules/
│   ├── test_searchbar.py          # 属性 21-22 的属性基测试
│   ├── test_breadcrumb.py         # 属性 23-25 的属性基测试
│   └── test_inputgroup.py         # 属性 26 的属性基测试
└── test_organisms/
    ├── test_message.py            # 属性 27-28 的属性基测试
    └── test_modal.py              # 属性 29-30 的属性基测试
```

### 单元测试覆盖重点

- 各组件的边界情况（空文本、极端尺寸值）
- 错误条件（无效 Token 文件、无效参数）
- 组件间集成（SearchBar 内部的 Input + Button 协作）
- 主题切换的端到端流程
- 组件生命周期（创建、样式绑定、销毁清理）


---

# 设计文档：Tyto UI 组件库 V1.0.1 - Gallery MVVM 重构

## 概述

V1.0.1 将 Gallery 预览画廊从单文件重构为基于 MVVM 架构的模块化结构。左侧提供按原子/分子/有机体分类的导航菜单，右侧展示选中组件的所有特性示例。架构设计确保新增组件时仅需添加 Showcase 模块并注册，无需修改框架代码。

## 架构

### Gallery MVVM 架构

```mermaid
graph TB
    subgraph View["View 层"]
        MainWindow["GalleryWindow<br/>主窗口"]
        NavMenu["NavigationMenu<br/>左侧导航菜单"]
        Showcase["ComponentShowcase<br/>右侧展示面板"]
        TopBar["TopBar<br/>顶部栏"]
    end

    subgraph ViewModel["ViewModel 层"]
        GalleryVM["GalleryViewModel<br/>管理导航状态与组件切换"]
    end

    subgraph Model["Model 层"]
        Registry["ComponentRegistry<br/>组件注册表"]
        CompInfo["ComponentInfo<br/>组件元数据"]
    end

    MainWindow --> TopBar
    MainWindow --> NavMenu
    MainWindow --> Showcase
    NavMenu --> GalleryVM
    Showcase --> GalleryVM
    TopBar --> GalleryVM
    GalleryVM --> Registry
    Registry --> CompInfo
```

### 目录结构

```
examples/
├── gallery.py                          # 入口文件，委托给 gallery 包
└── gallery/
    ├── __init__.py                     # 包初始化，导出 main()
    ├── __main__.py                     # 支持 python -m examples.gallery
    ├── models/
    │   ├── __init__.py
    │   ├── component_info.py           # ComponentInfo 数据模型
    │   └── component_registry.py       # ComponentRegistry 组件注册表
    ├── viewmodels/
    │   ├── __init__.py
    │   └── gallery_viewmodel.py        # GalleryViewModel
    ├── views/
    │   ├── __init__.py
    │   ├── gallery_window.py           # GalleryWindow 主窗口
    │   ├── navigation_menu.py          # NavigationMenu 左侧导航
    │   ├── component_showcase.py       # ComponentShowcase 右侧展示面板
    │   └── top_bar.py                  # TopBar 顶部栏
    ├── showcases/
    │   ├── __init__.py                 # register_all() 注册所有组件
    │   ├── base_showcase.py            # BaseShowcase 基类
    │   ├── button_showcase.py          # Button 展示
    │   ├── checkbox_showcase.py        # Checkbox 展示
    │   ├── radio_showcase.py           # Radio 展示
    │   ├── input_showcase.py           # Input 展示
    │   ├── switch_showcase.py          # Switch 展示
    │   ├── tag_showcase.py             # Tag 展示
    │   ├── searchbar_showcase.py       # SearchBar 展示
    │   ├── breadcrumb_showcase.py      # Breadcrumb 展示
    │   ├── inputgroup_showcase.py      # InputGroup 展示
    │   ├── message_showcase.py         # Message 展示
    │   └── modal_showcase.py           # Modal 展示
    └── styles/
        ├── __init__.py
        └── gallery_styles.py           # Gallery 专用样式常量
```

## 组件与接口

### 1. Model 层

#### ComponentInfo

```python
@dataclass
class ComponentInfo:
    """Component metadata for registry."""
    name: str                    # Display name, e.g. "Button"
    key: str                     # Unique key, e.g. "button"
    category: str                # "atoms" | "molecules" | "organisms"
    showcase_factory: Callable[[QWidget], QWidget]  # Factory to create showcase widget
```

#### ComponentRegistry

```python
class ComponentRegistry:
    """Singleton registry of all gallery components."""

    def register(self, info: ComponentInfo) -> None:
        """Register a component for the gallery."""

    def get_by_key(self, key: str) -> ComponentInfo | None:
        """Get component info by key."""

    def get_by_category(self, category: str) -> list[ComponentInfo]:
        """Get all components in a category."""

    def categories(self) -> list[str]:
        """Return ordered list of categories: ['atoms', 'molecules', 'organisms']."""

    def all_components(self) -> list[ComponentInfo]:
        """Return all registered components."""
```

### 2. ViewModel 层

#### GalleryViewModel

```python
class GalleryViewModel(QObject):
    """Manages gallery navigation state and component switching."""

    # Signals
    current_component_changed = Signal(str)  # component key
    theme_changed = Signal(str)              # "light" | "dark"

    def __init__(self, registry: ComponentRegistry) -> None: ...

    def select_component(self, key: str) -> None:
        """Select a component by key, emits current_component_changed."""

    def current_component_key(self) -> str | None:
        """Return the currently selected component key."""

    def toggle_theme(self, dark: bool) -> None:
        """Switch theme and emit theme_changed."""

    def get_registry(self) -> ComponentRegistry:
        """Return the component registry."""
```

### 3. View 层

#### NavigationMenu

```python
class NavigationMenu(QWidget):
    """Left sidebar navigation with categorized component list."""

    component_selected = Signal(str)  # component key

    def __init__(self, viewmodel: GalleryViewModel, parent: QWidget | None = None) -> None:
        """Build tree-style menu from registry categories."""

    def _on_item_clicked(self, key: str) -> None:
        """Handle menu item click, emit component_selected."""

    def set_active_item(self, key: str) -> None:
        """Highlight the active menu item."""
```

#### ComponentShowcase

```python
class ComponentShowcase(QScrollArea):
    """Right panel that displays the selected component's showcase."""

    def __init__(self, viewmodel: GalleryViewModel, parent: QWidget | None = None) -> None: ...

    def show_component(self, key: str) -> None:
        """Load and display the showcase for the given component key."""
```

#### TopBar

```python
class TopBar(QWidget):
    """Top bar with title and theme toggle switch."""

    def __init__(self, viewmodel: GalleryViewModel, parent: QWidget | None = None) -> None: ...
```

#### GalleryWindow

```python
class GalleryWindow(QWidget):
    """Main gallery window composing TopBar, NavigationMenu, and ComponentShowcase."""

    def __init__(self) -> None:
        """Initialize MVVM components and wire signals."""
```

### 4. Showcase 层

#### BaseShowcase

```python
class BaseShowcase(QWidget):
    """Base class for component showcases."""

    def __init__(self, parent: QWidget | None = None) -> None: ...

    def add_section(self, title: str, description: str, content: QWidget) -> None:
        """Add a showcase section with title, description, and content widget."""

    @staticmethod
    def hbox(*widgets: QWidget) -> QWidget:
        """Helper: wrap widgets in horizontal layout."""
```

每个具体 Showcase（如 ButtonShowcase）继承 BaseShowcase，在 `__init__` 中通过 `add_section()` 添加各特性区块。

### 5. 样式模块

#### GalleryStyles

```python
class GalleryStyles:
    """Gallery-specific style constants, theme-aware."""

    @staticmethod
    def nav_menu_style(theme: str) -> str:
        """Return QSS for navigation menu based on theme."""

    @staticmethod
    def top_bar_style(theme: str) -> str:
        """Return QSS for top bar based on theme."""

    @staticmethod
    def showcase_section_title_style() -> str:
        """Return QSS for showcase section titles."""

    @staticmethod
    def showcase_section_desc_style() -> str:
        """Return QSS for showcase section descriptions."""
```

## 信号流

```mermaid
sequenceDiagram
    participant User as 用户
    participant Nav as NavigationMenu
    participant VM as GalleryViewModel
    participant SC as ComponentShowcase

    User->>Nav: 点击组件项 "Button"
    Nav->>VM: select_component("button")
    VM-->>VM: current_component_changed.emit("button")
    VM-->>Nav: set_active_item("button")
    VM-->>SC: show_component("button")
    SC->>SC: 从 Registry 获取 showcase_factory
    SC->>SC: 创建 ButtonShowcase 并显示
```

## 组件注册示例

```python
# In examples/gallery/showcases/__init__.py
def register_all(registry: ComponentRegistry) -> None:
    """Register all component showcases."""
    from .button_showcase import ButtonShowcase
    from .checkbox_showcase import CheckboxShowcase
    # ... other imports

    registry.register(ComponentInfo(
        name="Button", key="button", category="atoms",
        showcase_factory=lambda parent: ButtonShowcase(parent),
    ))
    registry.register(ComponentInfo(
        name="Checkbox", key="checkbox", category="atoms",
        showcase_factory=lambda parent: CheckboxShowcase(parent),
    ))
    # ... register all components
```

## 正确性属性

### 属性 31：组件注册表完整性

*对于任意*已注册的 ComponentInfo，通过 `get_by_key(info.key)` 应返回与原始注册信息等价的 ComponentInfo 对象。

**验证需求：16.4, 17.5**

### 属性 32：分类查询一致性

*对于任意*已注册的 ComponentInfo，`get_by_category(info.category)` 返回的列表应包含该 ComponentInfo。

**验证需求：17.1, 17.2**

### 属性 33：ViewModel 组件切换信号

*对于任意*已注册的组件 key，调用 `GalleryViewModel.select_component(key)` 后，`current_component_key()` 应返回该 key，且 `current_component_changed` 信号应携带该 key。

**验证需求：17.4, 18.1**

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 选择未注册的组件 key | ViewModel 忽略请求，不发射信号 |
| Showcase 工厂创建失败 | ComponentShowcase 显示错误提示文字 |
| 注册重复 key | ComponentRegistry 覆盖旧注册，记录警告日志 |

## 测试策略

V1.0.1 的属性基测试聚焦于 Model 和 ViewModel 层的纯逻辑验证：

- **属性 31-32**：ComponentRegistry 的注册与查询逻辑
- **属性 33**：GalleryViewModel 的状态管理与信号发射

View 层（NavigationMenu、ComponentShowcase 等）通过手动 Gallery 运行验证，不编写自动化 UI 测试。


---

# 设计文档：Tyto UI 组件库 V1.0.1 - Bug 修复

## 概述

V1.0.1 Bug 修复版本解决 V1.0.0 中发现的 5 个组件共 10 个缺陷。问题根因集中在三个方面：(1) QSS 动态属性选择器在 `setStyleSheet()` 后未触发重新匹配；(2) Input 清空按钮布局在 QLineEdit 外部而非内部；(3) Message 组件的窗口标志和背景属性导致样式丢失及定位异常。

## Bug 根因分析

### Bug 1：Button 类型样式未生效

**现象**：不同 `button_type` 的按钮均显示为 DEFAULT 样式，无法区分 Primary/Dashed/Text 类型。

**根因**：`TButton.__init__()` 中先调用 `setProperty("buttonType", ...)` 设置动态属性，再调用 `apply_theme()` 执行 `setStyleSheet(qss)`。但 Qt 的 QSS 属性选择器（如 `[buttonType="primary"]`）依赖 widget 的 style 系统在属性变更后重新匹配规则。当 `setStyleSheet()` 在 `setProperty()` 之后调用时，Qt 不会自动重新 polish widget，导致属性选择器未生效。

**修复方案**：在 `apply_theme()` 中，调用 `setStyleSheet(qss)` 后，显式调用 `self.style().unpolish(self)` 和 `self.style().polish(self)` 强制 Qt 重新评估 QSS 属性选择器。

### Bug 2：Input 清空按钮位置错误

**现象**：当 `clearable=True` 时，清空按钮（✕）显示在 QLineEdit 右侧外部，而非输入框内部靠右边界处。

**根因**：`TInput.__init__()` 将 `_clear_btn`（QToolButton）作为独立 widget 添加到外层 `QHBoxLayout` 中，与 `QLineEdit` 并列排列。这导致清空按钮在 QLineEdit 边框之外渲染。

**修复方案**：使用 `QLineEdit.addAction(QAction, TrailingPosition)` 将清空动作嵌入 QLineEdit 内部。当文本非空时显示该 action，点击时触发清空逻辑。移除外层布局中的独立 QToolButton。同样处理密码可见性切换按钮。

### Bug 3：Tag 类型样式未生效

**现象**：不同 `tag_type` 的标签均显示为 DEFAULT 样式，无法区分 Primary/Success/Warning/Error 类型。标签无可见边框和背景色，无法辨识尺寸。

**根因**：与 Bug 1 相同。`TTag.__init__()` 中 `setProperty("tagType", ...)` 后调用 `apply_theme()` 的 `setStyleSheet()`，但未触发 QSS 属性选择器重新匹配。

**修复方案**：与 Bug 1 相同，在 `TTag.apply_theme()` 中 `setStyleSheet()` 后调用 `unpolish/polish`。

### Bug 4：Tag 关闭按钮无法删除标签

**现象**：当 `closable=True` 时，点击关闭按钮仅发射 `closed` 信号，但标签本身不会从界面中消失。

**根因**：`TTag` 的关闭按钮 `clicked` 信号仅连接到 `self.closed.emit()`，未执行任何隐藏或删除操作。`closed` 信号的设计意图是通知外部，但组件自身也应提供默认的自我隐藏行为。

**修复方案**：在关闭按钮的 `clicked` 处理中，先发射 `closed` 信号，然后调用 `self.setVisible(False)` 隐藏标签。外部代码可通过连接 `closed` 信号来决定是否真正删除 widget。

### Bug 5：SearchBar 清空按钮位置错误

**现象**：SearchBar 内部 TInput 的清空按钮位置与独立 TInput 相同，显示在输入框外部。

**根因**：SearchBar 内部使用 TInput 组件，继承了 Bug 2 的问题。

**修复方案**：修复 TInput（Bug 2）后，SearchBar 自动受益，无需额外修改。

### Bug 6：Message 触发按钮样式异常

**现象**：Message 展示面板中的触发按钮未显示对应的边框效果和背景颜色。

**根因**：与 Bug 1 相同，MessageShowcase 中使用的 TButton 受同一 QSS 属性选择器问题影响。

**修复方案**：修复 TButton（Bug 1）后，所有使用 TButton 的地方自动受益。

### Bug 7：Message 弹出位置不正确

**现象**：弹出的提示消息未显示在软件窗口的顶部水平居中位置。

**根因**：`MessageManager._show()` 中通过 `QApplication.instance().activeWindow()` 获取 parent，但 `TMessage` 使用了 `Qt.WindowType.Tool` 窗口标志，使其成为独立顶层窗口。`msg.move(cx, y)` 中的坐标是相对于屏幕的绝对坐标，而非相对于 parent 窗口。当 parent 窗口不在屏幕左上角时，消息位置偏移。

**修复方案**：在 `_update_positions()` 中，将 parent 窗口的全局坐标（`parent.mapToGlobal()`）纳入位置计算。水平居中应基于 parent 窗口的全局 x 坐标 + (parent 宽度 - message 宽度) / 2，垂直位置应基于 parent 窗口的全局 y 坐标 + 顶部边距。

### Bug 8：Message 无背景色和边框

**现象**：弹出的提示消息没有背景色和边框，内容悬浮在空中。

**根因**：`TMessage.__init__()` 设置了 `WA_TranslucentBackground` 属性，该属性使 widget 的背景完全透明。虽然 QSS 中定义了 `background-color` 和 `border`，但 `WA_TranslucentBackground` 会覆盖 QSS 的背景渲染。同时 `FramelessWindowHint` 移除了系统边框。

**修复方案**：移除 `WA_TranslucentBackground` 属性，或改为在 `TMessage` 内部使用一个带样式的容器 QFrame/QWidget 来承载内容，使 QSS 的背景色和边框能正确渲染。保留 `FramelessWindowHint` 以维持无系统标题栏的外观。

## 修改范围

### 需修改的源码文件

| 文件 | 修改内容 | 关联 Bug |
|------|---------|---------|
| `src/tyto_ui_lib/components/atoms/button.py` | `apply_theme()` 中添加 unpolish/polish | Bug 1 |
| `src/tyto_ui_lib/components/atoms/input.py` | 重构清空按钮为 QLineEdit 内部 action | Bug 2 |
| `src/tyto_ui_lib/components/atoms/tag.py` | `apply_theme()` 添加 unpolish/polish；关闭按钮添加 `setVisible(False)` | Bug 3, 4 |
| `src/tyto_ui_lib/components/organisms/message.py` | 修复位置计算；移除 `WA_TranslucentBackground` 或添加内容容器 | Bug 7, 8 |

### 无需修改的文件

- `searchbar.py`：修复 TInput 后自动受益（Bug 5）
- `message_showcase.py`：修复 TButton 后自动受益（Bug 6）
- QSS 模板文件：模板本身定义正确，问题在 Python 代码层

## 正确性属性

### 属性 34：Button QSS 属性选择器生效

*对于任意* ButtonType 枚举值，创建 TButton 后，通过 `self.styleSheet()` 获取的 QSS 应包含对应 `[buttonType="xxx"]` 的规则，且 widget 的实际渲染样式应与该规则匹配。

**验证需求：20.1, 20.2, 20.3, 20.4, 20.5**

### 属性 35：Input 清空按钮在 QLineEdit 内部

*对于任意* clearable=True 的 TInput，当输入框内有文本时，清空按钮的视觉位置应在 QLineEdit 的边框范围内。

**验证需求：21.1, 21.2**

### 属性 36：Tag QSS 属性选择器生效

*对于任意* TagType 枚举值，创建 TTag 后，widget 的 QSS 动态属性选择器应立即生效，渲染对应的背景色和边框色。

**验证需求：22.1, 22.2, 22.3, 22.4**

### 属性 37：Tag 关闭按钮隐藏标签

*对于任意* closable=True 的 TTag，模拟点击关闭按钮后，标签应变为不可见（`isVisible() == False`），且 `closed` 信号应被发射。

**验证需求：22.5**

### 属性 38：Message 窗口居中定位

*对于任意* TMessage 及其 parent 窗口，Message 的水平中心点应与 parent 窗口的水平中心点对齐（误差不超过 1px），且 Message 的顶部应位于 parent 窗口顶部附近。

**验证需求：24.1, 24.4**

### 属性 39：Message 背景色和边框可见

*对于任意* MessageType，创建并显示 TMessage 后，widget 应具有非透明的背景色和可见的边框。

**验证需求：24.2**

## 测试策略

V1.0.1 Bug 修复的测试聚焦于验证修复后的行为正确性：

- **属性 34**：通过 Hypothesis 生成任意 ButtonType，验证 QSS 属性选择器生效（检查 `property("buttonType")` 值和 `style().polish()` 调用）
- **属性 35**：验证 TInput clearable 模式下清空 action 存在于 QLineEdit 内部
- **属性 36**：通过 Hypothesis 生成任意 TagType，验证 QSS 属性选择器生效
- **属性 37**：验证 TTag closable 点击后 `isVisible()` 为 False
- **属性 38**：验证 Message 位置计算逻辑（单元测试，mock parent 窗口几何信息）
- **属性 39**：验证 TMessage 不设置 `WA_TranslucentBackground` 或内容容器具有背景色


---

# 设计文档：Tyto UI 组件库 V1.0.1 - Dark 模式颜色修复

## 概述

V1.0.1 Dark 模式修复版本解决在 "dark" 主题下组件和 Gallery 界面元素颜色显示异常的问题。问题根因集中在三个方面：(1) 部分组件使用 per-widget `setStyleSheet()` 覆盖了全局 QSS，导致主题切换后旧样式残留；(2) 自定义绘制组件（如 Switch 的轨道）在主题切换时未触发重绘；(3) Gallery 界面元素的 QSS 未正确使用 dark 主题 Token 值。

## 参考效果图

所有修复以 NaiveUI dark 主题风格为参考标准：

| 组件 | 参考图 |
|------|--------|
| Button | `docs/image/reference/v1.0.1_1.png` |
| Input | `docs/image/reference/v1.0.1_2.png` |
| Switch | `docs/image/reference/v1.0.1_3.png` |
| Tag | `docs/image/reference/v1.0.1_4.png` |
| SearchBar | `docs/image/reference/v1.0.1_5.png` |
| Gallery 列表/列表项 | `docs/image/reference/v1.0.1_6.png` |

## Dark 模式根因分析

### 问题 1：组件 per-widget setStyleSheet 覆盖全局 QSS

**现象**：TInput、TSwitch、TSearchBar 等组件在 `apply_theme()` 中调用 `self.setStyleSheet(qss)` 设置 per-widget 样式。当 `ThemeEngine.switch_theme()` 更新全局 QSS 后，per-widget 样式的优先级高于全局 QSS，导致组件仍显示旧主题的颜色。

**受影响组件**：TInput、TSwitch、TSearchBar

**根因**：Qt 的样式优先级规则为：per-widget `setStyleSheet()` > 全局 `QApplication.setStyleSheet()`。当组件在 `apply_theme()` 中调用 `self.setStyleSheet(qss)` 时，虽然使用了当前主题的 Token 重新渲染 QSS，但如果 `apply_theme()` 未被正确触发（例如信号连接问题），或者渲染的 QSS 中某些选择器未覆盖所有状态，就会出现颜色残留。

**修复方案**：统一组件的样式应用策略。对于已在全局 QSS 中定义了完整规则的组件（如 TButton、TTag），使用 `unpolish/polish` 方式让全局 QSS 生效。对于需要 per-widget 样式的组件（如 TInput、TSwitch、TSearchBar），确保 `apply_theme()` 在主题切换时被正确调用，并且重新渲染的 QSS 包含当前主题的所有 Token 值。

### 问题 2：Switch 自定义绘制未响应主题切换

**现象**：TSwitch 的轨道通过 `_SwitchTrack.paintEvent()` 自定义绘制，在绘制时通过 `ThemeEngine.get_token()` 获取颜色。主题切换后，虽然 Token 值已更新，但 `_SwitchTrack` 未调用 `update()` 触发重绘，导致轨道仍显示旧主题颜色。

**根因**：`TSwitch.apply_theme()` 仅调用 `self.setStyleSheet(qss)` 更新 QSS，但 `_SwitchTrack` 的颜色是通过 `paintEvent()` 中的 `get_token()` 实时获取的。需要在主题切换时显式调用 `self._track.update()` 触发重绘。

**修复方案**：在 `TSwitch.apply_theme()` 中，除了更新 QSS 外，显式调用 `self._track.update()` 强制轨道重绘。

### 问题 3：Gallery 界面元素主题切换不完整

**现象**：Gallery 的 NavigationMenu、TopBar 通过 `GalleryStyles` 生成 QSS，在主题切换时通过 `_on_theme_changed` 信号重新应用样式。但 ComponentShowcase 的容器背景和 BaseShowcase 的 section 标题/描述在主题切换时未更新。

**根因**：
- `ComponentShowcase` 的容器 `QWidget` 未设置背景色，依赖父级背景透传。在 dark 模式下，如果父级背景未更新，容器仍显示 light 主题背景。
- `ComponentShowcase._set_placeholder()` 中硬编码了 `color: #999`，未使用 Token。
- `GalleryWindow` 主窗口本身未设置背景色，导致 dark 模式下窗口背景仍为系统默认的浅色。

**修复方案**：
1. 在 `GalleryWindow` 中监听 `theme_changed` 信号，主题切换时更新主窗口和 showcase 区域的背景色。
2. 在 `ComponentShowcase` 中添加主题响应，更新容器背景色。
3. 移除 `_set_placeholder()` 中的硬编码颜色，使用 Token 值。

## 修改范围

### 需修改的源码文件

| 文件 | 修改内容 | 关联需求 |
|------|---------|---------|
| `src/tyto_ui_lib/components/atoms/switch.py` | `apply_theme()` 中添加 `self._track.update()` 触发轨道重绘 | 需求 27 |
| `src/tyto_ui_lib/components/atoms/input.py` | 确保 `apply_theme()` 正确重新渲染 dark 主题 QSS | 需求 26 |
| `src/tyto_ui_lib/components/molecules/searchbar.py` | 确保 `apply_theme()` 正确重新渲染 dark 主题 QSS | 需求 29 |
| `examples/gallery/views/gallery_window.py` | 添加主题切换时更新主窗口背景色 | 需求 30 |
| `examples/gallery/views/component_showcase.py` | 添加主题响应，更新容器背景色；修复硬编码颜色 | 需求 30 |
| `examples/gallery/styles/gallery_styles.py` | 添加 showcase 面板和主窗口的 dark 主题样式方法 | 需求 30 |

### 可能需要修改的 Token 文件

| 文件 | 修改内容 | 关联需求 |
|------|---------|---------|
| `src/tyto_ui_lib/styles/tokens/dark.json` | 根据参考图对比，调整 dark 主题 Token 值（如有偏差） | 需求 25-29 |

### 可能需要修改的 QSS 模板文件

| 文件 | 修改内容 | 关联需求 |
|------|---------|---------|
| `src/tyto_ui_lib/styles/templates/input.qss.j2` | 添加占位符颜色规则 `placeholder` | 需求 26 |

### 无需修改的文件

- `button.py`：TButton 已使用全局 QSS + unpolish/polish 方式，dark 主题 Token 通过全局 QSS 自动生效（需求 25）
- `tag.py`：TTag 已使用全局 QSS + unpolish/polish 方式，dark 主题 Token 通过全局 QSS 自动生效（需求 28）
- `button.qss.j2`、`tag.qss.j2`、`switch.qss.j2`、`searchbar.qss.j2`：模板已正确使用 Token 变量，无需修改

## 正确性属性

### 属性 40：组件 Dark 模式颜色一致性

*对于任意*组件（TButton、TInput、TSwitch、TTag、TSearchBar）和任意主题（light、dark），切换到该主题后，组件通过 `ThemeEngine.get_token()` 获取的颜色值应与当前主题 Token 文件中定义的值一致。

**验证需求：25.5, 26.4, 27.3, 28.3, 29.1**

### 属性 41：Switch 轨道重绘响应主题切换

*对于任意* TSwitch 和任意主题切换序列，每次主题切换后 `_SwitchTrack` 的 `paintEvent()` 应使用当前主题的 Token 颜色绘制轨道。

**验证需求：27.1, 27.2, 27.3**

### 属性 42：Gallery 界面 Dark 模式背景色

*对于任意*主题（light、dark），切换后 Gallery 主窗口、NavigationMenu、TopBar、ComponentShowcase 的背景色应与当前主题 Token 中定义的 `bg_default` 或 `bg_elevated` 一致。

**验证需求：30.1, 30.5, 30.6, 30.8**

## 测试策略

V1.0.1 Dark 模式修复的测试聚焦于验证主题切换后颜色的正确性：

- **属性 40**：通过 Hypothesis 生成任意主题名称（light/dark），验证切换后组件的 Token 值与 Token 文件一致
- **属性 41**：验证 TSwitch 主题切换后 `_track.update()` 被调用（通过 mock 或信号监听）
- **属性 42**：验证 Gallery 界面元素在主题切换后的背景色与 Token 值一致（单元测试）

View 层的视觉效果通过手动运行 `uv run python examples/gallery.py` 验证，对比参考效果图。
