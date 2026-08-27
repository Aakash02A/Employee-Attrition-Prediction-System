-- ============================================================
-- Employee Attrition Prediction System
-- MySQL Schema
-- ============================================================
--
-- ER Diagram (text form)
--
--   department (1) ──< (many) employees
--   job_role   (1) ──< (many) employees
--   app_user   (1) ──< (many) predictions   [requested_by, nullable]
--   employees  (1) ──< (many) predictions
--
--   ┌───────────┐        ┌───────────┐
--   │ department│        │ job_role  │
--   └─────┬─────┘        └─────┬─────┘
--         │ 1                  │ 1
--         │                    │
--         ▼ many          many ▼
--       ┌────────────────────────┐        ┌───────────┐
--       │        employees        │◄──────┤  app_user │
--       └───────────┬──────────────┘  1    └─────┬─────┘
--                    │ 1                          │ 1
--                    ▼ many                        ▼ many
--              ┌──────────────┐          (requested_by FK)
--              │  predictions  │───────────────────┘
--              └──────────────┘
--
-- Covers: authentication/roles, employee master data,
-- department/job-role lookups, and prediction history.
-- Engine: InnoDB (required for foreign keys)
-- Charset: utf8mb4 (safe default for names, emails, free text)
-- ============================================================

CREATE DATABASE IF NOT EXISTS employee_attrition_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE employee_attrition_db;

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. Lookup tables
-- ------------------------------------------------------------
-- Kept as normalized lookups rather than free-text columns on
-- `employees` so the frontend dropdowns and Chart.js groupings
-- stay consistent, and so new departments/roles don't require
-- a schema change.

