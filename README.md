# RestaurantQR - Restaurant Management System with QR Code Ordering

## 📋 Project Description

RestaurantQR is a comprehensive Django-based restaurant management system that enables QR code-based ordering. Guests can scan table QR codes, browse menus, and place orders directly from their mobile devices in real-time.

## ✨ Current Features (Backend Complete)

### ✅ For Guests:
- 📱 QR code table scanning
- 📖 Browse restaurant menu with categories
- 🛒 Create orders with item selection
- 👥 Multi-guest ordering per table (table sessions)
- 💰 Payment method selection (cash/online)
- 📊 Real-time order status tracking via WebSockets

### ✅ For Waiters:
- ✅ Order confirmation and management
- 📋 View active orders by table
- 🔔 Real-time notifications via WebSockets
- 💳 Payment processing and status updates
- 📱 Mobile-responsive waiter dashboard

### ✅ For Restaurant Administrators:
- 🏢 Complete restaurant management
- 🪑 Table management with QR code generation
- 🍽️ Menu management (categories, items, pricing)
- 👨‍💼 Staff management (waiters)
- 📈 Order statistics and analytics
- 🔐 Role-based access control

### ✅ For Super Administrators:
- 🏪 System-wide restaurant management
- 👥 User management across all restaurants
- 📊 Global analytics and reporting

## 🏗️ Архитектура

```
restaurant_qr_project/
├── config/                 # Настройки Django проекта
├── apps/
│   ├── restaurants/       # Модуль ресторанов
│   ├── tables/           # Модуль столиков
│   ├── menu/             # Модуль меню
│   ├── orders/           # Модуль заказов
│   ├── payments/         # Модуль платежей
│   └── accounts/         # Модуль пользователей
├── static/               # Статические файлы (CSS, JS, изображения)
├── media/                # Загружаемые файлы (фото блюд, QR-коды)
├── templates/            # HTML шаблоны
└── requirements.txt      # Зависимости Python
```

## 🗄️ Модели данных

### Restaurant (Ресторан)
- Название, адрес, описание
- Владелец (связь с User)
- Настройки (валюта, язык)

### Table (Столик)
- Номер столика
- Вместимость
- QR-код
- Статус (свободен/занят)
- Привязка к ресторану

### TableSession (Сессия столика)
- Активная сессия за столиком
- Время начала/окончания
- Уникальный код для подключения гостей
- Список подключенных гостей

### MenuItem (Блюдо в меню)
- Название, описание
- Цена
- Категория (Супы, Основные блюда, Десерты и т.д.)
- Фото
- Доступность

### Order (Заказ)
- Привязка к сессии столика
- Имя гостя (опционально)
- Позиции заказа
- Способ оплаты (cash/qr)
- Статус (pending → confirmed → preparing → ready → paid)
- Официант, подтвердивший заказ

## 🔐 Роли пользователей

1. **SuperAdmin** - Полный доступ к системе
2. **RestaurantOwner** - Управление своим рестораном
3. **Waiter** - Обработка заказов
4. **Guest** - Просмотр меню и создание заказов (без регистрации)

## 🚀 Technology Stack

### ✅ Implemented
- **Backend**: Django 5.0.1, Django REST Framework 3.15.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **Real-time**: Django Channels 4.2.0 with Redis
- **Authentication**: JWT tokens + Session auth
- **API Documentation**: DRF Spectacular (Swagger/OpenAPI)
- **Admin**: Enhanced Django admin with role-based access
- **WebSockets**: Full real-time order updates
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **QR Codes**: qrcode + Pillow libraries
- **File Processing**: Image handling for menu items
- **Testing**: pytest, factory-boy, coverage
- **Code Quality**: black, flake8, isort

### 🔄 Ready for Integration
- **Payments**: Framework ready for Stripe/PayPal
- **Email/SMS**: Django signals ready for notifications
- **Caching**: Redis configuration ready
- **Deployment**: Docker, gunicorn, whitenoise

## 📦 Установка и запуск

### Требования:
- Python 3.10+
- pip
- virtualenv (опционально)

### Шаги установки:

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd restaurant_qr_project

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Применить миграции
python manage.py migrate

# 5. Создать суперпользователя
python manage.py createsuperuser

# 6. Загрузить тестовые данные (опционально)
python manage.py loaddata fixtures/sample_data.json

# 7. Запустить сервер разработки
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

## 📱 Current Usage

### ✅ For Guests (Backend Ready):
1. Scan QR code on table
2. Browse restaurant menu with categories
3. Select items and create order
4. Choose payment method (cash/online)
5. Submit order and track status in real-time

### ✅ For Waiters (Fully Implemented):
1. Login to waiter dashboard (/waiter/dashboard/)
2. View real-time order notifications
3. Manage orders by status (pending, confirmed, ready, delivered)
4. Process payments and update order status
5. Mobile-responsive interface

### ✅ For Administrators (Complete):
1. Login to Django admin (/admin/) with role-based access
2. Manage restaurants, tables, menu items
3. Add/manage staff (waiters)
4. View comprehensive order statistics
5. Generate QR codes for tables

### 🔄 Frontend Status:
- **Waiter Panel**: ✅ Complete with WebSocket real-time updates
- **Guest Interface**: 🔄 Partially implemented (basic templates)
- **Owner Panel**: ❌ Not implemented
- **Admin Enhancements**: ✅ Complete with custom features

## 🔧 Настройка

### Переменные окружения (.env):
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📊 API Endpoints

- `/api/restaurants/` - Список ресторанов
- `/api/tables/<table_id>/menu/` - Меню для столика
- `/api/orders/` - Создание/просмотр заказов
- `/api/orders/<order_id>/confirm/` - Подтверждение заказа
- `/api/tables/<table_id>/session/` - Управление сессией столика

## 🧪 Тестирование

```bash
# Запуск всех тестов
python manage.py test

# Запуск тестов конкретного приложения
python manage.py test apps.orders

# Проверка покрытия кода
coverage run --source='.' manage.py test
coverage report
```

## 📝 TODO / Roadmap

- [ ] Интеграция с платежными системами (Stripe, PayPal)
- [ ] Мультиязычность (i18n)
- [ ] PWA для мобильных устройств
- [ ] Уведомления (Email, SMS, Push)
- [ ] Аналитика и отчеты для владельцев
- [ ] Программа лояльности
- [ ] Бронирование столиков
- [ ] Отзывы и рейтинги блюд

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License

## 👥 Авторы

Разработано для демонстрации возможностей Django в создании полнофункциональных веб-приложений.

## 📧 Контакты

Для вопросов и предложений: [your-email@example.com]
