"""
Order models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models import Sum, F


class Order(models.Model):
    """
    Модель заказа.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Ожидает подтверждения')
        CONFIRMED = 'confirmed', _('Подтвержден')
        PREPARING = 'preparing', _('Готовится')
        READY = 'ready', _('Готов')
        DELIVERED = 'delivered', _('Доставлен')
        PAID = 'paid', _('Оплачен')
        CANCELLED = 'cancelled', _('Отменен')
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('Наличные')
        QR = 'qr', _('QR код')
        CARD = 'card', _('Карта')
    
    # Привязка к сессии столика
    table_session = models.ForeignKey(
        'tables.TableSession',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Сессия столика')
    )
    
    # Привязка к гостю
    guest_session = models.ForeignKey(
        'accounts.GuestSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('Сессия гостя'),
        help_text=_('Кто из гостей сделал заказ')
    )
    
    guest_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Имя гостя'),
        help_text=_('Имя гостя для идентификации заказа')
    )
    
    # Официант
    waiter = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_orders',
        verbose_name=_('Официант'),
        help_text=_('Официант, подтвердивший заказ')
    )
    
    # Статус и способ оплаты
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Статус')
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name=_('Способ оплаты')
    )
    
    # Заметки
    notes = models.TextField(
        blank=True,
        verbose_name=_('Заметки'),
        help_text=_('Особые пожелания к заказу')
    )
    
    waiter_notes = models.TextField(
        blank=True,
        verbose_name=_('Заметки официанта')
    )
    
    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Время создания')
    )
    
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Время подтверждения')
    )
    
    ready_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Время готовности')
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Время доставки')
    )
    
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Время оплаты')
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Время отмены')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    
    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.pk} - {self.table_session.table} ({self.get_status_display()})"
    
    @property
    def restaurant(self):
        """Получить ресторан"""
        return self.table_session.table.restaurant
    
    @property
    def table(self):
        """Получить столик"""
        return self.table_session.table
    
    @property
    def subtotal(self):
        """Подсчет суммы без налогов и сервисного сбора"""
        total = self.items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or Decimal('0')
        return total
    
    @property
    def tax_amount(self):
        """Сумма налога"""
        restaurant = self.restaurant
        if restaurant.tax_rate > 0:
            return self.subtotal * (restaurant.tax_rate / 100)
        return Decimal('0')
    
    @property
    def service_charge_amount(self):
        """Сумма сервисного сбора"""
        restaurant = self.restaurant
        if restaurant.service_charge > 0:
            return self.subtotal * (restaurant.service_charge / 100)
        return Decimal('0')
    
    @property
    def total_amount(self):
        """Общая сумма заказа"""
        return self.subtotal + self.tax_amount + self.service_charge_amount
    
    @property
    def items_count(self):
        """Количество позиций в заказе"""
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    def confirm_order(self, waiter):
        """Подтверждение заказа официантом"""
        from django.utils import timezone
        
        self.waiter = waiter
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save()
    
    def mark_as_preparing(self):
        """Отметить заказ как готовящийся"""
        self.status = self.Status.PREPARING
        self.save()
    
    def mark_as_ready(self):
        """Отметить заказ как готовый"""
        from django.utils import timezone
        
        self.status = self.Status.READY
        self.ready_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        """Отметить заказ как доставленный"""
        from django.utils import timezone
        
        self.status = self.Status.DELIVERED
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_as_paid(self):
        """Отметить заказ как оплаченный"""
        from django.utils import timezone
        
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save()
    
    def cancel_order(self, reason=''):
        """Отменить заказ"""
        from django.utils import timezone
        
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        if reason:
            self.waiter_notes = f"{self.waiter_notes}\nПричина отмены: {reason}".strip()
        self.save()


class OrderItem(models.Model):
    """
    Позиция в заказе.
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Заказ')
    )
    
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('Позиция меню')
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Количество')
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена за единицу'),
        help_text=_('Цена на момент заказа')
    )
    
    # Выбранные опции (размер, дополнения и т.д.)
    selected_options = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Выбранные опции'),
        help_text=_('Выбранные опции для блюда')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Примечания'),
        help_text=_('Особые пожелания к блюду')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    class Meta:
        verbose_name = _('Позиция заказа')
        verbose_name_plural = _('Позиции заказов')
    
    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"
    
    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        # Сохранение цены на момент заказа
        if not self.price:
            self.price = self.menu_item.price
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """
    История изменения статусов заказа.
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Заказ')
    )
    
    status = models.CharField(
        max_length=20,
        choices=Order.Status.choices,
        verbose_name=_('Статус')
    )
    
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Изменено пользователем')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Примечания')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Время изменения')
    )
    
    class Meta:
        verbose_name = _('История статусов')
        verbose_name_plural = _('История статусов')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.order.pk} - {self.get_status_display()} ({self.created_at})"
