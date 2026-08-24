# Employee Attrition Prediction System
## Complete Project Document

**Version:** 1.0
**Status:** Finalized — Baseline Architecture

> This document consolidates the requirements, architecture, technology stack, database design, and development phases for the Employee Attrition Prediction System. It represents the agreed baseline. Any future change to scope, stack, or design should be recorded in the **Change Log** at the end of this document rather than silently edited into the sections above, so the project retains a clear history of decisions.

---

## Table of Contents

1. Project Overview
2. Objectives
3. System Users & Roles
4. Functional Requirements
5. Non-Functional Requirements
6. System Scope
7. Technology Stack
8. System Architecture
9. Database Design
10. API Design
11. Machine Learning Design
12. Security Design
13. UI/UX Design
14. Development Phases
15. Change Log

---

## 1. Project Overview

The **Employee Attrition Prediction System** is a full-stack machine-learning application that predicts whether an employee is likely to leave an organization. It combines a web-based frontend, a Java/Spring Boot backend, a Python-based machine-learning service, and a MySQL database.

The system accepts employee information through a web interface, processes it through the backend, sends the relevant features to a trained machine-learning model via a dedicated ML microservice, and returns the predicted attrition outcome, probability, and risk level to the user. Predictions are stored for history and analytics.

---

## 2. Objectives

- Predict whether an employee is likely to leave the organization using a trained ML model.
- Provide HR and management with a data-driven view of attrition risk across the workforce.
- Enable proactive retention action by surfacing high-risk employees before they leave.
- Provide analytics and visualizations to identify attrition patterns (department, role, age, income, satisfaction, etc.).
- Maintain a secure, role-based system for managing employee data and viewing predictions.

---

## 3. System Users & Roles

| Role | Description | Access Level |
|---|---|---|
| **Admin** | System owner / IT administrator | Full access — manage users, employees, all predictions, system settings |
| **HR** | Human Resources personnel | Manage employee records, run predictions, view analytics, view high-risk list |
| **Manager** | Department/team manager | View employees, view prediction results — no edit rights |

---

## 4. Functional Requirements

- User authentication (login/logout) with role-based access control
- Add, view, update, and delete employee records
- Submit employee attributes and receive an attrition prediction (Stay/Leave + probability + risk level)
- Store every prediction with a timestamp, linked to the employee and the requesting user
- View prediction history for an employee or across the organization
- Dashboard showing KPIs: total employees, attrition count, attrition rate, high-risk count, average probability
- Analytics screen with charts: attrition by department, job role, age group, salary range, job satisfaction, overtime
- High-risk employees list with filtering/sorting by risk level or probability
- Search and filter employees (by department, role, risk level, etc.)

---

## 5. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Security | Passwords hashed (bcrypt), JWT-based authentication, protected REST endpoints |
| Performance | Prediction response returned within a few seconds of submission |
| Scalability | Backend and ML service deployed as separate components, each scalable independently |
| Usability | Responsive UI (desktop and tablet) via Bootstrap 5 |
| Maintainability | Clear separation of frontend, backend, ML service, and database layers |
| Reliability | Proper error handling and validation on all API endpoints |
| Portability | Containerizable via Docker for consistent deployment across environments |
| Auditability | Model version and requesting user stored with every prediction |

---

## 6. System Scope

**In scope**
- Single organization, internal-use HR tool (not multi-tenant)
- Attrition prediction based on structured employee attributes (tabular data)
- Web application only (no native mobile app)
- Role-based access for three user types (Admin, HR, Manager)

**Out of scope (current version)**
- Real-time streaming data ingestion
- Multi-language / localization support
- Integration with third-party HRMS/payroll systems
- Automated retraining pipelines (retraining is manual, versioned)

---

## 7. Technology Stack

| Component | Selected Technology | Main Purpose |
|---|---|---|
| UI Structure | HTML5 | Web page structure |
| UI Styling | CSS3 | Design and styling |
| Client-side Logic | JavaScript | Dynamic interaction |
| UI Framework | Bootstrap 5 | Responsive interface |
| Visualization | Chart.js | Dashboard charts |
| Backend Language | Java | Server-side development |
| Backend Framework | Spring Boot | REST APIs and business logic |
| Authentication | Spring Security + JWT | Login, roles, endpoint protection |
| ORM | Spring Data JPA + Hibernate | MySQL integration |
| ML Language | Python | Machine-learning development |
| ML API Framework | FastAPI | Standalone ML microservice |
| Data Processing | Pandas | Dataset processing |
| Numerical Processing | NumPy | Numerical operations |
| ML Framework | Scikit-learn | Model training and evaluation |
| Advanced ML | XGBoost | Classification |
| Model Storage | Joblib | Serialized model persistence |
| Database | MySQL | Persistent data storage |
| API Format | REST + JSON | Frontend ↔ backend ↔ ML communication |
| API Testing | Postman | REST API testing |
| Java Build Tool | Maven | Dependency/build management |
| Version Control | Git / GitHub | Source-code management |
| Deployment | Docker | Containerized deployment |
| Testing | JUnit, Pytest | Backend and ML service testing |
| Dev Tools | IntelliJ IDEA / VS Code, Jupyter Notebook | Development and experimentation |

---

## 8. System Architecture

