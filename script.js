// SkillSwap Custom JavaScript

// Global app object
const SkillSwap = {
    // Initialize app functionality
    init() {
        this.setupEventListeners();
        this.setupAnimations();
        this.setupFormValidation();
        this.setupTooltips();
        this.setupAutoResizeTextareas();
    },

    // Set up global event listeners
    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Auto-dismiss alerts after 5 seconds
        document.querySelectorAll('.alert').forEach(alert => {
            if (!alert.querySelector('.btn-close')) return;
            
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });

        // Enhanced dropdown functionality
        document.querySelectorAll('.dropdown-toggle').forEach(dropdown => {
            dropdown.addEventListener('shown.bs.dropdown', function () {
                this.setAttribute('aria-expanded', 'true');
            });
            
            dropdown.addEventListener('hidden.bs.dropdown', function () {
                this.setAttribute('aria-expanded', 'false');
            });
        });
    },

    // Set up page animations
    setupAnimations() {
        // Add fade-in animation to cards on page load
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(20px)';
                    entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 100);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe cards for animation
        document.querySelectorAll('.card, .skill-card').forEach(card => {
            observer.observe(card);
        });
    },

    // Set up form validation
    setupFormValidation() {
        // Custom form validation for skill forms
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Focus on first invalid field
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
                
                form.classList.add('was-validated');
            });

            // Real-time validation feedback
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    if (this.checkValidity()) {
                        this.classList.remove('is-invalid');
                        this.classList.add('is-valid');
                    } else {
                        this.classList.remove('is-valid');
                        this.classList.add('is-invalid');
                    }
                });
            });
        });

        // Enhanced skill input validation
        document.querySelectorAll('input[name^="skills_"]').forEach(input => {
            input.addEventListener('input', function() {
                const value = this.value.trim();
                const minLength = 2;
                const maxLength = 100;
                
                if (value.length < minLength && value.length > 0) {
                    this.setCustomValidity(`Skill name must be at least ${minLength} characters long`);
                } else if (value.length > maxLength) {
                    this.setCustomValidity(`Skill name must be less than ${maxLength} characters long`);
                } else {
                    this.setCustomValidity('');
                }
            });
        });
    },

    // Set up Bootstrap tooltips
    setupTooltips() {
        // Initialize all tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => 
            new bootstrap.Tooltip(tooltipTriggerEl)
        );

        // Add tooltips to rating stars
        document.querySelectorAll('.rating i').forEach((star, index) => {
            const rating = index + 1;
            star.setAttribute('title', `${rating} star${rating > 1 ? 's' : ''}`);
            star.setAttribute('data-bs-toggle', 'tooltip');
            new bootstrap.Tooltip(star);
        });
    },

    // Set up auto-resizing textareas
    setupAutoResizeTextareas() {
        document.querySelectorAll('textarea').forEach(textarea => {
            // Set initial height
            this.resizeTextarea(textarea);
            
            // Add event listeners
            textarea.addEventListener('input', () => this.resizeTextarea(textarea));
            textarea.addEventListener('focus', () => this.resizeTextarea(textarea));
        });
    },

    // Resize textarea to fit content
    resizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    },

    // Utility functions
    utils: {
        // Show loading state on button
        showButtonLoading(button, text = 'Loading...') {
            const originalText = button.innerHTML;
            button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
            button.disabled = true;
            return originalText;
        },

        // Hide loading state on button
        hideButtonLoading(button, originalText) {
            button.innerHTML = originalText;
            button.disabled = false;
        },

        // Show toast notification
        showToast(message, type = 'info') {
            const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
            const toast = this.createToast(message, type);
            toastContainer.appendChild(toast);
            
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            // Remove toast after it's hidden
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        },

        // Create toast container if it doesn't exist
        createToastContainer() {
            const container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1200';
            document.body.appendChild(container);
            return container;
        },

        // Create toast element
        createToast(message, type) {
            const icons = {
                success: 'fas fa-check-circle text-success',
                error: 'fas fa-exclamation-circle text-danger',
                warning: 'fas fa-exclamation-triangle text-warning',
                info: 'fas fa-info-circle text-info'
            };

            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.setAttribute('role', 'alert');
            toast.innerHTML = `
                <div class="toast-header">
                    <i class="${icons[type] || icons.info} me-2"></i>
                    <strong class="me-auto">SkillSwap</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            `;
            return toast;
        },

        // Format date for display
        formatDate(date) {
            return new Intl.DateTimeFormat('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(new Date(date));
        },

        // Format relative time
        formatRelativeTime(date) {
            const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
            const diff = Date.now() - new Date(date).getTime();
            const seconds = Math.floor(diff / 1000);
            const minutes = Math.floor(seconds / 60);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);

            if (days > 0) return rtf.format(-days, 'day');
            if (hours > 0) return rtf.format(-hours, 'hour');
            if (minutes > 0) return rtf.format(-minutes, 'minute');
            return rtf.format(-seconds, 'second');
        },

        // Debounce function
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Throttle function
        throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    },

    // Search functionality
    search: {
        init() {
            this.setupSearchFilters();
            this.setupRealTimeSearch();
        },

        setupSearchFilters() {
            // Category filter auto-submit
            const categoryFilter = document.getElementById('category-filter');
            if (categoryFilter) {
                categoryFilter.addEventListener('change', function() {
                    this.form.submit();
                });
            }
        },

        setupRealTimeSearch() {
            const searchInput = document.getElementById('search-query');
            if (!searchInput) return;

            const debouncedSearch = SkillSwap.utils.debounce(() => {
                // Auto-submit search form after typing stops
                const form = searchInput.closest('form');
                if (form && searchInput.value.length >= 3) {
                    form.submit();
                }
            }, 500);

            searchInput.addEventListener('input', debouncedSearch);
        }
    },

    // Rating functionality
    rating: {
        init() {
            this.setupRatingInputs();
            this.setupRatingDisplay();
        },

        setupRatingInputs() {
            document.querySelectorAll('.rating-input').forEach(container => {
                const inputs = container.querySelectorAll('input[type="radio"]');
                const stars = container.querySelectorAll('.star');

                stars.forEach((star, index) => {
                    star.addEventListener('click', () => {
                        inputs[index].checked = true;
                        this.updateStars(container, index + 1);
                    });

                    star.addEventListener('mouseenter', () => {
                        this.updateStars(container, index + 1);
                    });
                });

                container.addEventListener('mouseleave', () => {
                    const checkedInput = container.querySelector('input[type="radio"]:checked');
                    const rating = checkedInput ? parseInt(checkedInput.value) : 0;
                    this.updateStars(container, rating);
                });
            });
        },

        updateStars(container, rating) {
            const stars = container.querySelectorAll('.star i');
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('text-warning');
                    star.classList.remove('text-muted');
                } else {
                    star.classList.add('text-muted');
                    star.classList.remove('text-warning');
                }
            });
        },

        setupRatingDisplay() {
            // Animate rating stars on page load
            document.querySelectorAll('.rating').forEach(rating => {
                const stars = rating.querySelectorAll('i');
                stars.forEach((star, index) => {
                    setTimeout(() => {
                        star.style.animation = 'fadeIn 0.3s ease-in-out';
                    }, index * 100);
                });
            });
        }
    },

    // Chat functionality
    chat: {
        init() {
            this.setupChatScroll();
            this.setupMessageForm();
        },

        setupChatScroll() {
            const chatMessages = document.querySelector('.chat-messages');
            if (chatMessages) {
                // Scroll to bottom on page load
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Auto-scroll when new content is added
                const observer = new MutationObserver(() => {
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                });
                
                observer.observe(chatMessages, { childList: true, subtree: true });
            }
        },

        setupMessageForm() {
            const messageForm = document.querySelector('form[action*="send_message"]');
            if (!messageForm) return;

            const contentTextarea = messageForm.querySelector('textarea[name="content"]');
            const submitButton = messageForm.querySelector('button[type="submit"]');

            if (contentTextarea) {
                contentTextarea.focus();
                
                // Submit form with Ctrl+Enter
                contentTextarea.addEventListener('keydown', (e) => {
                    if (e.ctrlKey && e.key === 'Enter') {
                        e.preventDefault();
                        messageForm.submit();
                    }
                });

                // Show loading state on submit
                messageForm.addEventListener('submit', () => {
                    if (submitButton) {
                        SkillSwap.utils.showButtonLoading(submitButton, 'Sending...');
                    }
                });
            }
        }
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    SkillSwap.init();
    SkillSwap.search.init();
    SkillSwap.rating.init();
    SkillSwap.chat.init();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Refresh data when page becomes visible again
        const refreshableElements = document.querySelectorAll('[data-refresh="true"]');
        refreshableElements.forEach(element => {
            // Could implement auto-refresh logic here
        });
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    SkillSwap.utils.showToast('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    SkillSwap.utils.showToast('You are offline. Some features may not work.', 'warning');
});

// Export for use in other scripts
window.SkillSwap = SkillSwap;
