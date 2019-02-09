from service import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.urls import path
from question import views
from question.models import Post, Answer, LikeDislike

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('hot/', views.hot, name='hot'),
    path('question/new/', views.question_new, name='question_new'),
    path('question/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('tag/<str:tag>', views.tag, name='tag'),

    path('api/article/<int:pk>/like/', views.VotesView.as_view(model=Post, vote_type=LikeDislike.LIKE),
    		name='question_like'),
    path('api/article/<int:pk>/dislike/', views.VotesView.as_view(model=Post, vote_type=LikeDislike.DISLIKE), 
    		name='question_dislike'),
    path('api/comment/<int:pk>/like/', views.AnswerVotesView.as_view(model=Answer, vote_type=LikeDislike.LIKE), 
    		name='answer_like'),
    path('api/comment/<int:pk>/dislike/', views.VotesView.as_view(model=Answer, vote_type=LikeDislike.DISLIKE), 
    		name='answer_like'),


    # path('like/', views.like, name='like'),
    path('question/<int:pk>/remove/', views.question_remove, name='question_remove'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
