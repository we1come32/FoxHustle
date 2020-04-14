from django.shortcuts import render, redirect
from .models import Profile
from Auth import views as SocialAuth
from Wall.models import Post
from django.conf import settings
from datetime import timedelta, datetime

# Create your views here.

def general(request, id):
    #request.session['access_token'] = "wohr4bbek62fu0m30yfsqenf6389a4vylbsbxyy47953dt3kedcpitzto89t1sg2pvr1tk6m2qdyebzstqxktsy88w0u9mdlxpo6a66"
    try:
        act = request.session.get('act')
    except:
        act = ""
    auth = SocialAuth.getUser(request)
    if auth.accept():
        if auth.allow('ProfileAccess'):
            users = Profile.objects.filter(id=id)
            if users.count() == 1:
                user = users[0]
                user = user.json()
                user['walls'] = [post.json() for post in Post.objects.filter(author=users[0])]
                return render(
                    request,
                    "profile/main.html",
                    {
                        'me': auth.json(),
                        'user': user,
                        'settings': settings.PAGE_SETTINGS
                    }
                )
    return redirect("/")

def friends(request, page="main"):
    try:
        page = request.session.get('page')
        if page not in ['subscribers', 'main', 'subscriptions']:
            if page.lower() in ['subscribers', 'main', 'subscriptions']:
                page = page.lower()
    except:
        page = "main"
    if page in ['subscribers', 'main', 'subscriptions']:
        auth = SocialAuth.getUser(request)
        if auth.accept():
            if auth.allow('ProfileAccess'):
                friends = auth.user.subscriptions.filter(subscriptions__id=auth.user.id)
                return render(
                        request,
                        "profile/friends.html",
                        {
                            'me': auth.json(),
                            'page': page,
                            'friends': {
                                'all': friends,
                                'online': friends.filter(online__gte=datetime.now()-timedelta(minutes=10)),
                            },
                            'subscribers': auth.user.subscribers.all(),
                            'subscriptions': auth.user.subscriptions.all(),
                            'settings': settings.PAGE_SETTINGS
                        }
                    )
    return redirect("/")