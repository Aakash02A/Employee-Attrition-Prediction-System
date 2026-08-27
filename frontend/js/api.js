/**
 * API Client — Auth & Api globals for the Employee Attrition Prediction System.
 *
 * Usage:
 *   Auth.requireLogin()             — redirect to login.html if no valid session
 *   Auth.login(email, password)     — POST /api/auth/login, saves JWT + user info
 *   Auth.logout()                   — clears session and redirects to login.html
 *   Auth.getUser()                  — { token, role, fullName }
 *   Auth.getToken()                 — raw JWT string (or null)
 *
 *   Api.getEmployees()              — GET  /api/employees
 *   Api.getEmployee(id)             — GET  /api/employees/:id
 *   Api.predict(employeeId)         — POST /api/predict  { employeeId }
 *   Api.getEmployeePredictions(id)  — GET  /api/predictions/employee/:id
 *   Api.getPredictions()            — GET  /api/predictions
 *   Api.getHighRiskPredictions()    — GET  /api/predictions/high-risk
 */

const API_BASE_URL = 'http://localhost:8080/api';

// ── Auth ──────────────────────────────────────────────────────

const Auth = (() => {
  const SESSION_KEY = 'eaps_session';

  /** Save the auth response into sessionStorage. */
  function saveSession(data) {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(data));
  }

  /** Get the stored session object, or null. */
  function getUser() {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  }

  /** Get the raw JWT token, or null. */
  function getToken() {
    const user = getUser();
    return user ? user.token : null;
  }

  /** Redirect to login.html if no valid session exists. */
  function requireLogin() {
    if (!getToken()) {
      window.location.href = 'login.html';
    }
  }

  /**
   * Authenticate with the backend.
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{token: string, role: string, fullName: string}>}
   */
  async function login(email, password) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.message || 'Invalid email or password.');
    }

    const data = await res.json();
    saveSession(data);
    return data;
  }

  /** Clear session and redirect to login. */
  function logout() {
    sessionStorage.removeItem(SESSION_KEY);
    window.location.href = 'login.html';
  }

  return { saveSession, getUser, getToken, requireLogin, login, logout };
})();

// ── Api ───────────────────────────────────────────────────────

const Api = (() => {
  /**
   * Internal fetch wrapper that adds the Authorization header automatically.
   * On 401/403, redirects to login.
   */
  async function _fetch(path, options = {}) {
    const token = Auth.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });

    if (res.status === 401 || res.status === 403) {
      Auth.logout();
      throw new Error('Session expired. Please log in again.');
    }

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.message || errBody.error || `Request failed (${res.status})`);
    }

    // Handle 204 No Content
    if (res.status === 204) return null;

    return res.json();
  }

  // ── Employees ─────────────────────────────────────────────

  /** GET /api/employees → EmployeeResponse[] */
  function getEmployees() {
    return _fetch('/employees');
  }

  /** GET /api/employees/:id → EmployeeResponse */
  function getEmployee(id) {
    return _fetch(`/employees/${id}`);
  }

  // ── Predictions ───────────────────────────────────────────

  /**
   * POST /api/predict  { employeeId }
   * Triggers the ML prediction for the given employee.
   * @param {number} employeeId
   * @returns {Promise<PredictionResponse>}
   */
  function predict(employeeId) {
    return _fetch('/predict', {
      method: 'POST',
      body: JSON.stringify({ employeeId }),
    });
  }

  /** GET /api/predictions/employee/:id → PredictionResponse[] */
  function getEmployeePredictions(employeeId) {
    return _fetch(`/predictions/employee/${employeeId}`);
  }

  /** GET /api/predictions → PredictionResponse[] */
  function getPredictions() {
    return _fetch('/predictions');
  }

  /** GET /api/predictions/high-risk → PredictionResponse[] */
  function getHighRiskPredictions() {
    return _fetch('/predictions/high-risk');
  }

  return {
    getEmployees,
    getEmployee,
    predict,
    getEmployeePredictions,
    getPredictions,
    getHighRiskPredictions,
  };
})();
