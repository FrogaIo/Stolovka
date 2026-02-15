from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import User as CustomUser, Allergy, Preference
from OrderService.models import Order, Payment, PurchaseRequest, Report
from MenuService.models import DailyMenu, Breakfast, Lunch, Product, MealPreparation
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import UserLoginForm
import json

def HeroZone(request):
    return render(request, 'HeroZone.html')

def Register(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password2')
        role = request.POST.get('role', 'student')
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
                    password=password,
                    role=role
                )
                user1.save()

                auth_login(request, user)
                messages.success(request, f'Добро пожаловать, {username}! Регистрация прошла успешно.')
                return redirect('menu')

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
                    # Получаем роль пользователя
                    try:
                        custom_user = CustomUser.objects.get(email=email)
                        if custom_user.role == 'admin':
                            return redirect('admin_dashboard')
                        elif custom_user.role == 'chef':
                            return redirect('chef_dashboard')
                    except CustomUser.DoesNotExist:
                        pass
                    messages.success(request, f'Добро пожаловать, {user.username}!')
                    return redirect('menu')
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
    return redirect('hero_zone')

@login_required
def profile(request):
    """Профиль пользователя"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    allergies = Allergy.objects.filter(user=user)
    preferences = Preference.objects.filter(user=user)
    
    if request.method == 'POST':
        # Обновление данных профиля
        new_allergy = request.POST.get('allergy')
        if new_allergy:
            Allergy.objects.create(user=user, name=new_allergy)
            messages.success(request, f'Аллергия "{new_allergy}" добавлена')
            return redirect('profile')
    
    context = {
        'user': user,
        'allergies': allergies,
        'preferences': preferences,
        'balance': user.balance,
        'subscription': user.get_subscription_display() if user.subscription != 'none' else 'Нет'
    }
    return render(request, 'Profile.html', context)

@login_required
def delete_allergy(request, allergy_id):
    """Удаление аллергии"""
    allergy = get_object_or_404(Allergy, id=allergy_id)
    try:
        user = CustomUser.objects.get(email=request.user.email)
        if allergy.user == user:
            allergy.delete()
            messages.success(request, 'Аллергия удалена')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Ошибка')
    
    return redirect('profile')

@login_required
def make_payment(request):
    """Оплата питания"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_type = request.POST.get('payment_type', 'single')
        
        if not amount:
            messages.error(request, 'Укажите сумму')
            return render(request, 'make_payment.html', {'user': user})
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Некорректная сумма')
            return render(request, 'make_payment.html', {'user': user})
        
        # Создание платежа
        receipt_number = f"RCP-{timezone.now().strftime('%Y%m%d%H%M%S')}-{user.id}"
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            payment_type=payment_type,
            receipt_number=receipt_number,
            status='paid'
        )
        
        # Обновление баланса и подписки
        user.balance += amount
        
        if payment_type == 'subscription_week':
            user.subscription = 'week'
            user.subscription_end = timezone.now().date() + timedelta(days=7)
        elif payment_type == 'subscription_month':
            user.subscription = 'month'
            user.subscription_end = timezone.now().date() + timedelta(days=30)
        elif payment_type == 'subscription_quarter':
            user.subscription = 'quarter'
            user.subscription_end = timezone.now().date() + timedelta(days=90)
        
        user.save()
        
        messages.success(request, f'Платеж принят! Баланс: {user.balance}р. Номер квитанции: {receipt_number}')
        return redirect('profile')
    
    context = {
        'user': user,
        'current_balance': user.balance,
        'subscription_prices': {
            'week': 150,
            'month': 500,
            'quarter': 1300
        }
    }
    return render(request, 'make_payment.html', context)

@login_required
def order_meal(request):
    """Заказ питания (для ученика)"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    if user.role != 'student':
        messages.error(request, 'Только ученики могут делать заказы')
        return redirect('menu')
    
    if request.method == 'POST':
        meal_type = request.POST.get('meal_type')
        breakfast_id = request.POST.get('breakfast_id')
        lunch_id = request.POST.get('lunch_id')
        
        if meal_type == 'breakfast' and breakfast_id:
            breakfast = get_object_or_404(Breakfast, id=breakfast_id)
            Order.objects.create(
                user=user,
                meal_type='breakfast',
                breakfast=breakfast
            )
            messages.success(request, 'Завтрак заказан!')
        elif meal_type == 'lunch' and lunch_id:
            lunch = get_object_or_404(Lunch, id=lunch_id)
            Order.objects.create(
                user=user,
                meal_type='lunch',
                lunch=lunch
            )
            messages.success(request, 'Обед заказан!')
        
        return redirect('my_orders')
    
    today_menu = DailyMenu.objects.filter(week_day__icontains=timezone.now().strftime('%A')).first()
    
    context = {
        'user': user,
        'today_menu': today_menu,
        'balance': user.balance
    }
    return render(request, 'order_meal.html', context)

@login_required
def my_orders(request):
    """Мои заказы"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'orders': orders
    }
    return render(request, 'my_orders.html', context)

