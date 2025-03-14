# Generated by Django 5.1.3 on 2024-11-21 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0002_remove_evaluation_choice_question_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='future_attendance',
            field=models.CharField(default='Yes', max_length=10),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='program',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q1',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q2',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q3',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q4',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q5',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q6',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q7',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q8',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='q9',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='suggestions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='year_level',
            field=models.CharField(default='1st Year', max_length=100),
        ),
    ]
