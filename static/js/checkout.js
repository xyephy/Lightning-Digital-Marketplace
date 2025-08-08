/**
 * Lightning Digital Marketplace - Checkout JavaScript
 * Stage 2: Commerce Core
 * 
 * Handles product checkout and Lightning payment flow
 */

class LightningCheckout {
    constructor() {
        this.currentProduct = null;
        this.currentOrder = null;
        this.paymentTimer = null;
        this.countdownInterval = null;
        
        this.init();
    }
    
    init() {
        this.loadProductDetails();
        this.setupEventListeners();
    }
    
    loadProductDetails() {
        // Get product ID from URL
        const pathParts = window.location.pathname.split('/');
        const productId = pathParts[pathParts.length - 1];
        
        if (productId && !isNaN(productId)) {
            this.fetchProductDetails(productId);
        } else {
            this.showError('Invalid product ID');
        }
    }
    
    async fetchProductDetails(productId) {
        try {
            const response = await fetch(`/api/products/${productId}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentProduct = data.product;
                this.displayProductDetails();
            } else {
                this.showError(data.error || 'Product not found');
            }
        } catch (error) {
            this.showError('Failed to load product details: ' + error.message);
        }
    }
    
    displayProductDetails() {
        const product = this.currentProduct;
        
        // Update product information
        document.getElementById('productName').textContent = product.name;
        document.getElementById('productDescription').textContent = product.description;
        document.getElementById('productPrice').textContent = `${product.price_sats.toLocaleString()} sats`;
        document.getElementById('productPriceBTC').textContent = `(${product.price_btc.toFixed(8)} BTC)`;
        
        if (product.image_url) {
            document.getElementById('productImage').src = product.image_url;
        }
        
        // Show checkout form
        document.getElementById('checkoutForm').style.display = 'block';
    }
    
    setupEventListeners() {
        // Purchase button
        const purchaseButton = document.getElementById('purchaseButton');
        if (purchaseButton) {
            purchaseButton.addEventListener('click', () => this.startPayment());
        }
        
        // Cancel payment button
        const cancelButton = document.getElementById('cancelPaymentButton');
        if (cancelButton) {
            cancelButton.addEventListener('click', () => this.cancelPayment());
        }
        
        // Customer email validation
        const emailInput = document.getElementById('customerEmail');
        if (emailInput) {
            emailInput.addEventListener('blur', () => this.validateEmail());
        }
        
        // Terms checkbox
        const termsCheckbox = document.getElementById('agreeTerms');
        if (termsCheckbox) {
            termsCheckbox.addEventListener('change', () => this.updatePurchaseButton());
        }
    }
    
    validateEmail() {
        const emailInput = document.getElementById('customerEmail');
        const email = emailInput.value.trim();
        
        if (email && !this.isValidEmail(email)) {
            this.showFieldError('customerEmail', 'Please enter a valid email address');
            return false;
        } else {
            this.clearFieldError('customerEmail');
            return true;
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    updatePurchaseButton() {
        const purchaseButton = document.getElementById('purchaseButton');
        const termsCheckbox = document.getElementById('agreeTerms');
        
        if (purchaseButton && termsCheckbox) {
            purchaseButton.disabled = !termsCheckbox.checked;
        }
    }
    
    async startPayment() {
        if (!this.validateCheckoutForm()) {
            return;
        }
        
        const customerEmail = document.getElementById('customerEmail').value.trim();
        
        try {
            // Show loading state
            this.showPaymentLoading();
            
            // Create payment request
            const response = await fetch('/api/create-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_id: this.currentProduct.id,
                    customer_email: customerEmail || null
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentOrder = data;
                this.displayPaymentRequest(data);
                this.startPaymentMonitoring(data.order_id);
            } else {
                throw new Error(data.error || 'Failed to create payment request');
            }
        } catch (error) {
            this.showError('Payment creation failed: ' + error.message);
            this.hidePaymentLoading();
        }
    }
    
    validateCheckoutForm() {
        let isValid = true;
        
        // Validate terms checkbox
        const termsCheckbox = document.getElementById('agreeTerms');
        if (termsCheckbox && !termsCheckbox.checked) {
            this.showError('Please agree to the terms and conditions');
            isValid = false;
        }
        
        // Validate email if provided
        const emailInput = document.getElementById('customerEmail');
        if (emailInput && emailInput.value.trim()) {
            isValid = this.validateEmail() && isValid;
        }
        
        return isValid;
    }
    
    displayPaymentRequest(paymentData) {
        // Hide checkout form and show payment details
        document.getElementById('checkoutForm').style.display = 'none';
        document.getElementById('paymentSection').style.display = 'block';
        
        // Update payment details
        document.getElementById('paymentAmount').textContent = `${paymentData.amount_sats.toLocaleString()} sats`;
        document.getElementById('paymentAmountBTC').textContent = `(${paymentData.amount_btc.toFixed(8)} BTC)`;
        document.getElementById('paymentRequest').textContent = paymentData.payment_request;
        document.getElementById('orderId').textContent = paymentData.order_id;
        
        // Generate QR code
        if (paymentData.qr_code_data) {
            this.displayQRCode(paymentData.qr_code_data);
        }
        
        // Start expiration countdown
        if (paymentData.expires_at) {
            this.startExpirationCountdown(paymentData.expires_at);
        }
        
        // Set up copy buttons
        this.setupCopyButtons();
    }
    
    displayQRCode(qrCodeData) {
        const qrContainer = document.getElementById('qrCodeContainer');
        if (qrContainer) {
            qrContainer.innerHTML = `<img src="data:image/png;base64,${qrCodeData}" alt="Lightning Invoice QR Code" class="img-fluid">`;
        }
    }
    
    startExpirationCountdown(expiresAt) {
        const expiryTime = new Date(expiresAt).getTime();
        const countdownElement = document.getElementById('expiryCountdown');
        
        if (!countdownElement) return;
        
        this.countdownInterval = setInterval(() => {
            const now = new Date().getTime();
            const timeLeft = expiryTime - now;
            
            if (timeLeft <= 0) {
                this.handlePaymentExpired();
                return;
            }
            
            const minutes = Math.floor(timeLeft / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
            
            countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
    
    setupCopyButtons() {
        // Copy payment request
        const copyPaymentButton = document.getElementById('copyPaymentRequest');
        if (copyPaymentButton) {
            copyPaymentButton.addEventListener('click', () => {
                this.copyToClipboard(document.getElementById('paymentRequest').textContent, 'Payment request copied!');
            });
        }
        
        // Copy order ID
        const copyOrderButton = document.getElementById('copyOrderId');
        if (copyOrderButton) {
            copyOrderButton.addEventListener('click', () => {
                this.copyToClipboard(document.getElementById('orderId').textContent, 'Order ID copied!');
            });
        }
    }
    
    async copyToClipboard(text, successMessage) {
        try {
            await navigator.clipboard.writeText(text);
            this.showSuccess(successMessage);
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showSuccess(successMessage);
        }
    }
    
    startPaymentMonitoring(orderId) {
        // Use real-time WebSocket monitoring if available
        if (window.lightningRealTime) {
            window.lightningRealTime.startPaymentMonitoring(orderId);
        } else {
            // Fallback to polling
            this.startPaymentPolling(orderId);
        }
    }
    
    startPaymentPolling(orderId) {
        this.paymentTimer = setInterval(async () => {
            try {
                const response = await fetch(`/api/payment-status/${orderId}`);
                const data = await response.json();
                
                if (data.success) {
                    this.handlePaymentStatusUpdate(data);
                    
                    // Stop polling if payment is complete
                    if (['paid', 'delivered', 'expired', 'cancelled'].includes(data.status)) {
                        this.stopPaymentMonitoring();
                    }
                }
            } catch (error) {
                console.error('Error checking payment status:', error);
            }
        }, 5000); // Poll every 5 seconds
    }
    
    stopPaymentMonitoring() {
        if (this.paymentTimer) {
            clearInterval(this.paymentTimer);
            this.paymentTimer = null;
        }
        
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
        
        if (window.lightningRealTime) {
            window.lightningRealTime.stopPaymentMonitoring();
        }
    }
    
    handlePaymentStatusUpdate(data) {
        const statusElement = document.getElementById('paymentStatusText');
        const spinnerElement = document.getElementById('paymentSpinner');
        
        if (statusElement) {
            statusElement.textContent = data.message || `Status: ${data.status}`;
        }
        
        switch (data.status) {
            case 'paid':
                this.handlePaymentConfirmed(data);
                break;
            case 'delivered':
                this.handleProductDelivered(data);
                break;
            case 'expired':
                this.handlePaymentExpired();
                break;
            case 'cancelled':
                this.handlePaymentCancelled();
                break;
        }
        
        // Hide spinner for final states
        if (['paid', 'delivered', 'expired', 'cancelled'].includes(data.status) && spinnerElement) {
            spinnerElement.style.display = 'none';
        }
    }
    
    handlePaymentConfirmed(data) {
        this.showSuccess('🎉 Payment confirmed! Processing your order...');
        
        // Update UI to show confirmation
        const statusSection = document.getElementById('paymentStatus');
        if (statusSection) {
            statusSection.className = 'alert alert-success';
            statusSection.innerHTML = `
                <h6><i class="fas fa-check-circle"></i> Payment Confirmed!</h6>
                <p>Your Lightning payment has been confirmed. Preparing your download...</p>
            `;
        }
    }
    
    handleProductDelivered(data) {
        this.showSuccess('✅ Product delivered! You can now download your purchase.');
        
        // Show download section
        this.displayDownloadSection(data);
        
        // Update status
        const statusSection = document.getElementById('paymentStatus');
        if (statusSection) {
            statusSection.className = 'alert alert-success';
            statusSection.innerHTML = `
                <h6><i class="fas fa-gift"></i> Product Delivered!</h6>
                <p>Your purchase is ready for download.</p>
            `;
        }
        
        this.stopPaymentMonitoring();
    }
    
    displayDownloadSection(data) {
        const downloadSection = document.getElementById('downloadSection');
        if (downloadSection) {
            downloadSection.style.display = 'block';
            
            // Add download link
            const downloadLink = document.getElementById('downloadLink');
            if (downloadLink && data.download_url) {
                downloadLink.href = data.download_url;
            }
        }
    }
    
    handlePaymentExpired() {
        this.showError('⏰ Payment expired. Please try again with a new payment request.');
        
        const statusSection = document.getElementById('paymentStatus');
        if (statusSection) {
            statusSection.className = 'alert alert-warning';
            statusSection.innerHTML = `
                <h6><i class="fas fa-clock"></i> Payment Expired</h6>
                <p>The payment window has expired. You can create a new payment request below.</p>
            `;
        }
        
        // Show retry button
        this.showRetryOption();
        this.stopPaymentMonitoring();
    }
    
    handlePaymentCancelled() {
        this.showError('❌ Payment was cancelled.');
        
        // Redirect to store after short delay
        setTimeout(() => {
            window.location.href = '/store';
        }, 2000);
        
        this.stopPaymentMonitoring();
    }
    
    async cancelPayment() {
        if (!this.currentOrder || !this.currentOrder.order_id) {
            return;
        }
        
        if (!confirm('Are you sure you want to cancel this payment?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/cancel-payment/${this.currentOrder.order_id}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.handlePaymentCancelled();
            } else {
                this.showError(data.error || 'Failed to cancel payment');
            }
        } catch (error) {
            this.showError('Failed to cancel payment: ' + error.message);
        }
    }
    
    showRetryOption() {
        const retrySection = document.getElementById('retrySection');
        if (retrySection) {
            retrySection.style.display = 'block';
        }
        
        const retryButton = document.getElementById('retryPaymentButton');
        if (retryButton) {
            retryButton.onclick = () => {
                // Reset to checkout form
                document.getElementById('paymentSection').style.display = 'none';
                document.getElementById('checkoutForm').style.display = 'block';
                document.getElementById('retrySection').style.display = 'none';
                this.currentOrder = null;
            };
        }
    }
    
    // UI Helper methods
    showPaymentLoading() {
        const button = document.getElementById('purchaseButton');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Payment...';
        }
    }
    
    hidePaymentLoading() {
        const button = document.getElementById('purchaseButton');
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-bolt"></i> Pay with Lightning';
        }
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showAlert(message, type) {
        const alertContainer = document.getElementById('alertContainer');
        if (alertContainer) {
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} alert-dismissible fade show`;
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
            `;
            
            alertContainer.appendChild(alert);
            
            // Auto-remove after 5 seconds for non-error alerts
            if (type !== 'danger') {
                setTimeout(() => {
                    if (alert.parentElement) {
                        alert.remove();
                    }
                }, 5000);
            }
        }
    }
    
    showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.classList.add('is-invalid');
            
            // Remove existing error message
            const existingError = field.parentElement.querySelector('.invalid-feedback');
            if (existingError) {
                existingError.remove();
            }
            
            // Add new error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = message;
            field.parentElement.appendChild(errorDiv);
        }
    }
    
    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.classList.remove('is-invalid');
            const errorDiv = field.parentElement.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
        }
    }
}

// Initialize checkout when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const checkout = new LightningCheckout();
    
    // Make it globally accessible for debugging
    window.lightningCheckout = checkout;
    
    console.log('Lightning Checkout initialized');
});