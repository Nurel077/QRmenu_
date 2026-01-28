# Структура проекта RestaurantQR

```
restaurant_qr_project/
│
├── config/                          # Конфигурация Django проекта
│   ├── __init__.py                 # Инициализация Celery
│   ├── settings.py                 # Основные настройки Django
│   ├── urls.py                     # Главный роутинг URL
│   ├── wsgi.py                     # WSGI конфигурация для production
│   ├── asgi.py                     # ASGI конфигурация для WebSockets
│   └── celery.py                   # Конфигурация Celery
│
├── apps/                            # Django приложения
│   │
│   ├── accounts/                    # Пользователи и аутентификация
│   │   ├── migrations/             # Миграции базы данных
│   │   ├── __init__.py
│   │   ├── admin.py                # Настройка админ-панели
│   │   ├── apps.py                 # Конфигурация приложения
│   │   ├── models.py               # User, GuestSession
│   │   ├── serializers.py          # DRF сериализаторы
│   │   ├── views.py                # API views
│   │   ├── urls.py                 # URL маршруты
│   │   ├── permissions.py          # Кастомные permissions
│   │   └── tests.py                # Unit тесты
│   │
│   ├── restaurants/                 # Рестораны
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py                # Restaurant, RestaurantSettings admin
│   │   ├── apps.py
│   │   ├── models.py               # Restaurant, RestaurantSettings
│   │   ├── serializers.py
│   │   ├── views.py                # CRUD операции
│   │   ├── urls.py                 # API endpoints
│   │   ├── urls_web.py             # Web views (landing page)
│   │   └── tests.py
│   │
│   ├── tables/                      # Столики
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py                # Table, TableSession admin
│   │   ├── apps.py
│   │   ├── models.py               # Table, TableSession
│   │   ├── serializers.py
│   │   ├── views.py                # Управление столиками, сессиями
│   │   ├── urls.py                 # API endpoints
│   │   ├── urls_web.py             # Guest interface URLs
│   │   ├── utils.py                # Генерация QR кодов
│   │   └── tests.py
│   │
│   ├── menu/                        # Меню
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py                # MenuCategory, MenuItem admin
│   │   ├── apps.py
│   │   ├── models.py               # MenuCategory, MenuItem, MenuItemOption
│   │   ├── serializers.py
│   │   ├── views.py                # CRUD меню
│   │   ├── urls.py                 # API endpoints
│   │   ├── filters.py              # Django-filter фильтры
│   │   └── tests.py
│   │
│   ├── orders/                      # Заказы
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py                # Order, OrderItem admin
│   │   ├── apps.py
│   │   ├── models.py               # Order, OrderItem, OrderStatusHistory
│   │   ├── serializers.py
│   │   ├── views.py                # Создание, управление заказами
│   │   ├── urls.py                 # API endpoints
│   │   ├── urls_waiter.py          # Waiter panel URLs
│   │   ├── consumers.py            # WebSocket consumers
│   │   ├── routing.py              # WebSocket routing
│   │   ├── signals.py              # Django signals для уведомлений
│   │   └── tests.py
│   │
│   └── payments/                    # Платежи
│       ├── migrations/
│       ├── __init__.py
│       ├── admin.py                # Payment, QRPaymentCode admin
│       ├── apps.py
│       ├── models.py               # Payment, QRPaymentCode
│       ├── serializers.py
│       ├── views.py                # Обработка платежей
│       ├── urls.py                 # API endpoints
│       ├── integrations/           # Интеграции с платежными системами
│       │   ├── __init__.py
│       │   ├── base.py             # Базовый класс
│       │   └── stripe.py           # Stripe интеграция (пример)
│       └── tests.py
│
├── templates/                       # HTML шаблоны
│   ├── base.html                   # Базовый шаблон
│   ├── index.html                  # Landing page
│   │
│   ├── guest/                      # Шаблоны для гостей
│   │   ├── table_menu.html         # Меню столика
│   │   ├── order_status.html       # Статус заказа
│   │   └── payment.html            # Страница оплаты
│   │
│   ├── waiter/                     # Панель официанта
│   │   ├── dashboard.html          # Главная панель
│   │   ├── orders_list.html        # Список заказов
│   │   ├── table_session.html      # Управление сессией
│   │   └── payment_confirm.html    # Подтверждение оплаты
│   │
│   ├── owner/                      # Панель владельца
│   │   ├── dashboard.html          # Дашборд
│   │   ├── menu_management.html    # Управление меню
│   │   ├── tables_management.html  # Управление столиками
│   │   └── analytics.html          # Аналитика
│   │
│   └── components/                 # Переиспользуемые компоненты
│       ├── menu_item_card.html
│       ├── order_card.html
│       └── navbar.html
│
├── static/                          # Статические файлы
│   ├── css/
│   │   ├── main.css                # Основные стили
│   │   ├── guest.css               # Стили для гостей
│   │   ├── waiter.css              # Стили для официантов
│   │   └── owner.css               # Стили для владельцев
│   │
│   ├── js/
│   │   ├── main.js                 # Основной JavaScript
│   │   ├── websocket.js            # WebSocket подключение
│   │   ├── order.js                # Логика заказов
│   │   └── menu.js                 # Логика меню
│   │
│   ├── img/
│   │   ├── logo.png
│   │   ├── placeholder.jpg
│   │   └── icons/
│   │
│   └── vendor/                     # Сторонние библиотеки
│       ├── bootstrap/
│       ├── jquery/
│       └── fontawesome/
│
├── media/                           # Загружаемые файлы
│   ├── avatars/                    # Аватары пользователей
│   ├── restaurants/                # Логотипы ресторанов
│   │   ├── logos/
│   │   └── covers/
│   ├── menu/                       # Фото блюд
│   │   └── items/
│   ├── tables/                     # QR коды столиков
│   │   └── qr_codes/
│   └── payments/                   # QR коды оплаты
│       └── qr_codes/
│
├── fixtures/                        # Тестовые данные
│   ├── sample_data.json            # Полный набор тестовых данных
│   ├── users.json                  # Тестовые пользователи
│   └── menu.json                   # Тестовое меню
│
├── scripts/                         # Утилиты и скрипты
│   ├── generate_sample_data.py     # Генерация тестовых данных
│   ├── generate_qr_codes.py        # Массовая генерация QR кодов
│   ├── backup_db.sh                # Скрипт backup БД
│   └── deploy.sh                   # Скрипт деплоя
│
├── logs/                            # Логи приложения
│   ├── django.log                  # Логи Django
│   ├── celery.log                  # Логи Celery
│   └── nginx.log                   # Логи Nginx (в production)
│
├── tests/                           # Интеграционные тесты
│   ├── __init__.py
│   ├── test_api.py                 # Тесты API
│   ├── test_orders.py              # Тесты заказов
│   ├── test_payments.py            # Тесты платежей
│   └── test_websockets.py          # Тесты WebSockets
│
├── docs/                            # Документация
│   ├── api/                        # API документация
│   ├── models/                     # Описание моделей
│   └── deployment/                 # Инструкции по деплою
│
├── .env.example                     # Пример переменных окружения
├── .env                            # Локальные переменные (не в git)
├── .gitignore                      # Git ignore файл
├── manage.py                       # Django management команды
├── requirements.txt                # Python зависимости
├── Dockerfile                      # Docker конфигурация
├── docker-compose.yml              # Docker Compose
├── nginx.conf                      # Конфигурация Nginx
├── README.md                       # Основное описание проекта
├── ARCHITECTURE.md                 # Документация архитектуры
├── API.md                          # API документация
├── DEPLOYMENT.md                   # Инструкции по развертыванию
└── PROJECT_STRUCTURE.md            # Этот файл
```

