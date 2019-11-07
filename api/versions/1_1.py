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


if True:
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


"""
def __t__e__s__t__(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'begin', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), True, 0),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                #
                #
                #
                # Your code
                #
                #
                #
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)
"""

# Вход по паре логин_пароль
def auth_login(request):
    global const
    try:
        need_params = [
            (int, 'app_id', lambda tmp: (tmp.isdigit()), False, getErrorCode(4)),
            (str, 'login', lambda tmp: (4<=len(tmp)<=20), False, getErrorCode(4)),
            (str, 'key', lambda tmp: (8<=len(tmp)<=20), False, getErrorCode(4)),
            (str, 'password', lambda tmp: (8<=len(tmp)<=20), False, getErrorCode(4)),
            ]
        result = getData(request, need_params)
        data = result['result']
        if result['flag']:
            params = result['result']
            data = App.objects.filter(app_id=params['app_id'], servise_key=params['key'])
            if data.count()>0:
                result = AuthLoginInfo.objects.filter(Q(email__mail=params['login']) | Q(profile__nickname=params['login']), password=params['password'])
                if len(result)>0:
                    data = {
                        "user": result[0].profile.Info(),
                        "app_id": params['app_id'],
                    }
                    if data['user']['deleted']==False:
                        result[0].profile.setOnline()
                        data["access_token"] = generate_token(params['app_id'], result[0])
                    data = {'response': data}
                else:
                    data = getErrorCode(3)
            else:
                data = getErrorCode(2)
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Выход
def auth_logout(request):
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'id', lambda tmp: (tmp.isdigit()), False, getErrorCode(4)),
            ]
        result = getData(request, need_params)
        data = result['result']
        if result['flag']:
            getparams = result['result']
            o = AuthInfo.objects.filter(token=getparams['access_token'])
            data = getErrorCode(5)
            if len(o)==1:
                if getparams['id'].isdigit():
                    if o[0].profile.id == int(getparams['id']):
                        o[0].delete()
                        data = {'response': 1}
                        data = str(data)
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Подтверждение почты
def confirm_email(request):
    global const
    return_message = "Email verification failed."
    try:
        if (request.method == "GET"):
            params = request.GET
        else:
            params = request.POST
        tmp = AuthLoginInfo.objects.filter(mail__confirm_code=params['hash'], profile__id=params['account_number'])
        if tmp[0].mail.confirm_code:
            return_message = "Mail \"{email}\" has been confirmed before."
        else:
            tmp[0].mail.confirm_code = True
            tmp[0].mail.save()
            return_message = "Mail \"{email}\" successfully confirmed!"
    except Exception as e:
        pass
    return Return(request, return_message)

