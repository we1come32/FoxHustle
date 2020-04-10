from django.db import models
from Profile.models import Profile
from datetime import datetime

# Create your models here.

class OnlineStatistic(models.Model):
    time = models.DateTimeField(default=datetime.now)

LoggingTypes = [
	('I','INFO',),
	('E','ERROR',),
	('W','WARN',),
	('D','DEBUG',),
]

class Logging(models.Model):
    time = models.DateTimeField(default=datetime.now)
    level = models.CharField(
		max_length=1,
		choices = LoggingTypes,
		default='US'
		)
    description = models.CharField(default="", max_length=4000)
    def __str__(self):
        return "{time}_{level}".format(level=self.level, time=self.time)