DROP TABLE IF EXISTS department;
CREATE TABLE department (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

DROP TABLE IF EXISTS job_role;
CREATE TABLE job_role (
    job_role_id      INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. Authentication / Authorization
-- ------------------------------------------------------------
-- Role is stored as an ENUM to match the three roles defined in
-- the architecture (ADMIN / HR / MANAGER). Password is stored
-- as a bcrypt hash — Spring Security's BCryptPasswordEncoder
-- output is always 60 chars, so VARCHAR(60) would also work,
-- but 255 leaves headroom if the hashing scheme ever changes.

DROP TABLE IF EXISTS app_user;
CREATE TABLE app_user (
    user_id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_name        VARCHAR(150) NOT NULL,
    email            VARCHAR(150) NOT NULL UNIQUE,
    password_hash    VARCHAR(255) NOT NULL,
    role             ENUM('ADMIN', 'HR', 'MANAGER') NOT NULL DEFAULT 'MANAGER',
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                         ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. Employee master data
-- ------------------------------------------------------------
-- Field set matches the "Important ML Features" list from the
-- tech stack document (Section 7), so the columns here map
-- directly onto the feature vector sent to the FastAPI service.
--
-- Nullability notes:
--   - Fields the ML model requires for a prediction are NOT NULL.
--   - `employee_code` is a human-readable ID (e.g. "EMP001") kept
--     separate from the surrogate `employee_id` primary key, since
--     the UI mockups display codes like EMP001 rather than raw IDs.

DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
    employee_id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_code           VARCHAR(20) NOT NULL UNIQUE,          -- e.g. EMP001
    first_name              VARCHAR(100) NOT NULL,
    last_name               VARCHAR(100) NOT NULL,
    email                    VARCHAR(150) UNIQUE,
    gender                   ENUM('Male', 'Female', 'Other') NOT NULL,
    age                      TINYINT UNSIGNED NOT NULL,
    department_id            INT NOT NULL,
    job_role_id               INT NOT NULL,
    job_level                TINYINT UNSIGNED NOT NULL,           -- e.g. 1-5
    monthly_income            DECIMAL(12,2) NOT NULL,
    last_salary_hike_percent  DECIMAL(5,2),                       -- e.g. 11.00 -> "Salary Hike: 11%"
    overtime                  BOOLEAN NOT NULL DEFAULT FALSE,
    job_satisfaction          TINYINT UNSIGNED NOT NULL,          -- e.g. 1-4
    work_life_balance         TINYINT UNSIGNED NOT NULL,          -- e.g. 1-4
    performance_rating        TINYINT UNSIGNED,                   -- e.g. 1-4
    distance_from_home        SMALLINT UNSIGNED,                  -- in km/miles
    years_at_company          SMALLINT UNSIGNED NOT NULL,
    years_in_current_role     SMALLINT UNSIGNED,
    total_working_years       SMALLINT UNSIGNED,
    num_companies_worked      TINYINT UNSIGNED,
    training_time_last_year   TINYINT UNSIGNED,                   -- days/hours of training
    is_active                BOOLEAN NOT NULL DEFAULT TRUE,        -- FALSE once marked as left
    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id) REFERENCES department(department_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT fk_employee_job_role
        FOREIGN KEY (job_role_id) REFERENCES job_role(job_role_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT chk_job_satisfaction CHECK (job_satisfaction BETWEEN 1 AND 4),
    CONSTRAINT chk_work_life_balance CHECK (work_life_balance BETWEEN 1 AND 4),
    CONSTRAINT chk_age CHECK (age BETWEEN 16 AND 80)
) ENGINE=InnoDB;

CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_job_role ON employees(job_role_id);
CREATE INDEX idx_employees_active ON employees(is_active);

-- ------------------------------------------------------------
-- 4. Prediction history
-- ------------------------------------------------------------
-- One row per prediction run for an employee. `model_version`
-- is included per the earlier recommendation so historical
-- predictions stay traceable to the model that produced them,
-- even after retraining. `requested_by` links back to the
-- app_user who triggered it (HR/Manager), supporting the
-- "Prediction History" screen and audit needs.

DROP TABLE IF EXISTS predictions;
CREATE TABLE predictions (
    prediction_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id          BIGINT NOT NULL,
    requested_by          BIGINT,                                -- app_user.user_id, nullable for system/batch runs
    prediction             ENUM('STAY', 'LEAVE') NOT NULL,
    probability             DECIMAL(5,4) NOT NULL,                -- 0.0000 - 1.0000
    risk_level              ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL,
    model_version           VARCHAR(50) NOT NULL,                 -- e.g. 'xgboost_v3_2026-08-01'
    prediction_date          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prediction_employee
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_prediction_user
        FOREIGN KEY (requested_by) REFERENCES app_user(user_id)
        ON UPDATE CASCADE ON DELETE SET NULL,

    CONSTRAINT chk_probability CHECK (probability BETWEEN 0 AND 1)
) ENGINE=InnoDB;

CREATE INDEX idx_predictions_employee ON predictions(employee_id);
CREATE INDEX idx_predictions_risk ON predictions(risk_level);
CREATE INDEX idx_predictions_date ON predictions(prediction_date);

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- 5. Seed data (lookups + one demo admin user)
-- ------------------------------------------------------------

INSERT INTO department (name) VALUES
    ('Sales'), ('Research & Development'), ('Human Resources'),
    ('IT'), ('Finance'), ('Marketing');

INSERT INTO job_role (name) VALUES
    ('Sales Executive'), ('Sales Representative'), ('Research Scientist'),
    ('Laboratory Technician'), ('Manufacturing Director'), ('Healthcare Representative'),
    ('Manager'), ('Human Resources'), ('Research Director');

-- Demo admin account. Replace password_hash with a real bcrypt
-- hash generated by Spring Security before using in any real
-- environment — this placeholder is NOT a valid hash.
INSERT INTO app_user (full_name, email, password_hash, role) VALUES
    ('System Admin', 'admin@company.com', '$2a$10$REPLACE_WITH_REAL_BCRYPT_HASH', 'ADMIN');


-- ============================================================
-- Migration: Add ML-required fields to `employees`
-- Run this AFTER schema.sql has already been applied.
-- ============================================================
-- Phase 6 (FastAPI /predict) requires 30 raw input fields, matching
-- the IBM HR Attrition dataset's columns. The original employees table
-- (Phase 3) covered ~20 of them. This migration adds the remaining ones
-- so `employees` becomes the single source of truth for predictions —
-- Spring Boot can map a row directly to the ML request body with no
-- guessing or defaulting required.

USE employee_attrition_db;

ALTER TABLE employees
    ADD COLUMN daily_rate                 INT UNSIGNED       NOT NULL DEFAULT 800  AFTER monthly_income,
    ADD COLUMN monthly_rate                INT UNSIGNED       NOT NULL DEFAULT 15000 AFTER daily_rate,
    ADD COLUMN hourly_rate                 SMALLINT UNSIGNED  NOT NULL DEFAULT 65   AFTER monthly_rate,
    ADD COLUMN business_travel             ENUM('Non-Travel', 'Travel_Rarely', 'Travel_Frequently')
                                                                NOT NULL DEFAULT 'Travel_Rarely',
    ADD COLUMN education                   TINYINT UNSIGNED   NOT NULL DEFAULT 3,   -- 1-5
    ADD COLUMN education_field             ENUM('Human Resources','Life Sciences','Marketing',
                                                   'Medical','Other','Technical Degree')
                                                                NOT NULL DEFAULT 'Life Sciences',
    ADD COLUMN environment_satisfaction    TINYINT UNSIGNED   NOT NULL DEFAULT 3,   -- 1-4
    ADD COLUMN job_involvement             TINYINT UNSIGNED   NOT NULL DEFAULT 3,   -- 1-4
    ADD COLUMN marital_status              ENUM('Single','Married','Divorced')
                                                                NOT NULL DEFAULT 'Single',
    ADD COLUMN relationship_satisfaction   TINYINT UNSIGNED   NOT NULL DEFAULT 3,   -- 1-4
    ADD COLUMN stock_option_level          TINYINT UNSIGNED   NOT NULL DEFAULT 0,   -- 0-3
    ADD COLUMN years_since_last_promotion  SMALLINT UNSIGNED  NOT NULL DEFAULT 0,
    ADD COLUMN years_with_curr_manager     SMALLINT UNSIGNED  NOT NULL DEFAULT 0,

    ADD CONSTRAINT chk_education CHECK (education BETWEEN 1 AND 5),
    ADD CONSTRAINT chk_environment_satisfaction CHECK (environment_satisfaction BETWEEN 1 AND 4),
    ADD CONSTRAINT chk_job_involvement CHECK (job_involvement BETWEEN 1 AND 4),
    ADD CONSTRAINT chk_relationship_satisfaction CHECK (relationship_satisfaction BETWEEN 1 AND 4),
    ADD CONSTRAINT chk_stock_option_level CHECK (stock_option_level BETWEEN 0 AND 3);

-- Note on Department / JobRole values:
-- The ML model was trained on IBM's category set: Department in
-- ('Sales', 'Research & Development', 'Human Resources') and 9 specific
-- JobRole values. The department/job_role lookup tables already seeded
-- in schema.sql include extra values (IT, Finance, Marketing) that the
-- model never saw during training. Predictions for employees in those
-- departments will still work (the encoder falls back to the reference
-- category), but won't reflect anything the model actually learned for
-- them — flag this as a known limitation, or restrict new employee
-- department/job-role dropdowns to the trained category set.