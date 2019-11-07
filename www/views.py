from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseRedirect
from api.models import *
from api.defaultFunctions import *
from django.http import HttpResponse, FileResponse
from random import random, randint
from time import time, strptime, ctime, strftime
from hashlib import md5
from background_task import background

robokassa_mrc_login = "foxhustle"
robokassa_pass_1 = "beK0bnMQy1LU7fxi39Nk"
robokassa_pass_2 = "a831artuqIXCex4C5zzp"

robokassa_testpass_1 = "fqKBwUem8PLN3V6j2Cd6"
robokassa_testpass_2 = "t3apkI87IvG3xXEk6SLF"

debug = True
url_parrent = "foxhustle.ru"

text = {
    'website': {
        'name': "Fox Hustle",
        'url': url_parrent,
        'protocol': "http",
        'time': timezone.now()
    }
}


#def get_file(request, url=""):


"""
# Decorator for auth profile
def decorator_login(function, *data, **kwargs):
    def function_1(request, *data, **kwargs):
        request.session = session = request.session
        session.set_expiry(86400*30)
        session.set_test_cookie()
        if session.test_cookie_worked():
            session.delete_test_cookie()
            access_token = session.get('access_token', 'none')
            if access_token != "none":
                tmp = AuthInfo.objects.filter(token=access_token)
                if tmp.count() == 0:
                    access_token = "none"
                else:
                    profile = tmp[0].profile
                    profile.setOnline()
            if access_token == "none":
                return HttpResponseRedirect("http://{url}/login".format(url=url_parrent))
            kwargs['profile'] = profile
            return function(request, **kwargs)
        return HttpResponseRedirect("http://{url}/no-cookies".format(url=url_parrent))
    return decorator_login
"""

class Message:
    def __init__(self, host="smtp.yandex.ru", port=587, from_mail="no-reply@foxhustle.ru", subject="", text="", to=[], ):
        self.server = smtplib.SMTP()


class Email_connection:
    def __init__(self, host="smtp.yandex.ru", port=465, username="", password=""):
        from smtplib import SMTP_SSL
        smtp = SMTP_SSL(host=host, port=port)
        self._username = username
        self._host = host
        self._password = password
        self._port = port
        smtp.ehlo()
        no_reply = smtp.login(user=username, password=password)
        if no_reply[0] == 235:
            self.smtp = smtp
            print("Successfully connection to '{host}:{port}'\n Login: \t{login}\n Password: \t{password}".format(host=self._host, port=self._port, login=self._username, password="*"*len(self._password)))
    def verify_connection(self):
        try:
            self.smtp
        except:
            return False
        return True
    def sendmail(self, to="", subject="", text=""):
        if self.verify_connection():
            try:
                message = "\r\n".join([
                    "From: {email}".format(email=self.smtp.user),
                    "To: {to}".format(to=to),
                    "Subject: {subject}".format(subject = subject),
                    "",
                    str(text)
                ])
                self.smtp.sendmail(self.smtp.user, to, message)
                return True
            except:
                pass
        return False
    def quit(self):
        return self.smtp.quit()

emails = {data:Email_connection(username="{data}@foxhustle.ru".format(data=data)) for data in ["no-reply", "support"]}

@background(queue="send-mail")
def sendmail(from_mail="no-reply", to_mail="", subject="", message=""):
    global emails
    try:
        emails[from_mail].sendmail(to=to_mail, subject=subject, text=message)
        return True
    except:
        return False


def create_payment_url(number, value):
    global robokassa_testpass_1, robokassa_pass_1, robokassa_mrc_login, debug
    summ = 10
    number = 15
    currency = "RUB"
    email = "ilya.kanyshev@mail.ru"
    locate = "ru"
    description = "Some descriptions"
    encoding = "utf-8"
    url = "https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin={mrc_login}&InvId={InvId}&Encoding={encoding}&OutSum={sum}&InvId={number_check}&Description={description}&SignatureValue={code}&Culture={locate}&email={email}&ExpirationDate={ExpDate}".format(
        mrc_login=robokassa_mrc_login, #OutSumCurrency={currency} currency=currency, {currency}:
        sum=summ,
        number_check=number,
        encoding=encoding,
        InvId=number,   
        description=description,
        code=md5("{mrc_login}:{sum}:{InvId}:{pass_1}".format(
            mrc_login=robokassa_mrc_login,
            sum=summ,
            InvId=number,
            pass_1=robokassa_testpass_1,
            ).encode(encoding)).hexdigest(),
        locate=locate,
        email=email,
        ExpDate=strftime("%Y-%m-%dT%H:%M:%S", strptime(ctime(time()+600))),
    )
    if debug:
        url += "&isTest=1"
    return url

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


