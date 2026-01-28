"""
Table models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import uuid


class Table(models.Model):
    """
    Модель столика в ресторане.
    """
    
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='tables',
        verbose_name=_('Ресторан')
    )
    
    number = models.CharField(
        max_length=20,
        verbose_name=_('Номер столика'),
        help_text=_('Номер или название столика (например: A1, VIP-1)')
    )
    
    capacity = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        verbose_name=_('Вместимость'),
        help_text=_('Количество мест за столиком')
    )
    
    qr_code = models.ImageField(
        upload_to='tables/qr_codes/',
        blank=True,
        null=True,
        verbose_name=_('QR код')
    )
    
    qr_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('URL для QR кода'),
        help_text=_('Генерируется автоматически')
    )
    
    is_occupied = models.BooleanField(
        default=False,
        verbose_name=_('Занят'),
        help_text=_('Есть ли активная сессия за столиком')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен'),
        help_text=_('Доступен ли столик для использования')
    )
    
    # Расположение
    zone = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Зона'),
        help_text=_('Зона размещения (Терраса, Основной зал, VIP и т.д.)')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание'),
        help_text=_('Дополнительная информация о столике')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    
    class Meta:
        verbose_name = _('Столик')
        verbose_name_plural = _('Столики')
        ordering = ['restaurant', 'number']
        unique_together = ['restaurant', 'number']
    
    def __str__(self):
        return f"{self.restaurant.name} - Столик {self.number}"
    
    def save(self, *args, **kwargs):
        # Генерация URL для QR кода
        if not self.qr_url:
            from django.conf import settings
            domain = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'
            self.qr_url = f"http://{domain}/table/{self.restaurant.slug}/{self.number}/"
        
        super().save(*args, **kwargs)
        
        # Генерация QR кода после сохранения (нужен ID)
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        """
        Генерация QR кода для столика.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Добавление текста с номером столика
        img = img.convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Сохранение в файл
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'table_{self.restaurant.slug}_{self.number}.png'
        
        self.qr_code.save(filename, File(buffer), save=False)
        self.save(update_fields=['qr_code'])
    
    @property
    def current_session(self):
        """Получить текущую активную сессию"""
        return self.sessions.filter(closed_at__isnull=True).first()
    
    @property
    def current_orders_count(self):
        """Количество активных заказов"""
        session = self.current_session
        if session:
            return session.orders.exclude(status='paid').count()
        return 0


class TableSession(models.Model):
    """
    Сессия столика - период времени, когда за столом сидят гости.
    """
    
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('Столик')
    )
    
    session_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Код сессии'),
        help_text=_('Уникальный код для подключения гостей')
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Время начала')
    )
    
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Время окончания')
    )
    
    waiter = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='table_sessions',
        verbose_name=_('Официант'),
        help_text=_('Официант, обслуживающий столик')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Заметки'),
        help_text=_('Заметки официанта о столике/гостях')
    )
    
    class Meta:
        verbose_name = _('Сессия столика')
        verbose_name_plural = _('Сессии столиков')
        ordering = ['-started_at']
    
    def __str__(self):
        status = "Активна" if not self.closed_at else "Завершена"
        return f"{self.table} - {status} ({self.started_at.strftime('%d.%m.%Y %H:%M')})"
    
    def save(self, *args, **kwargs):
        # Генерация уникального кода сессии
        if not self.session_code:
            self.session_code = str(uuid.uuid4())[:8].upper()
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Обновление статуса столика
        if is_new:
            self.table.is_occupied = True
            self.table.save(update_fields=['is_occupied'])
    
    def close_session(self):
        """Закрыть сессию столика"""
        from django.utils import timezone
        self.closed_at = timezone.now()
        self.save()
        
        # Обновить статус столика
        self.table.is_occupied = False
        self.table.save(update_fields=['is_occupied'])
    
    @property
    def is_active(self):
        """Проверка, активна ли сессия"""
        return self.closed_at is None
    
    @property
    def total_amount(self):
        """Общая сумма всех заказов в сессии"""
        from decimal import Decimal
        total = Decimal('0')
        for order in self.orders.all():
            total += order.total_amount
        return total
    
    @property
    def guests_count(self):
        """Количество гостей за столом"""
        return self.guest_sessions.count()
    
    @property
    def active_orders_count(self):
        """Количество активных заказов"""
        return self.orders.exclude(status='paid').count()
