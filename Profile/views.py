from django.shortcuts import render, redirect
from .models import Profile
from Auth import views as SocialAuth
from Wall.models import Post
from django.conf import settings

# Create your views here.

def general(request, id):
    #request.session['access_token'] = "wohr4bbek62fu0m30yfsqenf6389a4vylbsbxyy47953dt3kedcpitzto89t1sg2pvr1tk6m2qdyebzstqxktsy88w0u9mdlxpo6a66"
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
        else:
            print('not allowed')
    else:
        print('not accepted')
    return redirect("/")