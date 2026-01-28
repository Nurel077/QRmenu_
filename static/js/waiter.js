/**
 * Waiter Panel - WebSocket and Real-time Updates
 */

class WaiterPanel {
    constructor() {
        this.ws = null;
        this.waiterId = this.getWaiterId();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
    }

    /**
     * Initialize WebSocket connection
     */
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${window.location.host}/ws/waiters/${this.waiterId}/`;
        
        try {
            this.ws = new WebSocket(url);
            
            this.ws.onopen = () => this.handleOpen();
            this.ws.onmessage = (event) => this.handleMessage(event);
            this.ws.onerror = (error) => this.handleError(error);
            this.ws.onclose = () => this.handleClose();
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket connection open
     */
    handleOpen() {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.updateConnectionStatus(true);
        
        // Send initial message
        this.send({
            'action': 'get_tasks'
        });
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);
            
            // Dispatch to appropriate handler
            if (data.type === 'waiter_task') {
                this.handleTaskUpdate(data);
            } else if (data.type === 'order_update') {
                this.handleOrderUpdate(data);
            } else if (data.type === 'notification') {
                this.handleNotification(data);
            }
        } catch (error) {
            console.error('Error processing message:', error);
        }
    }

    /**
     * Handle task updates
     */
    handleTaskUpdate(data) {
        // Reload orders from API
        if (window.loadOrders) {
            window.loadOrders();
        }
        
        // Show notification
        this.showNotification(
            `New task: ${data.task_type || 'Order Update'}`,
            'info'
        );
    }

    /**
     * Handle order updates
     */
    handleOrderUpdate(data) {
        // Update order in UI if it exists
        if (window.updateOrderDisplay) {
            window.updateOrderDisplay(data.order);
        }
        
        // Show notification based on update type
        const messages = {
            'status_changed': `Order status changed to ${data.order.status}`,
            'item_added': 'New item added to order',
            'order_cancelled': 'Order has been cancelled'
        };
        
        this.showNotification(
            messages[data.update_type] || 'Order updated',
            'info'
        );
    }

    /**
     * Handle notifications
     */
    handleNotification(data) {
        this.showNotification(data.message, data.level || 'info');
    }

    /**
     * Handle WebSocket errors
     */
    handleError(error) {
        console.error('WebSocket error:', error);
        this.updateConnectionStatus(false);
    }

    /**
     * Handle WebSocket close
     */
    handleClose() {
        console.log('WebSocket disconnected');
        this.updateConnectionStatus(false);
        this.scheduleReconnect();
    }

    /**
     * Send message through WebSocket
     */
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not ready, message not sent:', data);
        }
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * this.reconnectAttempts;
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
            setTimeout(() => this.connect(), delay);
        } else {
            console.error('Max reconnection attempts reached');
            this.showNotification('Connection lost - please refresh the page', 'error');
        }
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(connected) {
        const status = document.getElementById('connectionStatus');
        if (!status) return;
        
        if (connected) {
            status.classList.remove('disconnected');
            status.innerHTML = '<span class="connection-dot"></span><span>WebSocket Connected</span>';
        } else {
            status.classList.add('disconnected');
            status.innerHTML = '<span class="connection-dot"></span><span>Reconnecting...</span>';
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${colors[type] || colors['info']};
            color: ${type === 'warning' ? '#333' : 'white'};
            border-radius: 5px;
            z-index: 999;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Get waiter ID from page context
     */
    getWaiterId() {
        // Try to get from data attribute
        const elem = document.querySelector('[data-waiter-id]');
        if (elem) return elem.dataset.waiterId;
        
        // Try to get from localStorage or session
        return localStorage.getItem('waiter_id') || '';
    }
}

/**
 * Initialize waiter panel on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    window.waiterPanel = new WaiterPanel();
    window.waiterPanel.connect();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+R to refresh orders
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            if (window.loadOrders) window.loadOrders();
        }
    });
});

/**
 * Add animations
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
