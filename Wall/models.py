from django.db import models
from Profile.models import Profile as Pr
from datetime import datetime


class Post(models.Model):
	number = models.IntegerField()
	author = models.ForeignKey(Pr, on_delete = models.CASCADE)
	text = models.CharField(max_length=4000, default="")
	created_date = models.DateTimeField(default=datetime.now)
	published_date = models.DateTimeField(default=datetime.now)
	likes = models.ManyToManyField(Pr, related_name="liked_posts")
	original = models.CharField(max_length=100, default="")


file_types = [
	('PC','Picture',),
	('DC','Document',),
]


class Document(models.Model):
	type_doc = models.CharField(
		max_length=2,
		choices=file_types, 
		default="PC"
		)
	id = models.AutoField(primary_key=True)
	file = models.FileField(upload_to='photo/')
	access_key = models.CharField(max_length=18)
	slug = models.SlugField()


