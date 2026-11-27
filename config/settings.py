"""Load base URL, browser, and headless mode for the smoke suite.

Precedence, highest first:

1. Process environment variables
2. ``config/settings.local.env`` (optional, gitignored)
3. ``config/settings.env`` (committed defaults for the public demo)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent
DEFAULT_FILE = CONFIG_DIR / "settings.env"
LOCAL_FILE = CONFIG_DIR / "settings.local.env"

ALLOWED_BROWSERS = ("chromium", "firefox", "webkit")
_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


@dataclass(frozen=True)
class Settings:
    base_url: str
    browser: str
    headless: bool


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid line in {path} at line {line_number}: {raw!r}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if not key:
            raise ValueError(f"Invalid line in {path} at line {line_number}: {raw!r}")
        values[key] = value
    return values


def _as_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in _TRUE:
        return True
    if normalized in _FALSE:
        return False
    raise ValueError(f"HEADLESS must be true or false, got {value!r}")


def load_settings(
    environ: dict[str, str] | None = None,
    default_file: Path = DEFAULT_FILE,
    local_file: Path = LOCAL_FILE,
) -> Settings:
    """Return the settings for this run.

    ``environ`` defaults to the process environment. Pass a dict in tests.
    """
    env = os.environ if environ is None else environ
    file_values = _parse_env_file(default_file)
    file_values.update(_parse_env_file(local_file))

    def pick(name: str, fallback: str) -> str:
        from_env = env.get(name)
        if from_env is not None and from_env.strip() != "":
            return from_env.strip()
        if name in file_values and file_values[name] != "":
            return file_values[name]
        return fallback

    base_url = pick("BASE_URL", "https://demo.playwright.dev/todomvc/")
    base_url = base_url.rstrip("/") + "/"
    browser = pick("BROWSER", "chromium").lower()
    if browser not in ALLOWED_BROWSERS:
        allowed = ", ".join(ALLOWED_BROWSERS)
        raise ValueError(f"BROWSER must be one of {allowed}, got {browser!r}")
    headless = _as_bool(pick("HEADLESS", "true"))
    return Settings(base_url=base_url, browser=browser, headless=headless)
