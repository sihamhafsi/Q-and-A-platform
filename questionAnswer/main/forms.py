from django.forms import ModelForm
from .models import Answer,Question,CustomUser

class AnswerForm(ModelForm):
    class Meta:
        model=Answer
        fields=('detail',)
        labels = {'detail':'Your answer'}

class QuestionForm(ModelForm):
    class Meta:
        model=Question
        fields=('title','detail','tags')
        labels = {'detail':'Question','tags':'Categories'}
        
        



