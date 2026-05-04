
from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),

    path('invite/create/', views.invite_create, name='invite_create'),
    path('invite/<uuid:token>/', views.invite_accept, name='invite_accept'),
    path('projects/<int:pk>/members/', views.manage_members, name='manage_members'),
    path('projects/<int:pk>/members/<int:user_id>/change-role/', views.member_change_role, name='member_change_role'),
    path('projects/<int:pk>/members/<int:user_id>/remove/', views.member_remove, name='member_remove'),
]