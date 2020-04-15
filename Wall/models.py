from django.db import models
from Profile.models import Profile as Pr
from django.utils import timezone
from datetime import datetime, timedelta


def editTime(delta, start):
	if delta < timedelta(minutes=5):
		tmpOnline = "Только что"
	elif delta < timedelta(hours=5):
		tmpOnline = "{minutes} минут назад".format(minutes=delta.seconds//60) 
	elif delta < timedelta(days=1):
		tmpOnline = "{hours} часов назад".format(hours=delta.seconds//3600)
	else:
		day = start.strftime("%d")
		month = ["Января","Февраля","Марта","Апреля","Мая","Июня","Июля","Августа","Сентября","Октября","Ноября","Декабря"][int(start.strftime("%m"))-1]
		year = start.strftime("%Y")
		if delta < timedelta(days=335):
			tmpOnline = "{day} {month}".format(day=day, month=month)
		else:
			tmpOnline = "{day} {month} {year}".format(day=day, month=month, year=year)
	return tmpOnline


class Post(models.Model):
	number = models.IntegerField()
	author = models.ForeignKey(Pr, on_delete = models.CASCADE)
	title = models.CharField(default="", max_length=40)
	text = models.CharField(max_length=4000, default="")
	created_date = models.DateTimeField(default=datetime.now)
	published_date = models.DateTimeField(default=datetime.now)
	published = models.BooleanField(default=True)
	likes = models.ManyToManyField(Pr, related_name="liked_posts", blank=True)
	original = models.CharField(max_length=100, default="", null=True, blank=True)
	def json(self):
		try:
			tmp = timezone.now() - self.published_date
		except:
			tmp = datetime.now() - self.published_date
		return {
			'id': self.number,
			'title': self.title,
			'author': self.author.json(),
			'text': self.text,
			'published_date': editTime(tmp, self.published_date),
			'likes': self.likes.count(),
			'original': self.original,
		}


file_types = [
	('PC','Picture',),
	('DC','Document',),
]


class Document(models.Model):
	type_doc = models.CharField(
		max_length = 2,
		choices = file_types, 
		default = "PC"
		)
	id = models.AutoField(primary_key=True)
	file = models.FileField(upload_to='photo/')
	access_key = models.CharField(max_length=18)
	slug = models.SlugField()


