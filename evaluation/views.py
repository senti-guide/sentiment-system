from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .forms import LoginForm, StudentRegistrationForm  # Import the registration form
#new import for admin evaluation
from django.shortcuts import render, redirect
from .models import Event, Evaluation, SentimentAnalysis
from .models import Profile  # Ensure the Profile model is imported


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

            # Add the user to the 'students' group
            try:
                students_group = Group.objects.get(name='students')  # Retrieve the 'students' group
                user.groups.add(students_group)  # Add the user to the group
            except Group.DoesNotExist:
                # Log an error or create the group dynamically if it doesn't exist
                messages.error(request, "The 'students' group does not exist. Please contact the admin.")

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

#GOOGLE

def google_login_redirect(request):
    if request.user.is_authenticated:
        # Check if user is in the students group
        if request.user.groups.filter(name='students').exists():
            return redirect('student_home')  # Redirect to student dashboard
        elif request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')  # Redirect to admin dashboard
        else:
            # Handle unexpected cases
            return redirect('student_home')  # Default redirection
    return redirect('login')  # Fallback for unauthenticated users

from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(user_signed_up)
def add_user_to_students_group(sender, request, user, **kwargs):
    # Ensure the 'students' group exists
    group, created = Group.objects.get_or_create(name='students')
    # Add the user to the group if not already in it
    if not user.groups.filter(name='students').exists():
        user.groups.add(group)


#STUDENT

def is_student(user):
    return user.groups.filter(name='students').exists()

@login_required
@user_passes_test(is_student)
def student_home_view(request):
    if request.method == 'POST':
        # Process profile setup form
        program = request.POST.get('program')
        year_level = request.POST.get('year_level')

        if program and year_level:
            # Check if profile exists for the user, and create it if not
            user = request.user
            profile, created = Profile.objects.get_or_create(user=user)  # No need for signals

            # Update profile fields
            profile.program = program
            profile.year_level = year_level
            profile.save()

            # Redirect to avoid duplicate form submissions on refresh
            return redirect('student_home')  # Replace with your student_home URL name

    # Render the student home page
    return render(request, 'student_home.html')

@login_required
@user_passes_test(is_student)
def student_evaluation_view(request):
    # Get search and filter parameters
    search_query = request.GET.get("search", "").strip()
    filter_status = request.GET.get("status", "")
    filter_month = request.GET.get("month", "")
    filter_year = request.GET.get("year", "")
    filter_semester = request.GET.get("semester", "")

    # Start with all events
    events = Event.objects.all()

    # Apply search filter (case-insensitive search in event title)
    if search_query:
        events = events.filter(title__icontains=search_query)

    # Apply month filter
    if filter_month and filter_month != "all":
        events = events.filter(date__month=filter_month)

    # Apply year filter
    if filter_year and filter_year != "all":
        events = events.filter(date__year=filter_year)

    # Apply semester filter
    if filter_semester and filter_semester != "all":
        events = events.filter(semester=filter_semester)

    # Sort events by most recent date
    events = events.order_by('-date')

    # Add evaluation status for the logged-in user to each event
    for event in events:
        evaluation = Evaluation.objects.filter(event=event, student=request.user).first()
        event.evaluation_status = (
            "submitted" if evaluation and evaluation.is_submitted else
            "pending" if evaluation else
            "waiting"
        )

    # Apply status filter based on computed evaluation_status
    if filter_status and filter_status != "all":
        events = [event for event in events if event.evaluation_status == filter_status]

    # Extract unique months, years, and semesters for dropdowns
    unique_months = Event.objects.annotate(month=ExtractMonth('date')).values_list('month', flat=True).distinct()
    unique_years = Event.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    unique_semesters = Event.objects.values_list('semester', flat=True).distinct()

    month_choices = [(month, calendar.month_name[month]) for month in sorted(unique_months)]
    year_choices = sorted(unique_years, reverse=True)
    semester_choices = sorted(unique_semesters)

    context = {
        'events': events,
        "month_choices": month_choices,
        "year_choices": year_choices,
        "semester_choices": semester_choices,
    }

    return render(request, 'student_evaluation.html', context)




