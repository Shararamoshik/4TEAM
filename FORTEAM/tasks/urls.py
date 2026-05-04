
from django.urls import path
from . import views

urlpatterns = [
    path('projects/<int:project_pk>/tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/change-status/', views.task_change_status, name='task_change_status'),
]