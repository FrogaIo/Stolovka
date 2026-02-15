from django.contrib import admin
from .models import User, Allergy, Preference, Comment, CommentLunch

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'balance', 'subscription')
    list_filter = ('role', 'subscription')
    search_fields = ('name', 'email')

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')
    search_fields = ('user__name', 'name')

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish_name', 'preference_type')
    list_filter = ('preference_type',)
    search_fields = ('user__name', 'dish_name')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'breakfast', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('author', 'text')

@admin.register(CommentLunch)
class CommentLunchAdmin(admin.ModelAdmin):
    list_display = ('author', 'lunch', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('author', 'text')
