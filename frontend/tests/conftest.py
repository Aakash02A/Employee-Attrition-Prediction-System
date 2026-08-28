import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5500"

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser_context):
    context = browser_context.new_context()
    page = context.new_page()
    yield page
    page.close()
    context.close()

@pytest.fixture
def authenticated_page(browser_context):
    context = browser_context.new_context()
    page = context.new_page()
    # Perform login
    page.goto(f"{BASE_URL}/login.html")
    page.fill("#email", "admin@eaps.com")
    page.fill("#password", "admin123")
    page.click("button[type='submit']")
    page.wait_for_url("**/dashboard.html", timeout=10000)
    yield page
    page.close()
    context.close()
