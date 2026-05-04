from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='login.html'),
         name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(next_page='/'),
         name='logout'),
    path('register/', views.register_view, name='register'),

    path('accounts/profile/', views.profile_view, name='profile'),
]