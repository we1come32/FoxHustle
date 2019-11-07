import requests

url = "http://94.103.88.10:8000"
urlAPI = "http://94.103.88.10:8000/api/"

def fixError(e, number):
    s = str(number)+") error"
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


class FoxHustle:
    __urlAPI = "http://94.103.88.10:8000/api/"
    __debug = False
    def setDebug(debug=False):
        self.__debug = debug
        return debug
    class APIError(BaseException):
        def __init__(self, error_code, error_description):
            self.txt = "Error code = {code}, error description: {desc}".format(code=error_code, desc=error_description)
    def __init__(self, app_id, key, v, debug=False):
        self.__app_id = app_id
        self.__key = key
        self.__debug = debug
        self.__v = v
    def login(self, **kwargs):
        method = self.__urlAPI + "auth.login"
        if 'debug' in kwargs.keys():
            self.__debug = kwargs['debug']
            del kwargs['debug']
        if 'app_id' not in kwargs.keys():
            kwargs['app_id'] = self.__app_id
        if 'key' not in kwargs.keys():
            kwargs['key'] = self.__key
        if 'v' not in kwargs.keys():
            kwargs['v'] = self.__v
        if self.__debug:
            print(method)
            print(kwargs)
        result = requests.post(method, data=kwargs)
        data = result.json()
        if 'error' in data.keys():
            error = data['error']
            raise self.APIError(error['error_code'], error['error_descriotion'])
        else:
            try:
                data = data['response']
            except:
                data = data
        return self.API(access_token=data['access_token'], v=kwargs['v'], app_id=kwargs['app_id'], key=kwargs['key'], debug=self.__debug)
    def register(self, **kwargs):
        method = self.__urlAPI + "auth.register"
        if 'debug' in kwargs.keys():
            self.__debug = kwargs['debug']
            del kwargs['debug']
        if 'app_id' not in kwargs.keys():
            kwargs['app_id'] = self.__app_id
        if 'key' not in kwargs.keys():
            kwargs['key'] = self.__key
        if 'v' not in kwargs.keys():
            kwargs['v'] = self.__v
        if self.__debug:
            print(method)
            print(kwargs)
        result = requests.post(method, data=kwargs)
        data = result.json()
        if 'error' in data.keys():
            error = data['error']
            raise self.APIError(error['error_code'], error['error_descriotion'])
        else:
            try:
                data = data['response']
            except:
                data = data
        print(data)
        return self.API(data['access_token'], v, app_id=kwargs['app_id'], key=kwargs['key'], v=kwargs['v'], debug=self.__debug)
    class API:
        __urlAPI = "http://94.103.88.10:8000/api/"
        class APIError(BaseException):
            def __init__(self, error_code, error_description):
                self.txt = "Error code = {code}, error description: {desc}".format(code=error_code, desc=error_description)
        class APIObject:
            __url = "http://94.103.88.10:8000"
            __urlAPI = "http://94.103.88.10:8000/api/"
            __allowObjects = [
                'photo',
                'auth',
                'profile',
                'app',
                'group',
            ]
            block = ""
            def __init__(self, access_token="", v="", name="", encoding=False, debug=False):
                self.__block = name
                self.__encoding = encoding
                self.__access_token = access_token
                self.__v = v
                self.__debug = debug
            def __getattr__(self, name):
                block="{start}{function}".format(
                        start=self.__block+("." if len(self.__block)>0 else ""),
                        function=name,
                    )
                if name in self.__allowObjects:
                    return self.__init__(name=block, encoding=self.__encoding,
                    access_token=self.__access_token,
                    v=self.__v,
                    debug=self.__debug)
                else:
                    return self.CallBlock(urlAPI=self.__urlAPI, method=block, access_token=self.__access_token, v=self.__v, debug=self.__debug)
            class CallBlock:
                class APIError(BaseException):
                    def __init__(self, error_code, error_description):
                        self.txt = "Error code = {code}, error description: {desc}".format(code=error_code, desc=error_description)
                def __init__(self, urlAPI="", method="", access_token="", v="", debug=False):
                    self.__urlAPI = urlAPI
                    self.__method = method
                    self.__access_token = access_token
                    self.__v = v
                    self.__debug = debug
                def __getResult(self, result):
                    data = result.json()
                    if self.__debug:
                        print(data)
                    try:
                        error = data['error']
                    except:
                        try:
                            return data['response']
                        except:
                            return data
                    if self.__debug:
                        print(error)
                    raise self.APIError(error['error_code'], error['error_descriotion'])
                def __call__(self, **params):
                    method = self.__urlAPI + self.__method
                    try:
                        params['access_token'] = self.__access_token
                        params['v'] = self.__v
                    except:
                        pass
                    if self.__debug:
                        print(method,"\nParams:")
                        [print("\t{name}{t}{value}".format(
                            name = _,
                            t = ("\t"*(5-len(_)//8)), 
                            value=params[_])) for _ in params.keys()]
                    result = requests.post(method, data=params)
                    data = self.__getResult(result)
                    return data
        __allowObjects = [
            'photo',
            'auth',
            'profile',
            'app',
            'group',
        ]
        def __init__(self, access_token="", v="", encoding=False, app_id="", key="", debug=False):
            import requests
            self.__debug = debug
            self.__app_id = app_id
            self.__key = key
            method = self.__urlAPI + "profile.get"
            result = requests.post(method, data={'access_token': access_token, 'v': v})
            data = result.json()
            if 'error' in data.keys():
                error = data['error']
                raise self.APIError(error['error_code'], error['error_descriotion'])
            else:
                try:
                    data = data['response']
                except:
                    data = data
            self.__access_token = access_token
            self.__encoding = encoding
        def __getattr__(self, name):
            if name == "access_token":
                return self.__access_token
            elif name in self.__allowObjects:
                return self.APIObject(name=name,encoding=self.__encoding, access_token=self.__access_token, v=self.__v, debug=self.__debug)

fox = FoxHustle(1, 'kasdfYGYGvbhbFu1',"1.0", debug=False)
user = fox.login(login='welc32', password='Katya1009')
spisok = [
    ('user.profile.setOnline', {},),
    ('user.profile.get', {"id": 2, "v": 56},),
]

for number, line in enumerate(spisok):
    method, data = line[0], line[1]
    #print(line)
    #try:
    #    result = method(*data)
    #    print("{number}) {result}".format(result=result, number=number))
    #except Exception as e:
    #    fixError(e, number)
    string = """
try:
    result = """+method+"""("""+"".join((a+", ") for a in ["{key}={value} ".format(key=_, value=data[_]) for _ in data.keys()])+""")
    #print(type(result))
    print("{number}) """+method+"""\t{result}".format(result=result, number="""+str(number+1)+"""))
except Exception as e:
    fixError(e, number)
"""
    #print(string)
    exec(string)