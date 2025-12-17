// CineSync JavaScript

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Add loading state to buttons on form submit
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('no-loading')) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    });
});

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const anchors = document.querySelectorAll('a[href^="#"]');
    anchors.forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// Confirm before deleting/canceling bookings
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}

// Format currency
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// Debounce function for search
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

// Search functionality (if needed)
const searchInput = document.querySelector('input[name="q"]');
if (searchInput) {
    searchInput.addEventListener('input', debounce(function(e) {
        // You can add live search suggestions here
        console.log('Searching for:', e.target.value);
    }, 300));
}

// Seat map helper functions
const SeatSelector = {
    selectedSeats: new Set(),
    bookedSeats: new Set(),
    seatPrice: 0,

    init: function(seatPrice, bookedSeats) {
        this.seatPrice = seatPrice;
        this.bookedSeats = new Set(bookedSeats);
        this.bindEvents();
    },

    bindEvents: function() {
        const seats = document.querySelectorAll('.seat:not(.booked)');
        seats.forEach(seat => {
            seat.addEventListener('click', () => this.toggleSeat(seat));
        });
    },

    toggleSeat: function(seatElement) {
        const seatId = seatElement.dataset.seatId;

        if (this.selectedSeats.has(seatId)) {
            this.selectedSeats.delete(seatId);
            seatElement.classList.remove('selected');
        } else {
            this.selectedSeats.add(seatId);
            seatElement.classList.add('selected');
        }

        this.updateSelection();
    },

    updateSelection: function() {
        const count = this.selectedSeats.size;
        const total = count * this.seatPrice;

        const selectedInfo = document.getElementById('selectedInfo');
        const proceedBtn = document.getElementById('proceedBtn');

        if (count > 0) {
            selectedInfo.style.display = 'block';
            proceedBtn.disabled = false;

            // Update display
            document.getElementById('selectedSeats').textContent =
                Array.from(this.selectedSeats).join(', ');
            document.getElementById('totalAmount').textContent = total.toFixed(2);

            // Update form
            const seatInputsDiv = document.getElementById('seatInputs');
            seatInputsDiv.innerHTML = '';
            this.selectedSeats.forEach(seatId => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'seat_ids';
                input.value = seatId;
                seatInputsDiv.appendChild(input);
            });
        } else {
            selectedInfo.style.display = 'none';
            proceedBtn.disabled = true;
        }
    }
};

// Toast notification helper
const Toast = {
    show: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(toast);
            bsAlert.close();
        }, 3000);
    }
};

// Form validation helper
const FormValidator = {
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    validatePhone: function(phone) {
        const re = /^[\d\s\-\+\(\)]+$/;
        return phone === '' || re.test(phone);
    },

    highlightError: function(input, message) {
        input.classList.add('is-invalid');
        const feedback = input.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = message;
        } else {
            const div = document.createElement('div');
            div.className = 'invalid-feedback';
            div.textContent = message;
            input.parentElement.appendChild(div);
        }
    },

    clearError: function(input) {
        input.classList.remove('is-invalid');
        const feedback = input.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    }
};

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Bootstrap popovers
    const popoverTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="popover"]')
    );
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Back to top button
document.addEventListener('DOMContentLoaded', function() {
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });

        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});
