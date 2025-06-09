from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns: list = [
    path('', views.task_list, name='task_list'),
    path('add/', views.add_task, name='add_task'),
    path('edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('toggle/<int:pk>/', views.toggle_task, name='toggle_task'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
        ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
        ),
    path('register/', views.user_register, name='register'),
    path('upload/', views.upload_tasks_csv, name='upload_tasks_csv'),
    path('upload-txt/', views.upload_tasks_txt, name='upload_tasks_txt'),
    path('export/pdf/', views.export_tasks_pdf, name='export_tasks_pdf'),
    path('export/csv/', views.export_tasks_csv, name='export_tasks_csv'),

]