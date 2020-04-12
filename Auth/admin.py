from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(API_info)
admin.site.register(AuthApp)
admin.site.register(AccessToken)
admin.site.register(ConfirmCode)
admin.site.register(restorationApplication)
admin.site.register(AuthInfoProfile)