# ============== VIEWS ДЛЯ ПОВАРА ==============

@login_required
def chef_dashboard(request):
    """Панель управления поваром"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    if user.role != 'chef':
        messages.error(request, 'Доступ запрещен')
        return redirect('menu')
    
    # Сегодняшние заказы
    today = timezone.now().date()
    today_orders = Order.objects.filter(date=today).select_related('breakfast', 'lunch')
    
    # Готовые блюда
    prepared_meals = MealPreparation.objects.filter(ready_to_serve=True)
    
    # Остатки продуктов
    products = Product.objects.all()
    low_stock_products = products.filter(quantity__lt=models.F('reorder_level'))
    
    context = {
        'user': user,
        'today_orders': today_orders,
        'prepared_meals': prepared_meals,
        'products': products,
        'low_stock_products': low_stock_products,
        'orders_count': today_orders.count()
    }
    return render(request, 'chef_dashboard.html', context)

@login_required
def mark_received(request, order_id):
    """Отметить блюдо как полученное (для повара)"""
    order = get_object_or_404(Order, id=order_id)
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    if user.role != 'chef':
        messages.error(request, 'Доступ запрещен')
        return redirect('menu')
    
    order.mark_as_received()
    messages.success(request, f'Блюдо для {order.user.name} отмечено как полученное')
    return redirect('chef_dashboard')

@login_required
def manage_inventory(request):
    """Управление инвентарем (остатки, продукты)"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    if user.role != 'chef':
        messages.error(request, 'Доступ запрещен')
        return redirect('menu')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_purchase_request':
            product_name = request.POST.get('product_name')
            quantity = request.POST.get('quantity')
            reason = request.POST.get('reason')
            
            PurchaseRequest.objects.create(
                created_by=user,
                product_name=product_name,
                quantity=int(quantity),
                reason=reason
            )
            messages.success(request, f'Заявка на закупку "{product_name}" создана')
            return redirect('manage_inventory')
    
    products = Product.objects.all()
    low_stock = products.filter(quantity__lt=models.F('reorder_level'))
    
    context = {
        'user': user,
        'products': products,
        'low_stock': low_stock
    }
    return render(request, 'manage_inventory.html', context)

# ============== VIEWS ДЛЯ АДМИНИСТРАТОРА ==============

@login_required
def admin_dashboard(request):
    """Панель управления администратором"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    if user.role != 'admin':
        messages.error(request, 'Доступ запрещен')
        return redirect('menu')
    
    # Общая статистика
    total_users = CustomUser.objects.filter(role='student').count()
    total_payments = Payment.objects.aggregate(total=models.Sum('amount'))['total'] or 0
    today_orders = Order.objects.filter(date=timezone.now().date()).count()
    pending_requests = PurchaseRequest.objects.filter(status='pending').count()
    
    context = {
        'user': user,
        'total_users': total_users,
        'total_payments': total_payments,
        'today_orders': today_orders,
        'pending_requests': pending_requests
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def approve_purchases(request):
    """Согласование заявок на закупки"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    if user.role != 'admin':
        messages.error(request, 'Доступ запрещен')
        return redirect('menu')
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        purchase_req = get_object_or_404(PurchaseRequest, id=request_id)
        
        if action == 'approve':
            purchase_req.approve(user)
            messages.success(request, f'Заявка на "{purchase_req.product_name}" одобрена')
        elif action == 'reject':
            purchase_req.status = 'rejected'
            purchase_req.save()
            messages.success(request, f'Заявка на "{purchase_req.product_name}" отклонена')
        
        return redirect('approve_purchases')
    
    pending_requests = PurchaseRequest.objects.filter(status='pending').select_related('created_by')
    approved_requests = PurchaseRequest.objects.filter(status='approved').select_related('created_by', 'approved_by')
    
    context = {
        'user': user,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests
    }
    return render(request, 'approve_purchases.html', context)

@login_required
def statistics(request):
    """Статистика и отчеты"""
    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('menu')
    
    if user.role != 'admin':
        messages.error(request, 'Доступ запрещен')
        return redirect('menu')
    
    # Статистика платежей
    payments_data = Payment.objects.filter(status='paid').values('payment_type').annotate(
        count=models.Count('id'),
        total=models.Sum('amount')
    )
    
    # Статистика посещаемости
    attendance_data = Order.objects.values('date').annotate(count=models.Count('id')).order_by('-date')[:30]
    
    # Статистика по популярности блюд
    lunch_orders = Order.objects.filter(meal_type='lunch').exclude(lunch=None).values('lunch__main').annotate(count=models.Count('id')).order_by('-count')[:5]
    breakfast_orders = Order.objects.filter(meal_type='breakfast').exclude(breakfast=None).values('breakfast__first_dish').annotate(count=models.Count('id')).order_by('-count')[:5]
    
    context = {
        'user': user,
        'payments_data': payments_data,
        'attendance_data': attendance_data,
        'lunch_orders': lunch_orders,
        'breakfast_orders': breakfast_orders
    }
    return render(request, 'statistics.html', context)

from django.db import models