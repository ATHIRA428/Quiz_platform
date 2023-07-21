from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView, UserLoginView, UserLogoutView
from .views import (
    QuizListView,
    QuizDetailView,
    QuizAnalyticsView,
    QuizCategoryListView,
    QuizCreateView,
    QuizCategoryCreateView,
    UserProfileView,
    QuizTakingView,
    QuizResultsView,UserListView, 
    UserListView, 
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('logout/', UserLogoutView.as_view()),
    path('quizzes/', QuizListView.as_view()),
    path('quizzes/<int:pk>/', QuizDetailView.as_view()),
    path('quizzes/create/', QuizCreateView.as_view()),
    path('quiz-categories/', QuizCategoryListView.as_view()),
    path('quiz-categories/create/', QuizCategoryCreateView.as_view()),
    path('profile/', UserProfileView.as_view()),
    path('quizzes/<int:quiz_id>/take/', QuizTakingView.as_view()),
    path('quizzes/<int:quiz_id>/results/', QuizResultsView.as_view()),
    path('analytics/', QuizAnalyticsView.as_view()),
    path('users/', UserListView.as_view()),
    path('users/<int:pk>/', UserListView.as_view()),
    path('users/create/', UserListCreateView.as_view()),
    path('users/<int:pk>/update/', UserRetrieveUpdateDestroyView.as_view()),
    path('users/<int:pk>/delete/', UserRetrieveUpdateDestroyView.as_view()),
]
