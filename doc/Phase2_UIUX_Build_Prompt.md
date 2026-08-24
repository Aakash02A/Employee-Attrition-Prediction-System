# Build Prompt — Phase 2: UI/UX for Employee Attrition Prediction System

Use this prompt as-is with a coding assistant (e.g. Claude Code, Cursor, or similar) to generate the frontend for Phase 2. It is self-contained — no other context is required.

---

## Prompt

You are building the **frontend UI** for an Employee Attrition Prediction System. This is Phase 2 (UI/UX) of a larger project — build static/functional screens only; backend and ML integration happen in later phases, so use mock/placeholder data and stub API calls with clear `TODO` comments where real endpoints will later be wired in.

### Tech constraints

- **HTML5 + CSS3 + vanilla JavaScript** (no frontend framework/build step)
- **Bootstrap 5** for layout, components, and responsiveness (via CDN)
- **Chart.js** for all charts (via CDN)
- Single shared layout (sidebar + top bar) reused across all authenticated screens
- Mobile/tablet responsive: sidebar collapses to a top nav below Bootstrap's `md` breakpoint
- Use semantic HTML, accessible form labels, and keyboard-navigable interactive elements
- Keep all custom CSS in one stylesheet (`styles.css`); keep all JS in one file per screen or a shared `app.js` plus per-screen scripts — your call, but be consistent
- Color-code risk levels consistently everywhere: 🟢 Low = green, 🟡 Medium = amber, 🔴 High = red

### Screens to build

Build these six screens as separate HTML files, all sharing the same sidebar/top-bar shell (except Login, which has no shell):

**1. Login (`login.html`)**
- Centered card: app title, email field, password field, Login button
- Client-side validation: required fields, basic email format check
- On submit: stub a `fakeLogin()` JS function that simulates a POST to `/api/auth/login`, shows a loading state, then redirects to `dashboard.html` on success or shows an inline error alert on failure (simulate both cases via a toggle/comment)

**2. Dashboard (`dashboard.html`)**
- Top row: 4 KPI cards — Total Employees, Attrition Count, Attrition Rate, At-Risk Count, Avg. Probability (use Bootstrap cards, one stat per card, large number + label)
- Second row: two charts side by side — Attrition Trend (line chart) and Risk Distribution (doughnut chart)
- Third row: two bar charts — Attrition by Department, Attrition by Job Role
- Populate all charts with realistic mock data defined in a JS object at the top of the file, structured so it's obvious where a real API response would later replace it

**3. Employee Prediction (`prediction.html`)**
- Left/top: form with fields — Age (number), Department (select), Job Role (select), Monthly Income (number), Years at Company (number), Job Satisfaction (select 1–4), Work-Life Balance (select 1–4), Overtime (select Yes/No), Job Level (select 1–5)
- Validate all fields before allowing submit (required, numeric ranges: age 16–80, satisfaction/balance 1–4, job level 1–5)
- "Predict Attrition" button triggers a stub `fakePredict()` function that simulates calling `/api/predict`, then renders a result card below the form: risk badge (color-coded), probability percentage, prediction label (Stay/Leave), and a one-line recommendation
- Result card should be hidden until a prediction is made, and should update in place on repeated submissions (no page reload)

**4. Analytics (`analytics.html`)**
- Optional filter bar at the top (Department dropdown, date range — non-functional stub is fine)
- Seven charts using Chart.js: Attrition by Department (bar), Attrition by Job Role (bar), Attrition by Age Group (bar), Attrition by Salary Range (bar), Attrition by Overtime (grouped bar), Attrition by Job Satisfaction (bar), Years at Company vs Attrition (scatter or grouped bar)
- Arrange in a responsive 2-column grid that stacks to 1 column on small screens

**5. High-Risk Employees (`high-risk.html`)**
- Bootstrap table: Employee Code, Department, Job Role, Risk (colored badge), Probability, Action (View button)
- Sortable columns (click header to sort — implement with plain JS, no library)
- Filter controls above the table: by Department and by Risk Level
- "View" button opens a Bootstrap modal showing that employee's full mock prediction history (table: Date, Prediction, Probability, Model Version)

**6. Prediction History (`history.html`)**
- Table: Employee Code, Prediction, Probability, Model Version, Date, Requested By
- Filter controls: Employee search box, date range, risk level dropdown
- Paginate client-side if mock data exceeds ~15 rows

### Shared shell requirements

- Sidebar links: Dashboard, Employees, Attrition Prediction, Analytics, High-Risk Employees, Prediction History, Settings — with icons (Bootstrap Icons via CDN is fine) and the current page highlighted as active
- Top bar: welcome message with a mock user name and role badge, plus a Logout button that redirects to `login.html`
- All screens must visually match (same fonts, spacing, card style, color palette)

### Mock data

Generate realistic mock JSON data inline (a `<script>` block or a separate `mock-data.js`) for:
- ~30–50 employees with varied departments, roles, ages, incomes, and risk levels
- Corresponding prediction history entries for at least 10 of them

Structure this mock data so it mirrors what a real REST API response would look like, to make later backend integration a straightforward swap rather than a rewrite.

### Deliverables

- `login.html`, `dashboard.html`, `prediction.html`, `analytics.html`, `high-risk.html`, `history.html`
- `styles.css` (shared styles)
- `app.js` (shared shell logic — sidebar, top bar, logout)
- `mock-data.js` (all mock/sample data)
- Brief `README.md` noting which parts are stubbed and where real API calls (`/api/...`, `/predict`) will later be wired in

---

### How to use this prompt

Paste the section above (from "You are building..." to the end of "Deliverables") into your coding assistant of choice. If you want me to build this directly instead, just say so and I'll generate the files here.
