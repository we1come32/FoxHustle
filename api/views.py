from django.shortcuts import render
from random import randint
from django.utils import timezone
#import requests
from .models import *
from django.db.models import Q
import time
from .defaultFunctions import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

"""
  Open tokens:


"""

# Длина текста в посте
const.post.text.length.max = 8000
const.post.text.length.min = 0

# Длина названия поста
const.post.title.length.max = 100
const.post.title.length.min = 0

# Количество прикреплений
const.post.attachment.count.max = 10
const.post.attachment.count.min = 0

# Длина комментария
const.comment.length.max = 4000
const.comment.length.min = 0

# Длина сообщения
const.message.length.max = 4000
const.message.length.min = 4000

#Получения IP клиента
def getClientIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Установка активности страницы
def setActivity(request, auth):
    try:
        if type(auth) == AuthInfo:
            ip = getClientIp(request)
            profile = auth.profile
            profile.setOnline()
            act = historyActivity.objects.create(ip=ip,token=auth)
            act.save()
            profile.activity.add(act)
            profile.save()
            return True
    except Exception as e:
        fixError(e)
    return False

# Получение информации об ошибке по её номеру
def getErrorCode(code):
    if code == 2:
        error_text = "Not found app"
    elif code == 3:
        error_text = "Incorrect email or password"
    elif code == 4:
        error_text = "Not all parameter are sent"
    elif code == 5:
        error_text = "Incorrect parameters" 
    elif code == 6:
        error_text = "Incorrect mail"
    elif code == 7:
        error_text = "Not found this method"
    elif code == 8:
        error_text = "Please confirm the mail. Some functions are not available to you now. After confirmation, they are unlocked."
    elif code == 9:
        error_text = "Not found data with this params."
    elif code == 100:
        error_text = "Unknown error"
    elif code == 101:
        error_text = "Not found API version."
    else:
        error_text = "Sorry, system error. Try again later"
        code = 1
    data = {
        'error': {
            "error_code": code,
            "error_descriotion": error_text
        }
    }
    return data

# Генерация токена и авторизация пользователя в сети
def generate_token(app_id, profile):
    a = "qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM"
    l = len(a)
    while True:
        s = ""
        for i in range(20):
            n = randint(0,l-1)
            s += a[n]
        if len(AuthInfo.objects.filter(token=s))==0:
            if type(app_id) != App:
                app_id = App.objects.filter(app_id=app_id)[0]
            if type(profile) != Profile:
                profile = profile.profile
            AuthInfo.objects.create(auth_app=app_id, profile=profile, token=s, date=timezone.now())
            return s

# Генерация подтверждающего почту ключа
def generate_email_code(mail):
    a = "qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM"
    l = len(a)
    while True:
        s = ""
        for i in range(20):
            n = randint(0,l-1)
            s += a[n]
        if Email.objects.filter(confirm_code=s).count()==0:
            a = Email.objects.create(mail=mail, confirm_code=s)
            a.save()
            return a

# Авторизация по токену
def getProfileFromToken(access_token, request):
    if type(access_token)==str:
        if len(access_token)>0:
            auth = AuthInfo.objects.filter(token=access_token)
            data = getErrorCode(5)
            if auth.count()==1:
                data = getErrorCode(1)
                auth = auth[0]
                profile = auth.profile
                data = getErrorCode(1)
                if setActivity(request, auth):
                    return {
                        'flag': True,
                        'profile': profile
                    }
    return {
        'flag': False
    }

# Результат в виде JSON формате
def Return(request, data):
    return JsonResponse(data, safe=True)

# Получение списка данных из from_data по параметрам data
def getData(request, data):
    if (request.method == "GET"):
        from_data = request.GET
    else:
        from_data = request.POST
    result = {}
    for tmp in data:
        type_data = tmp[0]
        name = tmp[1]
        function = tmp[2]
        default_flag = tmp[3]
        default = tmp[4]
        try:
            tmp = from_data[name]
            if function(tmp):
                result[name] = type_data(tmp)
            elif default_flag:
                result[name] = default
            else:
                return {'flag': False, 'result': default}
        except:
            print("Not found {key}".format(key=name))
            print(from_data)
            if default_flag:
                result[name] = default
            else:
                return {'flag': False, 'result': default}
    return {'flag': True, 'result': result}



#
#  Fox Hustle v 1.0
#  API methods
#  Author: Ilya Kanyshev
#  Repositiry: 
#

# API v1.0
class FoxHustleAPI:
    @staticmethod
    def 1_1(request, method):
        """
            'wall.sendcomment': walls_sendComment,
            'profile.createbot': profile_createbot,
            'wall.removecomment': walls_removeComment,
            'messages.getconversations': messages_getConversations,
        """
        from .versions.1_1 import *
        methods = {
            'auth.login': auth_login,
            'auth.logout': auth_logout,
            'auth.register': auth_register,
            'auth.confirmemail': confirm_email,
            'profile.get': profile_get,
            'profile.setonline': profile_setOnline,
            'profile.setwidjet': widjet_set,
            'profile.delwidjet': widjet_del,
            'profile.unsubscribe': profile_unsubscribe,
            'profile.subscribe': profile_unsubscribe,
            'profile.find': profile_find,
            'wall.create': walls_new,
            'wall.repost': walls_repost,
            'wall.remove': walls_remove,
            'news.get': news,
            'messages.sendmessage': messages_send,
            'wall.like': walls_like,
            'wall.unlike': walls_unlike,
            'wall.sendcomment': walls_sendComment,
        }
        try:
            method = method.lower()
            if method in methods.keys():
                return methods[method](request)
            return Return(request, getErrorCode(7))
        except Exception as e:
            fixError(e)
            return Return(request, getErrorCode(1))


# Информация по методам
@csrf_exempt
def getMethod(request, method):
    need_params = [
        (str, 'v', lambda tmp: True, False, getErrorCode(4)),
        ]
    result = getData(request, need_params)
    data = result['result']
    if result['flag']:
        getparams = result['result']
        v = getparams['result']['v']
        v = ".".join(_ for _ in v)[:-1]
        version = {
            '1.1': FoxHustleAPI.1_1
        }
        try:
            return Render(request, version[v](render, method))
        except:
            pass
    # not found api version
    return Render(request, getErrorCode(101))



