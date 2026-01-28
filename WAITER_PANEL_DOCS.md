# Waiter Panel Documentation

## Overview

The Waiter Panel is a real-time order management interface designed for restaurant waiters to efficiently track and manage customer orders throughout the service.

## Features

### 📊 Dashboard Statistics
- **Pending Orders**: Count of orders waiting for confirmation
- **Confirmed Orders**: Orders accepted by kitchen
- **Ready for Pickup**: Orders prepared and waiting for delivery
- **Delivered Orders**: Orders successfully served today

### 🎯 Order Management

#### Order Display
- **Order ID**: Unique identifier for each order
- **Table Number**: Which table the order belongs to
- **Guest Name**: Customer name (if provided)
- **Created Time**: When the order was placed
- **Order Status**: Visual status badge with color coding
- **Items List**: All items in the order with quantities and prices
- **Total Amount**: Order total in currency

#### Order Statuses
- **Pending** 🟡 - New order, awaiting confirmation
- **Confirmed** 🔵 - Accepted by kitchen staff
- **Ready** 🟢 - Prepared and ready for delivery
- **Delivered** 🟣 - Served to customer
- **Paid** 🟣 - Payment completed

#### Quick Actions
Each order displays context-appropriate action buttons:

**For Pending Orders:**
- ✓ Confirm - Accept order and send to kitchen

**For Confirmed Orders:**
- 🍽️ Ready - Mark as ready for pickup

**For Ready Orders:**
- ✓✓ Delivered - Confirm order was served

**For All Orders:**
- ℹ️ Details - View full order information

### 🔍 Filtering & Search

Filter orders by status:
- **All Orders** - Display all active orders
- **Pending** - Only unconfirmed orders
- **Confirmed** - Orders in kitchen
- **Ready** - Orders waiting to be served
- **Delivered** - Completed orders

### ⚡ Real-Time Updates

The waiter panel uses WebSocket technology to receive:
- New order notifications
- Order status updates from kitchen
- System notifications
- Live order modifications

**Connection Status**: Green indicator = Connected, Red indicator = Reconnecting

### 📱 Responsive Design

- Full-screen optimized for tablets and desktops
- Mobile-friendly layout for checking orders on the go
- Touch-friendly buttons for quick interactions
- Vertical and horizontal orientation support

---

## Access & Authentication

### Login
1. Navigate to `http://localhost:8000/waiter/`
2. Login with your waiter credentials
3. You'll be redirected to your dashboard

### Requirements
- User role must be **Waiter**
- Must be assigned to a restaurant
- Active account status

---

## API Endpoints

### Get Waiter Orders
```
GET /api/orders/?status=pending,confirmed,ready
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "order-id",
      "table_session": {
        "table": {
          "number": 5
        }
      },
      "guest_name": "John",
      "status": "pending",
      "items": [
        {
          "menu_item": {
            "name": "Caesar Salad"
          },
          "quantity": 1,
          "price": "12.99"
        }
      ],
      "total_amount": "12.99",
      "created_at": "2024-01-28T10:30:00Z"
    }
  ]
}
```

### Get Waiter Tasks
```
GET /waiter/api/tasks/
```

**Response:**
```json
{
  "pending_orders": 3,
  "ready_for_pickup": 2,
  "total_tasks": 5
}
```

### Update Order Status
```
PATCH /waiter/api/orders/<order_id>/
Content-Type: application/json

{
  "status": "confirmed"
}
```

**Status Options:**
- `pending` - Initial status
- `confirmed` - Accepted
- `ready` - Prepared
- `delivered` - Served
- `paid` - Payment complete

### Get Restaurant Statistics
```
GET /waiter/api/statistics/
```

**Response:**
```json
{
  "total_orders": 25,
  "pending_orders": 3,
  "confirmed_orders": 5,
  "ready_orders": 2,
  "delivered_orders": 15
}
```

---

## WebSocket Integration

### Connection
The panel automatically connects to WebSocket for real-time updates:

```
ws://localhost:8000/ws/waiters/<waiter_id>/
```

