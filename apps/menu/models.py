"""
Menu models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class MenuCategory(models.Model):
    """
    Категория меню (Супы, Салаты, Основные блюда и т.д.)
    """
    
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='menu_categories',
        verbose_name=_('Ресторан')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Иконка'),
        help_text=_('Название иконки (например: utensils, pizza-slice)')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок сортировки'),
        help_text=_('Чем меньше число, тем выше категория в списке')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
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
        verbose_name = _('Категория меню')
        verbose_name_plural = _('Категории меню')
        ordering = ['restaurant', 'order', 'name']
        unique_together = ['restaurant', 'name']
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"
    
    @property
    def items_count(self):
        """Количество блюд в категории"""
        return self.items.filter(is_available=True).count()


class MenuItem(models.Model):
    """
    Позиция меню (блюдо).
    """
    
    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Категория')
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    
    image = models.ImageField(
        upload_to='menu/items/',
        blank=True,
        null=True,
        verbose_name=_('Фото блюда')
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Цена')
    )
    
    # Дополнительная информация
    cooking_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Время приготовления (мин)'),
        help_text=_('Примерное время приготовления в минутах')
    )
    
    calories = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Калорийность'),
        help_text=_('Калорийность на порцию')
    )
    
    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Вес (г)'),
        help_text=_('Вес порции в граммах')
    )
    
    # Характеристики блюда
    is_vegetarian = models.BooleanField(
        default=False,
        verbose_name=_('Вегетарианское')
    )
    
    is_vegan = models.BooleanField(
        default=False,
        verbose_name=_('Веганское')
    )
    
    is_spicy = models.BooleanField(
        default=False,
        verbose_name=_('Острое')
    )
    
    spicy_level = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(5)],
        verbose_name=_('Уровень остроты'),
        help_text=_('От 0 (не острое) до 5 (очень острое)')
    )
    
    is_chef_special = models.BooleanField(
        default=False,
        verbose_name=_('Рекомендация шефа')
    )
    
    is_popular = models.BooleanField(
        default=False,
        verbose_name=_('Популярное'),
        help_text=_('Часто заказываемое блюдо')
    )
    
    # Аллергены
    allergens = models.TextField(
        blank=True,
        verbose_name=_('Аллергены'),
        help_text=_('Перечислите аллергены через запятую')
    )
    
    # Наличие и статус
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Доступно'),
        help_text=_('Можно ли заказать блюдо сейчас')
    )
    
    stock_quantity = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Остаток'),
        help_text=_('Оставьте пустым для неограниченного количества')
    )
    
    # Сортировка
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок сортировки')
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
        verbose_name = _('Позиция меню')
        verbose_name_plural = _('Позиции меню')
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category.restaurant.name})"
    
    @property
    def restaurant(self):
        """Получить ресторан через категорию"""
        return self.category.restaurant
    
    @property
    def is_in_stock(self):
        """Проверка наличия на складе"""
        if self.stock_quantity is None:
            return True
        return self.stock_quantity > 0
    
    def decrease_stock(self, quantity=1):
        """Уменьшить остаток при заказе"""
        if self.stock_quantity is not None:
            self.stock_quantity -= quantity
            if self.stock_quantity < 0:
                self.stock_quantity = 0
            self.save(update_fields=['stock_quantity'])
    
    def get_tags(self):
        """Получить список тегов для блюда"""
        tags = []
        if self.is_vegetarian:
            tags.append('Вегетарианское')
        if self.is_vegan:
            tags.append('Веганское')
        if self.is_spicy:
            tags.append('Острое')
        if self.is_chef_special:
            tags.append('От шефа')
        if self.is_popular:
            tags.append('Популярное')
        return tags


class MenuItemOption(models.Model):
    """
    Опции для позиции меню (размер, дополнения и т.д.)
    Например: Пицца - Маленькая/Средняя/Большая
    """
    
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name=_('Позиция меню')
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название опции'),
        help_text=_('Например: Размер, Добавки')
    )
    
    choices = models.JSONField(
        verbose_name=_('Варианты выбора'),
        help_text=_('Список вариантов в формате: [{"value": "small", "label": "Маленькая", "price_modifier": 0}]')
    )
    
    is_required = models.BooleanField(
        default=False,
        verbose_name=_('Обязательная'),
        help_text=_('Необходимо ли выбрать опцию при заказе')
    )
    
    class Meta:
        verbose_name = _('Опция позиции меню')
        verbose_name_plural = _('Опции позиций меню')
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.name}"