class informationOfSite:
    website = {
        'name': "Fox Hustle",
        'url': "http://foxhustle.ru",
    }
    settingsApp = {
        'message': False,
        'news': True,
        'profile': True,
        'subscriptions': False,
        'recomendation': False 
    }
    def __init__(self):
        self.website['time']: timezone.now()
    def get(self):
        return {
            'website': self.website,
            'settings': self.settingsApp,
        }

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
            tmp = EmailLetters.objects.create(
                to_mail=mail, 
                subject="[No-reply] Подтверждение почты для FoxHustle", 
                message="Это письмо было отправлено с сайта {protocol}://{host}\n\nВы получили это письмо, так как этот e-mail адрес был использован при регистрации на сайте. Если Вы не регистрировались на этом сайте, просто проигнорируйте это письмо и удалите его. Вы больше не получите такого письма.\n\nБлагодарим Вас за регистрацию.\nМы требуем от Вас подтверждения Вашей регистрации, для проверки того, что введенный Вами e-mail адрес - реальный. Это требуется для защиты от нежилательных злоупотреблений и спама.\n\nДля акивации Вашего аккаунта и получения доступа к некоторым заблокированным функциям, перейдите по следующей ссылке:\n\n{protocol}://verifery.{host}/email?confirm_code={code}&mail={mail}\n\nЕсли и при этих действиях ничего не получилось, возможно Ваш аккаунт заблокирован. В этом случае, обратитесь к Администратору (admin@foxhustle.ru), для разрешения проблемы.\n\nС уважением,\n\nАдминистрация {protocol}://{host}.".format(protocol=text['website']['protocol'], host=text['website']['url'], code=s, mail=mail),
                from_mail='no-reply')
            tmp.save()
            return a