### Incoming Messages

#### Task Update
```json
{
  "type": "waiter_task",
  "task_type": "new_order",
  "order_id": "order-123"
}
```

#### Order Status Update
```json
{
  "type": "order_update",
  "order": {
    "id": "order-123",
    "status": "ready",
    "table_number": 5
  },
  "update_type": "status_changed"
}
```

#### Notification
```json
{
  "type": "notification",
  "message": "New order received at Table 3",
  "level": "info"
}
```

### Outgoing Messages

#### Get Pending Tasks
```json
{
  "action": "get_tasks"
}
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + R` | Refresh all orders |

---

## User Experience Tips

### Workflow
1. **Check Dashboard** - Review pending and confirmed orders
2. **Confirm Orders** - Click "Confirm" for new orders
3. **Monitor Kitchen** - Watch for "Ready" status updates
4. **Deliver Orders** - Click "Delivered" when served
5. **Track Stats** - Monitor daily order counts

### Best Practices
- **Confirm Quickly** - Accept orders immediately to notify kitchen
- **Check Regularly** - Refresh every 1-2 minutes during service
- **Use Filters** - Filter by status to focus on critical orders
- **Note Details** - Click "Details" for special requests
- **Monitor Connection** - Watch for WebSocket disconnect warnings

### Performance Tips
- Use table filters during busy service
- Keep browser window focused for real-time updates
- Don't open multiple waiter panel windows
- Close completed order details to reduce memory usage

---

## Troubleshooting

### WebSocket Connection Issues

**Problem**: Red connection indicator
```
Solution: 
1. Check internet connection
2. Verify WebSocket server is running (port 8000)
3. Clear browser cache
4. Refresh the page
```

### Orders Not Updating

**Problem**: Order statuses not changing
```
Solution:
1. Click refresh button or press Ctrl+R
2. Check connection status
3. Try logging out and back in
4. Check server logs for errors
```

### Cannot See Assigned Orders

**Problem**: No orders visible
```
Solution:
1. Verify you're assigned to the restaurant
2. Check that orders exist in the system
3. Try filtering by different statuses
4. Contact administrator
```

### Slow Performance

**Problem**: Dashboard loads slowly
```
Solution:
1. Close other browser tabs
2. Clear browser cache
3. Check internet connection
4. Try a different browser
```

---

## Order Status Flow

```
Pending (Customer orders)
    ↓
Confirmed (Waiter confirms, sent to kitchen)
    ↓
Ready (Kitchen completes, ready for serving)
    ↓
Delivered (Waiter delivers to table)
    ↓
Paid (Payment processed)
```

---

## Integration with Other Systems

### Kitchen Display System (KDS)
Orders sync automatically to kitchen:
- New orders appear immediately
- Status updates sync in real-time
- Special requests visible to kitchen staff

### Payment System
After "Delivered" status:
- Guest can request payment
- Payment page opens automatically
- Waiter can process payment

### Guest Menu System
Customers order via QR code menu:
- Orders automatically appear in waiter panel
- Real-time synchronization
- Order history tracked

---

## Security

### Authentication
- JWT token-based authentication
- Session management for security
- HTTPS/WSS for encrypted communication

### Permissions
- Waiter can only view orders from their restaurant
- Cannot modify other restaurant's orders
- Admin can override permissions

### Data Privacy
- Order details visible only to assigned waiter
- Guest information encrypted
- Order history logged securely

---

## Requirements

### Browser Support
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

### Network
- Stable internet connection
- WebSocket support (automatically fallback available)
- HTTPS/WSS for production

### Server
- Django 5.0+
- Django Channels 4.0+
- Redis for channel layers (optional)
- Python 3.8+

---

## Support & Feedback

For issues or feature requests:
1. Check troubleshooting section above
2. Contact administrator
3. Check server logs: `manage.py` output
4. Review WebSocket connection status

---

## Version History

**v1.0.0** - Initial Release
- Order management dashboard
- Real-time WebSocket updates
- Status filtering and search
- Quick action buttons
- Mobile responsive design
- Statistics tracking
