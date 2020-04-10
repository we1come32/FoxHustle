from django.shortcuts import render
from Auth import views as SocialAuth
from datetime import datetime, timedelta

# Create your views here.

def getOnlineStatistic(request):
    auth = SocialAuth.getUser(request)
    if auth.allow('admin'):
        from .models import OnlineStatistic
        stat = OnlineStatistic.objects.filter(start_time__gt=(datetime.now()-timedelta(days=3)))
        return render(
            request, 
            'admin/onlinestatistic.html', 
            {
                'user': auth.json(),
                'statistic': OnlineStatistic.objects.filter()
            }
        )
