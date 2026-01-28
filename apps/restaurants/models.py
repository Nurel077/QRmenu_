"""
Restaurant models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Restaurant(models.Model):
    """
    Модель ресторана.
    """
    
    name = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL идентификатор'),
        help_text=_('Уникальный URL для ресторана')
    )
    
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='owned_restaurants',
        verbose_name=_('Владелец')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    
    logo = models.ImageField(
        upload_to='restaurants/logos/',
        blank=True,
        null=True,
        verbose_name=_('Логотип')
    )
    
    cover_image = models.ImageField(
        upload_to='restaurants/covers/',
        blank=True,
        null=True,
        verbose_name=_('Обложка')
    )
    
    # Контактная информация
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Телефон')
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name=_('Email')
    )
    
    website = models.URLField(
        blank=True,
        verbose_name=_('Веб-сайт')
    )
    
    # Адрес
    address = models.CharField(
        max_length=300,
        verbose_name=_('Адрес')
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name=_('Город')
    )
    
    country = models.CharField(
        max_length=100,
        default='Кыргызстан',
        verbose_name=_('Страна')
    )
    
    # Настройки
    currency = models.CharField(
        max_length=10,
        default='KGS',
        verbose_name=_('Валюта'),
        help_text=_('Код валюты (USD, EUR, KGS и т.д.)')
    )
    
    language = models.CharField(
        max_length=10,
        default='ru',
        verbose_name=_('Язык'),
        help_text=_('Язык меню по умолчанию')
    )
    
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Ставка налога (%)'),
        help_text=_('Налог в процентах (например, 10 для 10%)')
    )
    
    service_charge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Сервисный сбор (%)'),
        help_text=_('Сервисный сбор в процентах')
    )
    
    # Время работы
    opening_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('Время открытия')
    )
    
    closing_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('Время закрытия')
    )
    
    # Статус
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен'),
        help_text=_('Доступен ли ресторан для заказов')
    )
    
    # Дополнительные настройки
    allow_cash_payment = models.BooleanField(
        default=True,
        verbose_name=_('Разрешить наличные'),
        help_text=_('Принимать оплату наличными')
    )
    
    allow_qr_payment = models.BooleanField(
        default=True,
        verbose_name=_('Разрешить QR оплату'),
        help_text=_('Принимать оплату через QR код')
    )
    
    require_waiter_confirmation = models.BooleanField(
        default=True,
        verbose_name=_('Требуется подтверждение официанта'),
        help_text=_('Официант должен подтвердить заказы с наличной оплатой')
    )
    
    # Метаданные
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    
    class Meta:
        verbose_name = _('Ресторан')
        verbose_name_plural = _('Рестораны')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def total_tables(self):
        """Общее количество столиков"""
        return self.tables.count()
    
    @property
    def active_tables(self):
        """Количество занятых столиков"""
        return self.tables.filter(is_occupied=True).count()
    
    @property
    def is_open_now(self):
        """Проверка, открыт ли ресторан сейчас"""
        if not self.opening_time or not self.closing_time:
            return True
        
        from datetime import datetime
        now = datetime.now().time()
        
        if self.opening_time <= self.closing_time:
            return self.opening_time <= now <= self.closing_time
        else:
            # Работает через полночь
            return now >= self.opening_time or now <= self.closing_time


class RestaurantSettings(models.Model):
    """
    Дополнительные настройки ресторана.
    """
    
    restaurant = models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_('Ресторан')
    )
    
    # Уведомления
    email_notifications = models.BooleanField(
        default=True,
        verbose_name=_('Email уведомления'),
        help_text=_('Отправлять уведомления на email')
    )
    
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name=_('SMS уведомления'),
        help_text=_('Отправлять SMS уведомления')
    )
    
    # Оформление
    primary_color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name=_('Основной цвет'),
        help_text=_('Цвет в формате HEX (#000000)')
    )
    
    secondary_color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name=_('Вторичный цвет'),
        help_text=_('Цвет в формате HEX (#000000)')
    )
    
    # Кастомные тексты
    welcome_message = models.TextField(
        blank=True,
        verbose_name=_('Приветственное сообщение'),
        help_text=_('Сообщение, которое видят гости при сканировании QR кода')
    )
    
    footer_text = models.TextField(
        blank=True,
        verbose_name=_('Текст в подвале'),
        help_text=_('Текст внизу страницы меню')
    )
    
    class Meta:
        verbose_name = _('Настройки ресторана')
        verbose_name_plural = _('Настройки ресторанов')
    
    def __str__(self):
        return f"Настройки: {self.restaurant.name}"
