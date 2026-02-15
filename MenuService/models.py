from django.db import models

class Lunch(models.Model):
    id = models.AutoField(unique=True, auto_created=True, primary_key=True)
    soup = models.CharField(max_length=255)
    main = models.CharField(max_length=255)
    salad = models.CharField(max_length=255)
    drink = models.CharField(max_length=255)
    calories = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    contains_allergens = models.CharField(max_length=500, blank=True)  # Молоко, орехи и т.д.
    
    def __str__(self):
        return f"Обед: {self.main}"

class Breakfast(models.Model):
    id = models.AutoField(unique=True, auto_created=True, primary_key=True)
    first_dish = models.CharField(max_length=255)
    drink = models.CharField(max_length=255)
    calories = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    contains_allergens = models.CharField(max_length=500, blank=True)
    
    def __str__(self):
        return f"Завтрак: {self.first_dish}"

class DailyMenu(models.Model):
    id = models.AutoField(unique=True, auto_created=True, primary_key=True)
    week_day = models.CharField(max_length=100)
    breakfast = models.ForeignKey(Breakfast, on_delete=models.CASCADE, related_name='morning')
    lunch = models.ForeignKey(Lunch, on_delete=models.CASCADE, related_name='afternoon')
    
    def __str__(self):
        return f"Меню на {self.week_day}"

class Product(models.Model):
    """Продукты на складе"""
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()  # Количество в графаммах
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField()  # Уровень переупорядочения
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.quantity}г)"

class MealPreparation(models.Model):
    """Готовые блюда на кухне"""
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()  # Количество порций
    prepared_time = models.DateTimeField(auto_now_add=True)
    ready_to_serve = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.quantity} порций)"
