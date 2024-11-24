# urls.py
from django.urls import path
from . import views
from .views import student_evaluation_form_view

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('student_home/', views.student_home_view, name='student_home'),
    path('student_evaluation/', views.student_evaluation_view, name='student_evaluation'),
    path('about/', views.about_view, name='about'),
    path('student_evaluation_form/<int:event_id>/', views.student_evaluation_form_view, name='student_evaluation_form'),
    path('submit_evaluation/<int:event_id>/', views.submit_evaluation_view, name='submit_evaluation'),
    path('admin_dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin_evaluation/', views.admin_evaluation_view, name='admin_evaluation'),
    path('admin_results/<int:event_id>/', views.admin_results_view, name='admin_results'),
    path('admin_about/', views.admin_about_view, name='admin_about'),
    path('logout/', views.logout_view, name='logout'),
]
