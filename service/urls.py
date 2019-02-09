from django.conf.urls import include, url 
from django.contrib import admin
from django.urls import path
from question import views

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('question.urls')),
	path('profile/<int:pk>/', views.user_detail, name='user_detail'),
	path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.register, name='signup'),
    path('settings/', views.settings, name='settings'),
]
