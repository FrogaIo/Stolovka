from django.shortcuts import render

from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import User as CustomUser
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import  UserLoginForm
import threading

def HeroZone(request):
    return render(request, 'HeroZone.html')

def Register(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('Repeat_password')
        errors = []
        if not username or not email or not password or not password_confirm:
            errors.append('Все поля обязательны для заполнения.')
        if password != password_confirm:
            errors.append('Пароли не совпадают.')
        if password:
            if len(password) < 8:
                errors.append('Пароль должен содержать минимум 8 символов.')
            if not any(c.isalpha() for c in password):
                errors.append('Пароль должен содержать хотя бы одну букву.')
            if not any(c.isdigit() for c in password):
                errors.append('Пароль должен содержать хотя бы одну цифру.')
        if User.objects.filter(username=username).exists():
            errors.append('Пользователь с таким именем уже существует.')

        if User.objects.filter(email=email).exists():
            errors.append('Пользователь с таким email уже существует.')
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.save()

                user1 = CustomUser(
                    name=username,
                    email=email,
                    password=password
                )
                user1.save()

                auth_login(request, user)
                messages.success(request, f'Добро пожаловать, {username}! Регистрация прошла успешно.')
                return redirect('home')

            except Exception as e:
                messages.error(request, f'Ошибка при регистрации: {str(e)}')

    return render(request, 'Register.html')

def Login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Пожалуйста, заполните все поля.')
        else:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
    
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(request, f'Добро пожаловать, {user.username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Ваш аккаунт деактивирован.')
            else:
                messages.error(request, 'Неверный email или пароль.')
        
        form = UserLoginForm()
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


def logout(request):
    auth_logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('login')


@login_required
def home(request):
    return render(request, 'home.html', {'user': request.user})

