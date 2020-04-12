from django.db import models
from datetime import datetime

# Create your models here.

class Promocode(models.Model):
    code = models.CharField(default = "", max_length = 24)
    action = models.CharField(default = "", max_length = 100)
    count = models.BigIntegerField(default = 0)
    used = models.BigIntegerField(default = 0)
    description = models.CharField(default = "", max_length = 4000)
    create_date = models.DateTimeField(default = datetime.now)
    end_date = models.DateTimeField(default = datetime.now)
    def use(self):
        if self.can_use():
            self.used += 1
            return {
                'result': True,
                'action': self.action,
            }
        return {
            'result': False,
            }
    def can_use(self):
        now = datetime.now()
        return ( self.used != self.count ) and (self.start_time <= now) and (now <= self.end_date)
