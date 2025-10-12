from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.decorators import login_required

app_name='main'

urlpatterns = [
    #path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    #path('', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('', views.login_index, name='login'),
    path('login/', views.login_index, name='login'),
    path('userLogin/', views.user_login, name='userLogin'),
    path('selectDB/', views.main_index, name='selectDB'),
]