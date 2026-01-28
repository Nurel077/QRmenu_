#!/usr/bin/env python
"""
Quick start script for development server.
Run: python dev_server.py
"""
import os
import sys
import django

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    os.environ['DEBUG'] = 'True'  # Ensure DEBUG is True for development
    
    django.setup()
    
    from django.core.management import execute_from_command_line
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║           RestaurantQR Development Server                      ║
    ╠════════════════════════════════════════════════════════════════╣
    ║                                                                ║
    ║  🚀 Starting Django Development Server...                     ║
    ║                                                                ║
    ║  📱 Access Points:                                             ║
    ║     🌐 Main:     http://127.0.0.1:8000/                       ║
    ║     👤 Admin:    http://127.0.0.1:8000/admin/                 ║
    ║     📚 API Docs: http://127.0.0.1:8000/api/docs/              ║
    ║     🔍 Schema:   http://127.0.0.1:8000/api/schema/            ║
    ║                                                                ║
    ║  🔑 Default Admin Login:                                      ║
    ║     Username: admin                                            ║
    ║     Password: admin                                            ║
    ║                                                                ║
    ║  ⚠️  IMPORTANT: Use HTTP (not HTTPS) in development!          ║
    ║                                                                ║
    ║  Press Ctrl+C to stop the server                              ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