@login_required
@user_passes_test(is_student)
def about_view(request):
    return render(request, 'about.html')

from django.shortcuts import get_object_or_404
from .models import Event

@login_required
@user_passes_test(is_student)
def student_evaluation_form_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'student_evaluation_form.html', {'event_id': event_id, 'event_title': event.title, 'semester': event.semester,})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Evaluation, Event, Profile
from .sentiment_model import predict_sentiment

@login_required
@user_passes_test(is_student)
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
                # Fetch and store the student's profile info
                program=request.user.profile.program,
                year_level=request.user.profile.year_level,
            )
        
        # Update the evaluation fields
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






#ADMIN

def is_admin(user):
    return user.is_superuser or user.is_staff


from collections import Counter
from django.db.models import Count
from django.shortcuts import render
from .models import Evaluation, Event

from django.db.models import Count, Q, F, ExpressionWrapper, FloatField
from django.shortcuts import render
from .models import Evaluation, Event
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # Get all events
    events = Event.objects.all()

    # Prepare a list to hold event data with sentiment percentages
    event_data = []

    for event in events:
        evaluations = Evaluation.objects.filter(event=event)

        positive_count = evaluations.filter(sentiment_label='Positive').count()
        negative_count = evaluations.filter(sentiment_label='Negative').count()

        total_responses = evaluations.count()

        if total_responses > 0:
            positive_percentage = round((positive_count / total_responses) * 100, 2)
            negative_percentage = round((negative_count / total_responses) * 100, 2)
        else:
            positive_percentage = negative_percentage = 0.00

        event_data.append({
            'title': event.title,
            'positive_percentage': positive_percentage,
            'negative_percentage': negative_percentage,
        })

    # Sort and get the top 5 events
    sorted_positive_events = sorted(event_data, key=lambda x: x['positive_percentage'], reverse=True)[:5]
    sorted_negative_events = sorted(event_data, key=lambda x: x['negative_percentage'], reverse=True)[:5]

    # Sentiment breakdown by program (calculating percentages)
    sentiment_by_program = list(
        Evaluation.objects.values('program')
        .annotate(
            total_count=Count('id'),
            positive_count=Count('sentiment_label', filter=Q(sentiment_label='Positive')),
            neutral_count=Count('sentiment_label', filter=Q(sentiment_label='Neutral')),
            negative_count=Count('sentiment_label', filter=Q(sentiment_label='Negative'))
        )
    )

    # Convert counts to percentages
    for item in sentiment_by_program:
        total = item['total_count']
        item['positive_percentage'] = round((item['positive_count'] / total) * 100, 2) if total > 0 else 0.00
        item['neutral_percentage'] = round((item['neutral_count'] / total) * 100, 2) if total > 0 else 0.00
        item['negative_percentage'] = round((item['negative_count'] / total) * 100, 2) if total > 0 else 0.00

    # Sentiment breakdown by year level (calculating percentages)
    sentiment_by_year_level = list(
        Evaluation.objects.values('year_level')
        .annotate(
            total_count=Count('id'),
            positive_count=Count('sentiment_label', filter=Q(sentiment_label='Positive')),
            neutral_count=Count('sentiment_label', filter=Q(sentiment_label='Neutral')),
            negative_count=Count('sentiment_label', filter=Q(sentiment_label='Negative'))
        )
    )

    # Convert counts to percentages
    for item in sentiment_by_year_level:
        total = item['total_count']
        item['positive_percentage'] = round((item['positive_count'] / total) * 100, 2) if total > 0 else 0.00
        item['neutral_percentage'] = round((item['neutral_count'] / total) * 100, 2) if total > 0 else 0.00
        item['negative_percentage'] = round((item['negative_count'] / total) * 100, 2) if total > 0 else 0.00

    # Pass the data to the template
    context = {
        'positive_events': sorted_positive_events,
        'negative_events': sorted_negative_events,
        'sentiment_by_program': sentiment_by_program,
        'sentiment_by_year_level': sentiment_by_year_level,
    }

    return render(request, 'admin_dashboard.html', context)