# Регистрация
def auth_register(request):
    global const
    try:
        if (request.method == "GET"):
            params = request.GET
        else:
            params = request.POST
        try:
            """
            http://127.0.0.1:8000/api/auth.register?app_id=1&key=kasdfYGYGvbhbFu1&first_name=ХуеСос&last_name=принГлс&email=lol&password=123
            """
            params['app_id']
            params['first_name']
            params['last_name']
            params['key']
            params['email']
            params['password']
            params['nickname']
        except:
            data = getErrorCode(4)
            return Return(request, data)
        try:
            if len(App.objects.filter(app_id=params['app_id'], servise_key=params['key']))==0:
                data = getErrorCode(2)
                return Return(request, data)
            if len(params['first_name'][0])==0 or len(params['last_name'][0])==0:
                data = getErrorCode(5)
                return Return(request, data)
            else:
                print(type(params['first_name']))
                print(params['last_name'])
                first_name = params['first_name'][0].upper() + params['first_name'][1:].lower()
                last_name = params['last_name'][0].upper() + params['last_name'][1:].lower()
            email = params['email']
            if ((email.count("@") == 1) and (email.index("@") < email.rindex(".")) and (email.rindex(".")+1<len(email)))==False:
                data = getErrorCode(6)
                returnReturn(request, data)
            else:
                email = email.lower()
                if len(Email.objects.filter(mail=email))>0:
                    data = getErrorCode(6)
                    return Return(request, data)
        except Exception as e:
            fixError(e)
            data = getErrorCode(1)
            return Return(request, data)
        user_info = {
            "app_id": params['app_id'],
            "first_name": first_name,
            "last_name": last_name,
            "servise_key": params['key'],
            "email": email,
            "password": params['password']
        }
        user_info['nickname'] = "user"
        try:
            allowSimvols = {'1': True, '2': True, '3': True, '4': True, '5': True, '6': True, '7': True, '8': True, '9': True, '0': True, 'q': True, 'w': True, 'e': True, 'r': True, 't': True, 'y': True, 'u': True, 'i': True, 'o': True, 'p': True, 'a': True, 's': True, 'd': True, 'f': True, 'g': True, 'h': True, 'j': True, 'k': True, 'l': True, 'z': True, 'x': True, 'c': True, 'v': True, 'b': True, 'n': True, 'm': True, 'Q': True, 'W': True, 'E': True, 'R': True, 'T': True, 'Y': True, 'U': True, 'I': True, 'O': True, 'P': True, 'A': True, 'S': True, 'D': True, 'F': True, 'G': True, 'H': True, 'J': True, 'K': True, 'L': True, 'Z': True, 'X': True, 'C': True, 'V': True, 'B': True, 'N': True, 'M': True}
            if type(params['nickname']) == list:
                params['nickname'] = params['nickname'][0]
            e = 0
            l = 0
            for _ in params['nickname']:
                l += 1
                try:
                    allowSimvols[_]
                except:
                    e += 1
            if l > 10:
                params['nickname'] = params['nickname'][:10]
            if (l!=0) and (e == 0):
                user_info['nickname'] = params['nickname'].lower()
        except Exception as e:
            fixError(e)
        pay = Payment.objects.create()
        exp = Experience.objects.create()
        exp.save()
        perms = Permissions.objects.create(
            sendmessage=0,
        )
        p = Profile.objects.create(
            first_name=user_info['first_name'],
            last_name=user_info['last_name'],
            nickname=user_info['nickname'],
            delete=False,
            payments= pay,
            exp=exp
            )
        p.save()
        exp.master = p;
        pay.master = p;
        exp.save()
        pay.save()
        mail = generate_email_code(user_info['email'])
        AuthLoginInfo.objects.create(
            profile=p,
            email=mail,
            password=user_info['password']
        )
        token = generate_token(user_info['app_id'], p)
        p.setOnline()
        result = {
            "user": p.Info(),
            "access_token": token,
            "message": "Please, confirm your email-address"
        }
        data = {'response': result}
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Плучение информации о профиле
def profile_get(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'id', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), True, -1),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                if getparams['id'] == -1:
                    getparams['id'] = profile.id
                result = Profile.objects.filter(id=getparams['id'])
                if result.count()==1:
                    data = result[0].Info()
                else:
                    data = getErrorCode(9)
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Функция установки онлайна профилю
def profile_setOnline(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                data = {'response': 1}
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Новости профиля
def news(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'id', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), False, getErrorCode(5)),
            (int, 'count', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), True, 10),
            (int, 'end', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), True, 999999999),
            (int, 'begin', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), True, 1),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                result = profile.getNews(begin=getparams['begin']-1, end=getparams['end']+1, count=getparams['count'])
                if result['flag']:
                    data = {
                        'response': result['result'],
                    }
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Получение новых новостей
def walls_new(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                need_params = [
                    (str, 'text', lambda tmp: ((const.post.text.length.max >= len(tmp) >= const.post.text.length.min)), False, getErrorCode(5)),
                    (str, 'title', lambda tmp: ((const.post.title.length.max >= len(tmp) >= const.post.title.length.min)), True, ''),
                    (lambda tmp: Profile.objects.filter(id=tmp)[0], 'user_id', lambda tmp: Profile.objects.filter(id=tmp).count()==1, False, Profile.objects.filter(id=profile)),
                ]
                result = getData(request, need_params)
                if result['flag']:
                    getparams = result['result']
                    profile = profile['profile']
                    result = profile.NewPost(title=getparams['title'], text=getparams['text'], user=getparams['user_id'], save=True)
                    if result['flag']:
                        data = {
                            'response': result['result'],
                        }
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Репост
def walls_repost(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (str, 'post', lambda tmp: (6<=len(tmp)<=50), False, getErrorCode(5)),
            (str, 'text', lambda tmp: (const.post.text.length.min <= len(tmp) <= const.post.text.length.max), True, '')
        ]
        result = getData(request, need_params)
        data = result['result']
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                tmpData = profile.Repost(text=getparams['text'], post=getparams['post'])
                if tmpData['flag']:
                    data = {'response': tmpData['result']}
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Установка виджета пользователя
def widjet_set(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (str, 'post', lambda tmp: (6<=len(tmp)<=50), False, getErrorCode(5)),
            ]
        result = getData(request, need_params)
        data = result['result']
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                if profile.setWidjet(getparams['wall']):
                    data = {'response': 1}
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Удаление виджета
def widjet_del(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            ]
        result = getData(request, need_params)
        data = result['result']
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                if profile.delWidget():
                    data = {'response': 1}
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# ДОПИСАТЬ
# Получение диалогов пользователя
def messages_getConversations(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'begin', lambda tmp: (tmp.isdigit() and len(tmp)>0), True, 0),
        ]
        result = getData(request, need_params)
        data = result['result']
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# ДОПИСАТЬ
# Функция создания аккаунта бота
def profile_createbot(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (str, 'name', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'begin', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), True, 0),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                Profile.objects.create(
                    first_name="",
                    last_name=getparams['name'],
                    nickname=getparams['name'].lower(),
                    verifery=False,

                )
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Функция подписки на профиль
def profile_subscribe(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'id', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), False, getErrorCode(5)),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                data = getErrorCode(5)
                if profile.Subscribe(getparams['id']):
                    data = {'response': 1}
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Функция отписки от профиля
def profile_unsubscribe(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'id', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), False, getErrorCode(5)),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                data = getErrorCode(5)
                if profile.Subscribe(getparams['id']):
                    data = {'response': 1}
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Поиск профиля по vkid, dsid
def profile_find(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'dcid', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), True, -1),
            (int, 'vkid', lambda tmp: (tmp.isdigit()) and (len(tmp)>0), True, -1),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            if (getparams['dsid'] == -1) and (getparams['vkid'] == -1):
                data = getErrorCode(5)
            else:
                profile = getProfileFromToken(getparams['access_token'], request)
                data = getErrorCode(5)
                if profile['flag']:
                    profile = profile['profile']
                    if getparams['vkid'] == -1:
                        result = Profile.objects.filter(dcid=getparams['dcid'])
                    elif getparams['dcid'] == -1:
                        result = Profile.objects.filter(vkid=getparams['vkid'])
                    else:
                        result = Profile.objects.filter(vkid=getparams['vkid'], dcid=getparams['dcid'])
                    data = {
                        'count': result.count(),
                        'result': [_.Info() for _ in result],
                    }
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# ДОПИСАТЬ
# Отправление сообщений пользователю (не беседе временно, беседы не реализованы)
def messages_send(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (int, 'peer_id', lambda tmp: (6<=len(tmp)<=50), False, getErrorCode(5)),
            (str, 'text', lambda tmp: (const.message.text.length.min <= len(tmp) <= const.message.text.length.max), True, '')
            (str, 'attachments', lambda tmp: (const.post.attachments.length.min <= len(tmp) <= const.post.attachments.text.length.max), True, '')
        ]
        result = getData(request, need_params)
        data = result['result']
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            getparams['attachments'] = getAttachments(getparams['attachments'])
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                tmp = profile.messages.filter(id=getparams['peer_id'])
                if tmp.count() == 1:
                    data = {'response': 1}
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# ДОПИСАТЬ
# Комментирование поста (дописать)
def walls_sendComment(request):
    global const
    try:
        if (request.method == "GET"):
            params = request.GET
        else:
            params = request.POST
        getparams = {}
        try:
            getparams['access_token'] = params['access_token']
        except:
            data = getErrorCode(4)
            return Return(request, data)
        if True:
            try:
                tmp = params['begin']
                if (tmp.isdigit()==False) or (len(tmp)==0):
                    data = getErrorCode(5)
                    return Return(request, data)
                else:
                    getparams['begin'] = int(tmp)
            except:
                getparams['begin'] = 0
        profile = getProfileFromToken(getparams['access_token'], request)
        data = getErrorCode(5)
        if profile['flag']:
            profile = profile['profile']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Удаление поста
