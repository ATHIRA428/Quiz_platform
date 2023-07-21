from django.contrib.auth.models import AbstractUser
from django.db import models
import django_filters
from django.core.validators import MaxValueValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Quiz(models.Model):
    DIFFICULTY_LEVEL_CHOICES = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )

    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes_created')
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_LEVEL_CHOICES, default='Medium')
    passing_score = models.PositiveIntegerField(default=4) 
    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class QuizFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='exact')
    difficultylevel = django_filters.CharFilter(lookup_expr='exact')
    datecreated = django_filters.DateFilter(lookup_expr='exact')

    class Meta:
        model = Quiz
        fields = ['title', 'category', 'difficultylevel', 'datecreated']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text



class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.user.username} - {self.question.text}"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    timestamp = models.DateTimeField(auto_now_add=True)
    answers = models.ManyToManyField(UserAnswer, related_name='quiz_attempts', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - Score: {self.score}"




































