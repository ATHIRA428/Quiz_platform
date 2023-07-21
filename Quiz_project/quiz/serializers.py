from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Quiz, Question, Choice, QuizAttempt, UserAnswer, Category

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')


class ChoiceViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']



class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionViewSerializer(serializers.ModelSerializer):
    choices = ChoiceViewSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']
class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)

        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)

        return question        



class QuizListSerializer(serializers.ModelSerializer):
    questions = QuestionViewSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['title','category','difficulty_level','id', 'questions',]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not representation['questions']:
            representation['questions'] = None
        return representation





class QuizCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ['id', 'user', 'quiz', 'score', 'timestamp']

class QuizSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')
    questions = QuestionSerializer(many=True)
    user_score = serializers.SerializerMethodField()
    user_answers = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'category', 'created_at', 'questions', 'user_score', 'user_answers']

    def get_questions(self, quiz):
        questions = quiz.questions.all()
        question_data = []
        for question in questions:
            choices = question.choices.all().values('text')
            question_data.append({
                'text': question.text,
                'choices': list(choices)
            })
        return question_data

    def get_user_score(self, quiz):
        user = self.context.get('user')
        if user is not None:
            try:
                quiz_attempt = QuizAttempt.objects.filter(quiz=quiz, user=user).latest('timestamp')
                return quiz_attempt.score
            except QuizAttempt.DoesNotExist:
                pass
        return None

    def get_user_answers(self, quiz):
        user = self.context.get('user')
        if user is not None:
            try:
                quiz_attempt = QuizAttempt.objects.filter(quiz=quiz, user=user).latest('timestamp')
                user_answers = {}
                for answer in quiz_attempt.answers.all():
                    user_answers[answer.question.id] = answer.choice.id
                return user_answers
            except QuizAttempt.DoesNotExist:
                pass
        return {}


class UserProfileSerializer(serializers.ModelSerializer):
    quizzes_created = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'quizzes_created']

    def get_quizzes_created(self, user):
        quizzes = Quiz.objects.filter(creator=user)
        return QuizSerializer(quizzes, many=True).data



class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionViewSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['title','category','difficulty_level','id', 'questions',]


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not representation['questions']:
            representation['questions'] = None
        return representation

class QuizTakingSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'category', 'questions']

    def create(self, validated_data):
        pass

class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['question', 'choice']

class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    creator = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'category', 'created_at', 'questions', 'creator', 'difficulty_level']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            choices_data = question_data.pop('choices')
            question = Question.objects.create(quiz=quiz, **question_data)

            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)

        return quiz
