from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,ListAPIView,RetrieveAPIView
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from .models import User
from .models import Quiz, Question, Choice, QuizAttempt, UserAnswer, Category, QuizAttempt
from .serializers import (
    QuizSerializer,
    UserProfileSerializer,
    QuizTakingSerializer,
    QuizCategorySerializer,
    QuizCreateSerializer,
    QuestionSerializer,
    ChoiceSerializer,
    QuizAttemptSerializer,
    UserAnswerSerializer,
    QuizListSerializer,
    QuizDetailSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from .filters import QuizFilter
from django.db.models import Count, Avg, Max, Min

class QuizListView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuizFilter
    permission_classes = [IsAuthenticated]

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class QuizCategoryCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = QuizCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizCategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        quiz_categories = Category.objects.all()
        serializer = QuizCategorySerializer(quiz_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuizCreateView(generics.CreateAPIView):
    serializer_class = QuizCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class QuizDetailView(RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    permission_classes = [IsAuthenticated]

class QuizTakingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

        submitted_answers = request.data.get('answers', [])
        score = 0

        quiz_attempt = QuizAttempt.objects.create(quiz=quiz, user=request.user, score=score)

        for submitted_answer in submitted_answers:
            question_id = submitted_answer.get('question_id')
            choice_id = submitted_answer.get('choice_id')
            is_correct = False

            try:
                question = Question.objects.get(id=question_id)
                correct_choice = question.choices.get(is_correct=True)

                if choice_id == correct_choice.id:
                    is_correct = True
                    score += 1

            except Question.DoesNotExist:
                pass  

            user_answer = UserAnswer.objects.create(
                user=request.user,
                question=question,
                choice_id=choice_id,
                is_correct=is_correct
            )

            quiz_attempt.answers.add(user_answer)

        quiz_attempt.score = score
        quiz_attempt.save()

        return Response({'score': score, 'answers': submitted_answers}, status=status.HTTP_200_OK)


class QuizResultsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, quiz_id):
        quiz_attempts = QuizAttempt.objects.filter(quiz_id=quiz_id, user=request.user).order_by('-timestamp')

        if not quiz_attempts.exists():
            return Response({'error': 'Quiz attempt not found'}, status=status.HTTP_404_NOT_FOUND)

        latest_attempt = quiz_attempts.first()

        quiz = latest_attempt.quiz
        passing_score = quiz.passing_score  

        score = latest_attempt.score
        is_passed = score >= passing_score and score!=0 

        result_data = {
            'score': score,
            'is_passed': is_passed,
        }

        return Response(result_data, status=status.HTTP_200_OK)






class QuizAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request):
        total_quizzes = Quiz.objects.count()
        total_quiz_takers = QuizAttempt.objects.values('user').distinct().count()
        average_quiz_score = QuizAttempt.objects.aggregate(average_score=Avg('score'))['average_score']

        quiz_scores = QuizAttempt.objects.values('quiz').annotate(
            average_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score')
        )

        most_answered_question = UserAnswer.objects.values('question').annotate(
            answer_count=Count('question')
        ).order_by('-answer_count').first()
        least_answered_question = UserAnswer.objects.values('question').annotate(
            answer_count=Count('question')
        ).order_by('answer_count').first()

        analytics_data = {
            'quiz_overview': {
                'total_quizzes': total_quizzes,
                'total_quiz_takers': total_quiz_takers,
                'average_quiz_score': average_quiz_score,
            },
            'performance_metrics': quiz_scores,
            'question_statistics': {
                'most_answered_question': most_answered_question,
                'least_answered_question': least_answered_question,
            }
        }

        return Response(analytics_data, status=status.HTTP_200_OK)

#USER MANAGEMENT BY ADMIN
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] 

class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  

class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]








