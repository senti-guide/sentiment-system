# Generated by Django 5.1.3 on 2024-11-19 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evaluation',
            name='choice_question',
        ),
        migrations.RemoveField(
            model_name='evaluation',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='evaluation',
            name='course_year',
        ),
        migrations.RemoveField(
            model_name='evaluation',
            name='likert_answers',
        ),
        migrations.RemoveField(
            model_name='evaluation',
            name='student_email',
        ),
        migrations.RemoveField(
            model_name='evaluation',
            name='suggestions',
        ),
    ]
