from django.db import models
from django.utils import timezone
from datetime import datetime


# Разрешения
class Permission(models.Model):
	AuthAccess         = models.BooleanField(default=False)       # 32
	AppsAccess         = models.BooleanField(default=False)       # 64
	BugtrackerAccess   = models.BooleanField(default=False)       # 128
	ExperienceAccess   = models.BooleanField(default=False)       # 8
	GoodsAccess        = models.BooleanField(default=False)       # 256
	GroupAccess        = models.BooleanField(default=False)       # 4
	PaymentAccess      = models.BooleanField(default=False)       # 16
	ProfileAccess      = models.BooleanField(default=True)        # 1
	MessageAccess      = models.BooleanField(default=False)       # 2
	SysAccess          = models.BooleanField(default=False)       # 32768


types = [
	('AD','Admin',),
	('TS','Tester',),
	('US','User',),
	('MD','Moderator',),
	('HP','Helper',),
]


class FreezeProfile(models.Model):
	id = models.AutoField(primary_key=True)
	profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
	solution = models.CharField(max_length=4000)
	create_date = models.DateTimeField(default=datetime.now)
	to_date = models.DateTimeField(default=datetime.now)


class BlockProfile(models.Model):
	id = models.AutoField(primary_key=True)
	profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
	solution = models.CharField(max_length=4000)
	create_date = models.DateTimeField(default=datetime.now)


# Пользователь
class Profile(models.Model):
	id = models.AutoField(primary_key=True)
	online = models.DateTimeField(default=datetime.now)
	verifery = models.BooleanField(default=False)
	subscriptions = models.ManyToManyField('Profile', related_name="subscribers")
	userType = models.CharField(
		max_length=2,
		choices = types,
		default='US'
		)
	test = models.BooleanField(default=False)
	name = models.CharField(max_length=50, default="")
	surname = models.CharField(max_length=50, default="")
	patronymic = models.CharField(max_length=50, default="")
	perms = models.ForeignKey('Permission', on_delete=models.CASCADE)
	def __str__(self):
		return "Profile#{id}".format(self.id)




