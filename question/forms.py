from django import forms
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from question.models import User, Tag
from question.models import Post, Answer
from io import BytesIO
from PIL import Image

#from django.contrib.auth import get_user_model

#User = get_user_model()

class AuthorForm(forms.Form):
    name = forms.CharField(max_length = 256)
    birthday = forms.DateField(widget = forms.Textarea)

    def clean_name(self):  # такие обработчики ошибок нужны каждому полю
        name = self.cleaned_data('name');
        if name == 'asd':
            raise forms.ValidationError("It's invalid")
        return name

    def clean(): # такие обработчики нужны самой форме. когда нужно провалидировать два поля. когда нужно проверить логику всей формы
        name = self.cleaned_data('name');
        birthday = self.cleaned_data('birthday')
        if True:
            raise forms.ValidationError("It's invalid")
        return name

    def save(self):
        User.objects.create(**self.cleaned_data) # 26 и 27 Ананалогичны
#       User.objects.create(                     #
#            name = self.cleaned_data['name']
#            birthday = self.cleaned_data['birthday'])
    class Meta:
        model = User
        fields = ("username",)

class LoginForm(forms.Form):
    username = forms.CharField(
        required=True
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput()
    )

class RegisterForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput
    )
    nickname = forms.CharField(
        required=True
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
    )
    repeat_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
    )
    avatar = forms.FileField(
        allow_empty_file=False,
        widget=forms.ClearableFileInput,
        required=False
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar is None:
            return None
        if 'image' not in avatar.content_type:
            raise forms.ValidationError('Invalid file type')
        return avatar

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email == "":
            return email
        if email.find('@') < 1 or len(email) < 3:
            raise forms.ValidationError('Invalid email')
        try:
            _ = User.objects.get(email=email)
            raise forms.ValidationError('User with the same email is exist')
        except User.DoesNotExist:
            return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname', '')
        if len(nickname) > 30:
            raise forms.ValidationError('Nickname is to be less than 30 symbols')
        if len(nickname) < 6:
            raise forms.ValidationError('Nickname is to be more than 5 symbols')
        try:
            _ = User.objects.get(username=nickname)
            raise forms.ValidationError('User with the same nickname is exist')
        except User.DoesNotExist:
            return nickname

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if len(password) < 6:
            raise forms.ValidationError('Password is to be more than 5 symbols')
        return password

    def clean_repeat_password(self):
        repeat_password = self.cleaned_data.get('repeat_password', '')
        password = self.cleaned_data.get('password', '')
        if repeat_password != password:
            raise forms.ValidationError('Field isn\'t equal to password')
        return repeat_password

    def save(self, request):
        cdata = self.cleaned_data
        user = User.objects.create_user(
            cdata['nickname'],
            cdata['email'],
            cdata['password']
        )
        user.save()
        # profile = User.objects.create(username=cdata['nickname'])
        # if 'avatar' in self.files:
        #     try:
        #         user.upload = Image.open(self.files['avatar'])
        #     except IOError:
        #         pass
        #     else:
        #         io = BytesIO()
        #         user.upload.thumbnail((256, 256), Image.ANTIALIAS)
        #         user.upload.save(io, format='JPEG', quality=100)
        #         self.instance.upload.save(f'{uuid4()}.jpg', io)
        # return self.instance

        if 'avatar' in request.FILES:
            user.upload = request.FILES['avatar']
        user.save()


    class Meta:
        model = Post
        fields = ('title', 'text', 'tags')

class EditForm(forms.Form):
    nickname = forms.CharField(
        required=False
    )
    email = forms.EmailField(
        widget=forms.EmailInput,
        required=False
    )
    avatar = forms.FileField(
        allow_empty_file=False,
        widget=forms.ClearableFileInput,
        required=False
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email == '':
            return email
        if email.find('@') < 1 or len(email) < 3:
            raise forms.ValidationError('Wrong email')
        try:
            _ = User.objects.get(email=email)
            raise forms.ValidationError('User with the same email is exist')
        except User.DoesNotExist:
            return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname', '')
        if nickname == '':
            return nickname
        if len(nickname) > 30:
            raise forms.ValidationError('Nickname is to be less than 30 symbols')
        if len(nickname) < 6:
            raise forms.ValidationError('Nickname is to be more than 5 symbols')
        try:
            _ = User.objects.get(username=nickname)
            raise forms.ValidationError('User with the same nickname is exist')
        except User.DoesNotExist:
            return nickname

    def clean(self):
        cleaned_data = super(EditForm, self).clean()
        if  cleaned_data['email'] == '' and cleaned_data['nickname'] == '' \
                and cleaned_data['avatar'] is None:
            msg = 'You need to feel at least one field'
            self.add_error('nickname', msg)
            self.add_error('email', msg)
            raise forms.ValidationError(msg, code='empty')
        if cleaned_data['avatar']:
            if 'image' not in cleaned_data['avatar'].content_type:
                self.add_error('avatar', "Invalid type of file")
        return cleaned_data

    def save(self, request):
        self.clean()
        cdata = self.cleaned_data
        user = auth.get_user(request)
        # profile = User.objects.get(pk=user.pk)
        if 'nickname' in cdata and cdata['nickname'] != '':
            user.username = cdata['nickname']
            # profile.nickname = cdata['nickname']
        if 'email' in cdata and cdata['email'] != '':
            user.email = cdata['email']
        print(request.FILES)
        if 'avatar' in request.FILES:
            user.upload = request.FILES['avatar']
        # profile.save()
        user.save()

class AnswerForm(forms.ModelForm):
    text = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40})
    )

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text.strip()) == 0:
            raise forms.ValidationError("Text of question is to be not empty")
        return text

    def save(self, user, question):
        answer = Answer(
            text=self.data['text'],
            author=user,
            question=question
        )
        answer.save()

    class Meta:
        model = Answer
        fields = ('text',)

