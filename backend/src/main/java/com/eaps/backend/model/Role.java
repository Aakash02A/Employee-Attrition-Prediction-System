package com.eaps.backend.model;

/**
 * User roles for role-based access control.
 *
 * <ul>
 *   <li><b>ADMIN</b> — Full system access: manage users, employees, predictions, settings</li>
 *   <li><b>HR</b> — Manage employees, run predictions, view analytics</li>
 *   <li><b>MANAGER</b> — View-only access to employees and predictions</li>
 * </ul>
 */
public enum Role {
    ADMIN,
    HR,
    MANAGER
}
