from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5500"

def test_dashboard_kpis_and_charts(authenticated_page: Page):
    authenticated_page.goto(f"{BASE_URL}/dashboard.html")
    
    # Wait for KPI values to finish loading (spinner replaced with text)
    authenticated_page.wait_for_selector("#kpiTotalEmp:not(:has(.spinner-border))", timeout=10000)
    
    kpi_total = authenticated_page.locator("#kpiTotalEmp")
    kpi_attr = authenticated_page.locator("#kpiAttrCount")
    kpi_rate = authenticated_page.locator("#kpiAttrRate")
    
    expect(kpi_total).to_be_visible()
    expect(kpi_attr).to_be_visible()
    expect(kpi_rate).to_be_visible()
    
    # Canvas elements rendered
    expect(authenticated_page.locator("#trendChart")).to_be_visible()

def test_analytics_page(authenticated_page: Page):
    authenticated_page.goto(f"{BASE_URL}/analytics.html")
    
    # Verify page title
    expect(authenticated_page.locator(".page-title")).to_contain_text("Analytics")
    
    # Verify chart canvases or container elements
    authenticated_page.wait_for_timeout(2000)
    charts = authenticated_page.locator("canvas")
    assert charts.count() >= 1
