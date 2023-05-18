from django.urls import path
from . import views
urlpatterns=[
    path('all_questions',views.all_questions,name='all-questions'),
    path('detail/<int:id>',views.detail,name='detail'),
    path('save-comment',views.save_comment,name='save-comment'),
   
    # Ask QUestion
    path('ask-question',views.ask_form,name='ask-question'),
    path('confirm',views.confirm,name='confirm'),
    # Tag Page
    path('tag/<str:tag>',views.tag,name='tag'),
    # Tags Page
    path('tags',views.tags,name='tags'),

    path('',views.home,name='home'),
    path('edit-question/<int:pk>', views.edit_question, name='edit_question'),
    
]