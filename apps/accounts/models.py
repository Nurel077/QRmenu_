"""
User models and authentication.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями.
    """
    
    class Role(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', _('Супер-администратор')
        OWNER = 'OWNER', _('Владелец ресторана')
        WAITER = 'WAITER', _('Официант')
        GUEST = 'GUEST', _('Гость')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST,
        verbose_name=_('Роль')
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон')
    )
    
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('Ресторан'),
        help_text=_('Ресторан, к которому привязан пользователь (для владельцев и официантов)')
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )
    
    is_active_waiter = models.BooleanField(
        default=False,
        verbose_name=_('Активный официант'),
        help_text=_('Находится ли официант на смене')
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
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_superadmin(self):
        """Проверка, является ли пользователь супер-администратором"""
        return self.role == self.Role.SUPERADMIN or self.is_superuser
    
    @property
    def is_owner(self):
        """Проверка, является ли пользователь владельцем ресторана"""
        return self.role == self.Role.OWNER
    
    @property
    def is_waiter(self):
        """Проверка, является ли пользователь официантом"""
        return self.role == self.Role.WAITER
    
    @property
    def is_guest(self):
        """Проверка, является ли пользователь гостем"""
        return self.role == self.Role.GUEST
    
    def has_restaurant_access(self, restaurant):
        """
        Проверка доступа пользователя к ресторану.
        """
        if self.is_superadmin:
            return True
        if self.restaurant_id == restaurant.id:
            return True
        return False


class GuestSession(models.Model):
    """
    Сессия гостя (для неавторизованных пользователей).
    Позволяет отслеживать заказы гостей без регистрации.
    """
    
    session_key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Ключ сессии')
    )
    
    guest_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Имя гостя')
    )
    
    table_session = models.ForeignKey(
        'tables.TableSession',
        on_delete=models.CASCADE,
        related_name='guest_sessions',
        verbose_name=_('Сессия столика')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Последняя активность')
    )
    
    class Meta:
        verbose_name = _('Сессия гостя')
        verbose_name_plural = _('Сессии гостей')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Guest: {self.guest_name or 'Аноним'} - Table {self.table_session.table.number}"
