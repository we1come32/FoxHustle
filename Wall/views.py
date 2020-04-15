from django.shortcuts import render, redirect
from django.conf import settings
from Profile.models import Profile as Profiles
from Auth import views as SocialAuth
from .models import Post
from datetime import timedelta, datetime

# Create your views here.

def news(request):
    try:
        act = int(request.session.get('from'))
    except:
        act = 0
    auth = SocialAuth.getUser(request)
    if auth.accept():
        if auth.allow('WallAccess'):
            walls = Post.objects.filter(author__id__in=auth.user.subscriptions.all())
            walls = walls.order_by('-published_date')[act:act+10]
            return render(
                request,
                "Wall/main.html",
                {
                    'me': auth.json(),
                    'walls': walls,
                    'settings': settings.PAGE_SETTINGS,
                    'next_post': act+10
                }
            )
    return redirect("/")