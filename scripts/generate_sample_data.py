"""
Script to generate sample data for testing.
Usage: python manage.py shell < scripts/generate_sample_data.py
"""

from apps.accounts.models import User
from apps.restaurants.models import Restaurant, RestaurantSettings
from apps.tables.models import Table, TableSession
from apps.menu.models import MenuCategory, MenuItem
from apps.orders.models import Order, OrderItem
from django.utils import timezone
from decimal import Decimal

print("🚀 Generating sample data...")

# Create users
print("\n👥 Creating users...")
superadmin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'role': User.Role.SUPERADMIN,
        'first_name': 'Super',
        'last_name': 'Admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    superadmin.set_password('admin123')
    superadmin.save()
    print(f"✓ Created superadmin: {superadmin.username}")

# Create restaurant owner
owner, created = User.objects.get_or_create(
    username='owner1',
    defaults={
        'email': 'owner@example.com',
        'role': User.Role.OWNER,
        'first_name': 'Владелец',
        'last_name': 'Ресторана',
    }
)
if created:
    owner.set_password('owner123')
    owner.save()
    print(f"✓ Created owner: {owner.username}")

# Create restaurant
print("\n🏢 Creating restaurant...")
restaurant, created = Restaurant.objects.get_or_create(
    slug='test-restaurant',
    defaults={
        'name': 'Тестовый Ресторан',
        'owner': owner,
        'description': 'Лучший ресторан в городе с разнообразным меню',
        'phone': '+996700123456',
        'email': 'info@testrestaurant.com',
        'address': 'ул. Чуй, 123',
        'city': 'Бишкек',
        'country': 'Кыргызстан',
        'currency': 'KGS',
        'language': 'ru',
        'tax_rate': Decimal('10.00'),
        'service_charge': Decimal('5.00'),
        'is_active': True,
        'allow_cash_payment': True,
        'allow_qr_payment': True,
    }
)
if created:
    print(f"✓ Created restaurant: {restaurant.name}")

# Update owner's restaurant
owner.restaurant = restaurant
owner.save()

# Create restaurant settings
settings, created = RestaurantSettings.objects.get_or_create(
    restaurant=restaurant,
    defaults={
        'welcome_message': 'Добро пожаловать в наш ресторан!',
        'primary_color': '#e74c3c',
        'secondary_color': '#34495e',
    }
)

# Create waiters
print("\n👨‍🍳 Creating waiters...")
for i in range(1, 3):
    waiter, created = User.objects.get_or_create(
        username=f'waiter{i}',
        defaults={
            'email': f'waiter{i}@example.com',
            'role': User.Role.WAITER,
            'first_name': f'Официант',
            'last_name': f'№{i}',
            'restaurant': restaurant,
        }
    )
    if created:
        waiter.set_password('waiter123')
        waiter.save()
        print(f"✓ Created waiter: {waiter.username}")

# Create tables
print("\n🪑 Creating tables...")
zones = ['Основной зал', 'Терраса', 'VIP зона']
for i in range(1, 11):
    table, created = Table.objects.get_or_create(
        restaurant=restaurant,
        number=f'A{i}',
        defaults={
            'capacity': 4 if i <= 7 else 6,
            'zone': zones[i % 3],
            'is_active': True,
        }
    )
    if created:
        print(f"✓ Created table: {table.number}")

# Create menu categories
print("\n📖 Creating menu categories...")
categories_data = [
    {'name': 'Супы', 'icon': 'soup', 'order': 1},
    {'name': 'Салаты', 'icon': 'salad', 'order': 2},
    {'name': 'Горячие блюда', 'icon': 'utensils', 'order': 3},
    {'name': 'Пицца', 'icon': 'pizza-slice', 'order': 4},
    {'name': 'Десерты', 'icon': 'ice-cream', 'order': 5},
    {'name': 'Напитки', 'icon': 'glass', 'order': 6},
]

