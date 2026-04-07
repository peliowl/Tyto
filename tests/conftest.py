"""Shared pytest fixtures for Tyto UI Library tests."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Provide a shared QApplication instance for all tests.

    Uses session scope to avoid creating multiple QApplication instances,
    which is not allowed by Qt.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
