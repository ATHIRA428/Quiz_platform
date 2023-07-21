# Generated by Django 4.2.3 on 2023-07-19 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0011_remove_quizattempt_answers_useranswer_quiz_attempt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useranswer',
            name='is_correct',
        ),
        migrations.RemoveField(
            model_name='useranswer',
            name='quiz_attempt',
        ),
        migrations.AddField(
            model_name='quizattempt',
            name='answers',
            field=models.ManyToManyField(blank=True, related_name='quiz_attempts', to='quiz.useranswer'),
        ),
    ]
