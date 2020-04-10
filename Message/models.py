from django.db import models
from Profile.models import Profile as Pr
from datetime import datetime

# Create your models here.


class Chat(models.Model):
	id = models.AutoField(primary_key=True)
	creator = models.ForeignKey(Pr, on_delete=models.CASCADE)
	profiles = models.ManyToManyField(Pr, related_name="chats")
	messages = models.ManyToManyField('Message')


class Message(models.Model):
	id = models.AutoField(primary_key=True)
	author = models.ForeignKey(Pr, on_delete=models.CASCADE)
	text = models.CharField(max_length=8000)
	deleted = models.BooleanField(default=False)
	send_date = models.DateTimeField(default=datetime.now)


