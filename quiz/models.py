from django.db import models
from django.utils import timezone
from accounts.models import User

# Create your models here.
class Question(models.Model):
    question = models.CharField(max_length=250)
    answer = models.IntegerField()
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100, blank=True)
    option4 = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.question

class QuestionQuiz(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE, null=True)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, null=True)

class Quiz(models.Model):
    name = models.CharField(max_length=100)
    number_of_questions = models.IntegerField()
    marks = models.IntegerField(default=number_of_questions)
    questions = models.ManyToManyField("Question", through="QuestionQuiz")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Response(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=True)
    question = models.ForeignKey("Question", on_delete=models.CASCADE, null=True)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, null=True)
    response = models.IntegerField()
    isCorrect = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} Response'