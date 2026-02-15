from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from UserService import views as UserViews
from MenuService import views as MenuViews

urlpatterns = [
    # Auth URLs
    path('', UserViews.HeroZone, name='hero_zone'),
    path('login/', UserViews.Login, name='login'),
    path('register/', UserViews.Register, name='register'),
    path('logout/', UserViews.logout, name='logout'),
    
    # Menu URLs
    path('menu/', MenuViews.home, name='menu'),
    path('menu/add/item/', MenuViews.add, name='add'),
    path('menu/item/lunch/<int:id>/', MenuViews.itemLunch, name='itemLunch'),
    path('menu/item/breakfast/<int:id>/', MenuViews.itemBreakfast, name='itemBreakfast'),
    
    # Student URLs
    path('profile/', UserViews.profile, name='profile'),
    path('payment/', UserViews.make_payment, name='make_payment'),
    path('order/', UserViews.order_meal, name='order_meal'),
    path('my-orders/', UserViews.my_orders, name='my_orders'),
    path('allergy/delete/<int:allergy_id>/', UserViews.delete_allergy, name='delete_allergy'),
    
    # Chef URLs
    path('chef/dashboard/', UserViews.chef_dashboard, name='chef_dashboard'),
    path('chef/mark-received/<int:order_id>/', UserViews.mark_received, name='mark_received'),
    path('chef/inventory/', UserViews.manage_inventory, name='manage_inventory'),
    
    # Admin URLs
    path('admin/dashboard/', UserViews.admin_dashboard, name='admin_dashboard'),
    path('admin/purchases/', UserViews.approve_purchases, name='approve_purchases'),
    path('admin/statistics/', UserViews.statistics, name='statistics'),
    
    # Django admin (placed after custom admin pages so custom /admin/* routes take precedence)
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
