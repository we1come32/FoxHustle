from django.urls import path, include
from . import views
from django.contrib import admin
from django.http import HttpResponseRedirect
from api import views as api_views

url_host = "foxhustle.ru"

def splitUrl(request, url=""):
    global url_host
    urlpatterns = [
        ("login", views.login,),
        ("logout", views.logout,),
        ("register", views.register,),
        ("about", views.general,),
    ]
    url = url.split("/")
    for (urlpattern, function) in urlpatterns:
        if url[0] == urlpattern:
            return function(request, url="".join(_+"/" for _ in url[1:]))
    return HttpResponseRedirect("http://{url}/login".format(url=url_host))


def general(request, url=""):
    global url_host
    http_host = str(request.META.get('HTTP_HOST'))

    if url_host in http_host:
        subdomain = http_host.split(url_host)[0]
    else:
        subdomain = False
    keys = [
        #("api", api_views.general,),
        #("docs", docs.views.general,),
        #("longpool", longpool.views.general)
        ("user.", views.user,),
#        ("verifery.", views.confirm_,),
        ("", splitUrl, ),
    ]
    print(subdomain, request.session.get('access_token', 'none'))
    for (tmpSubDomain, function) in keys:
        if tmpSubDomain == subdomain:
            return function(request, url=url)
    #print(subdomain)
    return HttpResponseRedirect("http://{url}/login".format(url=url_host))

"""
urlpatterns = [
    path('login', views.login),
    path('register', views.register),
    path('restore', views.general),
    path('user/<str:url_user>', views.user),
    path('', views.general),
    path('no-cookies', views.no_cookies),
    path('logout', views.logout),
    path('pay/<str:data_url>', views.create_check),
]
"""
urlpatterns = [
    path('', general),
    path('<str:url>', general)
]