from django.http import JsonResponse
from .models import Evaluation

def get_chart_data(request):
    # Get latest data dynamically from the database
    positive_events = Evaluation.objects.order_by('-positive_percentage')[:5]
    negative_events = Evaluation.objects.order_by('-negative_percentage')[:5]
    
    sentiment_by_program = Evaluation.objects.values('program').annotate(
        positive_percentage=Avg('positive_percentage'),
        neutral_percentage=Avg('neutral_percentage'),
        negative_percentage=Avg('negative_percentage')
    )

    sentiment_by_year_level = Evaluation.objects.values('year_level').annotate(
        positive_percentage=Avg('positive_percentage'),
        neutral_percentage=Avg('neutral_percentage'),
        negative_percentage=Avg('negative_percentage')
    )

    data = {
        'positive_events': list(positive_events.values('title', 'positive_percentage')),
        'negative_events': list(negative_events.values('title', 'negative_percentage')),
        'sentiment_by_program': list(sentiment_by_program),
        'sentiment_by_year_level': list(sentiment_by_year_level),
    }
    
    return JsonResponse(data)


# Word Cloud
from wordcloud import WordCloud, STOPWORDS
from django.http import HttpResponse
import matplotlib
import matplotlib.pyplot as plt
import io

# Set matplotlib to use the non-GUI Agg backend
matplotlib.use('Agg')  # Use a non-GUI backend (suitable for headless environments)

@user_passes_test(is_admin)
def generate_wordcloud_view(request):
    # Fetch all comments
    comments = Evaluation.objects.values_list('comments', flat=True)
    all_comments = " ".join(filter(None, comments))

    # Use built-in stopwords and add custom ones
    stopwords = set(STOPWORDS)
    custom_stopwords = {"event", "really", "much", "SSG", "especially", "time", "next", "lot"}  # Add your custom stopwords here
    stopwords.update(custom_stopwords)

    # Generate Word Cloud with stopwords
    wordcloud = WordCloud(width=800, height=400, background_color="white", stopwords=stopwords).generate(all_comments)
    
    # Save the image to a buffer
    buffer = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    # Return the generated image as a response
    return HttpResponse(buffer, content_type="image/png")

from allauth.socialaccount.models import SocialAccount

@user_passes_test(is_admin)
def admin_student_evaluation_view(request):
    # Get all students (not just those who evaluated)
    students = User.objects.filter(groups__name='students').order_by('email')

    # Get all events
    total_events = Event.objects.count()

    # Get filtering parameters from the request
    search_query = request.GET.get('search', '').strip().lower()
    filter_option = request.GET.get('filter', '')

    evaluations_data = []
    for student in students:
        evaluated_count = Evaluation.objects.filter(student=student, is_submitted=True).count()

        # Fetch UID from SocialAccount (if exists)
        social_account = SocialAccount.objects.filter(user=student).first()
        uid = social_account.uid if social_account else "N/A"  # Handle cases where no social account exists

        # Apply filtering
        if filter_option == 'submitted' and evaluated_count == 0:
            continue  # Skip students who have NOT submitted if filter is 'submitted'
        elif filter_option == 'not-submitted' and evaluated_count > 0:
            continue  # Skip students who HAVE submitted if filter is 'not-submitted'

        # Apply search filtering
        if search_query and search_query not in student.email.lower():
            continue  # Skip students that don't match search

        evaluations_data.append({
            'student': student,
            'evaluated_count': evaluated_count,
            'total_events': total_events,
            'uid': uid,  # Include UID in context
        })

    return render(request, 'admin_student_evaluation.html', {
        'evaluations_data': evaluations_data
    })




