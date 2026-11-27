"""Locators for the public TodoMVC demo.

This is a thin helper so the tests read as actions. It is not a framework.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect


class TodoPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role("heading", name="todos", exact=True)
        self.new_todo = page.get_by_placeholder("What needs to be done?")
        self.items = page.get_by_test_id("todo-item")
        self.count = page.locator(".todo-count")
        self.footer = page.locator(".todoapp .footer")

    def open(self, base_url: str) -> None:
        """Open the app with an empty list.

        The demo stores todos in localStorage. Clear that storage before the
        page scripts run so one test cannot affect the next.
        """
        self.page.context.add_init_script("localStorage.clear()")
        self.page.goto(base_url)
        expect(self.heading).to_be_visible()
        expect(self.new_todo).to_be_visible()

    def add(self, text: str) -> None:
        self.new_todo.fill(text)
        self.new_todo.press("Enter")

    def item(self, title: str) -> Locator:
        title_label = self.page.get_by_test_id("todo-title").get_by_text(title, exact=True)
        return self.items.filter(has=title_label)

    def complete(self, title: str) -> None:
        self.item(title).get_by_role("checkbox", name="Toggle Todo").check()

    def show_completed(self) -> None:
        self.footer.get_by_role("link", name="Completed", exact=True).click()
