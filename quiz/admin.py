from django.contrib import admin
from .models import Question, Quiz, QuestionQuiz, Response, QuizResponse

# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionQuiz)
admin.site.register(Quiz)
admin.site.register(Response)
admin.site.register(QuizResponse)