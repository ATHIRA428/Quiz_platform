# Generated by Django 4.2.3 on 2023-07-20 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0014_quiz_passing_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='passing_score',
            field=models.PositiveIntegerField(default=4),
        ),
    ]
