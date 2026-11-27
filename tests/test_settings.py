"""Config file and environment precedence. These tests do not open a browser."""

from pathlib import Path

import pytest

from config.settings import load_settings


def test_committed_defaults_point_at_the_public_demo():
    """The committed config targets the public demo and a headless Chromium run."""
    missing_local = Path(__file__).resolve().parents[1] / "config" / "no-such-local.env"
    settings = load_settings(environ={}, local_file=missing_local)
    assert settings.base_url == "https://demo.playwright.dev/todomvc/"
    assert settings.browser == "chromium"
    assert settings.headless is True


def test_environment_overrides_local_file_and_defaults(tmp_path: Path):
    """Environment wins over the local file, which wins over the committed file."""
    default = tmp_path / "settings.env"
    local = tmp_path / "settings.local.env"
    default.write_text(
        "\n".join(
            [
                "# comment",
                "BASE_URL=https://example.test/from-file",
                "BROWSER=firefox",
                "HEADLESS=true",
            ]
        ),
        encoding="utf-8",
    )
    local.write_text("BROWSER=webkit\nBASE_URL=https://example.test/from-local\n", encoding="utf-8")
    settings = load_settings(
        environ={"BASE_URL": "https://example.test/from-env", "HEADLESS": "false"},
        default_file=default,
        local_file=local,
    )
    assert settings.base_url == "https://example.test/from-env/"
    assert settings.browser == "webkit"
    assert settings.headless is False


def test_unknown_browser_is_rejected(tmp_path: Path):
    default = tmp_path / "settings.env"
    default.write_text("BROWSER=chrome\n", encoding="utf-8")
    with pytest.raises(ValueError, match="BROWSER"):
        load_settings(environ={}, default_file=default, local_file=tmp_path / "missing.env")


def test_invalid_headless_value_is_rejected(tmp_path: Path):
    default = tmp_path / "settings.env"
    default.write_text("HEADLESS=maybe\n", encoding="utf-8")
    with pytest.raises(ValueError, match="HEADLESS"):
        load_settings(environ={}, default_file=default, local_file=tmp_path / "missing.env")
