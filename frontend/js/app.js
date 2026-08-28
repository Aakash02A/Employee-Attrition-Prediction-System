/**
 * Shared App Logic (Shell, Sidebar, Auth)
 */

document.addEventListener('DOMContentLoaded', () => {


  // Initialize Sidebar Logic
  initSidebar();
  initTheme();
});

function initSidebar() {
  // Mobile Sidebar Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const sidebar = document.getElementById('sidebar');

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth < 768) {
        if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target) && sidebar.classList.contains('show')) {
          sidebar.classList.remove('show');
        }
      }
    });
  }

  // Active Link Highlighting based on current path
  const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
  const navLinks = document.querySelectorAll('.sidebar .nav-link');
  
  navLinks.forEach(link => {
    // Match by exact filename
    const href = link.getAttribute('href');
    if (href && href !== '#' && href === currentPage) {
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    }
  });

  // User info & Logout
  if (typeof Auth !== 'undefined') {
    const user = Auth.getUser();
    if (user) {
      const nameEl = document.querySelector('.user-name');
      const roleEl = document.querySelector('.user-role');
      if (nameEl) nameEl.textContent = user.fullName || user.email || 'Admin';
      if (roleEl) roleEl.textContent = user.role || 'HR Admin';
    }
  }

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (typeof Auth !== 'undefined') {
        Auth.logout();
      } else {
        sessionStorage.clear();
        window.location.href = 'login.html';
      }
    });
  }
}

// Helper for formatting currency
const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

// Helper for formatting numbers
const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

// Theme Toggle Logic
function initTheme() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) return;
  
  const icon = themeToggle.querySelector('i');
  
  // Check local storage or system preference
  const currentTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  
  if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    document.documentElement.setAttribute('data-bs-theme', 'dark');
    if(icon) { icon.classList.remove('bi-sun'); icon.classList.add('bi-moon'); }
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
    document.documentElement.setAttribute('data-bs-theme', 'light');
    if(icon) { icon.classList.remove('bi-moon'); icon.classList.add('bi-sun'); }
  }
  
  themeToggle.addEventListener('click', () => {
    let theme = document.documentElement.getAttribute('data-theme');
    
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'light');
      document.documentElement.setAttribute('data-bs-theme', 'light');
      localStorage.setItem('theme', 'light');
      if(icon) { icon.classList.remove('bi-moon'); icon.classList.add('bi-sun'); }
    } else {
      document.documentElement.setAttribute('data-theme', 'dark');
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      localStorage.setItem('theme', 'dark');
      if(icon) { icon.classList.remove('bi-sun'); icon.classList.add('bi-moon'); }
    }
    
    // Dispatch event so charts can update if needed
    window.dispatchEvent(new Event('themeChanged'));
  });
}


