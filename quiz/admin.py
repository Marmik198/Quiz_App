from django.contrib import admin
from .models import Question, Quiz, QuestionQuiz, Response

# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionQuiz)
admin.site.register(Quiz)
admin.site.register(Response)