"""
Payment models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import uuid


class Payment(models.Model):
    """
    Модель платежа.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Ожидает оплаты')
        PROCESSING = 'processing', _('Обрабатывается')
        COMPLETED = 'completed', _('Завершен')
        FAILED = 'failed', _('Ошибка')
        CANCELLED = 'cancelled', _('Отменен')
        REFUNDED = 'refunded', _('Возвращен')
    
    class PaymentType(models.TextChoices):
        CASH = 'cash', _('Наличные')
        QR = 'qr', _('QR код')
        CARD = 'card', _('Карта')
        ONLINE = 'online', _('Онлайн')
    
    # Привязка к заказу или сессии столика
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('Заказ'),
        help_text=_('Оплата конкретного заказа')
    )
    
    table_session = models.ForeignKey(
        'tables.TableSession',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('Сессия столика'),
        help_text=_('Общая оплата за весь столик')
    )
    
    # Уникальный идентификатор платежа
    payment_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('ID платежа')
    )
    
    # Тип и статус
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.CASH,
        verbose_name=_('Тип оплаты')
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Статус')
    )
    
    # Суммы
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Сумма')
    )
    
    currency = models.CharField(
        max_length=10,
        default='KGS',
        verbose_name=_('Валюта')
    )
    
    # Информация о плательщике
    payer_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Имя плательщика')
    )
    
    payer_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Телефон плательщика')
    )
    
    payer_email = models.EmailField(
        blank=True,
        verbose_name=_('Email плательщика')
    )
    
    # Официант, принявший оплату
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments',
        verbose_name=_('Обработано')
    )
    
    # Данные транзакции (для онлайн-платежей)
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('ID транзакции'),
        help_text=_('ID транзакции от платежной системы')
    )
    
    payment_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Данные платежа'),
        help_text=_('Дополнительные данные от платежной системы')
    )
    
    # Возврат средств
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name=_('Сумма возврата')
    )
    
    refund_reason = models.TextField(
        blank=True,
        verbose_name=_('Причина возврата')
    )
    
    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата возврата')
    )
    
    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата завершения')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    
    # Заметки
    notes = models.TextField(
        blank=True,
        verbose_name=_('Примечания')
    )
    
    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Платежи')
        ordering = ['-created_at']
    
    def __str__(self):
        order_info = f"Заказ #{self.order.pk}" if self.order else f"Столик {self.table_session.table.number}"
        return f"Платеж {self.payment_id} - {order_info} ({self.amount} {self.currency})"
    
    def save(self, *args, **kwargs):
        # Генерация уникального ID платежа
        if not self.payment_id:
            self.payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def restaurant(self):
        """Получить ресторан"""
        if self.order:
            return self.order.restaurant
        elif self.table_session:
            return self.table_session.table.restaurant
        return None
    
    def complete_payment(self, user=None):
        """Завершить платеж"""
        from django.utils import timezone
        
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if user:
            self.processed_by = user
        self.save()
        
        # Обновить статус заказа
        if self.order:
            self.order.mark_as_paid()
    
    def fail_payment(self, reason=''):
        """Отметить платеж как неудачный"""
        self.status = self.Status.FAILED
        if reason:
            self.notes = f"{self.notes}\nОшибка: {reason}".strip()
        self.save()
    
    def refund_payment(self, amount=None, reason=''):
        """Вернуть средства"""
        from django.utils import timezone
        
        if amount is None:
            amount = self.amount
        
        self.status = self.Status.REFUNDED
        self.refund_amount = amount
        self.refund_reason = reason
        self.refunded_at = timezone.now()
        self.save()


class QRPaymentCode(models.Model):
    """
    QR коды для оплаты.
    """
    
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='qr_code',
        verbose_name=_('Платеж')
    )
    
    qr_code_image = models.ImageField(
        upload_to='payments/qr_codes/',
        blank=True,
        null=True,
        verbose_name=_('QR код')
    )
    
    qr_data = models.TextField(
        verbose_name=_('Данные QR кода'),
        help_text=_('URL или данные для QR кода оплаты')
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Срок действия')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    class Meta:
        verbose_name = _('QR код оплаты')
        verbose_name_plural = _('QR коды оплаты')
    
    def __str__(self):
        return f"QR код для платежа {self.payment.payment_id}"
    
    def generate_qr_code(self):
        """Генерация QR кода"""
        import qrcode
        from io import BytesIO
        from django.core.files import File
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'payment_qr_{self.payment.payment_id}.png'
        
        self.qr_code_image.save(filename, File(buffer), save=False)
        self.save()
    
    @property
    def is_expired(self):
        """Проверка истечения срока действия"""
        if not self.expires_at:
            return False
        
        from django.utils import timezone
        return timezone.now() > self.expires_at