categories = {}
for cat_data in categories_data:
    category, created = MenuCategory.objects.get_or_create(
        restaurant=restaurant,
        name=cat_data['name'],
        defaults={
            'icon': cat_data['icon'],
            'order': cat_data['order'],
            'is_active': True,
        }
    )
    categories[cat_data['name']] = category
    if created:
        print(f"✓ Created category: {category.name}")

# Create menu items
print("\n🍽️ Creating menu items...")
menu_items_data = [
    # Супы
    {'category': 'Супы', 'name': 'Борщ', 'price': '250', 'cooking_time': 15, 'is_popular': True},
    {'category': 'Супы', 'name': 'Солянка', 'price': '280', 'cooking_time': 20},
    {'category': 'Супы', 'name': 'Куриный суп', 'price': '220', 'cooking_time': 15},
    
    # Салаты
    {'category': 'Салаты', 'name': 'Цезарь', 'price': '320', 'cooking_time': 10, 'is_popular': True},
    {'category': 'Салаты', 'name': 'Греческий', 'price': '290', 'cooking_time': 10, 'is_vegetarian': True},
    {'category': 'Салаты', 'name': 'Оливье', 'price': '240', 'cooking_time': 10},
    
    # Горячие блюда
    {'category': 'Горячие блюда', 'name': 'Стейк рибай', 'price': '890', 'cooking_time': 25, 'is_chef_special': True},
    {'category': 'Горячие блюда', 'name': 'Куриное филе гриль', 'price': '450', 'cooking_time': 20},
    {'category': 'Горячие блюда', 'name': 'Лагман', 'price': '350', 'cooking_time': 20, 'is_popular': True},
    {'category': 'Горячие блюда', 'name': 'Плов', 'price': '380', 'cooking_time': 25, 'is_popular': True},
    
    # Пицца
    {'category': 'Пицца', 'name': 'Маргарита', 'price': '420', 'cooking_time': 15, 'is_vegetarian': True},
    {'category': 'Пицца', 'name': 'Пепперони', 'price': '480', 'cooking_time': 15, 'is_popular': True},
    {'category': 'Пицца', 'name': 'Четыре сыра', 'price': '520', 'cooking_time': 15, 'is_vegetarian': True},
    
    # Десерты
    {'category': 'Десерты', 'name': 'Тирамису', 'price': '280', 'cooking_time': 5},
    {'category': 'Десерты', 'name': 'Чизкейк', 'price': '260', 'cooking_time': 5},
    {'category': 'Десерты', 'name': 'Мороженое', 'price': '180', 'cooking_time': 2, 'is_vegetarian': True},
    
    # Напитки
    {'category': 'Напитки', 'name': 'Кола', 'price': '100', 'cooking_time': 1},
    {'category': 'Напитки', 'name': 'Свежевыжатый сок', 'price': '150', 'cooking_time': 3, 'is_vegetarian': True},
    {'category': 'Напитки', 'name': 'Кофе эспрессо', 'price': '120', 'cooking_time': 3},
    {'category': 'Напитки', 'name': 'Латте', 'price': '160', 'cooking_time': 5},
]

for item_data in menu_items_data:
    category_name = item_data.pop('category')
    item, created = MenuItem.objects.get_or_create(
        category=categories[category_name],
        name=item_data['name'],
        defaults={
            'description': f'Вкусное блюдо "{item_data["name"]}"',
            'price': Decimal(item_data['price']),
            'cooking_time': item_data.get('cooking_time', 10),
            'is_vegetarian': item_data.get('is_vegetarian', False),
            'is_popular': item_data.get('is_popular', False),
            'is_chef_special': item_data.get('is_chef_special', False),
            'is_available': True,
        }
    )
    if created:
        print(f"✓ Created menu item: {item.name}")

print("\n✅ Sample data generation completed!")
print("\n📝 Login credentials:")
print("   Superadmin: admin / admin123")
print("   Owner: owner1 / owner123")
print("   Waiter: waiter1 / waiter123")
print("\n🌐 Access the application at: http://127.0.0.1:8000/")
print("   Admin panel: http://127.0.0.1:8000/admin/")
