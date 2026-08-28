from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5500"

def test_prediction_flow(authenticated_page: Page):
    authenticated_page.goto(f"{BASE_URL}/prediction.html")
    
    # Wait for employee options to attach to the select element
    authenticated_page.wait_for_selector("#employeeSelect option[value='2'], #employeeSelect option:not([value=''])", state="attached", timeout=10000)
    
    # Select first valid employee option
    authenticated_page.select_option("#employeeSelect", index=1)
    authenticated_page.wait_for_timeout(1000)
    
    # Verify selected employee info card is shown
    expect(authenticated_page.locator("#selectedEmployeeInfo")).to_be_visible()
    
    # Click Predict button
    predict_btn = authenticated_page.locator("#predictBtn")
    expect(predict_btn).to_be_enabled()
    predict_btn.click()
    
    # Wait for resultCard to become visible
    authenticated_page.wait_for_selector("#resultCard:not(.d-none)", timeout=15000)
    
    # Check probability value and risk badge
    prob_el = authenticated_page.locator("#probValue")
    badge_el = authenticated_page.locator("#riskBadge")
    expect(prob_el).to_be_visible()
    expect(badge_el).to_be_visible()
    
    prob_text = prob_el.inner_text()
    assert "%" in prob_text or len(prob_text) > 0
