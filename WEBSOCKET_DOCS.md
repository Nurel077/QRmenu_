# WebSocket API Documentation

## Overview
This project uses Django Channels for real-time WebSocket communication. All WebSocket connections support live updates for orders, tables, and staff notifications.

## WebSocket Endpoints

### Order Updates
**Endpoint:** `ws://localhost:9000/ws/orders/<order_id>/`

**Purpose:** Real-time order status and details updates

**Connection:**
```javascript
const orderSocket = new WebSocket(`ws://localhost:9000/ws/orders/123/`);

orderSocket.onopen = function(e) {
    console.log('Order socket connected');
};

orderSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Order update:', data);
};
```

**Messages Received:**
- `order_status` - Order status changed
- `order_update` - General order update
- `order_items_update` - Items in order changed

**Send Actions:**
```javascript
// Get current order status
orderSocket.send(JSON.stringify({
    action: 'get_status'
}));

// Update order status (admin only)
orderSocket.send(JSON.stringify({
    action: 'update_status',
    status: 'ready'  // pending, confirmed, ready, delivered, cancelled
}));
```

---

### Order Items Updates
**Endpoint:** `ws://localhost:9000/ws/orders/<order_id>/items/`

**Purpose:** Real-time updates for items in an order

**Messages Received:**
- `items_list` - List of items in order
- `items_updated` - Items were updated

**Send Actions:**
```javascript
// Get current items
socket.send(JSON.stringify({
    action: 'get_items'
}));
```

---

### Table Status Updates
**Endpoint:** `ws://localhost:9000/ws/tables/<table_id>/`

**Purpose:** Real-time table status and occupancy

**Messages Received:**
- `table_status` - Table status changed
- `table_update` - General table update

**Send Actions:**
```javascript
// Mark table as occupied
tableSocket.send(JSON.stringify({
    action: 'occupy'
}));

// Mark table as free
tableSocket.send(JSON.stringify({
    action: 'release'
}));

// Get table status
tableSocket.send(JSON.stringify({
    action: 'get_status'
}));
```

---

### Table Session Updates
**Endpoint:** `ws://localhost:9000/ws/tables/sessions/<session_id>/`

**Purpose:** Real-time guest count and session status

**Messages Received:**
- `session_status` - Session status
- `session_update` - Session details changed

**Send Actions:**
```javascript
// Update guest count
sessionSocket.send(JSON.stringify({
    action: 'update_guests_count',
    guests_count: 4
}));

// Close session
sessionSocket.send(JSON.stringify({
    action: 'close_session'
}));
```

---

### Waiter Notifications
**Endpoint:** `ws://localhost:9000/ws/waiters/<waiter_id>/`

**Purpose:** Real-time notifications for individual waiters

**Messages Received:**
- `order_notification` - New order or order update
- `payment_notification` - Payment received
- `task_notification` - New task assigned
- `alert` - Priority alert message

**Send Actions:**
```javascript
// Get waiter tasks
waiterSocket.send(JSON.stringify({
    action: 'get_tasks'
}));

// Acknowledge notification
waiterSocket.send(JSON.stringify({
    action: 'acknowledge',
    notification_id: '123'
}));
```

---

### Restaurant Wide Notifications
**Endpoint:** `ws://localhost:9000/ws/restaurants/<restaurant_id>/notifications/`

**Purpose:** Restaurant-wide waiter notifications and alerts

**Messages Received:**
- `order_notification` - Order events
- `payment_notification` - Payment events
- `task_notification` - Task assignments
- `alert` - Priority alerts

---

### Restaurant Status Channel
**Endpoint:** `ws://localhost:9000/ws/restaurants/<restaurant_id>/`

**Purpose:** Restaurant-wide status broadcasts

**Messages Received:**
- `new_order` - New order placed
- `order_ready` - Order ready for service
- `payment_completed` - Payment completed
- `broadcast` - General broadcast message

**Send Actions:**
```javascript
// Get restaurant status
restaurantSocket.send(JSON.stringify({
    action: 'get_status'
}));
```

---

## Message Format

### Standard Response Format
```json
{
    "type": "message_type",
    "data": {
        "key": "value"
    }
}
```

### Error Format
```json
{
    "error": "Error message"
}
```

---

## Connection Events

### Order Update Example
```json
{
    "type": "order_status",
    "data": {
        "id": 1,
        "status": "ready",
        "status_display": "Ready",
        "total_amount": "250.00",
        "items_count": 3,
        "created_at": "2026-01-28T21:00:00Z",
        "confirmed_at": "2026-01-28T21:02:00Z",
        "ready_at": "2026-01-28T21:15:00Z",
        "delivered_at": null
    }
}
```

