from django.db import models
from datetime import datetime
from django.utils import timezone
from Profile.models import Profile, Permission

# Таблица с информацией об версиях API
class API_info(models.Model):
	name = models.CharField(max_length=5, default="")
	debug = models.BooleanField(default=True)
	start_date = models.DateTimeField(default=datetime.now)
	end_date = models.DateTimeField(default=datetime.now)
	slug = models.SlugField(default="")


# Информация о приложении для аутентификации
class AuthApp(models.Model):
	id = models.AutoField(primary_key=True)
	blocked = models.BooleanField(default=False)
	name = models.CharField(max_length=40, default="Unnamed app")
	blocked_date = models.DateTimeField(default=datetime.now)
	root = models.BooleanField(default=False)
	creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
	create_date = models.DateTimeField(default=datetime.now)
	perms = models.ForeignKey(Permission, on_delete=models.CASCADE)


# Ключи доступа
class AccessToken(models.Model):
	app = models.ForeignKey('AuthApp', on_delete=models.CASCADE)
	worked = models.BooleanField(default=True)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	access_token = models.CharField(max_length=255, default="")
	perms = models.ForeignKey(Permission, on_delete=models.CASCADE)
	create_date = models.DateTimeField(default=datetime.now)


# Ключи для допуска к збт
class AuthCode(models.Model):
	code = models.CharField(max_length=16, default="")
	confirm = models.BooleanField(default=False)


# Коды подтверждения
class ConfirmCode(models.Model):
	authInfoProfile = models.ForeignKey('AuthInfoProfile', on_delete=models.CASCADE)
	code = models.CharField(max_length=7)


# Заявки на восстановление страницы
class restorationApplication(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	create_date = models.DateTimeField(default=datetime.now)
	end_date = models.DateTimeField(default=datetime.now)
	solution = models.TextField(default="")
	status = models.IntegerField(default=0)
"""
			Status:
			0 - None answer
			1 - Wait answer from user
			2 - Accept
			3 - Rejected 
		"""


# Информация о пользователе
class AuthInfoProfile(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	email = models.EmailField()
	password = models.CharField(max_length=255, default="")
	created_date = models.DateTimeField(default=datetime.now)
