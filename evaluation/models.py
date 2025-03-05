from django.db import models
from django.contrib.auth.models import User  # Import the User model

# Event model
class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    semester = models.CharField(
        max_length=20,
        choices=[
            ("1st Semester", "1st Semester"),
            ("2nd Semester", "2nd Semester"),
        ],
        null=True,  # Allow old events to have no semester initially
        blank=True
    )

    def __str__(self):
        return self.title
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    program = models.CharField(max_length=100, null=True, blank=True)
    year_level = models.CharField(max_length=100, default="1st Year")

    def __str__(self):
        return f"Profile of {self.user.username}"

# Evaluation model
class Evaluation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='evaluations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations')  # Link to User (student)
    program = models.CharField(max_length=100, null=True, blank=True)  # Added program field
    year_level = models.CharField(max_length=100, default="1st Year")  # Added year_level field
    q1 = models.PositiveIntegerField(default=1)  # Temporarily set default
    q2 = models.PositiveIntegerField(default=1)  # Temporarily set default
    q3 = models.PositiveIntegerField(default=1)  # Temporarily set default
    q4 = models.PositiveIntegerField(default=1)  # Temporarily set default
    q5 = models.PositiveIntegerField(default=1)  # Temporarily set default
    q6 = models.PositiveIntegerField(default=1)  # Temporarily set default
    q7 = models.PositiveIntegerField(default=1)  # Temporarily set default
    q8 = models.PositiveIntegerField(default=1)  # Temporarily set default
    q9 = models.PositiveIntegerField(default=1)  # Temporarily set default
    future_attendance = models.CharField(max_length=10, default="Yes")
    comments = models.TextField(null=True, blank=True)  # Optional feedback
    sentiment_label = models.CharField(max_length=20, null=True, blank=True)  # Sentiment label for the comment
    suggestions = models.TextField(null=True, blank=True)  # Optional suggestions
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'student')  # Ensure one evaluation per user per event

    def __str__(self):
        return f"Evaluation for {self.event.title} by {self.student.username}"


# Sentiment model
class SentimentAnalysis(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='sentiments')
    positive_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    neutral_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    negative_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Sentiment Analysis for {self.evaluation.event.title}"
    

    
    
