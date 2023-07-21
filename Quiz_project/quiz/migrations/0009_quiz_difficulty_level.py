# Generated by Django 4.2.3 on 2023-07-19 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_remove_quizattempt_answers_quizattempt_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='difficulty_level',
            field=models.CharField(choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default='Medium', max_length=10),
        ),
    ]
