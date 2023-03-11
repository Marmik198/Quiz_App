from django.shortcuts import render
import random, json
from django.contrib import messages
from django.core import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from .models import Quiz, Question, QuestionQuiz, Response


# Quiz Views
class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'quiz/quiz-list.html'
    context_object_name = "quizs"

class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quiz/quiz-detail.html'

# QuestionQuiz Views
@login_required
def question_quiz_view(request, pk):
    user = request.user
    quiz = Quiz.objects.filter(id=pk).first()

    responseData = Response.objects.filter(user=user, quiz=quiz)
    if responseData:
        messages.error(request, _('You have already attempted this test!'))
        return redirect('quiz_list')
    
    else:
        questionsData = QuestionQuiz.objects.filter(quiz=quiz)
        questions = []
        for i in questionsData:
            question = Question.objects.filter(id=i.question_id).first()
            questions.append(question)

        random.shuffle(questions)
        questions = questions[0:quiz.number_of_questions]
        
        questId = []
        for i in questions:
            questId.append(i.id)

        request.session['quiz'] = quiz.id  
        request.session['questions'] = questId  
        
        return render(request, "quiz/question-quiz.html", {'quiz':quiz, 'questions':questions})

def submit_form(request):
    user = request.user
    quiz = Quiz.objects.filter(id=request.session['quiz']).first()
    questions = request.session['questions']

    for i in range(quiz.number_of_questions):
        answer = request.POST.get(str(i + 1))
        answer = int(answer)
        question = Question.objects.filter(id=questions[i]).first()
        isCorrect = True if question.answer == answer else False 

        response = Response(user=user, quiz=quiz, question=question, response=answer, isCorrect=isCorrect)
        response.save()

    messages.success(request, _('Your test has been submitted successfully!'))
    return redirect('index')


# Quiz Result Views
class QuizResultListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'quiz/quiz-result-list.html'
    context_object_name = "quizs"
    
    def get_queryset(self):
        response = Response.objects.filter(user=self.request.user)
        quizset = {}
        for i in response:
            quizset[i.quiz_id] = i.quiz_id
        quizs = []
        for key in quizset:
            quizs.append(Quiz.objects.filter(id=key).first())
        return quizs

# Quiz Result View
@login_required
def result_quiz_view(request, pk):
    quiz = Quiz.objects.filter(id=pk).first()
    response = Response.objects.filter(user=request.user, quiz=quiz)

    marks_per_question = quiz.marks / quiz.number_of_questions

    marks = 0
    correct = 0
    questions = []

    for i in response:
        if (i.isCorrect):
            marks += marks_per_question
            correct += 1

        question = Question.objects.filter(id=i.question_id).first()
        questions.append([question, i.response, i.isCorrect])

    context = {
        'quiz':quiz, 
        'marks':marks,
        'correct':correct,
        'questions':questions, 
    }

    return render(request, 'quiz/question-result.html', context)