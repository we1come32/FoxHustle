from django.db import models
from django.db.models import Q
from django.utils import timezone
import time
import random

url = "foxhustle.ru"

# Функция логирования ошибок в классах
def fixError(e):
    s = "Error"
    try:
        tmp = Errors.objects.create(
            date = timezone.now(),
            line = e.__traceback__.tb_lineno,
            directory = str(e.__traceback__.tb_frame.f_code.co_filename),
            description = str(e.args[0]),
        )
        tmp.save()
    except:
        s += " not in DB"
    spisok = [
        ("Description: ", e.args[0],),
        ("Line #",e.__traceback__.tb_lineno,),
        ("Dirrectory: ",e.__traceback__.tb_frame.f_code.co_filename,),
        ("Names: ","\n    "+ ", ".join((str(_)) for _ in e.__traceback__.tb_frame.f_code.co_names)[:])
    ]
    s = "Error"
    for _ in spisok:
        s += "\n  {}{}".format(_[0],_[1])
    print(s)

"""
        default = "Created a check#{number} from the {nickname1} to {nickname2} in the amount of {value} K.".format(
            number=self.number,
            nickname1=self.author.getNickname(),
            nickname2=self.to_profile.getNickname(),
            value=self.value
        )
"""

# Система чеков (переводов денег по требованию)
class Check(models.Model):
    number = models.AutoField(primary_key=True)
    to_profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    author = models.ForeignKey('CloneProfile', on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    status_message = models.CharField(
        max_length=200, default=""
        )
    created_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(default=timezone.now)
    def confirm(self, profile):
        try:
            if self.to_profile == profile:
                if profile.payments.value >= self.value:
                    if self.status == 1:
                        profile.payments.value -= self.value
                        profile.payments.save()
                        self.status = 2
                        self.update_date = timezone.now()
                        message = "{user} paid check#{number} in the amount of {value} K.".format(
                            user = self.to_profile.getNickname(),
                            number = self.number,
                            value = self.value
                        )
                        self.status_message=message
                        self.author.notify(message, "check#{number}".format(number=self.number))
                        self.author.save()
                        self.save()
                        return True
        except Exception as e:
            fixError(e)
        return False
    def cancel(self, profile):
        try:
            if self.status == 1:
                msg_profile = ""
                if profile == self.author:
                    message = "Check #{number} canceled by the sender {nickname}".format(
                        number=self.number,
                        nickname=self.author.getNickname(),
                    )
                    msg_profile = self.to_profile
                elif profile == self.to_profile:
                    message = "Check #{number} canceled by the payer {nickname}".format(
                        number=self.number,
                        nickname=self.to_profile.getNickname(),
                    )
                    msg_profile = self.author
                else:
                    return False
                msg_profile.notify(message, "check#{number}".format(number=self.number))
                msg_profile.save()
                self.status = 0
                self.update_date = timezone.now()
                self.save()
                return True
        except Exception as e:
            fixError(e)
        return False
    def Info(self):
        return {
            'status': self.status,
            'statusMessage': self.status_message,
            'sender': self.author.Info(),
            'recipient': self.to_profile.Info(),
            'value': self.value,
            'creationsDate': {
                'hour': self.created_date.hour,
                'minute': self.created_date.minute,
                'second': self.created_date.second,
                'day': self.created_date.day,
                'month': self.created_date.month,
                'year': self.created_date.year
            },
            'editDate': {
                'hour': self.update_date.hour,
                'minute': self.update_date.minute,
                'second': self.update_date.second,
                'day': self.update_date.day,
                'month': self.update_date.month,
                'year': self.update_date.year
            }
        }

# История оплаты
class PayHistory(models.Model):
    to_profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    check_data = models.ForeignKey('Check', on_delete=models.CASCADE, null=True, blank=True)
    def get(self):
        if self.check == "":
            return {
                'toProfile': self.to_profile.Info(),
                'value': self.value,
                'type': 'transfer',
                'date':{
                    'hour': self.date.hour,
                    'minute': self.date.minute,
                    'second': self.date.second,
                    'day': self.date.day,
                    'month': self.date.month,
                    'year': self.date.year,
                },
            }
        else:
            return {
                'toProfile': self.to_profile.Info(),
                'value': self.value,
                'type': 'check',
                'check': self.check.Info()
            } 

# Система оплаты
class Payment(models.Model):
    master = models.ForeignKey('Profile', on_delete=models.CASCADE, blank=True, null=True)
    value = models.IntegerField(default=0)
    history = models.ManyToManyField('PayHistory', blank=True)
    checks = models.ManyToManyField('Check', blank=True)
    def transfer(self, id, value):
        try:
            if type(id) == int:
                if self.value >= value:
                    tmp = Payment.objects.filter(master__id==id)
                    if tmp.count()==1:
                        tmp = tmp[0]
                        tmp.value += value
                        self.value -= value
                        tmp.save()
                        self.save()
                        return True
        except Exception as e:
            fixError(e)
        return False
    def addCheck(self, profile, value):
        try:
            if type(profile) == Profile:
                if type(value) == int:
                    if value>0:
                        if profile.type_profile==0 and self.master.type_profile==0:
                            c = Check.objects.create(
                                to_profile = profile,
                                author = self,
                                value=value
                            )
                            c.save()
                            message = "{type_profile} {nickname} presented you a check#{number} in the amount of {value} K.".format(
                                type_profile = self.master.getType(),
                                nickname = self.master.getNickname(),
                                number = c.number,
                                value=value,
                            )
                            profile.notify(message, "check#{number}".format(number=c.number))
                            profile.payments.checks.add(c)
                            self.checks.add(c)
                            profile.save()
                            self.save()
                            return True
        except Exception as e:
            fixError(e)
        return False
    def get(self, begin=0, count=10):
        tmp = self.history.count()
        return {
            'value': self.value,
            'history': [_.Info() for _ in self.history.all()[min(tmp, begin):min(tmp, begin+count)]],
            'checks':{
                'denied': {
                    'count': self.checks.filter(status=0)
                },
                'unpaid':{
                    'count': self.checks.filter(status=1)
                },
                'paid': {
                    'count': self.checks.filter(status=2)
                }
            }
        }
    def getUnPaid(self, begin=0, count=10):
        tmp = self.checks.filter(status=1)
        tmpLength = tmp.count()
        return {
            'count': tmpLength,
            'unpaid': [_.Info() for _ in tmp[min(tmpLength, begin):min(tmpLength, begin+count)]]
        }
    def getDenied(self, begin=0, count=10):
        tmp = self.checks.filter(status=0)
        tmpLength = tmp.count()
        return {
            'count': tmpLength,
            'denied': [_.Info() for _ in tmp[min(tmpLength, begin):min(tmpLength, begin+count)]]
        }
    def getPaid(self, begin=0, count=10):
        tmp = self.checks.filter(status=2)
        tmpLength = tmp.count()
        return {
            'count': tmpLength,
            'paid': [_.Info() for _ in tmp[min(tmpLength, begin):min(tmpLength, begin+count)]]
        }

# Закрепленная запись
class Widjets(models.Model):

    post = models.ForeignKey('Wall', on_delete=models.CASCADE)

# Запись
class Wall(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    post_id = models.IntegerField(default=0)
    repost_id = models.ForeignKey('Wall', on_delete=models.CASCADE, default="", null=True, blank=True)
    title = models.CharField(max_length = 100, default="", null=True, blank=True)
    text = models.CharField(max_length = 8000, default="", null=True, blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    comments = models.ManyToManyField('Comments',blank=True)
    flagPublish = models.BooleanField(default=False, blank=True)
    flagDelete = models.BooleanField(default=False, blank=True)
    delete_date = models.DateTimeField(blank = True, null = True)
    published_date = models.DateTimeField(blank = True, null = True)
    likes = models.ManyToManyField('CloneProfile', blank = True)
    def publish(self):
        self.published_date = timezone.now()
        self.publish = True
        self.save()
    def delete(self):
        self.delete_date = timezone.now()
        self.delete = True
        self.save()
    def Info(self, counter=1):
        try:
            result = {}
            if ((self.flagDelete==False)and(counter==1)) or (counter==2):
                result["author"] = self.author.Info()
                result["post_id"] = self.post_id
                try:
                    if (type(self.repost_id) == Wall):
                        result["repost"] = "wall"+str(self.repost_id.author.id)+"_"+str(self.repost_id.post_id)
                        if (counter<3) and ((self.repost_id.flagDelete==True)or(counter==1)):
                            data = self.repost_id.Info(counter=counter+1)
                            if data['flag']:
                                result["repost"] = data['result']
                    else:
                        result['title'] = self.title
                except:
                    result['title'] = self.title
                result['text'] = self.text
                if counter == 1:
                    result['comments'] = {
                        'count': self.comments.count()
                    }
                result['published_date'] = {
                    'hour': self.published_date.hour,
                    'minute': self.published_date.minute,
                    'second': self.published_date.second,
                    'day': self.published_date.day,
                    'month': self.published_date.month,
                    'year': self.published_date.year
                }
                #result['text'] = self.text
                return {
                    "flag": True,
                    "result": result
                } 
            else:
                return {
                    "flag": False
                }
        except Exception as e:
            fixError(e)
            return {
                "flag": False
            }
    def __str__(self):
        return "wall"+str(self.author.id)+"_"+str(self.post_id)
    def AllInfo(self):
        result = self.Info()
        if result['flag']:
            result['result']['comments'] = self.getComments()
        return result
    def getComments(self):
        """result = {
            'count': 0,
            'comments': [],
        }
        for _ in self.comments.All():
            if _.flagDelete == False:
                result['count'] += 1;
                result['comments'].append(_.Info())
        return result"""
    def sendComment(self, profile, text):
        try:
            if text != "":
                if type(profile) == Profile:
                    tmp = Comments.create(
                        author=profile,
                        text=text
                    )
                    tmp.save()
                    return {'flag': True, 'result': tmp.Info()}
        except Exception as e:
            fixError(e)
        return {'flag': False}
    def getComments(self, post, begin=0, end=99999999, count=10):
        if post == "":
            return {
                'flag': False
            }
        if (type(begin)!=int) or (type(end)!=int) or (type(count) != int) or (begin<0) or (end<0) or (type(post) != str):
            result = {
                'flag': False
            }
        else:
            result = {
                'flag': True
            }
        if result['flag']:
            tmp = post.split('_')
            if len(tmp)==2:
                if tmp[0].isdigit() and tmp[1].isdigit():
                    user = Profile.objects.filter(id=int(tmp[0]))
                    if user.count() == 1:
                        user = user[0]
                        tmpWall = user.walls.filter(post_id=int(tmp[1]))
                        if tmpWall.count() == 1:
                            result['result'] = tmpWall[0].getComments()
        return result
    def like(self, profile):
        try:
            if profile not in self.likes:
                self.likes.add(profile)
                self.save()
                return True
            return False
        except Exception as e:
            fixError(e)
            return False
    def unlike(self, profile):
        try:
            if profile in self.likes:
                self.likes.radd(profile)
                self.save()
                return True
            return False
        except Exception as e:
            fixError(e)
            return False

# Профиль пользователя. Все основные методы
class Profile(models.Model):
    id = models.AutoField(primary_key = True)
    first_name = models.CharField(max_length = 30, default="")
    last_name = models.CharField(max_length = 30, default="")
    verifery = models.BooleanField(default=False)
    nickname = models.CharField(max_length = 20, default="")
    delete = models.BooleanField(default = False)
    online = models.IntegerField(default=int(time.time()))
    widjet = models.ForeignKey('Widjets', on_delete=models.CASCADE, null=True, blank=True)
    permissions = models.ForeignKey('Permissions', on_delete=models.CASCADE, null=True, blank=True)
    subscribers = models.ManyToManyField('Subscriber', blank=True)
    subscriptions = models.ManyToManyField('Subscription', blank=True)
    activity = models.ManyToManyField('historyActivity', blank=True)
    dcid = models.IntegerField(default=-1)
    vkid = models.IntegerField(default=-1)
    walls = models.ManyToManyField('Wall', blank=True)
    messages = models.ManyToManyField('Dialog', blank=True)
    payments = models.ForeignKey('Payment', on_delete=models.CASCADE)
    exp = models.ForeignKey('Experience', on_delete=models.CASCADE)
    notifications = models.ManyToManyField('Notification', blank=True)
    links = models.ManyToManyField('Link', blank=True)
    menu_links = models.ManyToManyField('LinksMenu', blank=True)
    def setOnline(self):
        self.online = int(time.time())
        self.save()
    def Info(self):
        result = {
            "nickname": "{nickname}#{id}".format(nickname=self.nickname, id=self.id),
            "id": self.id,
            "deleted": self.delete,
        }
        if self.delete == False:
            tmp = self.exp.get()
            if tmp['flag']:
                result['exp'] = tmp['result']
            if type(self.widjet) == Wall:
                result['widjet'] = self.widjet.Info()
            result['first_name'] = self.first_name
            result['last_name'] = self.last_name
            result['online'] = self.online
            if self.verifery:
                result['verifery'] = self.verifery
        return result
    def AllInfo(self):
        result = self.Info()
        if result['deleted'] == False:
            if True: # subscriptions
                tmp = self.subscribers.filter(user__delete=False)
                #subscriptions = [_.Info() for _ in random.sample(tmp, 6)]
                #result['subscriptions'] = {
                #    'count': tmp.count(),
                #    'title': subscriptions
                #}
            if True: # subscribers
                tmp = self.subscribers.filter(user__delete=False)
                #subscribers = [_.Info() for _ in random.sample(tmp, 6)]
                #result['subscribers'] = {
                #    'count': tmp.count(),
                #    'title': subscribers
                #}
            if True: # count_wall
                pass
                #tmp = self.walls.All()
                #result['wallsCount'] = tmp
        return result
    def Subscribe(self, user):
        if type(user) == int:
            tmp = Profile.objects.filter(id=user)
            if tmp.count() == 1:
                user = tmp[0]
        if type(user) == Profile:
            if (self.subscriptions.filter(user=user).count()==0)and(Subscriber.objects.filter(user=self).count()==0):
                tmp = Subscription.object.create(user=user)
                tmp.save()
                self.subscriptions.add(tmp)
                self.save()
                tmp = Subscriber.object.create(user=self)
                tmp.save()
                user.subscribers.add(tmp)
                user.save()
                return True
        return False
    def Unsubscribe(self, user):
        if type(user) == int:
            tmp = Profile.objects.filter(id=user)
            if tmp.count() == 1:
                user = tmp[0]
        if type(user) == Profile:
            tmp1 = self.subscriptions.filter(user=user)
            tmp2 = user.subscribers.filter(user=self)
            if (tmp1.count()==1)and(tmp2.count()==1):
                [_.remove() for _ in tmp1]
                [_.remove() for _ in tmp2]
                self.save()
                user.save()
                return True
        return False
    def getNews(self, begin=0, end=99999999, count=10):
        if (type(begin)!=int) or(type(end)!=int) or (type(count) != int) or (begin<0) or (end<0):
            result = {
                'flag': False
            }
        else:
            result = {
                'flag': True
            }
            z = [ _.user for _ in self.subscriptions.filter()]
            walls = Wall.objects.filter(author__in=z, flagDelete=False, flagPublish=True)
            result['result'] = {
                'count': 0,
                'walls': []
            }
            for wall in walls[begin:max(end,walls.count())]:
                tmp = wall.Info()
                if tmp['flag']:
                    result['result']['count'] += 1
                    result['result']['walls'].append(tmp['result'])
                    if result['result']['count'] == count:
                        break
        return result
    def getWalls(self, user="", begin=0, end=99999999, count=10):
        if user == "":
            user = self
        if (type(begin)!=int) or(type(end)!=int) or (type(count) != int) or (begin<0)or(end<0):
            result = {
                'flag': False
            }
        else:
            result = {
                'flag': True
            }
        if type(user) == int:
            tmp = Profile.objects.filter(id=user)
            if tmp.count()>0:
                user = tmp[0]
        if (type(user) == Profile) and result['flag']:
            walls = user.walls.filter(flagDelete=False, flagPublish=True, post_id__lt=end, post_id__gt=begin)
            result['result'] = {
                'count': 0,
                'walls': []
            }
            for wall in walls:
                tmp = wall.Info()
                if tmp['flag']:
                    result['result']['count'] += 1
                    result['result']['walls'].append(tmp['result'])
                    if result['result']['count'] == count:
                        break
            return result
        return result
    def NewPost(self, title="", text="", user="", save=True):
        try:
            if user == "":
                user = self
            elif type(user) == int:
                data = Profile.objects.filter(id=user)
                if data.count()==1:
                    user = data[0]
            if (type(user) == Profile):
                if (text != "")or(repost != ""):
                    post = Wall.objects.create(
                        author = self,
                        post_id = user.walls.count()+1,
                        title = title,
                        text = text,
                        flagPublish = True,
                        published_date = timezone.now()
                        )
                    post.save()
                    user.walls.add(post)
                    user.save()
                    return post.Info()
        except Exception as e:
            fixError(e)
        return {
            'flag': False,
        }
    def Repost(self, text = "", post = ""):
        try:
            if type(post) == str:
                tmp = post.split("_")
                if len(tmp)==2:
                    if len(tmp[0])>4:
                        if tmp[0][0:4] == "wall":
                            user_id = tmp[0][4:]
                            post_id = tmp[1]
                            if user_id.isdigit() and post_id.isdigit() and (len(user_id)>0) and (len(post_id)>0):
                                user = Profile.objects.filter(id=user_id)
                                post_id = int(post_id)
                                if user.count()==1:
                                    user = user[0]
                                    if user.walls.count() >= post_id:
                                        tmpPost = user.walls.filter(post_id=post_id)
                                        if tmpPost.count() == 1:
                                            post = tmpPost[0]
            if type(post) == Wall:
                post = Wall.objects.create(
                    author=self,
                    post_id=self.walls.count()+1,
                    title="",
                    text=text,
                    repost_id = post,
                    published_date = timezone.now()
                )
                post.save()
                self.walls.add(post)
                self.save()
                return post.Info()
        except Exception as e:
            fixError(e)
        return {'flag':False}
    def deletePost(self, post):
        try:
            if type(post) == Wall:
                if post.author == self:
                    post.delete()
                    return True
        except Exception as e:
            fixError(e)
        return False
    def fixPost(self, post):
        try:
            wj = Widjets.objects.create(post=post)
            wj.save()
            self.widjet = wj
            return True
        except Exception as e:
            fixError(e)
            return False
    def unfixPost(self):
        try:
            self.widjet = ""
            return True
        except Exception as e:
            fixError(e)
            return False
    def __str__(self):
        return str(self.nickname)+"#"+str(self.id)
    def getProfile(self, profile):
        if type(profile) == str:
            if profile.isdigit() and len(profile)>0:
                profile = int(profile)
        if type(profile) == int:
            tmp = Profile.objects.filter(id=profile)
            if tmp.count() == 1:
                profile = tmp[0]
        if type(profile) == Profile:
            return {
                'flag': True,
                'result': profile.Info()
            }
        return {
            'flag': False
        }
    def setWidjet(self, wall):
        try:
            print(wall)
            if type(wall) == str:
                tmp = wall.split("_")
                if len(tmp) == 2:
                    if tmp[0] == ("wall{id}".format(id=self.id)):
                        if tmp[1].isdigit():
                            if tmp[1] != "":
                                wall = int(tmp[1])
            if type(wall) == int:
                tmp = self.walls.filter(post_id=wall)
                if tmp.count()==1:
                    wall = tmp[0]
            if type(wall) == Wall:
                if wall.flagPublish:
                    wj = Widjets.objects.create(post=wall)
                    wj.save()
                    self.widjet = wj
                    self.save()
                    return True
        except Exception as e:
            fixError(e)
        return False
    def delWidget(self):
        try:
            self.widjet = ""
            return True
        except Exception as e:
            fixError(e)
        return False
    def getConversations(self, begin=0, count=10):
        try:
            messages = self.messages
            tmpCount = messages.count()
            result = {
                'flag': True,
                'result': []
            }
            for _ in range(min(tmpCount, begin), min(begin+count, tmpCount)):
                result['result'] += [_.Info()]
            return result
        except Exception as e:
            fixError(e)
        return {'flag': False}
    def getType(self):
        return "User"
    def getNickname(self):
        return "{nick}#{id}".format(
            nick=self.nickname, 
            id=self.id
            )
    def notify(self, message, where=""):
        try:
            tmp = Notification.objects.create(
                where=where,
                message=message
            )
            tmp.save()
            self.notifications.add(tmp)
            self.save()
            return True
        except Exception as e:
            fixError(e)
        return True

class CloneProfile(models.Model):
    var = models.ForeignKey('Profile', on_delete=models.CASCADE)

# ДОПИСАТЬ!
# Боты
class Bot(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    nickname = models.CharField(max_length=20)
    verifery = models.BooleanField(default=False)
    delete = models.BooleanField(default = False)
    payments = models.ForeignKey('Payment', on_delete=models.CASCADE)
    creator = models.ForeignKey('Profile', on_delete=models.CASCADE)
    def __str__(self):
        return "Bot#{number}".format(
            number=self.id
        )

# История опыта пользователей
class ExpHistory(models.Model):
    date = models.DateTimeField(default=timezone.now)
    value = models.IntegerField(default=0)
    by = models.ForeignKey('Profile', on_delete=models.CASCADE)
    message = models.CharField(max_length=100, null=True, blank=True)
    def Info(self):
        result =  {
            'time':{
                'hour': self.date.hour,
                'minute': self.date.minute,
                'second': self.date.second,
                'day': self.date.day,
                'month': self.date.month,
                'year': self.date.year,
            },
            'value': self.value,
            'message': self.message
        }
        if self.value>=0:
            result['added_by'] = self.by.Info()
        else:
            result['sent_to'] = self.by.Info()
        return result

# Система опыта профиля
class Experience(models.Model):
    master = models.ForeignKey('Profile', on_delete=models.CASCADE, null=True, blank=True)
    exp = models.IntegerField(default=0)
    history = models.ManyToManyField('ExpHistory', blank=True)
    def add(self, value, profile):
        try:
            if type(value) == str:
                if value.isdigit():
                    if len(value)>0:
                        value = int(value)
            if (type(value) == int):
                if (value>0):
                    message = "{type} {nickname} has transferred you {money} exp.".format(
                        type=profile.getType(),
                        nickname=profile.getNickname()
                    )
                    if addHistory(value, message, profile):
                        self.exp += value
                        self.save()
                    return True
        except Exception as e:
            fixError(e)
        return False
    def get(self):
        result = {'flag': False}
        try:
            if self.exp>=0:
                scope = self.exp
                level = 1+int((-3+(9+8*scope/5)**0.5)/2)
                sc = lambda level: int(2.5*(level**2+3*level))
                result = {
                    'flag': True,
                    'result': {
                        'scope': scope,
                        'level': level,
                        'minLevelScope': sc(level-1),
                        'nextLevelScope': sc(level),
                    }
                }
        except Exception as e:
            fixError(e)
        return result
    def radd(self, value, profile):
        result = False
        try:
            if type(value) == str:
                if value.isdigit():
                    value = int(value)
            if type(value) == int:
                if self.exp >= value:
                    self.exp -= value
                    self.save()
                    result = True
        except Exception as e:
            fixError(e)
        return result
    def addHistory(self, value, message, profile):
        try:
            tmp = ExpHistory.objects.create(
                value=value,
                by=profile,
                message=message
            )
            tmp.save()
            self.history.add(tmp)
            self.save()
            return True
        except Exception as e:
            fixError(e)
        return False
    def getHistory(self, count=10, begin=0):
        try:
            tmp = self.history.all()
            tmpCount = tmp.count()
            result = []
            for _ in tmp[min(begin, tmpCount):min(begin+count, tmpCount)]:
                result.append(_.Info())
            return result
        except Exception as e:
            fixError(e)
            return False

# Оповещения
class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    where = models.CharField(max_length=50)
    message = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)

# Активность
class historyActivity(models.Model):
    time = models.DateTimeField(default=timezone.now)
    ip = models.GenericIPAddressField(protocol='both')
    token = models.ForeignKey('AuthInfo', on_delete=models.CASCADE)
    def __str__(self):
        return "{ip}:     {hour}:{minute}:{second} {day}.{month}.{year}".format(
            ip = self.ip,
            hour=self.time.hour,
            minute = self.time.minute,
            second = self.time.second,
            day = self.time.day,
            month = self.time.month,
            year = self.time.year
        )

# На кого подписан
class Subscription(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    def Info(self):
        user = self.user
        return user.Info()
    def __str__(self):
        try:
            return str(self.id)
        except:
            return "\_/"

# Кто подписан
class Subscriber(models.Model):
    id = models.AutoField(primary_key = True)
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    def Info(self):
        user = self.user
        return user.Info()
    def __str__(self):
        try:
            return str(self.id)
        except:
            return "\_/"

# Почты
class Email(models.Model):
    mail = models.EmailField(max_length=254, primary_key=True)
    confirm = models.BooleanField(default=False)
    confirm_code = models.CharField(default="", max_length=20)
    def __str__(self):
        return self.mail

# Приложения
class App(models.Model):
    app_id = models.AutoField(primary_key = True)
    app_name = models.CharField(max_length = 30,default="")
    app_creator = models.ForeignKey('Profile', on_delete=models.CASCADE)
    servise_key = models.CharField(max_length = 16, default="")
    verifery_app = models.BooleanField(default = False)
    def __str__(self):
        return "App#"+str(self.app_id)+"_"+self.app_name

# Логины и пароли
class AuthLoginInfo(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    email = models.ForeignKey('Email', on_delete=models.CASCADE)
    password = models.CharField(max_length = 20, default="")
    def __str__(self):
        return "Auth login/password for "+str(self.profile)

# Информация о входах в аккаунт
class AuthInfo(models.Model):
    auth_app = models.ForeignKey('App', on_delete=models.CASCADE)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    token = models.CharField(max_length = 20, primary_key = True, default="")
    work = models.BooleanField(default=True)
    def __str__(self):
        return "Auth token for "+str(self.profile)

# Все комментарии
class Comments(models.Model):
    id = models.AutoField(primary_key = True)
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    text = models.CharField(max_length=400, default='')
    create_date = models.DateTimeField(default=timezone.now)
    attachments = models.ForeignKey('Attachments', on_delete=models.CASCADE, blank=True, null=True)
    flagDelete = models.BooleanField(default=False)
    def delete(self):
        try:
            self.flagDelete = True
            self.save()
            return True
        except Exception as e:
            fixError(e)
        return False
    def Info(self):
        return {
            'id': self.id,
            'author': self.author.Info(),
            'text': self.text,
            'create_date': self.create_date,
            'attachments': self.attachments
        }
    def __str__(self):
        return "comment_"+str(self.id)+"_"+str(author)

# Прикрепления
class Attachments(models.Model):
    reductions = models.CharField(max_length=120)
    def get(self):
        return ""
    def __str__(self):
        return "Attachments..."

# Привелегии на сервере у пользователя
class Permissions(models.Model):
    sendmessage = models.IntegerField(default=0)
    viewStatsSystem = models.BooleanField(default=False)
    addAdministrator = models.BooleanField(default=False)
    getInformation = models.IntegerField(default=0)
    getChecks = models.IntegerField(default=5)
    getChecks = models.IntegerField(default=5)
    def __str__(self):
        return "Some of permissions..."

# Логи ошибок
class Errors(models.Model):
    date = models.DateTimeField(default=timezone.now)
    line = models.IntegerField()
    directory = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    def __str__(self):
        return "{hour}:{minute}:{second} {day}.{month}.{year}".format(
            hour=self.date.hour,
            minute = self.date.minute,
            second = self.date.second,
            day = self.date.day,
            month = self.date.month,
            year = self.date.year
        )

# НЕ СДЕЛАНО
# Фотография
class Photo(models.Model):
    url = models.CharField(max_length=100)
    creator = models.ForeignKey('Profile', on_delete=models.CASCADE)
    number = models.AutoField(primary_key=True)
    secret_key = models.CharField(max_length=15, null=True, blank=True)
    def __str__(self):
        s = "photo{id}_{key}".format(id=self.creator.id, key=self.number)
        if self.secret_key != "":
            s += "_{key}".format(key=self.secret_key)
        return s

# Ссылка, сокращение ссылок
class Link(models.Model):
    url = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    normal = models.BooleanField(default=False)
    reference = models.CharField(max_length=15)
    passedUser = models.IntegerField(default=0)
    count = 0
    def __str__(self):
        return "Link..."
    def get(self):
        global url
        self.count += 1
        if self.normal:
            return self.url
        return "http://{url}}/suspicious_link".format(
            url = url
        )


# Сообщение
class Message(models.Model):
    number = models.IntegerField(default=0)
    text = models.CharField(max_length=8000)
    attachments = models.ForeignKey('Attachments', on_delete=models.CASCADE)
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    flagReader = models.BooleanField(default=False)
    flagDelete = models.BooleanField(default=False)
    time = models.DateTimeField(default=timezone.now)
    def AllInfo(self):
        result = {'flag': False}
        if self.flagDelete == False:
            result = {
                'flag': True,
                'result':{
                    'id': self.number,
                    'from_id': self.author.Info(),
                    'text': self.text,
                    'time': {
                        'hour': self.time.hour,
                        'minute': self.time.minute,
                        'second': self.time.second,
                        'day': self.time.day,
                        'month': self.time.month,
                        'year': self.time.year
                    },
                    'readed': self.flagReader,
                    'attachments': self.attachments.Info()
                }
            }
        return result
    def Info(self):
        result = {'flag': False}
        if self.flagDelete == False:
            result = {
                'flag': True,
                'result':{
                    'id': self.number,
                    'from': self.author.Info(),
                    'text': self.text,
                }
            }
        return result
    def delete(self):
        if self.flagDelete:
            return False
        else:
            self.flagDelete = True
            self.save()
            return True
    def undelete(self):
        if self.flagDelete:
            self.flagDelete = False
            self.save()
            return {
                'flag': True,
                'message': self.Info()['result']
            }
        return {'flag': False}
    def __str__(self):
        return "Message from " + str(self.author) + " to "+str(self.reader)


# Диалог
class Dialog(models.Model):
    number = models.IntegerField(default=0)
    messageNumber = models.IntegerField(default=0)
    masterProfile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    messages = models.ManyToManyField('Message', blank=True)
    otherDialog = models.ForeignKey('Dialog', on_delete=models.CASCADE, null=True, blank=True)
    def get(self, begin=0, count=10):
        tmpUnread = self.messages.filter(flagReader = False, flagDelete = False, number__gt=begin)
        tmpCount = tmpUnread.count()
        result = {
            "id": self.number,
            "profile": self.profile.Info(),
            "count": self.messages.filter(flagDelete=False).count(),
            "unread": {
                'count': tmpUnread.count(),
                'messages': [_.Info()['result'] for _ in tmpUnread[min(tmpCount, begin) : min(begin+count, tmpCount)]]
            },
            "last_message": self.messages.filter(flagDelete = False)[0]
        }
        return result
    def getAll(self, begin=0, count=10):
        tmp = self.messages.filter(flagDelete = False, number__gt=begin)
        tmpCount = tmp.count()
        result = {
            "id": self.number,
            "profile": self.profile.Info(),
            "count": tmpCount,
            "unread": {
                'count': tmp.filter(flagReader = False).count(),
            },
            "messages": [
                _.AllInfo() for _ in tmp[min(tmpCount,begin) : min(begin+count, tmpCount)]
            ]
        }
        return result
    def sendMessage(self, profile, text="", attachment=""):
        try:
            self.messageNumber += 1
            msg = Message.objects.create(number=self.messageNumber, text=text, attachments=attachment,author=self.masterProfile)
            self.messages.add(msg)
            self.otherDialog.messages.add(msg)
            self.save()
            self.otherDialog.save()
            return True
        except Exception as e:
            fixError(e)
        return False
    def deleteMessage(self, message):
        try:
            msg = self.messages.filter(number=message)
            if msg.count() == 1:
                msg = msg[0]
                self.messages.remove(msg)
                self.save()
                return True
        except Exception as e:
            fixError(e)
        return False
    def deleteMessageForAll(self, message):
        try:
            msg = self.messages.filter(number=message)
            if msg.count() == 1:
                msg = msg[0]
                msg.flagDelete = True
                msg.save()
                return True
        except Exception as e:
            fixError(e)
        return False
    def __str__(self):
        return "Dialog #{number}".format(number=self.number)

"""
# НЕ СДЕЛАНО
# Беседа
class Conversation(models.Model):
    number = models.IntegerField(default=0)
    profiles = models.ManyToManyField('Profile', blank=True)
    messages = models.ManyToManyField('Message', blank=True)
    settings = models.ForeignKey('ConfSettings', blank=True)
    creator = models.ForeignKey('Profile', on_delete=models.CASCADE)
    def get(self, begin=0, count=10):
        tmpUnread = self.messages.filter(flagReader = False, flagDelete = False, number__gt=begin)
        tmpCount = tmpUnread.count()
        result = {
            "id": ("c" if self.profiles.count() > 0 else "") + str(self.number),
            "profiles": [_.Info() for _ in self.profiles],
            "count": self.messages.count(),
            "unread": {
                'count': tmpUnread.count(),
                'messages': [_.Info()['result'] for _ in tmpUnread[min(tmpCount, begin) : min(begin+count, tmpCount)]]
            },
            "last_message": self.messages.filter(flagDelete = False)[0]
        }
        return result
    def getAll(self, begin=0, count=10):
        tmp = self.messages.filter(flagDelete = False, number__gt=begin)
        tmpCount = tmp.count()
        result = {
            "id": ("c" if self.profiles.count() > 0 else "") + str(self.number),
            "profiles": [_.Info() for _ in self.profiles],
            "count": tmpCount,
            "unread": {
                'count': tmp.filter(flagReader = False).count(),
            },
            "messages": [
                _.AllInfo() for _ in tmp[min(tmpCount,begin) : min(begin+count, tmpCount)]
            ]
        }
        return result
    def __str__(self):
        return "Dialog #{number}".format(number=self.number)


class ConfSettings(models.Model):

    addUser = models.IntegerField(default=0)
"""

# Debug products
class Product(models.Model):
    number = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    create_by = models.ForeignKey('Profile', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    accept_level = models.IntegerField(default=0)
    def __str__(self):
        return "Product#{number}".format(number=self.numbr)


# Отчеты по найденным ошибкам
class Debug(models.Model):
    number = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey('Profile', on_delete=models.CASCADE)
    text = models.CharField(max_length=4000)
    title = models.CharField(max_length=100)
    type_problem = models.CharField(max_length=100)
    priority = models.IntegerField(default=0)
    severity = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    def Info(self):
        return {
            'number': self.number,
            'date':{
                'hour': self.date.hour,
                'minute': self.date.minute,
                'second': self.date.second,
                'day': self.date.day,
                'month': self.date.month,
                'year': self.date.year,
            },
            'title': self.title,
            'text': self.text,
            'type': self.type_problem,
            'priority': self.getPriority(),
            'severity': self.getSeverity(),
        }
    def getPriority(self):
        if self.priority==0:
            return "Low"
        elif self.priority==1:
            return "Medium"
        elif self.priority==2:
            return "High"
        else:
            return "Unregister priority"
    def getSeverity(self):
        if self.severity == 0:
            return "Trivial"
        elif self.severity == 1:
            return "Minor"
        elif self.severity == 2:
            return "Major"
        elif self.severity == 3:
            return "Critical"
        elif self.severity == 4:
            return "Blocker"
        else:
            return "Unregister severity"
    def __str__(self):
        return "Debug#{number}_{priority} {title} {date}".format(
            number=self.number,
            priority=self.priority,
            title=self.title,
            date="{day}.{month}.{year} {hh}:{mm}:{ss}".format(
                day=self.date.day,
                month=self.date.month,
                year=self.date.year,
                hh=self.date.hour,
                mm=self.date.minute,
                ss=self.date.second
            )
        )

class SystemParams(models.Model):
    text = models.CharField(max_length=100)
    type_text = models.CharField(max_length=3)
    value = models.CharField(max_length=100)

class EmailLetters(models.Model):
    to_mail = models.CharField(max_length=256)
    from_mail = models.CharField(max_length=256)
    subject = models.CharField(max_length=256)
    message = models.CharField(max_length=8000)
    flag = models.BooleanField(default=False)

class LinksMenu(models.Model):
    redirect_class = models.CharField(max_length=5)
    link = models.CharField(max_length=512)
