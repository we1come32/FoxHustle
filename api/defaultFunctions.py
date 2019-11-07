from .models import Errors
from django.utils import timezone



class ConstClass:
    class ConstError(TypeError): pass
    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except:
            self.__dict__[name] = ConstClass()
            return self.__dict__[name]
    def __setattr__(self, name, value):
        try:
            self.__dict__.has_key(name)
            raise self.ConstError("Can't rebind const(%s)"%name)
        except:
            self.__dict__[name] = value
    def __delattr__(self, name):
        raise self.ConstError("Can't delete const(%s)"%name)

const = ConstClass()

# Функция шифрования пары nickname#id в hash
def encode(string=""):
    def hex(number):
        s, var, count = "", "0123456789abcdefghijklmnopqrstuv", 0
        while number>0:
            s, number, count = var[number%16]+s, number//16, count+1
        s = "0"*(4-count)+s
        return s
    var, indexes, result = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_ #.0123456789", [], []
    if len(string)%2==1:
        string += " "
    tmp = 0
    for i, char in enumerate(string):
        if i%2:
            result.append(hex(tmp*67+var.index(char)))
        else:
            tmp = var.index(char)
    return "".join(_ for _ in result)
    
# Функция дешифрования hash в пару nickname#id
def decode(string=""):
    var, tmp, chars, constant = [], "", "0123456789abcdefghijklmnopqrstuv", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_ #.0123456789"
    for i, char in enumerate(string):
        if (i+1)%4==0:
            var.append(sum([chars.index(char2)*16**(3-i) for i, char2 in enumerate(tmp+char)]))
            tmp = ""
        else:
            tmp += char
    s = ""
    for _ in var:
        number1, number2 = _//67, _%67
        s += constant[number1]+constant[number2]
    if s[-1] == " ":
        s = s[:-1]
    return s