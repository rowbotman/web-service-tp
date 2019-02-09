from django.contrib import admin
#from .models import Post
#from django.contrib.auth import get_user_model
#from django.contrib.auth.admin import UserAdmin
from question import models
from question.models import User, Post

# admin.site.register([User, Post])
admin.site.register(models.Post)
admin.site.register(models.Answer)
admin.site.register(models.User)
admin.site.register(models.Tag)
admin.site.register(models.QuestionVote)
admin.site.register(models.AnswerVote)

#from .forms import CustomUserCreationForm, CustomUserChangeForm
# Register your models here.
#from .models import User

#User = get_user_model();
#class CustomUserAdmin(UserAdmin):
#    add_form = CustomUserCreationForm
#    form = CustomUserChangeForm
#    model = User
#    list_display = ['email', 'username',]

#admin.site.register(User, CustomUserAdmin)

#admin.site.register(Post)
#admin.site.register(Question)
#admin.site.register(Tags)
