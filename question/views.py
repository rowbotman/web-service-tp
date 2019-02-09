from django.shortcuts import render, get_object_or_404, render_to_response
from django.shortcuts import HttpResponseRedirect, Http404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import admin, auth

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.db.models import Count, Value, CharField
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone

from django.views.generic import ListView, DetailView, TemplateView, RedirectView
from django.views.generic.base import ContextMixin

from question.models import Post, User, Answer, QuestionVote, LikeDislike
from question.forms import UserProfileForm, QuestionForm, QuestionForm2, AnswerForm
from question.forms import LoginForm, RegisterForm, EditForm
from faker import Faker

import json
 
from django.contrib.contenttypes.models import ContentType


fake = Faker()

def current_profile(user):
	if user.is_authenticated:
		return User.objects.get(pk=user.pk)
	return None

def paginate(objects_list, request):
	paginator = Paginator(objects_list, 25)
	page = request.GET.get('page')
	try:
		objects_page = paginator.page(page)
	except PageNotAnInteger:
		objects_page = paginator.page(1)
	except EmptyPage:
		bjects_page = paginator.page(paginator.num_pages)

	return objects_page, paginator

@csrf_protect
def login(request):
	if request.POST:
		form = LoginForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			user = auth.authenticate(
				username=data['username'],
				password=data['password']
			)
			if user is not None:
				auth.login(request, user)
				return redirect(request.GET.get('redirect_to', reverse('post_list')))
			form.add_error('username', "Wrong username or password")
	else:
		form = LoginForm()
	return render(request, 'registration/login.html', {'form': form})

def logout(request):
	auth.logout(request)
	return redirect(request.GET.get('redirect_to', reverse('post_list')))

def post_list(request):
	post_list = Post.objects.get_feed()
	posts, paginator = paginate(post_list, request)
	return render(request,
				 'question/question_list.html',
				 { 'posts' : posts, 'profile' : current_profile(request.user) }
				 ) #question/index.html', {'posts': posts})

def register(request):
    if request.POST:
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request)
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'registration/registration.html', {'form': form})


def tag(request, tag):
	questions_list = Post.objects.get_tag(tag)
	posts, paginator = paginate(questions_list, request)

	return render(request, 'question/tags.html', {
		'posts': posts,
		'tag': tag,
		'profile' : current_profile(request.user)})

def question_detail(request, pk):
	question = get_object_or_404(Post, pk=pk) #Post.objects.get(pk=question_id)
	answers = Answer.objects.filter(question=question)
	answers, paginator = paginate(answers, request)
	if request.POST:
		form = AnswerForm(request.POST)
		if form.is_valid():
			form.save(request.user, question)
			redirect_to = question.get_absolute_url()\
						+ '?page={}#form'.format(paginator.num_pages)
			return redirect(redirect_to)

	form = AnswerForm()
	return render(request, 'question/question_detail.html', {
		'post': question,
		'answers' : answers,
		'form' : form,
		'profile' : current_profile(request.user) 
		})

def question_new(request):
	if request.POST:
		form = QuestionForm(request.POST)
		if form.is_valid():
			question = form.save(request.user)
			return redirect('question_detail', pk=question.id)
	else:
		form = QuestionForm()
	is_hot = False
	return render(
		request,
		'question/ask.html',
		{'form': form, 'profile': current_profile(request.user), 'status' : is_hot},
	)

def hot(request):
	questions_list = Post.objects.get_hot()
	# questions_list = LikeDislike.objects.questions()
	questions, paginator = paginate(questions_list, request)
	is_hot = True
	return render(
		request,
		'question/question_list.html',
		{'posts': questions, 'profile': current_profile(request.user), 'status' : is_hot},
	)

