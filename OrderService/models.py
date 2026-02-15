from django.db import models
from django.utils import timezone
from datetime import timedelta
from UserService.models import User
from MenuService.models import Breakfast, Lunch

PAYMENT_STATUS = [
    ('pending', 'В ожидании'),
    ('paid', 'Оплачено'),
    ('cancelled', 'Отменено'),
]

MEAL_TYPE = [
    ('breakfast', 'Завтрак'),
    ('lunch', 'Обед'),
]

ORDER_STATUS = [
    ('ordered', 'Заказано'),
    ('received', 'Получено'),
    ('cancelled', 'Отменено'),
]

class Payment(models.Model):
    """Платежи учеников"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=50, choices=[
        ('single', 'Одноразовая'),
        ('subscription', 'Абонемент'),
        ('subscription_week', 'Абонемент неделя'),
        ('subscription_month', 'Абонемент месяц'),
        ('subscription_quarter', 'Абонемент квартал'),
    ])
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    receipt_number = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return f"Платеж {self.user.name} - {self.amount}р"

class Order(models.Model):
    """Заказы питания"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    date = models.DateField(auto_now_add=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE)
    breakfast = models.ForeignKey(Breakfast, on_delete=models.SET_NULL, null=True, blank=True)
    lunch = models.ForeignKey(Lunch, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='ordered')
    received_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def mark_as_received(self):
        self.status = 'received'
        self.received_time = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Заказ {self.user.name} - {self.date} ({self.meal_type})"

class PurchaseRequest(models.Model):
    """Заявки на закупку продуктов"""
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'chef'})
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()  # Количество в граммах или штуках
    unit = models.CharField(max_length=20, default='г')  # г, шт, л и т.д.
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидает одобрения'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('ordered', 'Заказано'),
        ('received', 'Получено'),
    ], default='pending')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='approved_requests', limit_choices_to={'role': 'admin'})
    approval_date = models.DateTimeField(null=True, blank=True)
    
    def approve(self, admin_user):
        self.status = 'approved'
        self.approved_by = admin_user
        self.approval_date = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Заявка: {self.product_name} ({self.quantity}{self.unit})"

class Report(models.Model):
    """Отчеты по питанию и затратам"""
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=[
        ('payments', 'Отчет по платежам'),
        ('attendance', 'Отчет по посещаемости'),
        ('expenses', 'Отчет по затратам'),
        ('statistics', 'Статистика питания'),
    ])
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'admin'})
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()  # JSON или просто текст с данными
    
    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"
