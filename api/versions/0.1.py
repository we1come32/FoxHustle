from datetime import datetime
import random

# models
from Auth.models import *
from Profile.models import *
from BugTracker.models import *
from Message.models import *
from Wall.models import *


# Получение информации об ошибке по её номеру
def getErrorCode(code):
    if code == 2:
        error_text = "Not found app"
    elif code == 3:
        error_text = "Incorrect email or password"
    elif code == 4:
        error_text = "Not all parameter are sent"
    elif code == 5:
        error_text = "Incorrect {}" 
    elif code == 6:
        error_text = "Access denied" 
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

# check time
def check_time(function):
	def new_function(*args, **kwargs):
		global max_time, min_time, count, summ
		_time = time()
		value = function(*args, **kwargs)
		_time = time() - _time
		if max_time < _time:
			max_time = _time
		if min_time > _time:
			min_time = _time
		count += 1
		summ += _time
		return _time, value
	return new_function

# randomize chars in 'text'
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

# generate unique text certain length
def genKey(length):
	chifr, l = randomChars("0123456789qwertyuiopasdfghklzxcvbnm"), 35
	result = "".join(chifr[randint(0, l - 1)] for _ in range(length))
	return result

# generate tokens
def encoding(data):
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
	return ("".join((chifr[number] + result[number]) for number in range(length)) + result[length:])

# decoding tokens
def decoding(data):
	try:
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
	except:
		pass
	return False

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

# Функция получения привелегий
def getPermissions(requests):
	need_params = [
		(str, 'access_token', lambda tmp: True, True, ""),
		(str, 'app_id', lambda tmp: True, False, getErrorCode(4)),
		]
	result = getData(request, need_params)
	if result['flag']:
		params = result['result']
		token = params['access_token']
		data = decoding(token)
		if type(data) == dict:
			return data
		else:
			tmp = getErrorCode(5)
			tmp['error']['error_descriotion'].format('access_token')
			return tmp
	else:
		tmp = getErrorCode(5)
		tmp['error']['error_descriotion'].format('app_id')
		return tmp

# not wrided          ------------------------------------------------------------------------------------------
def auth_login(request):
	user = getPermissions(request)
	if 'error' in user.keys():
		return user
	elif user['type'] == 'guest':
		need_params = [
			(str, 'access_token', lambda tmp: True, True, ""),
			(str, 'app_id', lambda tmp: True, False, getErrorCode(4)),
			]

# logout
def auth_logout(request):
	user = getPermissions(request)
	if 'error' in user.keys():
		return user
	elif user['type'] in ['guest']:
		tmp = getErrorCode(5)
		tmp['error']['error_descriotion'].format('access_token')
		return tmp
	elif user['type'] in ['bot']:
		tmp = getErrorCode(6)
		return tmp



def profile_get(request):
	user = getPermissions(request)
	if 'error' in user.keys():
		return user
	elif type(user) == bool:
		need_params = [
			(str, 'id', lambda tmp: True, True, 0),
			(str, 'ds_id', lambda tmp: True, True, 0),
			(str, 'vk_id', lambda tmp: True, True, 0),
			(str, 'tg_id', lambda tmp: True, True, 0),
			(str, 'go_id', lambda tmp: True, True, 0),
			(str, 'fb_id', lambda tmp: True, True, 0),
			(str, 'in_id', lambda tmp: True, True, 0),
			]
		result = getData(request, need_params)
		if result['flag']:
			params = result['result']
			search_data = {}; c = 0
			if params['id'] != 0:
				search_data['id'] = params['id']; c+=1
			if params['ds_id'] != 0:
				search_data['ds_id'] = params['ds_id']; c+=1
			if params['vk_id'] != 0:
				search_data['vk_id'] = params['vk_id']; c+=1
			if params['tg_id'] != 0:
				search_data['tg_id'] = params['tg_id']; c+=1
			if params['go_id'] != 0:
				search_data['go_id'] = params['go_id']; c+=1
			if params['fb_id'] != 0:
				search_data['fb_id'] = params['fb_id']; c+=1
			if params['in_id'] != 0:
				search_data['in_id'] = params['in_id']; c+=1
			if c == 0:
				if user['type'] == 'user':
					try:
						tmp = Profile.objects.get(id=user['id'])
						return {'result': [tmp],}
					except:
						pass
				return getErrorCode(6)
			else:
				try:
					tmp = Profile.objects.get(**search_data)
				except:
					return {'result': []}





method = {
	'auth.login': auth_login,
	'auth.logout': auth_logout,
}

allow_methods = [
	'auth.login',
	'auth.logout',
	'auth.createapp',
	'auth.confirm',
]






