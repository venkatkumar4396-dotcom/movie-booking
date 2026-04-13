/* ==================== PRO FEATURES - TOAST NOTIFICATIONS & KEYBOARD SHORTCUTS ==================== */

// ======== TOAST NOTIFICATION SYSTEM ========
class Toast {
    constructor(message, type = 'info', duration = 4000) {
        this.message = message;
        this.type = type; // 'success', 'error', 'warning', 'info'
        this.duration = duration;
        this.element = null;
    }

    getIcon() {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[this.type] || icons['info'];
    }

    show() {
        const container = document.querySelector('.toast-container') || this.createContainer();
        
        this.element = document.createElement('div');
        this.element.className = `toast ${this.type}`;
        this.element.innerHTML = `
            <i class="${this.getIcon()}"></i>
            <span>${this.message}</span>
        `;

        container.appendChild(this.element);

        if (this.duration > 0) {
            setTimeout(() => this.hide(), this.duration);
        }

        // Trigger animation
        setTimeout(() => {
            this.element.style.opacity = '1';
        }, 10);
    }

    createContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    hide() {
        if (this.element) {
            this.element.classList.add('hide');
            setTimeout(() => this.element.remove(), 400);
        }
    }
}

// Global toast function
function showToast(message, type = 'info', duration = 4000) {
    const toast = new Toast(message, type, duration);
    toast.show();
    return toast;
}

// ======== KEYBOARD SHORTCUTS FOR SEAT SELECTION ========
class SeatKeyboardShortcuts {
    constructor() {
        this.setupListeners();
    }

    setupListeners() {
        document.addEventListener('keydown', (e) => {
            // Only work on booking page
            if (!document.getElementById('bookingForm')) return;

            switch(e.key) {
                case 'ArrowUp':
                    this.selectAdjacentSeat('up', e);
                    break;
                case 'ArrowDown':
                    this.selectAdjacentSeat('down', e);
                    break;
                case 'ArrowLeft':
                    this.selectAdjacentSeat('left', e);
                    break;
                case 'ArrowRight':
                    this.selectAdjacentSeat('right', e);
                    break;
                case 'Enter':
                    this.confirmBooking(e);
                    break;
                case 'Escape':
                    this.clearSelection(e);
                    break;
                case 'r':
                    if (e.ctrlKey || e.metaKey) {
                        this.recommendSeats(e);
                    }
                    break;
            }
        });
    }

    selectAdjacentSeat(direction, event) {
        // Get currently focused seat or first available
        const form = document.getElementById('bookingForm');
        const rows = form.querySelectorAll('.seat-row');
        
        showToast(`Arrow key: ${direction}`, 'info', 2000);
    }

    confirmBooking(event) {
        const proceedBtn = document.getElementById('proceedBtn');
        if (proceedBtn && !proceedBtn.disabled) {
            showToast('Proceeding to payment...', 'success');
            proceedBtn.click();
        }
    }

    clearSelection(event) {
        const form = document.getElementById('bookingForm');
        const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked');
        checkboxes.forEach(cb => cb.click());
        showToast('Selection cleared', 'info', 2000);
    }

    recommendSeats(event) {
        event.preventDefault();
        showToast('Loading smart recommendations...', 'info', 3000);
    }
}

// Initialize keyboard shortcuts when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new SeatKeyboardShortcuts();
    });
} else {
    new SeatKeyboardShortcuts();
}

// ======== SMART SEAT RECOMMENDATIONS ========
class SmartSeatRecommender {
    constructor() {
        this.screenCenterX = 0;
        this.screenCenterY = 0;
    }

    // Get recommendations based on screen position
    getRecommendations(seatsData, count = 5) {
        const available = seatsData.filter(seat => seat.is_available);
        
        // Score seats based on:
        // 1. Distance from screen center
        // 2. Seat category (premium scores higher)
        // 3. Adjacent available seats (togetherness)
        
        const scored = available.map(seat => {
            let score = 0;
            
            // Center position bonus
            const row = this.getRowFromSeat(seat);
            const screenCenter = this.estimateScreenCenter(seatsData);
            const distFromCenter = Math.abs(row - screenCenter);
            score += (50 - distFromCenter) * 2; // Center seats score higher
            
            // Category bonus
            if (seat.category === 'PREMIUM') score += 30;
            if (seat.category === 'VIP') score += 20;
            
            return { ...seat, score };
        });

        return scored.sort((a, b) => b.score - a.score).slice(0, count);
    }

    getRowFromSeat(seat) {
        // Extract row number from seat data
        return parseInt(seat.number.charCodeAt(0)) || 0;
    }

    estimateScreenCenter(seatsData) {
        return Math.floor(seatsData.length / 2);
    }
}

// ======== ACCESSIBILITY ENHANCEMENTS ========
function enhanceAccessibility() {
    // Add ARIA labels to interactive elements
    document.querySelectorAll('.seat-label').forEach((seat, index) => {
        const seatNumber = seat.textContent.trim();
        const isBooked = seat.classList.contains('booked');
        const category = seat.className.match(/\b(regular|vip|premium|balcony)\b/)?.[1] || 'regular';
        
        const ariaLabel = isBooked 
            ? `${seatNumber} - Booked, unavailable`
            : `${seatNumber} - ${category} seat, available for selection`;
        
        seat.setAttribute('role', 'checkbox');
        seat.setAttribute('aria-label', ariaLabel);
        seat.setAttribute('tabindex', isBooked ? '-1' : '0');
    });

    // Enhanced button labels
    document.querySelectorAll('button').forEach(btn => {
        if (!btn.getAttribute('aria-label') && btn.textContent.trim()) {
            btn.setAttribute('role', 'button');
        }
    });

    // Skip to main content
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-to-main';
    skipLink.textContent = 'Skip to main content';
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Add main content landmark
    const mainContent = document.querySelector('main') || document.querySelector('.container');
    if (mainContent && !mainContent.id) {
        mainContent.id = 'main-content';
    }
}

// Initialize accessibility when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceAccessibility);
} else {
    enhanceAccessibility();
}

// ======== ENHANCED BUTTON LOADING STATES ========
function setupLoadingButtons() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                // Add loading class
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                // Show loading toast
                showToast('Processing your request...', 'info', 5000);
            }
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupLoadingButtons);
} else {
    setupLoadingButtons();
}

// Premium modal interactions (shows a Bootstrap modal and simulates subscription)
function initPremiumInteractions() {
    const btn = document.getElementById('becomeMemberBtn');
    const modalEl = document.getElementById('premiumModal');
    if (!btn || !modalEl) return;

    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    });

    const subscribeBtn = document.getElementById('subscribeBtn');
    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showToast('Subscription successful — welcome to Premium!', 'success', 3000);
            const modalInstance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            modalInstance.hide();
        });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPremiumInteractions);
} else {
    initPremiumInteractions();
}