def question_edit(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == "POST":
		form = QuestionForm2(request.POST, instance=post)
		print('QUESTION FORM: ',form, form.is_valid(), end='\n')
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			post.save()
			return redirect('question_detail', pk=post.id)
	else:
		form = QuestionForm2(instance=post)
	return render(request, 'question/question_edit.html', {'form': form})

def question_remove(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.user == post.author:
		post.delete()
	return redirect('post_list')



def user_profile(request, pk):
	if request.method == 'POST':
		form = UserProfileForm(request.POST, pk=request.user.pk)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/')
	else:
		user = request.user
		pk = user.pk
		form = UserProfileForm(pk=pk)

	args = {}
	args.update(request)

	args['form'] = form
	return render_to_response('user/user_detail.html',
		{'form': form, 'profile': get_object_or_404(User, pk=pk)})

@login_required(login_url='login', redirect_field_name='redirect_to')
def user_detail(request, pk):
	user = get_object_or_404(User, pk=pk)
	questions = Post.objects.filter(author=user)
	return render(
		request,
		'user/user_profile.html',
		{'posts' : questions, 'profile': user}
	)

@login_required(login_url='login', redirect_field_name='redirect_to')
def settings(request):
	if request.POST:
		form = EditForm(request.POST, request.FILES)
		if form.is_valid():
			form.save(request)
			return redirect('settings')
	else:
		form = EditForm()
	return render(
		request,
		'user/user_detail.html',
		{'form': form, 'profile': current_profile(request.user)}
	)


def user_auth(request):
	if request.method == 'POST':
		form = AuthForm(request.POST)
		if form.is_valid():
			form.save(commit=False)

			return redirect('question_detail', pk=post.pk)
	else:
		form = AuthForm()
	return render(request, 'question/login.html', {'form': form})


@login_required(login_url='login', redirect_field_name='redirect_to')
def like(request):
	if request.method == 'POST':
		value = int(request.POST.get('value'))
		pk = request.POST.get('pk')
		print(pk)
		question = Post.objects.get(pk=pk)
		try:
			like = question.likes.get(user=request.user)
			if like.value != value:
				question.rating += value * 2
				like.value = value
				like.save()
				question.save()
		except Like.DoesNotExist:
			like = Like(value=value, user=request.user, content_object=question)
			like.save()
			# question.rating += value
			question.save()
		response_data = {'result': question.rating}
		return HttpResponse(
			json.dumps(response_data),
			content_type='application/json'
		)
 
# @login_required(login_url='login', redirect_field_name='redirect_to')
class VotesView(View):
	model = None    # Модель данных - Статьи или Комментарии
	vote_type = None # Тип комментария Like/Dislike

	def post(self, request, pk):
		obj = self.model.objects.get(pk=pk)
		# GenericForeignKey не поддерживает метод get_or_create
		try:
			likedislike = LikeDislike.objects.get(content_type=ContentType.objects.get_for_model(obj),
												  object_id=obj.id, user=request.user)
			if likedislike.vote is not self.vote_type:
				likedislike.vote = self.vote_type
				likedislike.save(update_fields=['vote'])
				result = True
			else:
				likedislike.delete()
				result = False
		except LikeDislike.DoesNotExist:
			obj.votes.create(user=request.user, vote=self.vote_type)
			result = True

		obj.rating = obj.votes.sum_rating()
		return HttpResponse(
			json.dumps({
				"result": result,
				"like_count": obj.votes.sum_rating(),# obj.votes.likes().count() - obj.votes.dislikes().count(),
				"dislike_count":  obj.votes.sum_rating(),#obj.votes.likes().count() - obj.votes.dislikes().count(),
				"sum_rating": obj.votes.sum_rating(),
			}),
			content_type="application/json"
		)

class AnswerVotesView(View):
	model = None    # Модель данных - Статьи или Комментарии
	vote_type = None # Тип комментария Like/Dislike

	def post(self, request, pk):
		obj = self.model.objects.get(pk=pk)
		# GenericForeignKey не поддерживает метод get_or_create
		try:
			likedislike = LikeDislike.objects.get(content_type=ContentType.objects.get_for_model(obj),
												  object_id=obj.id, user=request.user)

			if likedislike.vote:
				likedislike.vote = self.vote_type
				likedislike.save(update_fields=['vote'])
				obj.is_active = False
				obj.save()
				result = True
			else:
				likedislike.delete()
				result = False
		except LikeDislike.DoesNotExist:
			obj.votes.create(user=request.user, vote=self.vote_type)
			question = Post.objects.get(pk=obj.question.pk)
			question.is_active = False
			question.save()
			result = True

		obj.rating = obj.votes.sum_rating()
		return HttpResponse(
			json.dumps({
				"result": result,
				"like_count":  obj.votes.likes().count() - obj.votes.dislikes().count(),
				"dislike_count":  obj.votes.likes().count() - obj.votes.dislikes().count(),
				"sum_rating": obj.votes.sum_rating(),
			}),
			content_type="application/json"
		)