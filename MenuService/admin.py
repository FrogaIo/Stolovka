from django.contrib import admin
from .models import Breakfast, Lunch, DailyMenu, Product, MealPreparation

@admin.register(Breakfast)
class BreakfastAdmin(admin.ModelAdmin):
    list_display = ('first_dish', 'drink', 'calories', 'price')
    search_fields = ('first_dish', 'drink')

@admin.register(Lunch)
class LunchAdmin(admin.ModelAdmin):
    list_display = ('main', 'soup', 'salad', 'drink', 'calories', 'price')
    search_fields = ('main', 'soup', 'salad')

@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ('week_day', 'breakfast', 'lunch')
    search_fields = ('week_day',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'price_per_unit', 'reorder_level', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('name',)

@admin.register(MealPreparation)
class MealPreparationAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'ready_to_serve', 'prepared_time')
    list_filter = ('ready_to_serve', 'prepared_time')
    search_fields = ('name',)
