# Generated by Django 5.1.3 on 2024-11-23 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0005_alter_evaluation_student_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='status',
            field=models.CharField(choices=[('waiting_for_response', 'Waiting for Response'), ('pending', 'Pending'), ('submitted', 'Submitted')], default='waiting_for_response', max_length=20),
        ),
    ]
