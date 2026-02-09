from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from UserService import views as UserViews
from MenuService import views as MenuViews
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', UserViews.HeroZone, ),
    path('login/', UserViews.Login, name="login"),
    path('register/', UserViews.Register, name="register"),
    path('menu/', MenuViews.home, name="home"),
    path('menu/add/item', MenuViews.add, name="add"),
    path('menu/item/lucnh/<int:id>/', MenuViews.itemLunch, name="itemLunch"),
    path('menu/item/breakfast/<int:id>/', MenuViews.itemBreakfast, name="itemBreakfast"),
]

