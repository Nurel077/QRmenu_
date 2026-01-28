# API Documentation

## Authentication

### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "secure_password",
  "role": "WAITER",
  "restaurant": 1
}
```

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user123",
  "password": "secure_password"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user123",
    "role": "WAITER",
    "restaurant": 1
  }
}
```

## Restaurants

### List Restaurants
```http
GET /api/restaurants/
Authorization: Bearer {token}

Response:
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Ресторан А",
      "slug": "restoran-a",
      "address": "ул. Примерная, 123",
      "phone": "+996700123456",
      "is_active": true,
      "total_tables": 15,
      "active_tables": 5
    }
  ]
}
```

### Get Restaurant
```http
GET /api/restaurants/{id}/
Authorization: Bearer {token}
```

### Create Restaurant (Owner only)
```http
POST /api/restaurants/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Новый ресторан",
  "address": "ул. Новая, 1",
  "city": "Бишкек",
  "phone": "+996700111222",
  "currency": "KGS"
}
```

## Tables

### List Tables
```http
GET /api/tables/?restaurant=1
Authorization: Bearer {token}

Response:
{
  "results": [
    {
      "id": 1,
      "number": "A1",
      "capacity": 4,
      "is_occupied": false,
      "qr_url": "http://example.com/table/restoran-a/A1/",
      "zone": "Основной зал"
    }
  ]
}
```

### Get Table Menu (Public - for guests)
```http
GET /api/tables/{id}/menu/

Response:
{
  "table": {
    "id": 1,
    "number": "A1",
    "restaurant": {
      "name": "Ресторан А",
      "logo": "..."
    }
  },
  "menu": [
    {
      "category": "Супы",
      "items": [
        {
          "id": 1,
          "name": "Борщ",
          "description": "Классический борщ",
          "price": "250.00",
          "image": "...",
          "is_available": true
        }
      ]
    }
  ]
}
```

### Start Table Session
```http
POST /api/tables/{id}/start-session/
Content-Type: application/json

{
  "guest_name": "Иван"
}

Response:
{
  "session_code": "ABC123XY",
  "table_session_id": 42,
  "guest_session_id": 15
}
```

## Menu

### List Menu Categories
```http
GET /api/menu/categories/?restaurant=1

Response:
{
  "results": [
    {
      "id": 1,
      "name": "Супы",
      "description": "Горячие супы",
      "items_count": 5,
      "order": 1
    }
  ]
}
```

### List Menu Items
```http
GET /api/menu/items/?category=1

Response:
{
  "results": [
    {
      "id": 1,
      "name": "Борщ",
      "description": "Классический борщ",
      "price": "250.00",
      "image": "...",
      "cooking_time": 15,
      "is_vegetarian": false,
      "is_spicy": false,
      "tags": ["Популярное"],
      "options": [
        {
          "name": "Размер",
          "choices": [
            {"value": "small", "label": "Маленькая", "price_modifier": 0},
            {"value": "large", "label": "Большая", "price_modifier": 50}
          ],
          "is_required": true
        }
      ]
    }
  ]
}
```

## Orders

### Create Order (Guest)
```http
POST /api/orders/
Content-Type: application/json

{
  "table_session": 42,
  "guest_session": 15,
  "guest_name": "Иван",
  "payment_method": "cash",
  "notes": "Без лука, пожалуйста",
  "items": [
    {
      "menu_item": 1,
      "quantity": 2,
      "selected_options": {
        "size": "large"
      },
      "notes": "Средней прожарки"
    }
  ]
}

Response:
{
  "id": 100,
  "table_session": 42,
  "status": "pending",
  "payment_method": "cash",
  "subtotal": "500.00",
  "tax_amount": "50.00",
  "service_charge_amount": "25.00",
  "total_amount": "575.00",
  "items": [...],
  "created_at": "2026-01-28T14:30:00Z"
}
```