class UserProfileForm(forms.ModelForm):
    def __init__(self, pk, *args, **kwargs):
        self.pk = pk
        super().__init__(args, kwargs)
    class Meta:
        model = User
        fields = '__all__'


class QuestionForm(forms.Form):
    title = forms.CharField(
        required=True
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 40})
    )
    tags = forms.CharField(
        required=True
    )

    # def __init__(self, author, *args, **kwargs):
    #     self.author = author
    #     super().__init__(args, kwargs)

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text.strip()) == 0:
            raise forms.ValidationError("Text of question is to be not empty")
        return text

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if len(title.strip()) == 0:
            raise forms.ValidationError("Title is to be not empty")
        return title

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        tag_list = tags.split()
        if len(tag_list) == 0:
            raise forms.ValidationError("Tags are to be not empty")
        for tag in tag_list:
            for sym in tag:
                if not sym.isalpha():
                    raise forms.ValidationError("You can use only letters in tags")

        return tags

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.author = self.author
        if commit:
            obj.save()
        return obj

    def save(self, user):
        data = self.cleaned_data
        question = Post.objects.create(
            title=data['title'],
            text=data['text'],
            author=user
        )

        tag_lables = data['tags'].split()
        for lable in tag_lables:
            tag, _ = Tag.objects.get_or_create(title=lable)
            question.tags.add(tag)
        question.save()
        return question

    class Meta:
        model = Post
        fields = ['text', 'title', 'tags',]


class QuestionForm2(forms.ModelForm):


    class Meta:
        model = Post
        fields = ['text', 'title', 'tags',]


#class CustomUserCreationForm(UserCreationForm):
#
#    class Meta(UserCreationForm):
#        model = User#get_user_model()
#        fields = ('username', 'email')
#
#class CustomUserChangeForm(UserChangeForm):
#
#    class Meta:
#        model = User#get_user_model()
#        fields = ('username', 'email')
