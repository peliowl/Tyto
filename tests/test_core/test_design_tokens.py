"""Unit tests for DesignTokenSet data model and token file loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tyto_ui_lib.core.tokens import (
    DesignTokenSet,
    TokenFileError,
    load_tokens_from_file,
)


def _make_valid_token_data(name: str = "test") -> dict:
    """Return a minimal valid token dictionary."""
    return {
        "name": name,
        "colors": {
            "primary": "#18a058",
            "primary_hover": "#36ad6a",
            "primary_pressed": "#0c7a43",
            "success": "#18a058",
            "warning": "#f0a020",
            "error": "#d03050",
            "info": "#2080f0",
            "info_hover": "#4098fc",
            "info_pressed": "#1060c9",
            "bg_default": "#ffffff",
            "bg_elevated": "#f8f8fa",
            "text_primary": "#333639",
            "text_secondary": "#667085",
            "text_disabled": "#c2c2c2",
            "border": "#e0e0e6",
            "border_focus": "#18a058",
            "white": "#ffffff",
            "mask": "rgba(0, 0, 0, 0.4)",
        },
        "spacing": {"small": 4, "medium": 8, "large": 16, "xlarge": 24},
        "radius": {"small": 2, "medium": 4, "large": 8},
        "font_sizes": {"small": 12, "medium": 14, "large": 16, "xlarge": 20},
        "shadows": {
            "small": "0 2px 8px rgba(0,0,0,0.08)",
            "medium": "0 4px 16px rgba(0,0,0,0.12)",
            "large": "0 8px 32px rgba(0,0,0,0.16)",
        },
    }


class TestDesignTokenSet:
    """Tests for the DesignTokenSet dataclass."""

    def test_to_dict_round_trip(self) -> None:
        data = _make_valid_token_data("round_trip")
        ts = DesignTokenSet(
            name=data["name"],
            colors=data["colors"],
            spacing=data["spacing"],
            radius=data["radius"],
            font_sizes=data["font_sizes"],
            shadows=data["shadows"],
        )
        result = ts.to_dict()
        assert result["name"] == "round_trip"
        assert result["colors"] == data["colors"]
        assert result["spacing"] == data["spacing"]

    def test_default_values(self) -> None:
        ts = DesignTokenSet()
        assert ts.name == ""
        assert ts.colors == {}


class TestLoadTokensFromFile:
    """Tests for load_tokens_from_file function."""

    def test_load_valid_file(self, tmp_path: Path) -> None:
        data = _make_valid_token_data("light")
        fp = tmp_path / "light.json"
        fp.write_text(json.dumps(data), encoding="utf-8")

        tokens = load_tokens_from_file(fp)
        assert tokens.name == "light"
        assert tokens.colors["primary"] == "#18a058"
        assert tokens.spacing["medium"] == 8

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError, match="Token file not found"):
            load_tokens_from_file("/nonexistent/path.json")

    def test_invalid_json_syntax(self, tmp_path: Path) -> None:
        fp = tmp_path / "bad.json"
        fp.write_text("{invalid json", encoding="utf-8")

        with pytest.raises(TokenFileError, match="Invalid JSON syntax"):
            load_tokens_from_file(fp)

    def test_missing_category(self, tmp_path: Path) -> None:
        data = _make_valid_token_data()
        del data["colors"]
        fp = tmp_path / "no_colors.json"
        fp.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(TokenFileError, match="Missing required category 'colors'"):
            load_tokens_from_file(fp)

    def test_missing_required_key(self, tmp_path: Path) -> None:
        data = _make_valid_token_data()
        del data["colors"]["primary"]
        fp = tmp_path / "missing_key.json"
        fp.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(TokenFileError, match="Missing required keys in 'colors'"):
            load_tokens_from_file(fp)

    def test_wrong_value_type(self, tmp_path: Path) -> None:
        data = _make_valid_token_data()
        data["spacing"]["small"] = "not_an_int"
        fp = tmp_path / "bad_type.json"
        fp.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(TokenFileError, match="expected int, got str"):
            load_tokens_from_file(fp)

    def test_non_object_root(self, tmp_path: Path) -> None:
        fp = tmp_path / "array.json"
        fp.write_text("[1, 2, 3]", encoding="utf-8")

        with pytest.raises(TokenFileError, match="root must be a JSON object"):
            load_tokens_from_file(fp)
