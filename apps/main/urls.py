from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.decorators import login_required

app_name='main'

urlpatterns = [
    path('', views.main_index, name='selectDB'),
    path('login/', views.login_index, name='login'),
    path('userLogin/', views.user_login, name='userLogin'),
    path('selectDB/', views.main_index, name='selectDB'),
    path('logout/', views.user_logout, name='userLogout')
]