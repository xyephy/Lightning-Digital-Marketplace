/**
 * Lightning Digital Marketplace - Real-Time JavaScript Client
 * Stage 3: Real-Time Features
 * 
 * Handles WebSocket connections and real-time payment updates
 */

class LightningRealTimeClient {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentOrderId = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        
        this.init();
    }
    
    init() {
        // Initialize Socket.IO connection
        this.socket = io();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set up connection status indicators
        this.setupConnectionStatus();
    }
    
    setupEventListeners() {
        // Connection events
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('connected');
            this.showNotification('Connected to Lightning Marketplace', 'success');
            console.log('Connected to WebSocket server');
        });
        
        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
            this.showNotification('Disconnected from server', 'warning');
            console.log('Disconnected from WebSocket server');
            
            // Attempt to reconnect
            this.attemptReconnect();
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.updateConnectionStatus('error');
            this.attemptReconnect();
        });
        
        // Payment update events
        this.socket.on('payment_update', (data) => {
            this.handlePaymentUpdate(data);
        });
        
        // General notifications
        this.socket.on('general_notification', (data) => {
            this.handleGeneralNotification(data);
        });
        
        // Lightning status updates
        this.socket.on('lightning_status_update', (data) => {
            this.handleLightningStatusUpdate(data);
        });
        
        // Room events
        this.socket.on('room_joined', (data) => {
            console.log('Joined room:', data.room);
            this.showNotification(`Monitoring payment: ${data.order_id}`, 'info');
        });
        
        this.socket.on('room_left', (data) => {
            console.log('Left room:', data.room);
        });
        
        // Connection status response
        this.socket.on('connection_status', (data) => {
            console.log('Connection status:', data);
        });
        
        // Ping/pong for connection testing
        this.socket.on('pong', (data) => {
            console.log('Pong received:', data);
        });
    }
    
    setupConnectionStatus() {
        // Add connection status indicator to page
        const statusIndicator = document.createElement('div');
        statusIndicator.id = 'realtime-status';
        statusIndicator.className = 'realtime-status position-fixed top-0 end-0 m-3 p-2 rounded shadow-sm';
        statusIndicator.style.zIndex = '1060';
        statusIndicator.innerHTML = `
            <small>
                <i class="fas fa-circle" id="status-icon"></i>
                <span id="status-text">Connecting...</span>
            </small>
        `;
        document.body.appendChild(statusIndicator);
    }
    
    updateConnectionStatus(status) {
        const statusIcon = document.getElementById('status-icon');
        const statusText = document.getElementById('status-text');
        const statusContainer = document.getElementById('realtime-status');
        
        if (!statusIcon || !statusText || !statusContainer) return;
        
        switch (status) {
            case 'connected':
                statusIcon.className = 'fas fa-circle text-success';
                statusText.textContent = 'Real-time connected';
                statusContainer.className = statusContainer.className.replace(/bg-\w+/, '') + ' bg-light';
                break;
            case 'disconnected':
                statusIcon.className = 'fas fa-circle text-warning';
                statusText.textContent = 'Reconnecting...';
                statusContainer.className = statusContainer.className.replace(/bg-\w+/, '') + ' bg-warning';
                break;
            case 'error':
                statusIcon.className = 'fas fa-circle text-danger';
                statusText.textContent = 'Connection error';
                statusContainer.className = statusContainer.className.replace(/bg-\w+/, '') + ' bg-danger text-white';
                break;
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            this.showNotification('Unable to reconnect. Please refresh the page.', 'danger');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
        
        console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.socket.connect();
            }
        }, delay);
    }
    
    // Payment monitoring methods
    startPaymentMonitoring(orderId) {
        this.currentOrderId = orderId;
        this.socket.emit('join_payment_room', { order_id: orderId });
        console.log(`Started monitoring payment: ${orderId}`);
    }
    
    stopPaymentMonitoring(orderId = null) {
        const orderToStop = orderId || this.currentOrderId;
        if (orderToStop) {
            this.socket.emit('leave_payment_room', { order_id: orderToStop });
            if (orderToStop === this.currentOrderId) {
                this.currentOrderId = null;
            }
            console.log(`Stopped monitoring payment: ${orderToStop}`);
        }
    }
    
    handlePaymentUpdate(data) {
        console.log('Payment update received:', data);
        
        const orderId = data.order_id;
        const updateType = data.type;
        const status = data.status;
        const message = data.message;
        
        // Update UI based on payment status
        this.updatePaymentUI(data);
        
        // Show notification for important updates
        if (['payment_confirmed', 'product_delivered', 'payment_expired', 'payment_cancelled'].includes(updateType)) {
            const notificationType = updateType === 'payment_confirmed' || updateType === 'product_delivered' ? 'success' :
                                   updateType === 'payment_expired' || updateType === 'payment_cancelled' ? 'warning' : 'info';
            this.showNotification(message, notificationType);
        }
        
        // Handle specific update types
        switch (updateType) {
            case 'payment_confirmed':
                this.handlePaymentConfirmed(data);
                break;
            case 'product_delivered':
                this.handleProductDelivered(data);
                break;
            case 'payment_expired':
                this.handlePaymentExpired(data);
                break;
            case 'payment_cancelled':
                this.handlePaymentCancelled(data);
                break;
            case 'payment_pending':
                this.handlePaymentPending(data);
                break;
        }
    }
    
    updatePaymentUI(data) {
        // Update payment status text
        const statusElement = document.getElementById('paymentStatusText');
        if (statusElement) {
            statusElement.innerHTML = `<i class="fas fa-info-circle"></i> ${data.message}`;
        }
        
        // Update spinner based on status
        const spinner = document.getElementById('paymentSpinner');
        if (spinner && ['paid', 'delivered', 'expired', 'cancelled'].includes(data.status)) {
            spinner.style.display = 'none';
        }
        
        // Update countdown if present
        if (data.time_remaining && data.time_remaining > 0) {
            const countdownElement = document.getElementById('expiryCountdown');
            if (countdownElement) {
                const minutes = Math.floor(data.time_remaining / 60);
                const seconds = data.time_remaining % 60;
                countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }
    }
    
    handlePaymentConfirmed(data) {
        // Show success animation
        this.showPaymentSuccess();
        
        // Update UI to show payment confirmed
        const statusElement = document.getElementById('paymentStatusText');
        if (statusElement) {
            statusElement.innerHTML = '<i class="fas fa-check-circle text-success"></i> Payment confirmed! Preparing download...';
        }
    }
    
    handleProductDelivered(data) {
        // Show download modal or update UI
        if (data.download_link) {
            this.showDownloadReady(data);
        }
    }
    
    handlePaymentExpired(data) {
        // Update UI to show expiration
        const statusElement = document.getElementById('paymentStatusText');
        if (statusElement) {
            statusElement.innerHTML = '<i class="fas fa-clock text-danger"></i> Payment expired';
        }
        
        // Disable payment elements
        this.disablePaymentElements();
    }
    
    handlePaymentCancelled(data) {
        // Redirect to store or show cancellation message
        setTimeout(() => {
            window.location.href = '/store';
        }, 2000);
    }
    
    handlePaymentPending(data) {
        // Update countdown and status
        this.updatePaymentUI(data);
    }
    
    handleGeneralNotification(data) {
        this.showNotification(data.message, data.notification_type);
    }
    
    handleLightningStatusUpdate(data) {
        // Update Lightning network status indicators
        const lightningStatus = document.getElementById('lightning-status');
        if (lightningStatus) {
            const isConnected = data.status.polar_running;
            lightningStatus.innerHTML = isConnected ? 
                '<i class="fas fa-check-circle text-success"></i> Lightning Connected' :
                '<i class="fas fa-exclamation-triangle text-warning"></i> Lightning Disconnected';
        }
    }
    
    // UI Helper methods
    showPaymentSuccess() {
        // Add celebration animation or effects
        document.body.style.animation = 'flash 0.5s';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 500);
    }
    
    showDownloadReady(data) {
        // Show success modal with download link
        const modalHtml = `
            <div class="modal fade show" style="display: block;" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-check-circle"></i> Payment Complete!
                            </h5>
                        </div>
                        <div class="modal-body text-center">
                            <h6>${data.product_name}</h6>
                            <p>Your payment has been confirmed and your product is ready!</p>
                            <div class="d-grid">
                                <a href="${data.download_link}" class="btn btn-success btn-lg">
                                    <i class="fas fa-download"></i> Download Now
                                </a>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" onclick="window.location.href='/store'">
                                Continue Shopping
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modals
        document.querySelectorAll('.modal.show').forEach(modal => modal.remove());
        
        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
    
    disablePaymentElements() {
        // Disable payment-related buttons and elements
        const cancelButton = document.querySelector('button[onclick*="cancelPayment"]');
        if (cancelButton) {
            cancelButton.textContent = 'Payment Expired';
            cancelButton.disabled = true;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create and show toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${this.getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 80px; right: 20px; z-index: 1070; min-width: 300px; max-width: 400px;';
        toast.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 150);
            }
        }, 5000);
    }
    
    getBootstrapAlertClass(type) {
        const mapping = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return mapping[type] || 'info';
    }
    
    getNotificationIcon(type) {
        const mapping = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-triangle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        return mapping[type] || 'fa-info-circle';
    }
    
    // Public methods for testing
    sendPing() {
        this.socket.emit('ping');
    }
    
    sendTestNotification(message, type = 'info') {
        fetch('/api/notify/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                type: type
            })
        }).catch(error => console.error('Error sending test notification:', error));
    }
}

// Global real-time client instance
let lightningRealTime = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if Socket.IO is available
    if (typeof io !== 'undefined') {
        lightningRealTime = new LightningRealTimeClient();
        console.log('Lightning Real-Time client initialized');
        
        // Make it globally accessible for debugging
        window.lightningRealTime = lightningRealTime;
    } else {
        console.warn('Socket.IO not available - real-time features disabled');
    }
});

// CSS animations for payment success
const style = document.createElement('style');
style.textContent = `
    @keyframes flash {
        0% { background-color: rgba(40, 167, 69, 0.1); }
        50% { background-color: rgba(40, 167, 69, 0.3); }
        100% { background-color: transparent; }
    }
    
    .realtime-status {
        transition: all 0.3s ease;
        font-size: 0.875rem;
        border: 1px solid rgba(0,0,0,0.1);
    }
    
    .payment-update-animation {
        animation: slideInRight 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
