from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    
    # Авторизация
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API
    path('api/users/save/', views.save_user),
    path('api/users/', views.get_users),
    path('api/contracts/', views.get_contracts, name='contracts'),
]