# register function
def register(request, url=""):
    global url_parrent
    request.session = session = request.session
    session.set_test_cookie()
    if session.test_cookie_worked():
        access_token = session.get('access_token', 'none')
        if access_token != "none":
            tmp = AuthInfo.objects.filter(token=access_token)
            if tmp.count() == 0:
                del session['access_token']
                access_token = "none"
            else:
                p = tmp[0].profile
                return HttpResponseRedirect("http://user.{url}/{nickname}".format(nickname=encode(p.getNickname()), url=url_parrent))
        if access_token == "none":
            try:
                if (request.method == "GET"):
                    params = request.GET
                else:
                    params = request.POST
                try:
                    params['first_name']
                    params['last_name']
                    params['email']
                    params['password']
                    params['repeat-password']
                    params['nickname']
                except Exception as e:
                    data = informationOfSite().get()
                    data['tmp'] = {'login': False, 'register': True, 'about': False}
                    return render(request, 'login.html', data)
                app_id = 1
                user_data = {}
                resultCount = 0
                errorMessage = []
                # Проверка данных на подлинность
                if params['password'] == params['repeat-password']:
                    if len(params['password'])>7:
                        charTopCount, charLowerCount, numberCount, simvolCount, tmpCount = 0, 0, 0, 0, 0
                        for char in params['password']:
                            tmpCount += 1
                            if char.lower() in 'qwertyuiopasdfghjklzxcvbnm':
                                if char in 'qwertyuiopasdfghjklzxcvbnm':
                                    charLowerCount += 1
                                else:
                                    charTopCount += 1
                            elif char in '.-_':
                                simvolCount += 1
                            elif char in '1234567890':
                                numberCount += 1
                            else:
                                print(char)
                        if charTopCount + charLowerCount + numberCount + simvolCount == tmpCount:
                            if charTopCount>0:
                                if charLowerCount>0:
                                    if numberCount>0:
                                        user_data['password'] = params['password']
                                        resultCount += 1
                                    else:
                                        print(113)
                                        errorMessage += ['В пароле должны присутствовать цифры.']
                                else:
                                    print(116)
                                    errorMessage += ['В пароле должны присутствовать символы нижнего регистра (a-z).']
                            else:
                                print(119)
                                errorMessage += ['В пароле должны присутствовать символы верхнего регистра (A-Z).']
                        else:
                            print(122)
                            errorMessage += ['В пароле могут быть только английские буквы A-Z любого регистра, цифры и символы .-_']
                    else:
                        print(125)
                        errorMessage += ['Пароль должен быть не короче 8 символов.']
                else:
                    print(128)
                    errorMessage += ['Пароли не совпадают.']
                if 20>len(params['nickname'])>5:
                    nickname = params['nickname']
                    charCount, numberCount, simvolCount, tmpCount = 0, 0, 0, 0
                    for char in nickname:
                        tmpCount += 1
                        if char.lower() in 'qwertyuiopasdfghjklzxcvbnm':
                            charCount += 1
                        elif char in '.-_':
                            simvolCount += 1
                        elif char in '1234567890':
                            numberCount += 1
                        else:
                            print(char)
                    if (tmpCount == charCount+numberCount+simvolCount) and (tmpCount > 4):
                        resultCount += 1
                        user_data['nickname'] = params['nickname']
                    else:
                        print(149)
                        errorMessage += ['В псевдониме могут быть только английские буквы A-Z любого регистра, цифры и символы .-_']
                else:
                    print(142)
                    errorMessage += ['Имя пользователя должно быть не короче 6 символов и не длиннее 20']
                if (len(params['first_name'])>1):
                    resultCount += 1
                    user_data['first_name'] = params['first_name']
                else:
                    print(148)
                    errorMessage += ['Некорректные данные поля "Фамилия"']
                if(len(params['last_name'])>1):
                    resultCount += 1
                    user_data['last_name'] = params['last_name']
                else:
                    print(154)
                    errorMessage += ['Некорректные данные поля "Имя"']
                print("Email length:", len(params['email']))
                if 254>=len(params['email'])>=8:
                    flag = True
                    email = params['email'].lower().split('@')
                    if len(email)==2:
                        email = [email[0]] + email[1].split('.')
                        if len(email)==3:
                            if 254>len(email[0])>2 and 8>len(email[1])>1 and 3>=len(email[2])>=2:
                                user_data['email'] = params['email'].lower()
                                if Email.objects.filter(mail=user_data['email']).count()==0:
                                    resultCount += 1
                                else:
                                    errorMessage += ['На данную электрочную почту уже зарегистрирован аккаунт, попробуйте другую почту']
                                flag = False
                    if flag:
                        print(168)
                        errorMessage += ['Вы ввели некорректную электронную почту']
                else:
                    print(171)
                    errorMessage += ['Email должен быть не короче 8 символов и не длиннее 20']
                #print(errorMessage)
                if resultCount != 5:
                    data = informationOfSite().get()
                    data['tmp'] = {'login': False, 'register': True, 'about': False}
                    data['register_errors'] = errorMessage
                    data['reg_data'] = params
                    return render(request, 'login.html', data)
                pay = Payment.objects.create()
                exp = Experience.objects.create()
                exp.save()
                perms = Permissions.objects.create(
                    sendmessage=0,
                )
                p = Profile.objects.create(
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    nickname=user_data['nickname'],
                    delete=False,
                    payments= pay,
                    exp=exp
                    )
                p.save()
                exp.master = p;
                pay.master = p;
                exp.save()
                pay.save()
                mail = generate_email_code(user_data['email'])
                AuthLoginInfo.objects.create(
                    profile=p,
                    email=mail,
                    password=user_data['password']
                )
                token = generate_token(1, p)
                session['access_token'] = token
                p.setOnline()
                result = {
                    "user": p.Info(),
                    "access_token": token,
                    "message": "Please, confirm your email-address"
                }
                p.notify(message="Please, confirm your email-address")
                print(result)
                return HttpResponseRedirect("http://user.{url}/{nickname}".format(nickname=encode(p.getNickname()), url=url_parrent))
            except Exception as e:
                fixError(e)
            return HttpResponseRedirect("http://{url}/register".format(url=url_parrent))
    else:
        return HttpResponseRedirect("http://{url}/no-cookies".format(url=url_parrent))
        
# login function
def login(request, url=""):
    global url_parrent
    request.session = session = request.session
    session.set_test_cookie()
    if session.test_cookie_worked():
        access_token = session.get('access_token', 'none')
        if access_token != "none":
            tmp = AuthInfo.objects.filter(token=access_token)
            if tmp.count() == 0:
                del session['access_token']
                access_token = "none"
            else:
                p = tmp[0].profile
                return HttpResponseRedirect("http://user.{url}/{nickname}".format(nickname=encode(p.getNickname()),url=url_parrent))
        if access_token == "none":
            #try:
            if True:
                need_params = [
                    (str, 'login', lambda tmp: (4<=len(tmp)<=20), False, False),
                    (str, 'password', lambda tmp: (4<=len(tmp)<=20), False, False),
                    ]
                app_id = 1
                key = ""
                result = getData(request, need_params)
                data = result['result']
                if result['flag']:
                    params = result['result']
                    data = App.objects.filter(app_id=app_id)
                    if data.count()>0:
                        result = AuthLoginInfo.objects.filter(Q(email__mail=params['login']) | Q(profile__nickname=params['login']), password=params['password'])
                        if len(result)>0:
                            #print()
                            if result[0].profile.delete == False:
                                #EmailMessage('Hello', 'People {nickname} is login :)'.format(nickname=result[0].profile.getNickname()), settings.EMAIL_HOST_USER,
                                #    ['ilya.kanyshev@mail.ru'], ['ilya_kanyshev@mail.ru'],
                                #    reply_to=['another@example.com']).send()
                                print("Start_mail")
                                send_mail('Theme', 'Hello))0)', settings.EMAIL_HOST_USER, ['ilya.kanyshev@mail.ru'])
                                print("End mail")
                                result[0].profile.setOnline()
                                access_token = generate_token(app_id, result[0])
                                session['access_token'] = access_token
                                print(session['domain'])
                                return HttpResponseRedirect("http://user.{url}/{nickname}".format(nickname=encode(result[0].profile.getNickname()),url=url_parrent))
                data = informationOfSite().get()
                data['tmp'] = {'login': True, 'register': False, 'about': False}
                return render(request, 'login.html', data)
            #except Exception as e:
            #    fixError(e)
            data = informationOfSite().get()
            data['tmp'] = {'login': True, 'register': False, 'about': False}
            return render(request, 'login.html', data)
    else:
        return HttpResponseRedirect("http://{url}/no-cookies".format(url=url_parrent))

# Create your views here.
def general(request, url=''):
    global url_parrent
    dataSite = informationOfSite().get()
    request.session = session = request.session
    session.set_expiry(86400*30)
    session.set_test_cookie()
    if session.test_cookie_worked():
        session.delete_test_cookie()
        access_token = session.get('access_token', 'none')
        if access_token != "none":
            tmp = AuthInfo.objects.filter(token=access_token)
            if tmp.count() == 0:
                access_token = "none"
            else:
                profile = tmp[0].profile
                return HttpResponseRedirect("http://user.{url}/{nickname}".format(nickname=encode(profile.getNickname()), url=url_parrent))
        if access_token == "none":
            if url == "register":
                return register(request)
            elif url == "login":
                return login(request)
            elif url == "":
                data = informationOfSite().get()
                data['tmp'] = {'login': True, 'register': False, 'about': False}
                return render(request, 'login.html', data)
            elif url == "about":
                data = informationOfSite().get()
                data['tmp'] = {'login': False, 'register': False, 'about': True}
                return render(request, 'login.html', data)
            else:
                return HttpResponseRedirect("http://{url}".format(url=url_parrent))
    return render(request, 'no-cookies.html', {})

# logout function
def logout(request, url=""):
    request.session = session = request.session
    session.set_test_cookie()
    if session.test_cookie_worked():
        access_token = session.get('access_token', 'none')
        if access_token != "none":
            tmp = AuthInfo.objects.filter(token=access_token)
            if tmp.count() == 0:
                access_token = "none"
            else:
                tmp[0].delete()
            del session['access_token']
            return HttpResponseRedirect("http://{url}/".format(url=url_parrent))
    else:
        return HttpResponseRedirect("http://{url}/no-cookies".format(url=url_parrent))

def user(request, url=""):
    global url_parrent
    url = url.split("/")
    #if (len(url) != 1) or (len(url) == 3):
    #    return HttpResponseRedirect("http://user.{url}/{nickname}".format(nickname="".join((_+"/") for _ in [url[0], "walls"]), url=url_parrent))
    #else:
    url_user = url[0]
    dataSite = informationOfSite().get()
    request.session = session = request.session
    session.set_expiry(86400*30)
    session.set_test_cookie()
    if session.test_cookie_worked():
        session.delete_test_cookie()
        access_token = session.get('access_token', 'none')
        if access_token != "none":
            tmp = AuthInfo.objects.filter(token=access_token)
            if tmp.count() == 0:
                access_token = "none"
            else:
                profile = tmp[0].profile
                profile.setOnline()
                url_user = url_user.split("/")
                if len(url_user)==1 or (len(url_user)==2 and url_user[1]==""):
                    try:
                        user = decode(url_user[0]).split("#")
                        dataSite['profile'] = profile.Info()
                        dataSite['my_profile'] = profile.AllInfo()
                        if len(user)==2:
                            if len(user[1])>0 and len(user[0])>0 and (user[1].isdigit()):
                                user = Profile.objects.filter(nickname=user[0], id=user[1])
                                if user.count()==1:
                                    dataSite['profile'] = user[0].AllInfo()
                                    dataSite['profile']['hash'] = encode(user[0].getNickname())
                                    dataSite['profile']['walls'] = [_.Info()['result'] for _ in user[0].walls.filter(flagPublish=True, flagDelete=False)]
                        tmp = int(time()-dataSite['profile']['online'])
                        if tmp<300:
                            dataSite['profile']['online'] = "Онлайн"
                        elif tmp<3600:
                            dataSite['profile']['online'] = "Был(а) в сети {min} мин. назад".format(min=tmp//60)
                        elif tmp<86400:
                            dataSite['profile']['online'] = "Был(а) в сети {hour} ч. назад".format(hour=tmp//3600)
                        else:
                            dataSite['profile']['online'] = "Когда-то был(а) в сети -_-"
                        return render(request, 'profile.html', dataSite)
                    except Exception as e:
                        fixError(e)
                        return HttpResponseRedirect("http://user.{url}/{nickname}".format(nickname=encode(profile.getNickname()), url=url_parrent))
                else:
                    return HttpResponseRedirect("http://user.{url}/{nickname}".format(nickname=encode(profile.getNickname()), url=url_parrent))
        if access_token == "none":
            return HttpResponseRedirect("http://{url}/login".format(url=url_parrent))
    return HttpResponseRedirect("http://{url}/no-cookies".format(url=url_parrent))

def create_check(request, sum=100, data_url=""):
    dataSite = informationOfSite().get()
    request.session = session = request.session
    session.set_expiry(86400*30)
    session.set_test_cookie()
    if session.test_cookie_worked():
        session.delete_test_cookie()
        access_token = session.get('access_token', 'none')
        if access_token != "none":
            tmp = AuthInfo.objects.filter(token=access_token)
            if tmp.count() == 0:
                access_token = "none"
                request.GET.keys()
            else:
                profile = tmp[0].profile
                profile.setOnline()
                #print(url)
                #return HttpResponseRedirect("/login")
                return HttpResponseRedirect(url)
        if access_token == "none":
            return HttpResponseRedirect("http://{url}/login".format(url=url_parrent))
    return HttpResponseRedirect("http://{url}/no-cookies".format(url=url_parrent))

# Ошибка использования Cookie
def no_cookies(request):
    session.set_expiry(86400*30)
    session.set_test_cookie()
    if session.test_cookie_worked():
        return HttpResponseRedirect("http://{url}/login".format(url=url_parrent))
    else:
        return render(request, 'no-cookies.html', {})

def confirm(request, url=""):
    global url_parrent
    dataSite = informationOfSite().get()
    request.session = session = request.session
    session.set_expiry(86400*30)
    session.set_test_cookie()
    if session.test_cookie_worked():
        session.delete_test_cookie()
        if (url == "email") or (url == "email/"):
            try:
                mail = request.GET['email']
                confirm_code = request.GET['confirm_code']
                tmp = Email.objects.filter(mail=mail)
                if tmp.count() == 1:
                    tmp = tmp[0]
                    if tmp.confirm:
                        dataSite['conform']['status_flag'] = False
                        dataSite['confirm']['description'] = "Вы уже подтвердили свою почту"
                    elif tmp.confirm_code == confirm_code:
                        tmp.confirm = True
                        dataSite['confirm']['status_flag'] = True
                        dataSite['confirm']['description'] = "Вы успешно подтвердили свою почту! Теперь вам доступны некоторые действия в блоках \"Сообщения\" и \"Друзья\". Авторизуйтесь и "
                    else:
                        return HttpResponseRedirect("http://{url}/login".format(url=url_parrent))
                else:
                    dataSite['confirm']['status_flag'] = False
                    dataSite['confirm']['description'] = "У вас нет почты для подтверждения"
                return render(request, "confirm_", dataSite)
            except Exception as e:
                fixError(e)
        return HttpResponseRedirect("http://{url}/login".format(url=url_parrent))
    return HttpResponseRedirect("http://{url}/no-cookies".format(url=url_parrent))
