# Employee Attrition Prediction System - Frontend (Phase 10 Integration)

This directory contains the frontend for the Employee Attrition Prediction System, fully integrated with the Spring Boot backend (`http://localhost:8080/api`) and FastAPI ML microservice (`http://localhost:8000`).

## Technologies Used
- HTML5, CSS3, vanilla JavaScript (ES6+ async/await)
- Bootstrap 5 (CSS & JS via CDN)
- Bootstrap Icons (via CDN)
- Chart.js (via CDN)
- JWT Bearer Authentication & Session Storage

## File Structure
- `login.html`: Authenticates against `POST /api/auth/login` and stores JWT session token.
- `dashboard.html`: Live executive dashboard querying `/api/analytics/dashboard`, `/api/analytics/by-department`, `/api/analytics/by-role`, and `/api/predictions`.
- `employees.html`: Full CRUD employee directory (GET, POST, PUT, DELETE `/api/employees`) supporting all 30 ML model feature fields.
- `prediction.html`: Live ML inference interface calling `POST /api/predict` via Spring Boot and FastAPI model v2.
- `analytics.html`: Detailed organization-wide charts populated from `/api/analytics/*` endpoints.
- `high-risk.html`: High and medium risk employee dashboard with individual prediction history modal.
- `history.html`: Paginated log of historical predictions from `/api/predictions` with search and date filters.
- `settings.html`: User profile and configuration preferences.
- `css/styles.css`: Custom design tokens, dark mode styles, and responsive SaaS layout.
- `js/api.js`: Unified API client managing JWT authentication and REST API endpoints.
- `js/app.js`: Shared shell logic, dynamic header user profile, dark mode toggle, and logout handlers.
- `js/sidebar.js`: Shared navigation sidebar component.

