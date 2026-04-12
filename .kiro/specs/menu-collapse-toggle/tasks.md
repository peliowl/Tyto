# Implementation Plan: Menu Collapse Toggle Button

## Overview

为 TMenu 组件增加内置的折叠/展开切换按钮。实现分为：创建 `_CollapseToggleButton` 私有类、集成到 TMenu、编写测试、更新 Playground 演示。

## Tasks

- [x] 1. Implement _CollapseToggleButton widget
  - [x] 1.1 Create the `_CollapseToggleButton` class in `src/tyto_ui_lib/components/organisms/menu.py`
    - Add as a module-level private class (before TMenuItem)
    - Inherit from QWidget, include `clicked = Signal()`
    - Implement `__init__` with internal state: `_collapsed`, `_disabled`, `_hovered`, token-derived color fields
    - Implement `apply_theme` to read colors and size from ThemeEngine tokens (bg_default, border, text_secondary, hover_color, text_disabled, component_sizes.small.height)
    - Implement `sizeHint` returning `QSize(_btn_size, _btn_size)`
    - Reuse existing `_CHEVRON_PATH_DATA` and `_parse_svg_path` for the chevron icon
    - _Requirements: 3.3, 3.5_

  - [x] 1.2 Implement painting and interaction methods for `_CollapseToggleButton`
    - `paintEvent`: draw circular background (with hover variant), circular border, and chevron path (rotated 180° for expanded / 0° for collapsed)
    - `enterEvent` / `leaveEvent`: toggle `_hovered` flag and call `update()`
    - `mousePressEvent`: emit `clicked` signal if not `_disabled`
    - `set_collapsed(collapsed: bool)`: update `_collapsed` and call `update()`
    - `set_disabled(disabled: bool)`: update `_disabled`, change cursor, call `update()`
    - `reposition()`: position at parent right edge, vertically centered, half-protruding
    - _Requirements: 1.1, 1.2, 2.4, 3.1, 3.2, 3.4, 6.1_

  - [ ]* 1.3 Write property test for toggle button positioning
    - **Property 1: Toggle button positioning**
    - **Validates: Requirements 1.1, 1.2**

- [x] 2. Integrate _CollapseToggleButton into TMenu
  - [x] 2.1 Modify TMenu.__init__ and _build_ui
    - Create `_CollapseToggleButton` instance in `__init__` after `super().__init__`
    - Connect `_collapse_toggle.clicked` to a lambda that calls `self.set_collapsed(not self._collapsed)`
    - Add `_update_toggle_visibility()` private method
    - Call `_update_toggle_visibility()` at end of `_build_ui`
    - Set initial collapsed state on the toggle button if `collapsed=True`
    - _Requirements: 1.3, 1.4, 1.5, 4.3_

  - [x] 2.2 Modify TMenu.set_collapsed to sync toggle button state
    - After existing collapsed logic, call `self._collapse_toggle.set_collapsed(collapsed)`
    - _Requirements: 4.1_

  - [x] 2.3 Modify TMenu.set_mode to update toggle visibility
    - After existing mode switch logic, call `self._update_toggle_visibility()`
    - _Requirements: 1.4, 1.5_

  - [x] 2.4 Modify TMenu.set_disabled to sync toggle disabled state
    - After existing disabled logic, call `self._collapse_toggle.set_disabled(disabled)`
    - _Requirements: 6.1, 6.2_

  - [x] 2.5 Modify TMenu.apply_theme to propagate to toggle button
    - After existing theme logic, call `self._collapse_toggle.apply_theme()`
    - _Requirements: 3.5_

  - [x] 2.6 Override TMenu.resizeEvent to reposition toggle button
    - Call `super().resizeEvent(event)` then `self._collapse_toggle.reposition()`
    - _Requirements: 1.1_

  - [ ]* 2.7 Write property test for click inverts collapsed state
    - **Property 2: Click inverts collapsed state**
    - **Validates: Requirements 2.1, 2.2, 2.4**

  - [ ]* 2.8 Write property test for programmatic set_collapsed syncs button
    - **Property 3: Programmatic set_collapsed syncs button state**
    - **Validates: Requirements 4.1, 4.3**

- [x] 3. Checkpoint - Ensure core integration works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Write unit tests and remaining property tests
  - [x]* 4.1 Write unit tests for toggle visibility and mode switching
    - Test horizontal mode hides button (Req 1.3)
    - Test vertical→horizontal hides button (Req 1.4)
    - Test horizontal→vertical shows button (Req 1.5)
    - Test chevron direction in expanded vs collapsed (Req 3.1, 3.2)
    - Test hover state toggle (Req 3.4)
    - Test initialization with collapsed=True (Req 4.3)
    - Test clicked signal wiring to set_collapsed (Req 2.3, 4.2)
    - _Requirements: 1.3, 1.4, 1.5, 2.3, 3.1, 3.2, 3.4, 4.2, 4.3_

  - [x]* 4.2 Write property test for disabled state blocks interaction
    - **Property 4: Disabled state blocks toggle interaction**
    - **Validates: Requirements 6.1, 6.2**

- [x] 5. Update Playground demo
  - [x] 5.1 Update `examples/playground/definitions/menu_props.py`
    - Ensure the factory `_make_menu` creates a TMenu that shows the toggle button
    - The toggle button should be visible by default in vertical mode (no code change needed if TMenu auto-creates it)
    - Verify the playground reflects collapse/expand when toggle is clicked
    - _Requirements: 5.1, 5.2_

- [x] 6. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The `_CollapseToggleButton` is a private internal class, not exported from the package
