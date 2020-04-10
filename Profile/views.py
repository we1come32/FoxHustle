from django.shortcuts import render, redirect
from .models import Profile
from Auth import views as SocialAuth

# Create your views here.

def general(request, id):
    auth = SocialAuth.getUser(request)
    if auth.allow('user'):
        users = Profile.objects.filter(id=id)
        if users.count() == 1:
            user = users[0]
            return {
                'me': auth.json(),
                'user': user,
            }
    return redirect("/")