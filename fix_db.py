#!/usr/bin/env python
"""Fix the database migration state"""
import sqlite3
import os

db_path = 'db.sqlite3'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear all migrations
    cursor.execute('DELETE FROM django_migrations')
    conn.commit()
    print("✅ Cleared migration history")
    
    # Delete all tables except django_ tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for (table_name,) in tables:
        if not table_name.startswith('sqlite_'):
            try:
                cursor.execute(f'DROP TABLE [{table_name}]')
                print(f"   Dropped table: {table_name}")
            except:
                pass
    
    conn.commit()
    conn.close()
    print("✅ Cleaned database")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Now run migrations
print("\nApplying migrations...")
os.system('python manage.py migrate')
