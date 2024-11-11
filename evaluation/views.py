from django.shortcuts import render

def welcome_view(request):
    return render(request, 'welcome.html')

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def home_view(request):
    return render(request, 'home.html')
