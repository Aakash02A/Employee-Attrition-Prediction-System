from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5500"

def test_view_employee_list(authenticated_page: Page):
    authenticated_page.goto(f"{BASE_URL}/employees.html")
    authenticated_page.wait_for_selector("#empTableBody tr td", timeout=10000)
    rows = authenticated_page.locator("#empTableBody tr")
    expect(rows.first).to_be_visible()
    assert rows.count() > 0

def test_search_filter_employees(authenticated_page: Page):
    authenticated_page.goto(f"{BASE_URL}/employees.html")
    authenticated_page.wait_for_selector("#empTableBody tr td", timeout=10000)
    
    # Filter by Sales department
    authenticated_page.select_option("#filterDept", "Sales")
    authenticated_page.wait_for_timeout(500)
    
    # Search by keyword
    authenticated_page.fill("#searchEmp", "Sales")
    authenticated_page.wait_for_timeout(500)
    
    # Reset filter
    authenticated_page.select_option("#filterDept", "All")
    authenticated_page.fill("#searchEmp", "")
    authenticated_page.wait_for_timeout(500)
    expect(authenticated_page.locator("#empTableBody tr").first).to_be_visible()

def test_add_employee(authenticated_page: Page):
    authenticated_page.goto(f"{BASE_URL}/employees.html")
    authenticated_page.wait_for_selector("#empTableBody tr td", timeout=10000)
    
    # Open Add Modal
    authenticated_page.click("button:has-text('Add Employee')")
    authenticated_page.wait_for_selector("#employeeModal.show", timeout=5000)
    
    # Tab 1: Personal Info
    authenticated_page.fill("#f_age", "32")
    authenticated_page.select_option("#f_gender", "Female")
    authenticated_page.select_option("#f_maritalStatus", "Single")
    authenticated_page.fill("#f_distanceFromHome", "4")
    authenticated_page.select_option("#f_education", "3")
    authenticated_page.select_option("#f_educationField", "Life Sciences")
    
    # Switch to Tab 2 and adjust Job
    authenticated_page.click("#tab-job-btn")
    authenticated_page.wait_for_timeout(300)
    authenticated_page.select_option("#f_department", "Research & Development")
    authenticated_page.select_option("#f_jobRole", "Research Scientist")
    
    # Submit Add
    authenticated_page.click("#saveEmployeeBtn")
    
    # Verify alert appears
    authenticated_page.wait_for_selector("#pageAlert:not(.d-none)", timeout=10000)
    alert = authenticated_page.locator("#pageAlert")
    expect(alert).to_be_visible()

def test_delete_modal_interaction(authenticated_page: Page):
    authenticated_page.goto(f"{BASE_URL}/employees.html")
    authenticated_page.wait_for_selector("#empTableBody tr td", timeout=10000)
    
    # Find delete button on first row
    delete_btn = authenticated_page.locator("#empTableBody tr button.btn-outline-danger, #empTableBody tr a.text-danger, #empTableBody tr [onclick*='openDeleteModal']").first
    if delete_btn.is_visible():
        delete_btn.click()
        authenticated_page.wait_for_selector("#deleteEmployeeModal.show", timeout=5000)
        expect(authenticated_page.locator("#deleteEmployeeModal")).to_be_visible()
        # Dismiss modal
        authenticated_page.click("#deleteEmployeeModal button:has-text('Cancel')")
        authenticated_page.wait_for_timeout(500)
