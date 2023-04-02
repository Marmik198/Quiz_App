from django.urls import path, include
from .views import QuizResultListView ,QuizDetailView, QuizListView
from . import views

urlpatterns = [
    path('', QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('results/', QuizResultListView.as_view(), name='quiz_result'),
    path('<int:pk>/results/', views.result_quiz_view, name='result_quiz'),
    path('<int:pk>/questions/', views.question_quiz_view, name='question_quiz'),
    path('submit-form/', views.submit_form, name='submit_form'),
]
