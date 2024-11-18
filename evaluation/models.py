from django.db import models

# Event model
class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return self.title

# Evaluation model
class Evaluation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='evaluations')
    student_email = models.EmailField()
    course_year = models.CharField(max_length=100)
    likert_answers = models.JSONField()  # To store 9 Likert scale answers as a dictionary
    choice_question = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('Maybe', 'Maybe'), ('No', 'No')])
    comments = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    is_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"Evaluation for {self.event.title} by {self.student_email}"

# Sentiment model
class SentimentAnalysis(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='sentiments')
    positive_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    neutral_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    negative_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Sentiment Analysis for {self.evaluation.event.title}"
    
    
