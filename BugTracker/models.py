from django.db import models
from Profile.models import Profile as Pr
from datetime import datetime

# Create your models here.

class Tester(models.Model):
	profile = models.ForeignKey(Pr, on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	


class Product(models.Model):
	creator = models.ForeignKey(Pr, on_delete=models.CASCADE, related_name="products")
	create_date = models.DateTimeField(default=datetime.now)
	managers = models.ManyToManyField('Tester', related_name="managered_products")
	testers = models.ManyToManyField('Tester', related_name="test_products")


report_severity = [
	('BL','Blocker',),
	('CR','Critical',),
	('MJ','Major',),
	('MN','Minor',),
	('TR','Trivial',),
]

report_priority = [
	('HG','High',),
	('MD','Medium',),
	('LW','Low',),
]

class Report(models.Model):
	id = models.AutoField(primary_key=True)
	deleted = models.BooleanField(default=False)
	product = models.ForeignKey('Product', on_delete=models.CASCADE)
	creator = models.ForeignKey('Tester', on_delete=models.CASCADE)
	text = models.TextField(max_length=4000)
	severity = models.CharField(max_length=2, choices=report_severity, default='TR')
	priority = models.CharField(max_length=2, choices=report_priority, default='LW')
	create_date = models.DateTimeField(default=datetime.now)
	update_date = models.DateTimeField(default=datetime.now)
	status = models.SmallIntegerField(default=0)
	replaied_user = models.ManyToManyField('Tester', related_name="replayed_reports")


class Comment(models.Model):
	author = models.ForeignKey('Tester', on_delete=models.CASCADE)
	text = models.TextField(max_length=4000)
	profuct = models.ForeignKey('Report', on_delete=models.CASCADE, related_name="comments")


