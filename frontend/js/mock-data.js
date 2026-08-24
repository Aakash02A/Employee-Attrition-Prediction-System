/**
 * Mock Data for Employee Attrition Prediction System
 * This file stubs the responses that would eventually come from the backend API.
 */

const MockData = {
  // --- Dashboard Aggregations ---
  kpis: {
    totalEmployees: 1206,
    totalEmployeesTrend: 5, // +5%
    attritionCount: 184,
    attritionTrend: -2, // -2% (good)
    attritionRate: 15.2, // %
    attritionRateTrend: -1.5,
    atRiskCount: 89,
    atRiskTrend: 10,
    avgProbability: 42.5, // %
  },

  charts: {
    // Trend line (last 6 months)
    attritionTrend: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      data: [25, 32, 28, 45, 30, 24]
    },
    // Doughnut
    riskDistribution: {
      labels: ['Low Risk', 'Medium Risk', 'High Risk'],
      data: [750, 367, 89],
      colors: ['#10b981', '#f59e0b', '#ef4444']
    },
    // Bar
    byDepartment: {
      labels: ['Sales', 'R&D', 'HR', 'Support', 'Marketing'],
      data: [65, 80, 15, 14, 10]
    },
    // Bar
    byRole: {
      labels: ['Sales Exec', 'Research Sci', 'Lab Tech', 'Manager', 'HR Rep'],
      data: [45, 35, 40, 15, 10]
    }
  },

  // --- Analytics Page Charts ---
  analytics: {
    byDepartment: {
      labels: ['Sales', 'R&D', 'HR', 'Support'],
      data: [65, 80, 15, 14]
    },
    byRole: {
      labels: ['Sales Exec', 'Research Sci', 'Lab Tech', 'Manager', 'HR'],
      data: [45, 35, 40, 15, 10]
    },
    byAgeGroup: {
      labels: ['18-25', '26-35', '36-45', '46-55', '55+'],
      data: [45, 80, 30, 20, 9]
    },
    bySalaryRange: {
      labels: ['< $2.5k', '$2.5k-$5k', '$5k-$10k', '$10k+'],
      data: [75, 60, 35, 14]
    },
    byOvertime: {
      labels: ['Yes', 'No'],
      left: [95, 30],
      stayed: [150, 750]
    },
    byJobSatisfaction: {
      labels: ['1 (Low)', '2', '3', '4 (High)'],
      data: [66, 46, 73, 52]
    },
    byYearsAtCompany: {
      labels: ['0-2 Years', '3-5 Years', '6-10 Years', '11+ Years'],
      data: [90, 50, 30, 14]
    }
  },

  // --- Right Panel Specific ---
  contextual: {
    retentionTarget: 85, // %
    retentionCurrent: 84.8,
    topRiskDepartments: [
      { name: 'R&D', riskScore: 78, change: '+5%' },
      { name: 'Sales', riskScore: 65, change: '-2%' },
      { name: 'Support', riskScore: 42, change: '+1%' }
    ]
  },

  // --- Employees List (abbreviated ~30 items for mockup) ---
  employees: Array.from({ length: 30 }).map((_, i) => {
    const depts = ['Sales', 'Research & Development', 'Human Resources', 'Support'];
    const roles = ['Sales Executive', 'Research Scientist', 'Laboratory Technician', 'Manager', 'Healthcare Representative', 'Human Resources'];
    
    // Generate deterministic randoms based on index for mockup consistency
    const dept = depts[i % depts.length];
    const role = roles[(i * 3) % roles.length];
    const prob = ((i * 17) % 85) + 5; // 5 to 90
    
    let riskLevel = 'Low';
    if (prob > 40 && prob <= 70) riskLevel = 'Medium';
    if (prob > 70) riskLevel = 'High';

    return {
      empCode: `EMP-${1000 + i}`,
      age: 25 + (i % 35), // 25-60
      department: dept,
      jobRole: role,
      monthlyIncome: 3000 + ((i * 1300) % 15000),
      yearsAtCompany: (i * 2) % 15,
      probability: prob,
      riskLevel: riskLevel
    };
  }),

  // --- Prediction History ---
  history: Array.from({ length: 15 }).map((_, i) => {
    const prob = ((i * 23) % 85) + 5;
    let prediction = prob > 50 ? 'Leave' : 'Stay';
    
    return {
      id: 5000 + i,
      empCode: `EMP-${1000 + (i % 5)}`,
      prediction: prediction,
      probability: prob,
      modelVersion: 'v2.1.0',
      date: new Date(Date.now() - (i * 86400000)).toISOString().split('T')[0],
      requestedBy: 'Robert Brown'
    };
  })
};

// Make available globally
window.MockData = MockData;
