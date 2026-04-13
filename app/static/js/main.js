/* ==================== Main JavaScript ==================== */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers if using Bootstrap
    initializeBootstrapComponents();
    
    // Add any global event listeners
    setupEventListeners();
});

/**
 * Initialize Bootstrap tooltips and popovers
 */
function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => 
        new bootstrap.Tooltip(tooltipTriggerEl)
    );
    
    // Popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => 
        new bootstrap.Popover(popoverTriggerEl)
    );
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Add confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = '₹') {
    return currency + parseFloat(amount).toFixed(2);
}

/**
 * Format date
 */
function formatDate(dateString, format = 'DD-MM-YYYY') {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Show loading spinner
 */
function showLoader() {
    const loader = document.createElement('div');
    loader.className = 'spinner-border text-primary';
    loader.setAttribute('role', 'status');
    loader.innerHTML = '<span class="visually-hidden">Loading...</span>';
    document.body.appendChild(loader);
    return loader;
}

/**
 * Hide loading spinner
 */
function hideLoader(loader) {
    if (loader) {
        loader.remove();
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 3000) {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    };
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass[type] || alertClass['info']} alert-dismissible fade show`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.alert-container') || document.body;
    container.insertBefore(alert, container.firstChild);
    
    if (duration > 0) {
        setTimeout(() => {
            alert.remove();
        }, duration);
    }
    
    return alert;
}

/**
 * Fetch API helper
 */
async function apiCall(url, method = 'GET', data = null, headers = {}) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Local storage helpers
 */
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('LocalStorage set failed:', error);
        }
    },
    get: (key) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('LocalStorage get failed:', error);
            return null;
        }
    },
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('LocalStorage remove failed:', error);
        }
    },
    clear: () => {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('LocalStorage clear failed:', error);
        }
    }
};

// Export functions for use in other scripts
window.movieAppUtils = {
    formatCurrency,
    formatDate,
    showLoader,
    hideLoader,
    showNotification,
    apiCall,
    debounce,
    throttle,
    storage
};
