import os

apps = ['accounts', 'restaurants', 'tables', 'menu', 'orders', 'payments']
base_path = '/home/claude/restaurant_qr_project/apps'

for app in apps:
    app_path = os.path.join(base_path, app)
    
    # Create __init__.py if not exists
    init_file = os.path.join(app_path, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write(f"default_app_config = 'apps.{app}.apps.{app.capitalize()}Config'\n")
    
    # Create apps.py
    apps_file = os.path.join(app_path, 'apps.py')
    app_class = app.capitalize() + 'Config'
    content = f'''from django.apps import AppConfig


class {app_class}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app}'
    verbose_name = '{app.capitalize()}'
'''
    with open(apps_file, 'w') as f:
        f.write(content)
    
    print(f"Created files for {app}")

print("All app files created!")
