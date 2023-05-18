from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse
from .models import Question,Answer,Comment
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import AnswerForm,QuestionForm
from django.db.models import Count
from django.contrib.auth.decorators import login_required
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
# Load the pre-trained spaCy model
nlp = spacy.load('en_core_web_md')

# Home Page
#@login_required(login_url='login')
def all_questions(request):
    if 'q' in request.GET:
        q=request.GET['q']
        quests=Question.objects.annotate(total_comments=Count('answer__comment')).filter(title__icontains=q).order_by('-id')
    else:
        quests=Question.objects.annotate(total_comments=Count('answer__comment')).all().order_by('-id')
    paginator=Paginator(quests,10)
    page_num=request.GET.get('page',1)
    quests=paginator.page(page_num)
    return render(request,'all-questions.html',{'quests':quests})

# Detail
def detail(request,id):
    quest=Question.objects.get(pk=id)
    tags=quest.tags.split(',')
    answers=Answer.objects.filter(question=quest)
    answerform=AnswerForm
    if request.method=='POST':
        answerData=AnswerForm(request.POST)
        if answerData.is_valid():
            answer=answerData.save(commit=False)
            answer.question=quest
            answer.user=request.user
            answer.save()
            messages.success(request,'Answer has been submitted.')
    return render(request,'detail.html',{
        'quest':quest,
        'tags':tags,
        'answers':answers,
        'answerform':answerform
    })

# Save Comment
def save_comment(request):
    if request.method=='POST':
        comment=request.POST['comment']
        answerid=request.POST['answerid']
        answer=Answer.objects.get(pk=answerid)
        user=request.user
        Comment.objects.create(
            answer=answer,
            comment=comment,
            user=user
        )
        return JsonResponse({'bool':True})


# Ask Form
def ask_form(request):
    form=QuestionForm
    if request.method=='POST':
        questForm=QuestionForm(request.POST)
        if questForm.is_valid():
            input_question = questForm.cleaned_data['detail']
            input_title = questForm.cleaned_data['title']
            input_tags = questForm.cleaned_data['tags']
            candidate_questions = [q.detail for q in Question.objects.all()]
            # Calculate the similarity scores only if there are candidate questions
            if candidate_questions:
                question_vectors = [nlp(question).vector for question in candidate_questions]
                input_question_vector = nlp(input_question).vector
                similarity_scores = cosine_similarity([input_question_vector], question_vectors)[0]
                # Find the index of the most similar question
                most_similar_index = np.argmax(similarity_scores)
                most_similar_question = candidate_questions[most_similar_index]
                score = similarity_scores[most_similar_index]
                if score > 0.7:
                    s_title = Question.objects.filter(detail=most_similar_question).values_list('title', flat=True).first()
                    s_tags = Question.objects.filter(title=s_title, detail=most_similar_question).values_list('tags', flat=True).first()
                    context = {'s_title':s_title,
                               'most_similar_question':most_similar_question,
                               's_tags':s_tags
                               }
                    confirm(request,input_title,input_question,input_tags)
                    return render(request,'confirm.html',context)

            # If there are no candidate questions or similarity score is below threshold, save the new question
            questForm=questForm.save(commit=False)
            questForm.user=request.user
            questForm.save()
            messages.success(request,'Question has been added.')

    return render(request,'ask-question.html',{'form':form})


def confirm(request,title,detail,tags):
    messages.info(request,"There is a similar question, are you sure you want to add your question?")
    context = {'title': title}
    context = {'detail': detail}
    context = {'tags': tags}
    form=QuestionForm
    if request.method=='POST':
        question = Question(title=title, detail=detail, tags=tags)
        question.user = request.user
        question.save()
        return render(request,'ask-question.html',{'form':form})

# Questions according to tag
def tag(request,tag):
    quests=Question.objects.annotate(total_comments=Count('answer__comment')).filter(tags__icontains=tag).order_by('-id')
    paginator=Paginator(quests,10)
    page_num=request.GET.get('page',1)
    quests=paginator.page(page_num)
    return render(request,'tag.html',{'quests':quests,'tag':tag})


# Tags Page
def tags(request):
    quests=Question.objects.all()
    tags=[]
    for quest in quests:
        qtags=[tag.strip() for tag in quest.tags.split(',')]
        for tag in qtags:
            if tag not in tags:
                tags.append(tag)
    # Fetch Questions
    tag_with_count=[]
    for tag in tags:
        tag_data={
            'name':tag,
            'count':Question.objects.filter(tags__icontains=tag).count()
        }
        tag_with_count.append(tag_data)
    return render(request,'tags.html',{'tags':tag_with_count})

def home(request):
    return render(request,'home.html')

@login_required
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk, user=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('detail', id=question.pk)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'edit_question.html', {'form': form})