# 🚀 RestaurantQR - Quick Start Guide

## Backend is READY! ✅

Your Django backend is now fully configured and running. Here's how to access it:

---

## 📍 Access Points

### 1. **API Documentation (Swagger UI)**
- **URL:** http://127.0.0.1:8000/api/docs/
- **Purpose:** Interactive API documentation, test all endpoints
- **Features:** Try-it-out buttons, request/response examples

### 2. **Admin Panel**
- **URL:** http://127.0.0.1:8000/admin/
- **Credentials:** 
  - Username: `admin`
  - Password: `admin`
- **Purpose:** Manage restaurants, menus, tables, users, orders, payments

### 3. **API Root Endpoint**
- **URL:** http://127.0.0.1:8000/api/
- **Purpose:** Browse all available API endpoints

---

## 🎬 Starting the Server

### Option 1: Double-click Batch File (Windows Only)
```bash
# In Windows Explorer, double-click:
run_dev.bat
```
Server starts automatically on http://127.0.0.1:8000/

### Option 2: Python Script (All Platforms)
```bash
python dev_server.py
```

### Option 3: Django Command
```bash
python manage.py runserver 127.0.0.1:8000
```

---

## ✨ What's Included

### 🔐 Authentication
- JWT Token-based authentication
- Session authentication fallback
- Custom User model with roles

### 🏪 Restaurant Management
- Multi-restaurant support
- Owner-based data isolation
- Restaurant settings

### 📋 Menu Management
- Categories and items
- Pricing and availability
- Dietary options

### 🪑 Table Management  
- Table tracking
- Session management
- QR code support

### 📦 Order Management
- Order creation and tracking
- Order items with pricing
- Status workflow (pending → confirmed → ready → delivered)

### 💳 Payment Processing
- Multiple payment methods
- Payment status tracking
- Revenue statistics

### 🔑 Role-Based Access Control
- **SUPERADMIN:** Full system access
- **OWNER:** Manage own restaurant
- **WAITER:** Take orders and manage tables
- **GUEST:** Browse menu and create orders

---

## 🧪 Testing the API

### 1. Open Swagger UI
Go to http://127.0.0.1:8000/api/docs/

### 2. Authenticate
- Click "Authorize" button
- Go to Users endpoint: POST `/api/users/login/`
- Click "Try it out"
- Enter credentials:
  ```json
  {
    "username": "admin",
    "password": "admin"
  }
  ```
- Copy the returned `access` token
- Click "Authorize" and paste token in format: `Bearer <token>`

### 3. Test Endpoints
Now all endpoints are unlocked! Try:
- **GET** `/api/restaurants/` - List restaurants
- **POST** `/api/restaurants/` - Create restaurant
- **GET** `/api/menu/categories/` - List menu categories
- **GET** `/api/tables/` - List tables
- **GET** `/api/orders/` - List orders

---

## 📁 Project Structure

```
restaurant_qr_project/
├── manage.py                 # Django management
├── db.sqlite3               # Database
├── requirements.txt         # Python packages
├── .env                     # Environment variables
├── config/                  # Django settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                    # Django apps
│   ├── accounts/           # Users & authentication
│   ├── restaurants/        # Restaurant management
│   ├── tables/            # Table management
│   ├── menu/              # Menu items
│   ├── orders/            # Order management
│   └── payments/          # Payment processing
├── scripts/               # Utility scripts
│   └── generate_sample_data.py
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
└── fixtures/             # Test data
```

---

## 📚 API Endpoints (50+)

### **Authentication** (`/api/users/`)
- POST `/login/` - Get JWT tokens
- POST `/register/` - Create new user
- GET `/profile/` - Get current user
- PUT `/profile/` - Update profile
- POST `/change-password/` - Change password

### **Restaurants** (`/api/restaurants/`)
- GET `/` - List all restaurants
- POST `/` - Create restaurant (owners only)
- GET `/{id}/` - Restaurant details
- PUT `/{id}/` - Update restaurant
- DELETE `/{id}/` - Delete restaurant
- GET `/{id}/settings/` - Restaurant settings
- GET `/{id}/menu-categories/` - Menu categories
- GET `/{id}/tables/` - Restaurant tables
- GET `/my-restaurants/` - User's restaurants (owners only)

### **Menu** (`/api/menu/`)
- **Categories**
  - GET `/categories/` - List categories
  - POST `/categories/` - Create category
  - GET `/categories/{id}/` - Category details
  
- **Items**
  - GET `/items/` - List items
  - POST `/items/` - Create item
  - GET `/items/{id}/` - Item details
  - GET `/items/popular/` - Popular items
  - GET `/items/chef-special/` - Chef specials
  - GET `/items/vegetarian/` - Vegetarian items

### **Tables** (`/api/tables/`)
- GET `/` - List tables
- POST `/` - Create table
- GET `/available/` - Available tables
- GET `/occupied/` - Occupied tables
- POST `/{id}/open-session/` - Open table session
- POST `/{id}/close-session/` - Close table session
- GET `/sessions/` - List sessions

### **Orders** (`/api/orders/`)
- GET `/` - List orders
- POST `/` - Create order
- GET `/{id}/` - Order details
- POST `/{id}/confirm/` - Confirm order
- POST `/{id}/mark-ready/` - Mark as ready
- POST `/{id}/mark-delivered/` - Mark as delivered
- POST `/{id}/cancel/` - Cancel order
- GET `/active/` - Active orders
- GET `/pending/` - Pending orders

### **Payments** (`/api/payments/`)
- GET `/` - List payments
- POST `/` - Create payment
- GET `/{id}/` - Payment details
- POST `/{id}/confirm/` - Confirm payment
- POST `/{id}/refund/` - Refund payment
- GET `/statistics/` - Payment statistics

---

## 🛠️ Helpful Scripts

### Reset Database
```bash
python fix_db.py
```
Clears all data and resets migrations.

### Verify Setup
```bash
python verify_setup.py
```
Checks all components and displays system status.

### Create Admin User
```bash
python create_admin.py
```
Creates/resets admin credentials (admin / admin).

### Generate Sample Data
```bash
python scripts/generate_sample_data.py
```
Populates database with example restaurants, menus, tables, and orders.

---

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check for port conflicts
netstat -ano | findstr :8000

# Kill process on port 8000 (Windows)
taskkill /PID <pid> /F
```

### SSL/HTTPS error?
- Use `http://` (not `https://`)
- This is a development server, only supports HTTP
- Clear browser cache (Ctrl+Shift+Del)
- Open in incognito window

### Database errors?
```bash
python fix_db.py
```

### Import errors?
```bash
pip install -r requirements.txt
python manage.py check
```

---

## 📞 API Authentication

All endpoints except login/register require authentication.

### Getting a Token
```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using the Token
```bash
curl -X GET http://127.0.0.1:8000/api/restaurants/ \
  -H "Authorization: Bearer <your_access_token>"
```

---

## 🎯 Next Steps

1. ✅ Start server (`python manage.py runserver`)
2. ✅ Open Swagger UI (http://127.0.0.1:8000/api/docs/)
3. ✅ Authenticate with admin/admin
4. ✅ Test endpoints
5. ✅ Generate sample data (`python scripts/generate_sample_data.py`)
6. 📋 Build frontend (React/Vue/Angular)
7. 🚀 Deploy to production

---

## 📖 Documentation Files

- **ARCHITECTURE.md** - System design and components
- **API.md** - Detailed API documentation
- **DEPLOYMENT.md** - Production setup
- **QUICKSTART.md** - (this file)

---

**Backend is complete and ready for frontend development!** 🎉
