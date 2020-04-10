from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Profile)
admin.site.register(FreezeProfile)
admin.site.register(BlockProfile)
admin.site.register(Permission)