from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register/', views.register_view, name='register'),  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_dashboard/', views.user_dashboard_view, name='user_dashboard'),
    path('my_applications/', views.my_applications_view, name='my_applications'),
    path('Apply_job/<int:job_id>/', views.Apply_job_view, name='Apply_job'),
    path('emp_dashboard/', views.emp_dashboard_view, name='emp_dashboard'),
    path('employer_applicants/<int:job_id>/', views.employer_applicants_view, name='employer_applicants'),
    path('post_job/', views.post_job_view, name='post_job'),
    path('edit_job/<int:id>/', views.edit_job_view, name='edit_job'),
    path('delete_job/<int:id>/', views.delete_job, name='delete_job'),
]