### Table Update Example
```json
{
    "type": "table_update",
    "data": {
        "table_id": 5,
        "table_number": "5",
        "is_occupied": true,
        "is_active": true,
        "zone": "A",
        "restaurant": "Restaurant Name",
        "session": {
            "id": 1,
            "session_code": "ABC123",
            "guests_count": 4,
            "started_at": "2026-01-28T21:00:00Z"
        }
    }
}
```

### Waiter Notification Example
```json
{
    "type": "order_notification",
    "data": {
        "order_id": 5,
        "table_number": "5",
        "items_count": 3,
        "message": "New order for table 5"
    }
}
```

---

## Auto Broadcasts via Django Signals

The following events automatically trigger WebSocket broadcasts:

### Order Changes
- New order created → Broadcast to restaurant and waiter
- Order status changed → Broadcast to order consumers
- Order ready → Broadcast to restaurant and waiter

### Table Changes
- Table occupied/released → Broadcast to table and restaurant consumers
- Guest count changed → Broadcast to session consumers
- Session closed → Update table occupancy

### Payment Changes
- Payment received → Notify assigned waiter and restaurant
- Payment completed → Broadcast to restaurant

---

## Example JavaScript Client

```javascript
class RestaurantQRClient {
    constructor(orderId, tableId, waiterId, restaurantId) {
        this.orderId = orderId;
        this.tableId = tableId;
        this.waiterId = waiterId;
        this.restaurantId = restaurantId;
        this.sockets = {};
    }
    
    connectOrder() {
        const url = `ws://localhost:9000/ws/orders/${this.orderId}/`;
        this.sockets.order = new WebSocket(url);
        
        this.sockets.order.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleOrderUpdate(data);
        };
        
        this.sockets.order.onerror = (e) => {
            console.error('Order socket error:', e);
        };
    }
    
    connectTable() {
        const url = `ws://localhost:9000/ws/tables/${this.tableId}/`;
        this.sockets.table = new WebSocket(url);
        
        this.sockets.table.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleTableUpdate(data);
        };
    }
    
    connectWaiter() {
        const url = `ws://localhost:9000/ws/waiters/${this.waiterId}/`;
        this.sockets.waiter = new WebSocket(url);
        
        this.sockets.waiter.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleWaiterNotification(data);
        };
    }
    
    connectRestaurant() {
        const url = `ws://localhost:9000/ws/restaurants/${this.restaurantId}/`;
        this.sockets.restaurant = new WebSocket(url);
        
        this.sockets.restaurant.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleRestaurantBroadcast(data);
        };
    }
    
    handleOrderUpdate(data) {
        console.log('Order updated:', data);
        // Update UI with new order data
    }
    
    handleTableUpdate(data) {
        console.log('Table updated:', data);
        // Update UI with table status
    }
    
    handleWaiterNotification(data) {
        console.log('Waiter notification:', data);
        // Show notification to waiter
    }
    
    handleRestaurantBroadcast(data) {
        console.log('Restaurant broadcast:', data);
        // Show broadcast to all staff
    }
    
    disconnect() {
        Object.values(this.sockets).forEach(socket => {
            if (socket) socket.close();
        });
    }
}

// Usage
const client = new RestaurantQRClient(1, 5, 10, 2);
client.connectOrder();
client.connectTable();
client.connectWaiter();
client.connectRestaurant();
```

---

## Testing WebSocket Connections

### Using wscat (Command Line Tool)
```bash
# Install wscat
npm install -g wscat

# Connect to order updates
wscat -c ws://localhost:9000/ws/orders/1/

# Send message
> {"action":"get_status"}
```

### Using Python
```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:9000/ws/orders/1/"
    async with websockets.connect(uri) as websocket:
        # Receive initial status
        message = await websocket.recv()
        print(f"Received: {message}")
        
        # Send action
        await websocket.send(json.dumps({"action": "get_status"}))
        
        # Receive response
        response = await websocket.recv()
        print(f"Response: {response}")

asyncio.run(test_websocket())
```

---

## Configuration

### settings.py
```python
# Channels configuration
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

For production with Redis:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}
```

---

## Troubleshooting

### WebSocket Connection Refused
- Check if Channels is running (not just Django runserver)
- Verify WebSocket endpoint URL is correct
- Check firewall rules

### Messages Not Received
- Verify you're connected to the right group
- Check browser console for errors
- Ensure Django signals are registered

### High Memory Usage
- Consider using Redis channel layer instead of in-memory
- Monitor number of open connections
- Implement connection timeouts

---

## Performance Notes

- Each WebSocket consumer holds an open connection
- Use room/group names for efficient broadcasting
- Django signals handle automatic broadcasts
- Consider Redis for distributed deployments

