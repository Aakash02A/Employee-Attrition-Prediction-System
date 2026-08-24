# Employee Attrition Prediction System - Frontend (Phase 2)

This directory contains the Phase 2 UI/UX static frontend build for the Employee Attrition Prediction System. 
It implements a modern, responsive, 3-column SaaS dashboard layout.

## Technologies Used
- HTML5, CSS3, vanilla JavaScript
- Bootstrap 5 (CSS & JS via CDN)
- Bootstrap Icons (via CDN)
- Chart.js (via CDN)

## File Structure
- `login.html`: The authentication screen with simulated login logic.
- `dashboard.html`: The main dashboard featuring KPIs, high-level charts, and contextual retention stats.
- `prediction.html`: The form to input employee data and run ML predictions.
- `analytics.html`: Detailed breakdowns of attrition drivers across the organization.
- `high-risk.html`: A sortable, filterable list of employees flagged with High/Medium risk.
- `history.html`: A paginated log of past predictions.
- `css/styles.css`: All custom styling, design tokens, and layout overrides.
- `js/app.js`: Shared application logic (sidebar toggling, active links, logout).
- `js/mock-data.js`: Centralized mock JSON data simulating backend API responses.

## Backend Integration Guide (Phase 3+)
The current application uses static/mock data to demonstrate functionality. When wiring up the real backend, look for these areas:

1. **Authentication (`login.html`)**:
   - Locate `fakeLogin()` logic inside the `<script>` tag. Replace the `setTimeout` with a real `fetch('/api/auth/login')` call.

2. **Dashboard & Analytics (`js/mock-data.js`)**:
   - The global `MockData` object supplies all KPIs and chart data.
   - Replace the static assignment of `window.MockData` with a data fetching service that retrieves this data from the backend (e.g., `/api/dashboard/stats`).

3. **Running a Prediction (`prediction.html`)**:
   - Locate the `<script>` tag at the bottom.
   - The form submission currently triggers a mocked probability calculation. Replace this with a POST request to `/api/predict` sending the form fields as JSON. The result card UI updating logic is already in place to handle the response.

4. **Data Tables (`high-risk.html`, `history.html`)**:
   - These pages pull from `MockData.employees` and `MockData.history`.
   - Update the `currentData` initialization to fetch from endpoints like `/api/employees/high-risk` and `/api/predictions/history`. Pagination logic in `history.html` may need to be updated from client-side to server-side depending on dataset size.
