from django.db import models

# Create your models here.

class Lunch(models.Model):
    id = models.AutoField(unique=True, auto_created=True, primary_key=True)
    soup = models.CharField()
    main = models.CharField()
    salad = models.CharField()
    drink = models.CharField()

class Breakfast(models.Model):
    id = models.AutoField(unique=True, auto_created=True, primary_key=True)
    first_dish = models.CharField()
    drink = models.CharField()

class DailyMenu(models.Model):
    id = models.AutoField(unique=True, auto_created=True, primary_key=True)
    week_day = models.CharField(max_length=100)
    breakfast = models.ForeignKey(Breakfast, on_delete=models.CASCADE, related_name='morning')
    lunch = models.ForeignKey(Lunch, on_delete=models.CASCADE, related_name='afternoon')
