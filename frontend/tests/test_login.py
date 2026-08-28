from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5500"

def test_login_successful(page: Page):
    page.goto(f"{BASE_URL}/login.html")
    page.fill("#email", "admin@eaps.com")
    page.fill("#password", "admin123")
    page.click("button[type='submit']")
    page.wait_for_url("**/dashboard.html", timeout=10000)
    assert "dashboard.html" in page.url

def test_login_invalid_password(page: Page):
    page.goto(f"{BASE_URL}/login.html")
    page.fill("#email", "admin@eaps.com")
    page.fill("#password", "wrongpassword999")
    page.click("button[type='submit']")
    page.wait_for_timeout(2000)
    assert "login.html" in page.url
    # Verify error message is visible
    error_el = page.locator("#error-msg, .error, .toast, .alert")
    if error_el.count() > 0:
        expect(error_el.first).to_be_visible()

def test_unauthenticated_redirect(page: Page):
    # Navigate to dashboard with no token in localStorage
    page.goto(f"{BASE_URL}/dashboard.html")
    page.wait_for_url("**/login.html", timeout=10000)
    assert "login.html" in page.url
