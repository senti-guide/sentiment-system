from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import LoginForm, StudentRegistrationForm  # Import the registration form
#new import for admin evaluation
from django.shortcuts import render, redirect
from .models import Event, Evaluation, SentimentAnalysis

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

#STUDENT

@login_required
def student_home_view(request):
    return render(request, 'student_home.html')

@login_required
def student_evaluation_view(request):
    # Fetch all events
    events = Event.objects.all()

    # Add evaluation status for the logged-in user to each event
    for event in events:
        evaluation = Evaluation.objects.filter(event=event, student=request.user).first()
        event.evaluation_status = (
            "submitted" if evaluation and evaluation.is_submitted else
            "pending" if evaluation else
            "waiting"
        )

    return render(request, 'student_evaluation.html', {'events': events})


@login_required
def about_view(request):
    return render(request, 'about.html')

from django.shortcuts import get_object_or_404
from .models import Event

@login_required
def student_evaluation_form_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'student_evaluation_form.html', {'event_id': event_id, 'event_title': event.title})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Evaluation, Event
from .sentiment_model import predict_sentiment

@login_required
def submit_evaluation_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if the evaluation already exists for the logged-in user and event
    evaluation = Evaluation.objects.filter(event=event, student=request.user).first()
    
    # If an evaluation exists and it's already submitted, redirect to prevent resubmission
    if evaluation and evaluation.is_submitted:
        return redirect('student_evaluation')  # Redirect to another page if already submitted

    if request.method == 'POST':
        # Create a new evaluation if none exists
        if not evaluation:
            evaluation = Evaluation.objects.create(
                event=event,
                student=request.user,  # Automatically link to the logged-in user
            )
        
        # Update the evaluation fields
        evaluation.program = request.POST.get('program', '')
        evaluation.year_level = request.POST.get('year_level', '')
        evaluation.q1 = request.POST.get('q1', '')
        evaluation.q2 = request.POST.get('q2', '')
        evaluation.q3 = request.POST.get('q3', '')
        evaluation.q4 = request.POST.get('q4', '')
        evaluation.q5 = request.POST.get('q5', '')
        evaluation.q6 = request.POST.get('q6', '')
        evaluation.q7 = request.POST.get('q7', '')
        evaluation.q8 = request.POST.get('q8', '')
        evaluation.q9 = request.POST.get('q9', '')
        evaluation.future_attendance = request.POST.get('future_attendance', '')
        evaluation.comments = request.POST.get('comments', '')
        evaluation.suggestions = request.POST.get('suggestions', '')

        # Sentiment Analysis: Process comments and get sentiment label
        if evaluation.comments:  # Check if comments are not empty
            evaluation.sentiment_label = predict_sentiment(evaluation.comments)
        
        # Mark the evaluation as submitted
        evaluation.is_submitted = True
        
        # Save the updated evaluation
        evaluation.save()
        
        return redirect('student_evaluation')  # Redirect after submission
    
    # Render the evaluation form for GET requests
    return render(request, 'submit_evaluation.html', {'event': event})


def is_admin(user):
    return user.is_superuser or user.is_staff

#ADMIN

@user_passes_test(is_admin)
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')

@user_passes_test(is_admin)
def admin_about_view(request):
    return render(request, 'admin_about.html')

@user_passes_test(is_admin)
def admin_evaluation_view(request):
    if request.method == 'POST':
        # Handle event creation
        title = request.POST.get('event_title')
        date = request.POST.get('event_date')

        if title and date:
            Event.objects.create(title=title, date=date)
            # Redirect to prevent duplicate form submissions on refresh
            return redirect('admin_evaluation')  # Replace with your URL name if different

    # Fetch all events
    events = Event.objects.all()

    # Data for each event
    event_data = []

    for event in events:
        # Fetch evaluations related to this event
        evaluations = Evaluation.objects.filter(event=event)

        # Count total responses (evaluations)
        total_responses = evaluations.count()

        # Initialize counts for each sentiment type
        positive_count = 0
        neutral_count = 0
        negative_count = 0

        # Loop through evaluations and count sentiments
        for evaluation in evaluations:
            sentiment = evaluation.sentiment_label  # Using the sentiment_label directly

            if sentiment == 'Positive':
                positive_count += 1
            elif sentiment == 'Neutral':
                neutral_count += 1
            elif sentiment == 'Negative':
                negative_count += 1

        # Calculate sentiment distribution percentages
        if total_responses > 0:
            positive_percentage = round((positive_count / total_responses) * 100, 2)
            neutral_percentage = round((neutral_count / total_responses) * 100, 2)
            negative_percentage = round((negative_count / total_responses) * 100, 2)
        else:
            positive_percentage = neutral_percentage = negative_percentage = 0.00

        # Add event data to the list
        event_data.append({
            'id': event.id,  # Add the event ID here
            'title': event.title,
            'date': event.date,
            'total_responses': total_responses,
            'positive_percentage': positive_percentage,
            'neutral_percentage': neutral_percentage,
            'negative_percentage': negative_percentage,
        })

    # Pass the data to the template
    context = {
        'event_data': event_data,
    }

    return render(request, 'admin_evaluation.html', context)




from django.shortcuts import get_object_or_404, render
from django.db.models import Avg
from .models import Event, Evaluation

@user_passes_test(is_admin)
def admin_results_view(request, event_id):
    # Fetch the event
    event = get_object_or_404(Event, pk=event_id)

    # Get all evaluations for the event
    evaluations = Evaluation.objects.filter(event=event, is_submitted=True)

    # Data for the Comments table
    comments_data = [
        {"comment": evaluation.comments, "label": evaluation.sentiment_label or "No label"}  # Include sentiment_label
        for evaluation in evaluations if evaluation.comments
    ]

    # Calculate average scores for each question (Q1 to Q9)
    question_data = {
        f"q{i}": evaluations.aggregate(Avg(f"q{i}"))[f"q{i}__avg"] or 0 for i in range(1, 10)
    }

    # Data for Suggestions table
    suggestions = [evaluation.suggestions for evaluation in evaluations if evaluation.suggestions]

    # Data for Future Attendance (Pie chart)
    future_attendance_labels = ["Yes", "No", "Maybe"]
    future_attendance_counts = [
        evaluations.filter(future_attendance=label).count() for label in future_attendance_labels
    ]

    # Data for Program Distribution (Pie chart)
    program_data = evaluations.values("program").annotate(count=Avg("id"))
    program_labels = [entry["program"] for entry in program_data]
    program_counts = [entry["count"] for entry in program_data]

    # Data for Year Level Distribution (Pie chart)
    year_level_data = evaluations.values("year_level").annotate(count=Avg("id"))
    year_level_labels = [entry["year_level"] for entry in year_level_data]
    year_level_counts = [entry["count"] for entry in year_level_data]

    # Prepare context for rendering
    context = {
        "event": event,
        "comments_data": comments_data,
        "question_data": question_data,  # For bar charts (Questions 1-9)
        "suggestions": suggestions,

        # Future Attendance Pie Chart
        "future_attendance_labels": future_attendance_labels,
        "future_attendance_counts": future_attendance_counts,

        # Program Distribution Pie Chart
        "program_labels": program_labels,
        "program_counts": program_counts,

        # Year Level Distribution Pie Chart
        "year_level_labels": year_level_labels,
        "year_level_counts": year_level_counts,
    }

    return render(request, "admin_results.html", context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')
