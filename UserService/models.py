from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from MenuService.models import DailyMenu, Breakfast, Lunch

ROLE_CHOICES = [
    ('student', 'Ученик'),
    ('chef', 'Повар'),
    ('admin', 'Администратор'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'В ожидании'),
    ('paid', 'Оплачено'),
    ('cancelled', 'Отменено'),
]

SUBCRIPTION_CHOICES = [
    ('none', 'Без абонемента'),
    ('week', 'Неделя (5 дней)'),
    ('month', 'Месяц'),
    ('quarter', 'Квартал'),
]

class User(models.Model):
    id = models.AutoField(unique=True, auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subscription = models.CharField(max_length=20, choices=SUBCRIPTION_CHOICES, default='none')
    subscription_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def set_password(self, password: str) -> None:
        self.encrypted_password = make_password(password)

    def check_password(self, password: str) -> bool:
        return check_password(password, self.encrypted_password)
    
    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

class Allergy(models.Model):
    """Аллергии пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='allergies')
    name = models.CharField(max_length=100)  # Молоко, орехи, глютен и т.д.
    
    def __str__(self):
        return f"{self.user.name} - {self.name}"

class Preference(models.Model):
    """Предпочтения пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences')
    dish_name = models.CharField(max_length=200)
    preference_type = models.CharField(max_length=20, choices=[
        ('like', 'Нравится'),
        ('dislike', 'Не нравится'),
    ])
    
    def __str__(self):
        return f"{self.user.name} - {self.dish_name}"

class Comment(models.Model):
    breakfast = models.ForeignKey(Breakfast, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    created_at = models.DateTimeField(auto_now_add=True)

class CommentLunch(models.Model):
    lunch = models.ForeignKey(Lunch, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    created_at = models.DateTimeField(auto_now_add=True)