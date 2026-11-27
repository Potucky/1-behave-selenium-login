"""Introductory smoke checks against the public TodoMVC demo."""

import re

from playwright.sync_api import expect

APP_TITLE = "React \u2022 TodoMVC"


def test_app_loads_with_an_empty_list(todo_page):
    """The demo loads, shows its title and heading, and starts with no todos."""
    expect(todo_page.page).to_have_title(APP_TITLE)
    expect(todo_page.page).to_have_url(re.compile(r"demo\.playwright\.dev/todomvc/"))
    expect(todo_page.heading).to_be_visible()
    expect(todo_page.new_todo).to_be_visible()
    expect(todo_page.items).to_have_count(0)
    expect(todo_page.footer).to_be_hidden()


def test_add_and_complete_a_todo(todo_page):
    """Adding one todo and marking it complete updates the row and the counter."""
    todo_page.add("Buy milk")
    row = todo_page.item("Buy milk")
    expect(row).to_be_visible()
    expect(todo_page.footer).to_be_visible()
    expect(todo_page.count).to_have_text("1 item left")

    todo_page.complete("Buy milk")
    expect(row.get_by_role("checkbox", name="Toggle Todo")).to_be_checked()
    expect(row).to_have_class("completed")
    expect(todo_page.count).to_have_text("0 items left")


def test_blank_entry_is_not_saved(todo_page):
    """A whitespace-only entry is ignored and the empty list stays empty."""
    todo_page.add("   ")
    expect(todo_page.items).to_have_count(0)
    expect(todo_page.footer).to_be_hidden()


def test_completed_filter_is_empty_when_nothing_is_done(todo_page):
    """The Completed filter shows nothing while the only todo is still active."""
    todo_page.add("Read the report")
    expect(todo_page.count).to_have_text("1 item left")

    todo_page.show_completed()
    expect(todo_page.page).to_have_url(re.compile(r"#/completed$"))
    expect(todo_page.items).to_have_count(0)
    expect(todo_page.count).to_have_text("1 item left")
