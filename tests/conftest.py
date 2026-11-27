"""Browser fixtures for the TodoMVC smoke tests."""

from __future__ import annotations

import pytest

from pages.todo_page import TodoPage

NAVIGATION_TIMEOUT_MS = 20_000
ACTION_TIMEOUT_MS = 15_000


@pytest.fixture
def todo_page(page, base_url: str) -> TodoPage:
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    page.set_default_timeout(ACTION_TIMEOUT_MS)
    screen = TodoPage(page)
    screen.open(base_url)
    return screen