def walls_remove(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (str, 'wall', lambda tmp: (len(tmp)>0), False, getErrorCode(4)),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                wall = getparams['wall'].split("_")
                if len(wall)==2:
                    if wall[0][:4] == 'wall':
                        wall[0] = wall[4]
                        if wall[0].isdigit() and wall[1].isdigit():
                            user = Profile.objects.filter(id=wall[0])
                            if user.count() == 1:
                                user = user[0]
                                wall = user.walls.filter(post_id=wall[2])
                                if wall.count() == 1:
                                    wall.remove()
                                    wall.save()
                                    data = {'response': 1}
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Лайк на пост
def walls_like(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (str, 'wall', lambda tmp: (len(tmp)>0), False, getErrorCode(4)),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                wall = getparams['wall'].split("_")
                if len(wall)==2:
                    if wall[0][:4] == 'wall':
                        wall[0] = wall[4]
                        if wall[0].isdigit() and wall[1].isdigit():
                            user = Profile.objects.filter(id=wall[0])
                            if user.count() == 1:
                                user = user[0]
                                wall = user.walls.filter(post_id=wall[2])
                                if wall.count() == 1:
                                    if wall.like(profile):
                                        wall.save()
                                        data = {'response': 1}
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Убрать лайк с поста
def walls_unlike(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (str, 'wall', lambda tmp: (len(tmp)>0), False, getErrorCode(4)),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                wall = getparams['wall'].split("_")
                if len(wall)==2:
                    if wall[0][:4] == 'wall':
                        wall[0] = wall[4]
                        if wall[0].isdigit() and wall[1].isdigit():
                            user = Profile.objects.filter(id=wall[0])
                            if user.count() == 1:
                                user = user[0]
                                wall = user.walls.filter(post_id=wall[2])
                                if wall.count() == 1:
                                    if wall.unlike(profile):
                                        wall.save()
                                        data = {'response': 1}
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)

# Отправка сообщения
def walls_sendComment(request):
    global const
    try:
        need_params = [
            (str, 'access_token', lambda tmp: (len(tmp)==20), False, getErrorCode(4)),
            (str, 'wall', lambda tmp: (len(tmp)>0), False, getErrorCode(4)),
            (str, 'text', lambda tmp: (len(tmp)>0), False, getErrorCode(4)),
        ]
        result = getData(request, need_params)
        if result['flag']:
            getparams = result['result']
            profile = getProfileFromToken(getparams['access_token'], request)
            data = getErrorCode(5)
            if profile['flag']:
                profile = profile['profile']
                wall = getparams['wall'].split("_")
                if len(wall)==2:
                    if wall[0][:4] == 'wall':
                        wall[0] = wall[4]
                        if wall[0].isdigit() and wall[1].isdigit():
                            user = Profile.objects.filter(id=wall[0])
                            if user.count() == 1:
                                user = user[0]
                                wall = user.walls.filter(post_id=wall[2])
                                if wall.count() == 1:
                                    if wall.sendComment(profile, getparams['text']):
                                        wall.save()
                                        data = {'response': 1}
        else:
            data = result['result']
    except Exception as e:
        fixError(e)
        data = getErrorCode(1)
    return Return(request, data)