```text
                    ┌─────────────────────┐
                    │      FRONTEND       │
                    │ HTML5 / CSS3 / JS   │
                    │ Bootstrap 5         │
                    │ Chart.js            │
                    └──────────┬──────────┘
                               │
                         REST / JSON
                               │
                               ▼
                    ┌─────────────────────┐
                    │     SPRING BOOT     │
                    │       JAVA          │
                    │                     │
                    │ Spring Security     │
                    │ JWT Authentication  │
                    │ Business Logic      │
                    │ REST Controllers    │
                    └──────┬────────┬─────┘
                           │        │
                    JPA / SQL       │ REST / JSON
                           │        │
                           ▼        ▼
                    ┌──────────┐  ┌──────────────┐
                    │  MySQL   │  │ Python ML API│
                    │ Database │  │   FastAPI    │
                    └──────────┘  └──────┬───────┘
                                         │
                                  ┌──────▼──────┐
                                  │ ML Model    │
                                  │ Scikit-learn│
                                  │ / XGBoost   │
                                  └─────────────┘
```

**Design decision:** the ML model is served via a standalone FastAPI microservice rather than Java invoking a Python script per request. This gives a clean separation between the enterprise backend and the ML layer, keeps each independently testable and deployable, and avoids the performance/reliability issues of process-per-request execution.

---

## 9. Database Design

### 9.1 Entity Overview

| Table | Purpose |
|---|---|
| `app_user` | Authentication and role-based access (Admin/HR/Manager) |
| `department` | Lookup table for departments |
| `job_role` | Lookup table for job roles |
| `employees` | Employee master data and ML feature source |
| `predictions` | Prediction history, linked to employee and requesting user |

### 9.2 Key Fields

**employees** — mirrors the ML feature set: age, gender, department, job role, job level, monthly income, overtime, job satisfaction, work-life balance, performance rating, distance from home, years at company, years in current role, total working years, number of companies worked, training time.

**predictions** — prediction (`STAY`/`LEAVE`), probability, risk level (`LOW`/`MEDIUM`/`HIGH`), `model_version` (for traceability across retraining), `requested_by` (audit trail), timestamp.

A full SQL script (`schema.sql`) implementing this design, including constraints, indexes, and seed data, has been finalized separately as part of Phase 3.

---

## 10. API Design

### 10.1 Spring Boot REST Endpoints

| Method | Endpoint | Purpose | Roles |
|---|---|---|---|
| POST | `/api/auth/login` | Authenticate and issue JWT | All |
| POST | `/api/employees` | Add employee | Admin, HR |
| GET | `/api/employees` | List employees | Admin, HR, Manager |
| GET | `/api/employees/{id}` | Get employee by ID | Admin, HR, Manager |
| PUT | `/api/employees/{id}` | Update employee | Admin, HR |
| DELETE | `/api/employees/{id}` | Delete employee | Admin |
| POST | `/api/predict` | Predict attrition for an employee | Admin, HR |
| GET | `/api/predictions` | View prediction history | Admin, HR, Manager |
| GET | `/api/analytics/*` | Aggregated data for dashboard/charts | Admin, HR, Manager |

### 10.2 FastAPI ML Endpoint

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/predict` | Accepts employee feature JSON, returns prediction, probability, risk level |
| GET | `/health` | Service health check |

---

## 11. Machine Learning Design

**Workflow:** Data Collection → Cleaning → EDA → Feature Engineering → Categorical Encoding → Train/Test Split → Class Imbalance Handling → Model Training → Evaluation → Best Model Selection → Serialization (Joblib) → Prediction Service.

**Class imbalance:** attrition datasets are typically imbalanced (majority "Stay"). SMOTE or class weighting will be applied, with threshold tuning rather than relying on default 0.5 cutoffs.

**Evaluation metrics:** Accuracy, Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix — accuracy alone is not sufficient given class imbalance.

**Candidate algorithms:** Logistic Regression, Decision Tree, Random Forest, SVM, Gradient Boosting, XGBoost — compared and the best performer selected.

**Model versioning:** every serialized model is tagged with a version identifier (e.g. `xgboost_v3_2026-08-01`), stored alongside each prediction row for traceability.

---

## 12. Security Design

```text
ADMIN
  └── Full system access

HR
  ├── Employee management
  ├── Predictions
  └── Analytics

MANAGER
  ├── View employees
  └── View prediction results
```

- Spring Security + JWT for authentication
- Role-based authorization (`@PreAuthorize`) on all protected endpoints
- Passwords stored as bcrypt hashes, never plaintext
- CORS configured on both Spring Boot and FastAPI for cross-origin frontend requests

---

## 13. UI/UX Design

**Layout:** left sidebar navigation (Dashboard, Employees, Attrition Prediction, Analytics, High-Risk Employees, Prediction History, Settings) with a main content area for KPI cards, charts, forms, and tables.

**Core screens:**
1. **Login** — email/password authentication
2. **Dashboard** — KPI cards (Total Employees, Attrition Count, Attrition Rate, High-Risk Count, Avg. Probability) plus trend and distribution charts
3. **Employee Prediction** — form capturing employee attributes, submits to `/api/predict`, displays result card (risk level, probability, recommendation)
4. **Analytics** — Chart.js visualizations: attrition by department, job role, age, salary, overtime, satisfaction, years at company
5. **High-Risk Employees** — sortable/filterable table with risk indicator and drill-down action

---

## 14. Development Phases

1. Requirement Analysis
2. UI/UX Design
3. Database Design
4. Dataset Preparation & EDA
5. Machine Learning Development
6. Python ML API Development
7. Spring Boot Backend Development
8. Authentication & Authorization
9. Frontend Development
10. System Integration
11. Testing
12. Deployment
13. Documentation
14. Final Demonstration

---

## 15. Change Log

> This section is the **only** place future changes should be recorded. Sections 1–14 represent the finalized baseline; if scope, stack, or design decisions change later, add a dated entry below describing what changed and why, rather than editing the baseline sections silently.

| Date | Change Description | Reason |
|---|---|---|
| — | Baseline document created | Initial finalized architecture and requirements |

