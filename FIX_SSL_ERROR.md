# 🔧 Fix: "This site can't provide a secure connection" Error

## ⚡ Quick Fix (30 seconds)

### **Option 1: Clear Browser Cache & Use New Tab**
1. **Clear your browser cache:**
   - Chrome: `Ctrl+Shift+Delete` → Clear All Time → Clear data
   - Firefox: `Ctrl+Shift+Delete` → Clear All → Clear Now
   - Edge: `Ctrl+Shift+Delete` → Clear browsing data

2. **Open a NEW INCOGNITO/PRIVATE window**

3. **Go to (copy-paste exactly):**
   ```
   http://127.0.0.1:8000/api/docs/
   ```
   ⚠️ Use **HTTP** (not HTTPS)!

---

## 🚀 Recommended: Use dev_server.py

Instead of `python manage.py runserver`, use:

```bash
python dev_server.py
```

This ensures:
- ✅ DEBUG is set to True
- ✅ HTTP only (no SSL redirect)
- ✅ Server runs on 0.0.0.0:8000
- ✅ Shows helpful startup messages

---

## 📝 What's the Problem?

**Root Cause:**
- Browser cached an HTTPS redirect
- Django settings have `SECURE_SSL_REDIRECT = True` (for production)
- Development server only supports HTTP

**Solution:**
- Use `.env` file to set `DEBUG=True`
- This disables SSL redirect in development
- Always use `http://` not `https://`

---

## ✅ Verify It's Working

After opening `http://127.0.0.1:8000/api/docs/`, you should see:

```
┌─────────────────────────────────────────┐
│  RestaurantQR API                      │
│                                         │
│  /api/auth/register/                   │
│  /api/auth/token/                      │
│  /api/restaurants/                     │
│  /api/menu/categories/                 │
│  /api/tables/                          │
│  /api/orders/                          │
│  /api/payments/                        │
│                                         │
│  [Try it out buttons for each endpoint]│
└─────────────────────────────────────────┘
```

---

## 🎯 Testing Endpoints

### **1. Get JWT Token (copy URL to your browser):**
```
http://127.0.0.1:8000/api/auth/token/
```
```json
POST /api/auth/token/
{
  "username": "admin",
  "password": "admin"
}
```

### **2. List Restaurants:**
```
http://127.0.0.1:8000/api/restaurants/
```

### **3. Admin Panel:**
```
http://127.0.0.1:8000/admin/
```
- Username: `admin`
- Password: `admin`

---

## 🐛 Still Having Issues?

Try these commands:

```bash
# 1. Kill any existing Django processes
taskkill /F /IM python.exe

# 2. Clear Django cache
python manage.py clear_cache

# 3. Reset browser
# Close ALL browser windows
# Open fresh window
# Try: http://127.0.0.1:8000/

# 4. Use different port if 8000 is in use
python manage.py runserver 8001
```

---

## 💡 Key Points to Remember

| Item | Development | Production |
|------|-------------|-----------|
| URL | `http://` | `https://` |
| DEBUG | `True` | `False` |
| SSL Redirect | Off | On |
| Secret Key | Default | Random |
| Allowed Hosts | localhost | Your domain |

---

## ✨ Now You're Good to Go!

Your API is ready to use:
- ✅ HTTP server running
- ✅ No SSL issues
- ✅ Full API documentation
- ✅ Admin panel accessible
- ✅ Ready for development

Start with: `python dev_server.py`