@user_passes_test(is_admin)
def admin_student_evaluated_events_view(request, student_id):
    student = User.objects.get(id=student_id)  # Get the student
    events = Event.objects.all().order_by('-date')  # Sort events by newest first

    evaluations_data = []
    
    for event in events:
        evaluation = Evaluation.objects.filter(student=student, event=event).first()
        
        if evaluation:
            status = "Submitted" if evaluation.is_submitted else "Pending"
        else:
            status = "Not Submitted"

        evaluations_data.append({
            'event': event,
            'date': event.date,  # Include event date
            'semester': event.semester,
            'status': status,
        })

    return render(request, 'admin_student_evaluated_events.html', {
        'student': student,
        'evaluations_data': evaluations_data
    })


@user_passes_test(is_admin)
def admin_about_view(request):
    return render(request, 'admin_about.html')

from django.db.models import Q
from django.db.models.functions import ExtractMonth, ExtractYear
import calendar

@user_passes_test(is_admin)
def admin_evaluation_view(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        event_title = request.POST.get("event_title")
        event_date = request.POST.get("event_date")
        event_semester = request.POST.get("event_semester")

        if event_id:
            event = get_object_or_404(Event, id=event_id)
            event.title = event_title
            event.date = event_date
            event.semester = event_semester
            event.save()
        else:
            Event.objects.create(
                title=event_title,
                date=event_date,
                semester=event_semester
            )
        return redirect("admin_evaluation")

    # Get search and filter parameters from the request
    search_query = request.GET.get("search", "").strip()
    filter_month = request.GET.get("month", "")
    filter_year = request.GET.get("year", "")
    filter_semester = request.GET.get("semester", "")

    # Start with all events
    events = Event.objects.all()

    # Apply search filter (case-insensitive search in event title)
    if search_query:
        events = events.filter(title__icontains=search_query)

    # Apply month filter
    if filter_month and filter_month != "all":
        events = events.filter(date__month=filter_month)

    # Apply year filter
    if filter_year and filter_year != "all":
        events = events.filter(date__year=filter_year)

    # Apply semester filter
    if filter_semester and filter_semester != "all":
        events = events.filter(semester=filter_semester)

    # Sort by date (most recent first)
    events = events.order_by('-date')

    # Extract unique months, years, and semesters for dropdowns
    unique_months = Event.objects.annotate(month=ExtractMonth('date')).values_list('month', flat=True).distinct()
    unique_years = Event.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    unique_semesters = Event.objects.values_list('semester', flat=True).distinct()

    month_choices = [(month, calendar.month_name[month]) for month in sorted(unique_months)]
    year_choices = sorted(unique_years, reverse=True)
    semester_choices = sorted(unique_semesters)

    # Process event data for sentiment distribution
    event_data = []
    for event in events:
        evaluations = Evaluation.objects.filter(event=event)
        total_responses = evaluations.count()

        positive_count = evaluations.filter(sentiment_label="Positive").count()
        neutral_count = evaluations.filter(sentiment_label="Neutral").count()
        negative_count = evaluations.filter(sentiment_label="Negative").count()

        if total_responses > 0:
            positive_percentage = round((positive_count / total_responses) * 100, 2)
            neutral_percentage = round((neutral_count / total_responses) * 100, 2)
            negative_percentage = round((negative_count / total_responses) * 100, 2)
        else:
            positive_percentage = neutral_percentage = negative_percentage = 0.00

        event_data.append({
            'id': event.id,
            'title': event.title,
            'date': event.date,
            'semester': event.semester,
            'total_responses': total_responses,
            'positive_percentage': positive_percentage,
            'neutral_percentage': neutral_percentage,
            'negative_percentage': negative_percentage,
        })

    context = {
        'event_data': event_data,
        "month_choices": month_choices,
        "year_choices": year_choices,
        "semester_choices": semester_choices,
    }

    return render(request, 'admin_evaluation.html', context)


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.db.models import Avg, Count
from .models import Event, Evaluation

@user_passes_test(is_admin)
def admin_results_view(request, event_id):
    # Fetch the event
    event = get_object_or_404(Event, pk=event_id)

    # Get all evaluations for the event
    evaluations = Evaluation.objects.filter(event=event, is_submitted=True).order_by('-id')

    # Data for the Comments table
    comments_data = [
        {"comment": evaluation.comments, "label": evaluation.sentiment_label or "No label"}
        for evaluation in evaluations if evaluation.comments
    ]

    # Data for Suggestions table
    suggestions_data = [evaluation.suggestions for evaluation in evaluations if evaluation.suggestions]

        # Handle pagination for Comments
    comments_page_number = request.GET.get("comments_page", 1)
    comments_paginator = Paginator(comments_data, 5)  # Show 5 comments per page
    try:
        comments_page = comments_paginator.page(comments_page_number)
    except PageNotAnInteger:
        comments_page = comments_paginator.page(1)  # Default to page 1 if not an integer
    except EmptyPage:
        comments_page = comments_paginator.page(comments_paginator.num_pages)  # Last page if out of range

    # Handle pagination for Suggestions
    suggestions_page_number = request.GET.get("suggestions_page", 1)
    suggestions_paginator = Paginator(suggestions_data, 5)  # Show 5 suggestions per page
    try:
        suggestions_page = suggestions_paginator.page(suggestions_page_number)
    except PageNotAnInteger:
        suggestions_page = suggestions_paginator.page(1)  # Default to page 1 if not an integer
    except EmptyPage:
        suggestions_page = suggestions_paginator.page(suggestions_paginator.num_pages)  # Last page if out of range


    # Calculate average scores for each question (Q1 to Q9)
    question_data = {
        f"q{i}": evaluations.aggregate(Avg(f"q{i}"))[f"q{i}__avg"] or 0 for i in range(1, 10)
    }

    # Data for Future Attendance (Pie chart)
    future_attendance_labels = ["Yes", "No", "Maybe"]
    future_attendance_counts = [
        evaluations.filter(future_attendance=label).count() for label in future_attendance_labels
    ]

    # Data for Program Distribution (Pie chart)
    program_data = (
        evaluations.values("program")
        .annotate(count=Count("id"))
        .order_by("program")
    )
    program_labels = [entry["program"] for entry in program_data]
    program_counts = [entry["count"] for entry in program_data]

    # Data for Year Level Distribution (Pie chart)
    year_level_data = (
        evaluations.values("year_level")
        .annotate(count=Count("id"))
        .order_by("year_level")
    )
    year_level_labels = [entry["year_level"] for entry in year_level_data]
    year_level_counts = [entry["count"] for entry in year_level_data]

    # Prepare context for rendering
    context = {
        "event": event,
        "comments_page": comments_page,
        "suggestions_page": suggestions_page,
        "question_data": question_data,
        "future_attendance_labels": future_attendance_labels,
        "future_attendance_counts": future_attendance_counts,
        "program_labels": program_labels,
        "program_counts": program_counts,
        "year_level_labels": year_level_labels,
        "year_level_counts": year_level_counts,
    }

    return render(request, "admin_results.html", context)

from django.shortcuts import get_object_or_404, redirect
from .models import Event

# View to delete an event
def delete_event(request, event_id):

    # Get the event object or 404 if it doesn't exist
    event = get_object_or_404(Event, id=event_id)

    # Delete the event
    event.delete()

    # Redirect to the event list page (admin_evaluation page)
    return redirect('admin_evaluation')



from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

def logout_view(request):
    # Log the user out of Django
    logout(request)

    # Clear the session
    request.session.flush()

    # Add a success message
    messages.success(request, "You have successfully logged out.")

    # Redirect to Google's logout URL
    google_logout_url = (
        "https://accounts.google.com/Logout"
        "?continue=https://appengine.google.com/_ah/logout"
        f"?continue={settings.LOGOUT_REDIRECT_URL}"
    )
    return redirect(google_logout_url)

