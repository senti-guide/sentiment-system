# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('student_home/', views.student_home_view, name='student_home'),
    path('student_evaluation/', views.student_evaluation_view, name='student_evaluation'),
    path('about/', views.about_view, name='about'),
    path('student_evaluation_form/', views.student_evaluation_form_view, name='student_evaluation_form'),
    path('admin_dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
