from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


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
	FriendsAccess      = models.BooleanField(default=True)        # 512
	WallAccess         = models.BooleanField(default=True)        # 1024
	MessageAccess      = models.BooleanField(default=False)       # 2
	SysAccess          = models.BooleanField(default=False)       # 32768
	DevLogsAccess      = models.BooleanField(default=False)       # 63536
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
			a.WallAccess = min(self.WallAccess, other.WallAccess)
			
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
	action = models.CharField(default="", max_length=255, null=True, blank=True)
	author = models.ForeignKey("Profile", on_delete=models.CASCADE)
	title = models.CharField(default="", max_length=40)
	description = models.CharField(default="", max_length=4000)
	unread = models.BooleanField(default=True)
	def read(self):
		print(self.unread)
		if self.unread:
			self.unread = False
			self.save()
			return True
		return False
	def json(self):
		return {
			'id': self.id,
			'action': self.action,
			'author': self.author.json(),
			'title': self.title,
			'description': self.description,
			'unread': self.unread,
		}

# Пользователь
class Profile(models.Model):
	id = models.AutoField(primary_key=True)
	img = models.CharField(default="/image/default.png", max_length=100)
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
	patronymic = models.CharField(max_length=50, default="", null=True, blank=True)
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
	def json(self):
		delta = timezone.now()-self.online
		if True:
			if delta < timedelta(minutes=5):
				online = "Онлайн"
			elif delta < timedelta(hours=5):
				online = "Был(а) в сети {minutes} минут назад".format(minutes=delta.seconds//60) 
			elif delta < timedelta(days=1):
				online = "Был(а) в сети {hours} часов назад".format(hours=delta.seconds//3600)
			else:
				day = self.online.strftime("%d")
				month = ["Января","Февраля","Марта","Апреля","Мая","Июня","Июля","Августа","Сентября","Октября","Ноября","Декабря"][int(self.online.strftime("%m"))-1]
				year = self.online.strftime("%Y")
				if delta < timedelta(days=335):
					online = "Был(а) в сети {day} {month}".format(day=day, month=month)
				else:
					online = "Был(а) в сети {day} {month} {year}".format(day=day, month=month, year=year)
		return {
			'id': str(self.id),
			'img': str(self.img),
			'online': online,
			'nickname': str(self.nickname),
			'verifery': bool(self.verifery),
			'userType': str(self.userType),
			'tester': bool(self.test),
			'surname': str(self.surname),
			'name': str(self.name),
			'subscribers': self.subscribers.count(),
			'subscriptions': self.subscriptions.count(),
			'friends': self.subscriptions.filter(subscriptions__id=self.id).count(),
		}
	def getNotifications(self):
		result = []
		a = Notification.objects.filter(author=self, unread=True)
		print("NOTIFICATION", a)
		for tmp in a:
			result += [tmp.json()]
			tmp.read()
		return result
	def online(self):
		try:
			self.online = datetime.now()
			self.save()
			return True
		except:
			return False

