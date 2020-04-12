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
	def __add__(self, other):
		if type(self) == type(other):
			a = Permission()
			a.AuthAccess = min(self.AuthAccess, other.AuthAccess)
			a.AppsAccess = min(self.AppsAccess, other.AppsAccess)
			a.BugtrackerAccess = min(self.BugtrackerAccess, other.BugtrackerAccess)
			a.ExperienceAccess = min(self.ExperienceAccess, other.ExperienceAccess)
			a.GoodsAccess = min(self.GoodsAccess, other.GoodsAccess)
			a.GroupAccess = min(self.GroupAccess, other.GroupAccess)
			a.PaymentAccess = min(self.PaymentAccess, other.PaymentAccess)
			a.ProfileAccess = min(self.ProfileAccess, other.ProfileAccess)
			a.MessageAccess = min(self.MessageAccess, other.MessageAccess)
			a.SysAccess = min(self.SysAccess, other.SysAccess)
			return a
		return 0


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


class Notification(models.Model):
	id = models.AutoField(primary_key=True)
	action = models.CharField(default="", max_length=255)
	author = models.ForeignKey("Profile", on_delete=models.CASCADE)
	title = models.CharField(default="", max_length=40)
	description = models.CharField(default="", max_length=4000)
	unread = models.BooleanField(default=True)
	def read(self):
		if self.unread:
			self.unread = False
			return True
		return False


# Пользователь
class Profile(models.Model):
	id = models.AutoField(primary_key=True)
	online = models.DateTimeField(default=datetime.now)
	nickname = models.CharField(default="", max_length=20)
	verifery = models.BooleanField(default=False)
	subscriptions = models.ManyToManyField('Profile', related_name="subscribers", blank=True)
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
		return "Profile#{id}".format(id=self.id)
	def notify(self, description="", action="", title=""):
		tmp = Notification.objects.create()
		tmp.action = action
		tmp.description = description
		tmp.title = title
		tmp.author = self
		tmp.save()




