from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from MenuService.models import DailyMenu, Breakfast, Lunch

class User(models.Model):
    id = models.AutoField(unique=True, auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def set_password(self, password: str) -> None:
        self.encrypted_password = make_password(password)

    def check_password(self, password: str) -> bool:
        return check_password(password, self.encrypted_password)

class Comment(models.Model):
    breakfast = models.ForeignKey(Breakfast, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CommentLunch(models.Model):
    lunch = models.ForeignKey(Lunch, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)