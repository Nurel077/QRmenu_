#!/usr/bin/env python
import os
import sqlite3

db_path = 'db.sqlite3'

# Remove database
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Removed {db_path}")

# Run migrations
os.system('python manage.py migrate')
print("\n✅ Migrations complete")

# Create superuser
os.system('python manage.py createsuperuser --noinput --username admin --email admin@example.com')
print("✅ Created admin user (password: admin)")
