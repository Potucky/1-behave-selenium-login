"""Apply file and environment configuration to the Playwright pytest run."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from config.settings import Settings, load_settings

ASSERTION_TIMEOUT_MS = 15_000


def _settings() -> Settings:
    try:
        return load_settings()
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc


def pytest_metadata(metadata: dict, config: pytest.Config) -> None:
    settings = _settings()
    browsers = config.getoption("browser") or [settings.browser]
    metadata["Base URL"] = config.getoption("base_url") or settings.base_url
    metadata["Browser"] = ", ".join(browsers)
    if config.getoption("headed"):
        metadata["Headless"] = "false"
    else:
        metadata["Headless"] = "true" if settings.headless else "false"


def pytest_configure(config: pytest.Config) -> None:
    settings = _settings()
    if not config.getoption("browser"):
        config.option.browser = [settings.browser]
    if not config.getoption("base_url"):
        config.option.base_url = settings.base_url


def pytest_html_report_title(report) -> None:
    report.title = "Playwright Python basic smoke"


def pytest_report_header(config: pytest.Config) -> list[str]:
    settings = _settings()
    browsers = ", ".join(config.getoption("browser") or [settings.browser])
    headless = "false" if config.getoption("headed") else str(settings.headless).lower()
    return [f"browser: {browsers}", f"headless: {headless}"]


@pytest.fixture(scope="session", autouse=True)
def _assertion_timeout() -> None:
    expect.set_options(timeout=ASSERTION_TIMEOUT_MS)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, pytestconfig: pytest.Config):
    """Honor HEADLESS from config unless the run was started with --headed."""
    settings = _settings()
    launch_args = dict(browser_type_launch_args)
    if not pytestconfig.getoption("headed"):
        launch_args["headless"] = settings.headless
    return launch_args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }
