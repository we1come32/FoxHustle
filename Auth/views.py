from django.shortcuts import render, redirect
from . import models
from Profile.models import Permission
from Profile.models import Profile as Profiles
from Profile.models import Notification

# Create your views here.

def randomChars(text, on_dict = False):
    result = "" 
    l = len (text) 
    new_dict = {}
    for number in range(l):
        tmp = randint (0, l - 1) 
        l -= 1
        result += text[tmp] 
        text = text[: tmp] + text[(tmp + 1):]
        new_dict[result[-1]] = number
    if on_dict:
        return result, new_dict
    return result 

def genKey(length):
    chifr, l = randomChars("0123456789qwertyuiopasdfghklzxcvbnm"), 35
    result = "".join(chifr[randint(0, l - 1)] for _ in range(length))
    return result

def encoding(data, user):
    if data['type'] == "user":
        text = data['type'][0] + "0" * max (0, 11 - len (str (data['id']))) + str (data['id']) + "0"*max(0, 11-len(str (data['app_id'])))+str (data['app_id']) + genKey(45)
    elif data['type'] == "bot":
        text =  data['type'][0] + "0" * max (0, 11 - len (str (data['id']))) + str (data['id']) + genKey(56)
    else:
        raise Exception('Not fix this data encription: ' + str(data))
    length, result = 35, ""
    chifr, chift_dict = randomChars("0123456789qwertyuiopasdfghklzxcvbnm", on_dict = True)
    e, n = 31, 35
    result = "".join(chifr[(chift_dict[_]+(number+1)**2)**e%n] for number, _ in enumerate(text))
    token = ("".join((chifr[number] + result[number]) for number in range(length)) + result[length:])
    perms = Permission.objects.create()
    app = models.AuthApp.get(id=data['app_id'])
    a = models.AccessToken.objects.create(
        app=app,
        worked=True,
        profile=user,
        access_token=token,
        perms=perms + app.perms,
    )
    a.save()
    return token

def decoding(data):
    d, n, length = 7, 35, 35
    chifr = data[:(length*2):2]
    data = data[1:(length*2+2):2]+data[(length*2+1):]
    _result = "".join(chifr[(chifr.index(_)**d%n -(number+1)**2)%n] for number, _ in enumerate(data))
    if _result[0] == "u":
        return {
            'type': 'user',
            'id': int(_result[1:12]),
            'app_id': int(_result[12:23]),
        }
    elif _result[0] == "b":
        return {
            'type': 'bot',
            'id': int(_result[1:12]),
        }

# function for get information about any users, who enter the site
def getUser(request):
    class AuthProfileData:
        params = {
            'AuthAccess': 0,
            'AppsAccess': 0,
            'BugtrackerAccess': 0,
            'ExperienceAccess': 0,
            'GoodsAccess': 0,
            'GroupAccess': 0,
            'PaymentAccess': 0,
            'ProfileAccess': 0,
            'MessageAccess': 0,
            'SysAccess': 0,
            'DevLogsAccess': 0,
        }
        user = 0
        worked = False
        def accept(self):
            return self.worked
        def allow(self, param=""):
            if param in self.params:
                return self.params[param]
            return 0
        def json(self):
            return {
                'perms': { key: value for key, value in self.params.items() },
                'profile': self.user.json(),
                'slug': self.user.id,
                'notifications': [notification.json() for notification in Notification.objects.filter(author=self.user, unread=False)],
            }
    access_token = request.session.get('access_token', False)
    tmpData = AuthProfileData()
    if access_token:
        try:
            user = decoding(access_token)
            app = models.AuthApp.objects.get(id=user['app_id'])
            user = Profiles.objects.get(id=user['id'])
            perms = user.perms + app.perms
            tmpData.user = user
            tmpData.params['AuthAccess'] = perms.AuthAccess
            tmpData.params['AppsAccess'] = perms.AppsAccess
            tmpData.params['BugtrackerAccess'] = perms.BugtrackerAccess
            tmpData.params['ExperienceAccess'] = perms.ExperienceAccess
            tmpData.params['GoodsAccess'] = perms.GoodsAccess
            tmpData.params['GroupAccess'] = perms.GroupAccess
            tmpData.params['PaymentAccess'] = perms.PaymentAccess
            tmpData.params['ProfileAccess'] = perms.ProfileAccess
            tmpData.params['MessageAccess'] = perms.MessageAccess
            tmpData.params['SysAccess'] = perms.SysAccess
            tmpData.params['DevLogsAccess'] = perms.DevLogsAccess
            tmpData.worked = True
        except Exception as e:
            tmpData.worked = False
    return tmpData
    



def login(request, app=1):
    data = {}
    flag = True
    names = [
        'login', 
        'password'
        ]
    for name in names:
        try:
            data[name] = request.session.get(name)
        except:
            flag = False
    if flag:
        try:
            from Crypto.Hash import SHA256
            hash = SHA256.new()
            hash.update(data['password'].encode())
            user = models.AuthInfoProfile.objects.get(
                email=data['login'],
                password=hash.digest(),
            )
            data = {
                'type': 'user',
                'id': user.profile.id,
                'app_id': app,
            }
            token = encoding(data, user=user.profile)
            request.set_cookie(access_token=token)
        except:
            pass
    return redirect('/login')


def confirm_email(request):
    try:
        id = request.session.get('id')
        secret_key = request.session.get('secret_key')
        model = models.ConfirmCode.objects.get(id=id, code=secret_key)
        model.authInfoProfile.email_confirmed = True
        model.authInfoProfile.save()
        model.delete()
        model.authInfoProfile.notify(
            action="", 
            title="Аккаунт активирован.", 
            description="Вы подтвердили свою почту. Теперь Вы можете пользоваться всеми доступными функциями сайта."
            )
    except:
        return redirect('/')



def registration(request):
    pass

