@echo off
REM RestaurantQR Development Server Starter for Windows

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           RestaurantQR Development Server                      ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║                                                                ║
echo ║  Starting Django server with HTTP (no SSL)...                 ║
echo ║                                                                ║
echo ║  Access Points:                                                ║
echo ║    🌐 Main:     http://127.0.0.1:8000/                        ║
echo ║    👤 Admin:    http://127.0.0.1:8000/admin/                  ║
echo ║    📚 API Docs: http://127.0.0.1:8000/api/docs/               ║
echo ║                                                                ║
echo ║  ⚠️  IMPORTANT: Use HTTP (not HTTPS)!                         ║
echo ║                                                                ║
echo ║  Press Ctrl+C to stop the server                              ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Set DEBUG to True for development
set DEBUG=True

REM Run Django development server
python manage.py runserver 0.0.0.0:8000