## Описание ключевых компонентов

### Models (Модели)

**accounts/models.py:**
- `User` - Кастомная модель пользователя с ролями
- `GuestSession` - Сессии неавторизованных гостей

**restaurants/models.py:**
- `Restaurant` - Ресторан с настройками
- `RestaurantSettings` - Расширенные настройки ресторана

**tables/models.py:**
- `Table` - Столик с QR кодом
- `TableSession` - Активная сессия за столиком

**menu/models.py:**
- `MenuCategory` - Категория меню
- `MenuItem` - Блюдо в меню
- `MenuItemOption` - Опции для блюд

**orders/models.py:**
- `Order` - Заказ
- `OrderItem` - Позиция в заказе
- `OrderStatusHistory` - История изменений статуса

**payments/models.py:**
- `Payment` - Платеж
- `QRPaymentCode` - QR код для оплаты

### Views (Представления)

**API Views (DRF ViewSets):**
- Стандартный CRUD для всех моделей
- Кастомные actions для специфичных операций
- Permissions для разграничения доступа

**Web Views (Template Views):**
- Guest views - для неавторизованных пользователей
- Waiter views - для официантов
- Owner views - для владельцев

### WebSocket Consumers

**orders/consumers.py:**
- `OrderConsumer` - Real-time обновления заказов
- `TableConsumer` - Обновления столика
- `WaiterConsumer` - Уведомления официанта

### Signals

**orders/signals.py:**
- `order_created` - При создании заказа
- `order_status_changed` - При изменении статуса
- `payment_completed` - При завершении платежа

### Celery Tasks

**orders/tasks.py:**
- `send_order_notification` - Отправка уведомлений
- `check_pending_orders` - Проверка старых заказов

**payments/tasks.py:**
- `process_payment` - Обработка платежа
- `expire_qr_codes` - Истечение QR кодов

## Соглашения об именовании

### Модели
- CamelCase для классов: `MenuItem`, `TableSession`
- snake_case для полей: `created_at`, `is_active`

### URLs
- kebab-case: `/api/menu-items/`, `/table-sessions/`
- Версионирование API: `/api/v1/`

### Views и ViewSets
- ViewSet suffix: `MenuItemViewSet`
- Generic views: `MenuItemListView`

### Templates
- snake_case: `table_menu.html`, `order_status.html`
- Префикс для компонентов: `_component_name.html`

### Static files
- CSS: kebab-case `main-theme.css`
- JS: camelCase для функций, kebab-case для файлов

## Миграции

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Просмотр SQL миграции
python manage.py sqlmigrate app_name migration_name

# Откат миграции
python manage.py migrate app_name migration_name
```

## Тестирование

```bash
# Запуск всех тестов
python manage.py test

# Тесты конкретного приложения
python manage.py test apps.orders

# С покрытием кода
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Команды управления

```bash
# Создание суперпользователя
python manage.py createsuperuser

# Загрузка fixture
python manage.py loaddata fixtures/sample_data.json

# Выгрузка данных в fixture
python manage.py dumpdata app_name.Model --indent 2 > fixture.json

# Запуск shell
python manage.py shell

# Запуск Celery worker
celery -A config worker -l info

# Запуск Celery beat
celery -A config beat -l info
```

## Development Workflow

1. Создание feature branch
2. Разработка функционала
3. Написание тестов
4. Проверка code quality (flake8, black)
5. Commit с описанием изменений
6. Push и создание Pull Request
7. Code review
8. Merge в main
9. Deploy на staging
10. Тестирование на staging
11. Deploy на production

## Code Quality

```bash
# Форматирование кода
black .

# Проверка импортов
isort .

# Линтинг
flake8 .

# Type checking (если используется)
mypy .
```
