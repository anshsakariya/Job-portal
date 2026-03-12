from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register/', views.register_view, name='register'),  
    path('login/', views.login_view, name='login'),
    path('user_dashboard/', views.user_dashboard_view, name='user_dashboard'),
    path('Apply_job/<int:job_id>/', views.Apply_job_view, name='Apply_job'),
    path('emp_dashboard/', views.emp_dashboard_view, name='emp_dashboard'),
    path('edit_job/<int:id>/', views.edit_job_view, name='edit_job'),
    path('delete_job/<int:id>/', views.delete_job, name='delete_job'),
]
