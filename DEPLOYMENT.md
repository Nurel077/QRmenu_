# Руководство по развертыванию RestaurantQR

## Оглавление
- [Локальная разработка](#локальная-разработка)
- [Развертывание с Docker](#развертывание-с-docker)
- [Производственное развертывание](#производственное-развертывание)
- [Настройка Nginx](#настройка-nginx)
- [Backup и восстановление](#backup-и-восстановление)

---

## Локальная разработка

### Требования
- Python 3.10+
- PostgreSQL 13+ (опционально, можно использовать SQLite)
- Redis 6+ (для WebSockets)
- Node.js 16+ (если используются frontend инструменты)

### Быстрый старт

1. **Клонировать репозиторий**
```bash
git clone <repository-url>
cd restaurant_qr_project
```

2. **Создать виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установить зависимости**
```bash
pip install -r requirements.txt
```

4. **Настроить переменные окружения**
```bash
cp .env.example .env
# Отредактируйте .env файл
```

5. **Применить миграции**
```bash
python manage.py migrate
```

6. **Создать суперпользователя**
```bash
python manage.py createsuperuser
```

7. **Загрузить тестовые данные (опционально)**
```bash
python manage.py loaddata fixtures/sample_data.json
```

8. **Запустить сервер разработки**
```bash
# В одном терминале - Django
python manage.py runserver

# В другом терминале - Channels (для WebSockets)
daphne -b 127.0.0.1 -p 8001 config.asgi:application

# В третьем терминале - Redis (если не запущен)
redis-server
```

9. **Открыть приложение**
- Веб-интерфейс: http://127.0.0.1:8000/
- Админ-панель: http://127.0.0.1:8000/admin/
- API документация: http://127.0.0.1:8000/api/docs/

---

## Развертывание с Docker

### Запуск с Docker Compose

1. **Убедитесь, что Docker установлен**
```bash
docker --version
docker-compose --version
```

2. **Создайте .env файл**
```bash
cp .env.example .env
# Настройте переменные окружения
```

3. **Запустите все сервисы**
```bash
docker-compose up -d
```

4. **Выполните миграции**
```bash
docker-compose exec web python manage.py migrate
```

5. **Создайте суперпользователя**
```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Загрузите тестовые данные (опционально)**
```bash
docker-compose exec web python manage.py loaddata fixtures/sample_data.json
```

7. **Проверьте статус**
```bash
docker-compose ps
```

Приложение будет доступно по адресу: http://localhost/

### Полезные команды Docker

```bash
# Просмотр логов
docker-compose logs -f web

# Перезапуск сервисов
docker-compose restart

# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Пересборка образов
docker-compose build --no-cache

# Выполнение команд в контейнере
docker-compose exec web python manage.py <command>

# Доступ к оболочке контейнера
docker-compose exec web bash

# Доступ к Django shell
docker-compose exec web python manage.py shell
```

---

## Производственное развертывание

### Подготовка сервера (Ubuntu 22.04)

1. **Обновление системы**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Установка зависимостей**
```bash
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx redis-server
```

3. **Настройка PostgreSQL**
```bash
sudo -u postgres psql

CREATE DATABASE restaurant_qr;
CREATE USER restaurant_qr_user WITH PASSWORD 'strong_password';
ALTER ROLE restaurant_qr_user SET client_encoding TO 'utf8';
ALTER ROLE restaurant_qr_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE restaurant_qr_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE restaurant_qr TO restaurant_qr_user;
\q
```

4. **Клонирование проекта**
```bash
cd /var/www/
sudo git clone <repository-url> restaurant_qr
cd restaurant_qr
```

5. **Настройка виртуального окружения**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

6. **Настройка переменных окружения**
```bash
sudo nano .env
```

Пример production .env:
```env
SECRET_KEY=your-very-long-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://restaurant_qr_user:strong_password@localhost/restaurant_qr
REDIS_URL=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

7. **Применение миграций и сбор статики**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

8. **Настройка Gunicorn**
```bash
sudo nano /etc/systemd/system/restaurant_qr.service
```

```ini
[Unit]
Description=RestaurantQR Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/restaurant_qr
EnvironmentFile=/var/www/restaurant_qr/.env
ExecStart=/var/www/restaurant_qr/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/restaurant_qr/restaurant_qr.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

9. **Настройка Daphne (для WebSockets)**
```bash
sudo nano /etc/systemd/system/restaurant_qr_daphne.service
```

```ini
[Unit]
Description=RestaurantQR Daphne daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/restaurant_qr
EnvironmentFile=/var/www/restaurant_qr/.env
ExecStart=/var/www/restaurant_qr/venv/bin/daphne \
          -u /var/www/restaurant_qr/daphne.sock \
          config.asgi:application

[Install]
WantedBy=multi-user.target
```

10. **Запуск сервисов**
```bash
sudo systemctl start restaurant_qr
sudo systemctl enable restaurant_qr
sudo systemctl start restaurant_qr_daphne
sudo systemctl enable restaurant_qr_daphne

# Проверка статуса
sudo systemctl status restaurant_qr
sudo systemctl status restaurant_qr_daphne
```

---

## Настройка Nginx

1. **Создание конфигурации Nginx**
```bash
sudo nano /etc/nginx/sites-available/restaurant_qr
```

```nginx
upstream restaurant_qr_app {
    server unix:/var/www/restaurant_qr/restaurant_qr.sock;
}

upstream restaurant_qr_ws {
    server unix:/var/www/restaurant_qr/daphne.sock;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/restaurant_qr/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/restaurant_qr/media/;
        expires 30d;
    }

    # WebSocket connections
    location /ws/ {
        proxy_pass http://restaurant_qr_ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Application
    location / {
        proxy_pass http://restaurant_qr_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **Активация конфигурации**
```bash
sudo ln -s /etc/nginx/sites-available/restaurant_qr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

3. **Настройка SSL (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Автообновление сертификата
sudo certbot renew --dry-run
```

---

## Celery для фоновых задач

1. **Настройка Celery Worker**
```bash
sudo nano /etc/systemd/system/restaurant_qr_celery.service
```

```ini
[Unit]
Description=RestaurantQR Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/restaurant_qr
EnvironmentFile=/var/www/restaurant_qr/.env
ExecStart=/var/www/restaurant_qr/venv/bin/celery -A config worker -l info

[Install]
WantedBy=multi-user.target
```

2. **Настройка Celery Beat**
```bash
sudo nano /etc/systemd/system/restaurant_qr_celerybeat.service
```

```ini
[Unit]
Description=RestaurantQR Celery Beat
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/restaurant_qr
EnvironmentFile=/var/www/restaurant_qr/.env
ExecStart=/var/www/restaurant_qr/venv/bin/celery -A config beat -l info

[Install]
WantedBy=multi-user.target
```

3. **Запуск**
```bash
sudo systemctl start restaurant_qr_celery
sudo systemctl enable restaurant_qr_celery
sudo systemctl start restaurant_qr_celerybeat
sudo systemctl enable restaurant_qr_celerybeat
```

---

## Backup и восстановление

### Backup базы данных

```bash
# Создание backup
pg_dump -U restaurant_qr_user restaurant_qr > backup_$(date +%Y%m%d).sql

# С сжатием
pg_dump -U restaurant_qr_user restaurant_qr | gzip > backup_$(date +%Y%m%d).sql.gz

# Автоматический backup (crontab)
0 2 * * * pg_dump -U restaurant_qr_user restaurant_qr | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
```

### Восстановление базы данных

```bash
# Из обычного backup
psql -U restaurant_qr_user restaurant_qr < backup_20260128.sql

# Из сжатого backup
gunzip -c backup_20260128.sql.gz | psql -U restaurant_qr_user restaurant_qr
```

### Backup media файлов

```bash
# Создание архива
tar -czf media_backup_$(date +%Y%m%d).tar.gz /var/www/restaurant_qr/media/

# Синхронизация с удаленным хранилищем (AWS S3)
aws s3 sync /var/www/restaurant_qr/media/ s3://your-bucket/media/
```

---

## Мониторинг и логи

### Просмотр логов

```bash
# Django logs
tail -f /var/www/restaurant_qr/logs/django.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Systemd logs
journalctl -u restaurant_qr -f
journalctl -u restaurant_qr_daphne -f
```

### Мониторинг производительности

```bash
# Мониторинг CPU и памяти
htop

# Мониторинг процессов Django
ps aux | grep gunicorn
ps aux | grep daphne

# Мониторинг соединений PostgreSQL
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Мониторинг Redis
redis-cli monitor
```

---

## Обновление приложения

```bash
# 1. Получить последние изменения
cd /var/www/restaurant_qr
sudo git pull origin main

# 2. Активировать venv
source venv/bin/activate

# 3. Обновить зависимости
pip install -r requirements.txt

# 4. Применить миграции
python manage.py migrate

# 5. Собрать статику
python manage.py collectstatic --noinput

# 6. Перезапустить сервисы
sudo systemctl restart restaurant_qr
sudo systemctl restart restaurant_qr_daphne
sudo systemctl restart restaurant_qr_celery
sudo systemctl restart restaurant_qr_celerybeat
```

---

## Troubleshooting

### Проблемы с миграциями
```bash
# Проверка состояния миграций
python manage.py showmigrations

# Откат миграции
python manage.py migrate app_name migration_name

# Создание fake миграции
python manage.py migrate --fake app_name migration_name
```

### Проблемы с static файлами
```bash
# Пересборка статики
python manage.py collectstatic --clear --noinput

# Проверка прав доступа
sudo chown -R www-data:www-data /var/www/restaurant_qr/staticfiles/
sudo chmod -R 755 /var/www/restaurant_qr/staticfiles/
```

### Проблемы с WebSockets
```bash
# Проверка Redis
redis-cli ping

# Проверка Daphne
sudo systemctl status restaurant_qr_daphne
journalctl -u restaurant_qr_daphne -n 50
```

---

## Контрольный список для production

- [ ] DEBUG=False в .env
- [ ] Установлен секретный SECRET_KEY
- [ ] Настроены ALLOWED_HOSTS
- [ ] Включен HTTPS (SSL сертификат)
- [ ] Настроены SECURE_* настройки
- [ ] Настроен файрвол (ufw)
- [ ] Настроены backup базы данных
- [ ] Настроены backup media файлов
- [ ] Настроен мониторинг логов
- [ ] Настроены email уведомления об ошибках
- [ ] Протестированы все основные функции
- [ ] Документация обновлена