### List Orders
```http
GET /api/orders/?table_session=42
Authorization: Bearer {token}

Response:
{
  "results": [
    {
      "id": 100,
      "table": "A1",
      "guest_name": "Иван",
      "status": "pending",
      "items_count": 2,
      "total_amount": "575.00",
      "created_at": "2026-01-28T14:30:00Z"
    }
  ]
}
```

### Confirm Order (Waiter)
```http
POST /api/orders/{id}/confirm/
Authorization: Bearer {token}
Content-Type: application/json

{
  "waiter_notes": "Заказ принят"
}

Response:
{
  "id": 100,
  "status": "confirmed",
  "confirmed_at": "2026-01-28T14:32:00Z",
  "waiter": {
    "id": 5,
    "username": "waiter1"
  }
}
```

### Update Order Status (Waiter)
```http
PATCH /api/orders/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "preparing"
}
```

### Get Order Updates (WebSocket)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/orders/100/');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Order status:', data.status);
  // data = {type: 'order_update', status: 'ready', ...}
};
```

## Payments

### Create Payment
```http
POST /api/payments/
Authorization: Bearer {token}
Content-Type: application/json

{
  "order": 100,
  "payment_type": "cash",
  "amount": "575.00"
}

Response:
{
  "payment_id": "PAY-ABC123456789",
  "status": "pending",
  "amount": "575.00",
  "currency": "KGS",
  "created_at": "2026-01-28T15:00:00Z"
}
```

### Complete Payment (Waiter)
```http
POST /api/payments/{payment_id}/complete/
Authorization: Bearer {token}

Response:
{
  "payment_id": "PAY-ABC123456789",
  "status": "completed",
  "completed_at": "2026-01-28T15:05:00Z"
}
```

### Generate QR Payment Code
```http
POST /api/payments/{payment_id}/generate-qr/
Authorization: Bearer {token}

Response:
{
  "qr_code_url": "/media/payments/qr_codes/payment_PAY-ABC123456789.png",
  "qr_data": "https://payment.example.com/pay/PAY-ABC123456789",
  "expires_at": "2026-01-28T16:00:00Z"
}
```

## Waiter Panel

### Get Active Orders
```http
GET /api/waiter/orders/active/
Authorization: Bearer {token}

Response:
{
  "pending": [
    {
      "id": 100,
      "table": "A1",
      "guest_name": "Иван",
      "items_count": 2,
      "created_at": "...",
      "total_amount": "575.00"
    }
  ],
  "confirmed": [...],
  "preparing": [...],
  "ready": [...]
}
```

### Get Table Sessions
```http
GET /api/waiter/table-sessions/
Authorization: Bearer {token}

Response:
{
  "results": [
    {
      "id": 42,
      "table": "A1",
      "started_at": "...",
      "guests_count": 3,
      "orders_count": 5,
      "total_amount": "2500.00",
      "is_active": true
    }
  ]
}
```

## Error Responses

```http
HTTP/1.1 400 Bad Request
{
  "error": "Validation error",
  "details": {
    "items": ["This field is required."]
  }
}

HTTP/1.1 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

HTTP/1.1 403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}

HTTP/1.1 404 Not Found
{
  "detail": "Not found."
}

HTTP/1.1 500 Internal Server Error
{
  "error": "Internal server error",
  "message": "An unexpected error occurred."
}
```

## Rate Limiting

- Guest endpoints: 100 requests/hour
- Authenticated endpoints: 1000 requests/hour
- WebSocket connections: 10 concurrent connections per user

## Pagination

All list endpoints support pagination:
```http
GET /api/orders/?page=2&page_size=20

Response:
{
  "count": 150,
  "next": "http://api.example.com/api/orders/?page=3",
  "previous": "http://api.example.com/api/orders/?page=1",
  "results": [...]
}
```

## Filtering & Search

```http
GET /api/menu/items/?search=борщ
GET /api/menu/items/?is_vegetarian=true
GET /api/orders/?status=pending&payment_method=cash
GET /api/orders/?created_at__gte=2026-01-28
```

## Ordering

```http
GET /api/menu/items/?ordering=price
GET /api/menu/items/?ordering=-created_at
GET /api/orders/?ordering=created_at,-total_amount
```
