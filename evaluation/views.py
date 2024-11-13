from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import LoginForm, StudentRegistrationForm  # Import the registration form

def welcome_view(request):
    return render(request, 'welcome.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Get email and password from the form
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                # Try to find the user by email
                user = User.objects.get(email=email)
                
                # Authenticate using the username from the retrieved user
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    # Log the user in
                    login(request, user)
                    
                    # Redirect based on user role
                    if user.is_superuser or user.is_staff:
                        return redirect('admin_dashboard')  # Ensure this name matches your URLs
                    else:
                        return redirect('student_home')  # Ensure this name matches your URLs
                else:
                    # Invalid credentials
                    messages.error(request, "Invalid email or password.")
            except User.DoesNotExist:
                # No user found with the provided email
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user with proper password hashing
            user = form.save(commit=False)  # Create user but don't save yet
            user.username = form.cleaned_data['email']  # Set username to email
            user.set_password(form.cleaned_data['password'])  # Hash the password (Changed from password1 to password)
            user.save()  # Save the user in the database

            # Display a success message
            messages.success(request, "Registration successful! You can now log in.")

            # Redirect to the login page
            return redirect('login')  # After registration, redirect to the login page

        else:
            # Form is invalid; display error messages
            messages.error(request, "There was an error with your registration. Please fix the errors below.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def student_home_view(request):
    return render(request, 'student_home.html')

@login_required
def student_evaluation_view(request):
    return render(request, 'student_evaluation.html')

def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin)
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')
