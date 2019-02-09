from django.db import models
from django.utils import timezone
from django.conf import settings
from django.shortcuts import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db.models import Sum
import os

class QuestionManager(models.Manager):
	def get_hot(self):
		return self.order_by('-rating')

		
	def get_feed(self, order_by=None):
		# order_by = order_by or ('-created_date', '-votes')
		# return self.filter(is_active=True).order_by(*order_by)
		return self.order_by('-created_date')

	def get_tag(self, tag):
		return self.filter(tags__title=tag)	

class UserManager(BaseUserManager):
    def get_best(self, n_users):
        return self.order_by('-votes')[:n_users]

class User(AbstractUser):
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
	upload = models.ImageField(upload_to='uploads/%Y/%m/%d/', default='default.png')   # добавляем нулл, чтоб в базе явно определять есть ли картинка у поста или нет # upload_to - media root = абсолютный путь к папке с медиа данными
# разбиваем на дату для того, чтобы быстрее          '|`   просматривать дирректоррии
	username = models.CharField(max_length=40, unique=True, db_index=True, null=True)

	def image_path(self):
		if self.upload:
			return self.upload.url
		else:
			return os.path.join(settings.MEDIA_URL, "default.png")

class TagManager(models.Manager):
	def get_best(self, n_tags):
		return self.order_by('-n_posts')[:n_tags]


class Tag(models.Model):
	title = models.CharField(max_length=200, unique=True, verbose_name='tag name')
	n_posts = models.IntegerField(default=0, verbose_name='number of posts')
	objects = TagManager()

	def get_absolute_url(self):
		return reverse("tag", kwargs={'tag': self.title})

	def __str__(self):
		return self.title

class Like(models.Model):
	VALUES = (
		('UP', 1),
		('DOWN', -1),
	)
	value = models.SmallIntegerField(default=0, choices=VALUES)
	user = models.ForeignKey(User, related_name='liker', on_delete=models.CASCADE)

	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

class LikeDislikeManager(models.Manager):
	use_for_related_fields = True

	def likes(self):
		# Забираем queryset с записями больше 0
		return self.get_queryset().filter(vote__gt=0)

	def dislikes(self):
		# Забираем queryset с записями меньше 0
		return self.get_queryset().filter(vote__lt=0)

	def sum_rating(self):
		# Забираем суммарный рейтинг
		obj = self.get_queryset().aggregate(Sum('vote')).get('vote__sum')
		if obj is None:
			obj = 0
		return obj #self.get_queryset().aggregate(Sum('vote')).get('vote__sum')

	def questions(self):
		for post in self.all():
			print(post.vote)
		query = self.get_queryset().filter(content_type__model='questions').order_by('-questions__created_date')
		for post in query: 
			print(post)
		print("its all")
		return self.get_queryset().filter(content_type__model='questions').order_by('-questions__created_date')
 
	def answers(self):
		return self.get_queryset().filter(content_type__model='answers').order_by('-answers__created_date')

	def get_hot(self):
		return self.get_queryset().filter(content_type__model='questions').order_by('-questions__votes')

		# return super(LikeDislikeManager, self).get_queryset().filter(content_type__model='questions').order_by('-vote')

class LikeDislike(models.Model):
	LIKE = 1
	DISLIKE = -1
 
	VOTES = (
		(DISLIKE, 'UP'),
		(LIKE, 'DOWN'),
	)
 
	vote = models.SmallIntegerField(verbose_name="vote", choices=VOTES)
	user = models.ForeignKey(User, verbose_name="liker", on_delete=models.CASCADE)
 
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey()
	objects = LikeDislikeManager()



class Post(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	title = models.CharField(max_length=200)
	text = models.TextField()
	objects = QuestionManager()
	tags = models.ManyToManyField(to='Tag', related_name='questions')
	created_date = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True, verbose_name="Is active")
	votes = GenericRelation(LikeDislike, related_query_name='questions')
	rating = models.IntegerField(default=0, verbose_name='rating')

	def publish(self):
		self.published_date = timezone.now()
		self.save()


	def vote(self, user, value):
		vote = QuestionVote.objects.filter(question=self, author=user).first()
		if vote:
			vote.value = value
		else:
			vote = QuestionVote(question=self, author=user, value=value)
		vote.save()

	def get_answers(self, order_by=None):
		return self.answer_set.get_feed(order_by)

	def get_user(self):
		return User.objects.get(user=self.author)

	def get_absolute_url(self):
		return reverse('question_detail', kwargs={'pk': self.pk})

	def get_like_url(self):
		return reverse('like-toggle', kwargs={'pk' : self.pk })

	def get_api_like_url(self):
		return reverse('like-api-toggle', kwargs={'pk' : self.pk })

	def add_tags(self, tags):
		for tag in tags:
			if tag.pk:
				self.tags.add(tag)
			else:
				try:
					tag.save()
				except IntegrityError:
					t = Tag.objects.filter(title=tag.title).first()
					self.tags.add(t)
				else:
					self.tags.add(tag)

	def __str__(self):
		return self.title


class AnswerManager(models.Manager):
	def get_feed(self, order_by=None):
		order_by = order_by or ('-votes', 'created_date')
		return self.filter(is_active=True).order_by(*order_by)


class Answer(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	question = models.ForeignKey(Post, on_delete=models.CASCADE)
	created_date = models.DateTimeField(default=timezone.now)
	published_date = models.DateTimeField(blank=True, null=True)
	votes = GenericRelation(LikeDislike, related_query_name='answers')

	text = models.TextField(null=True)
	def publish(self):
		self.published_date = timezone.now()
		self.save()

	def get_like_url(self):
		return reverse('choose_answer', kwargs={'pk' : self.question.pk })

	def get_api_like_url(self):
		return reverse('answer-api-toggle', kwargs={'pk' : self.question.pk })
		
	def vote(self, user, value):
		vote = AnswerVote.objects.filter(question=self,
                                         author=user).first()
		if vote is None:
			AnswerVote(question=self, author=user, value=value).save()
		else:
			vote.value = value
			vote.save()
	
	def __str__(self):
		return self.text


class QuestionVote(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
								verbose_name='voter')
	question = models.ForeignKey(Post, on_delete=models.CASCADE, null=True,
								verbose_name='voted for')
	value = models.IntegerField(default=0, verbose_name='vote value')

	class Meta:
		unique_together = ('author', 'question')

		verbose_name = "answer"
		verbose_name_plural = "answers"

class AnswerVote(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
	value = models.IntegerField()

class Login(object):
	def __init__(self, arg):
		super(Login, self).__init__()
		self.arg = arg

# class CorrectAnswerManager(models.Manager):
# 	use_for_related_fields = True

# 	def sum_rating(self):
# 		# Забираем суммарный рейтинг
# 		return self.get_queryset().aggregate(Sum('vote')).get('vote__sum')


# class CorrectAnswer(models.Model):
# 	CORRECT = 1
# 	vote = models.SmallIntegerField(verbose_name="vote", choices=CORRECT)
# 	user = models.ForeignKey(User, verbose_name="author", on_delete=models.CASCADE)
 
# 	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
# 	object_id = models.PositiveIntegerField()
# 	content_object = GenericForeignKey()
# 	objects = CorrectAnswerManager()