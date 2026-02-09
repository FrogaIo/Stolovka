from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DailyMenu, Lunch, Breakfast
from UserService.models import User, Comment, CommentLunch

def home(request):
    today = timezone.now().date()
    days_since_monday = (today.weekday())  # 0=Пн 6=Вс
    monday = today - timedelta(days=days_since_monday)
    week_menu = []
    for i in range(7):
        day_date = monday + timedelta(days=i)
        day_name = day_date.strftime('%A')
        day_names_ru = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник', 
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }
        day_menu = DailyMenu.objects.filter(week_day__icontains=day_names_ru[day_name]).first()
        week_menu.append({
            'day_name': day_names_ru[day_name],
            'date': day_date.strftime('%d.%m'),
            'breakfast': day_menu.breakfast if day_menu else None,
            'lunch': day_menu.lunch if day_menu else None
        })
    
    context = {
        'week_menu': week_menu[:5]
    }
    return render(request, 'home.html', context)

def add(request):
    if request.method == 'POST':
        soupL = request.POST.get('soup')
        mainL = request.POST.get('main')
        saladL = request.POST.get('salad') 
        lunch_drink = request.POST.get('lunch_drink')

        first_dishB = request.POST.get('first_dish')
        breakfast_drink = request.POST.get('breakfast_drink')
        weekday = request.POST.get('weekday')

        if not all([soupL, mainL, saladL, lunch_drink, first_dishB, breakfast_drink, weekday]):
            return render(request, 'add.html', {'error': 'Заполните все поля'})
        
        
        breakfast = Breakfast.objects.create(
            first_dish=first_dishB,
            drink=breakfast_drink, 
        )
        
        lunch = Lunch.objects.create(
            soup=soupL,
            main=mainL,
            salad=saladL,
            drink=lunch_drink,
        )
        
        DailyMenu.objects.create(
            week_day=weekday,
            breakfast=breakfast,
            lunch=lunch,
        )
        return redirect('home')
    return render(request, 'add.html')


def itemLunch(request, id):
    lunch = get_object_or_404(Lunch, id=id)
    comments = CommentLunch.objects.filter(lunch=lunch)
    if request.method == 'POST':
        CommentLunch.objects.create(
            lunch=lunch,
            text=request.POST['comment'],
            author=request.POST.get('author', 'Аноним')
        )
        return redirect('itemLunch', id=id)
    
    return render(request, 'itemLunch.html', {
        'lunch': lunch,
        'comments': comments
    })

def itemBreakfast(request, id):
    breakfast = get_object_or_404(Breakfast, id=id)
    comments = Comment.objects.filter(breakfast=breakfast)
    if request.method == 'POST':
        Comment.objects.create(
            breakfast=breakfast,
            text=request.POST['comment'],
            author=request.POST.get('author', 'Аноним')
        )
        return redirect('itemBreakfast', id=id)
    
    return render(request, 'itemBreak.html', {
        'breakfast': breakfast,
        'comments': comments
    })