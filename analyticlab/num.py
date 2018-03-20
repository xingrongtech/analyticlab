# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 21:34:44 2018

@author: xingrongtech
"""

from math import log10, fabs, floor
from .const import Const
from .system.numberformat import f, getDigitFront, getDigitBehind, getBound
from .system.exceptions import expressionInvalidException

class Num():
    '''Num类为分析数值运算类，该类能够按照有效数字的保留和运算法则，进行数值的运算，即运算过程中会自动保留有效数字，最终运算结果按照有效数字位数输出。'''
    __num = 0.0
    __d_front = __d_behind = __d_valid = 0
    __sci_bound = 3
    __isRelative = False
    __lastIsPM = False
    
    def __init__(self, numStr, isRelative=False):
        '''初始化一个Num数值
        【参数说明】
        1.numStr（str）：要生成数值的字符串表达式，可以是一般计数法或科学记数法。注意要以字符串的形式给出，而不是直接给出int和float。
        2.isRelative（可选，bool）：是否为相对比（百分数形式）。默认isRelative=False。
        【应用举例】
        >>> t = Num('1.62')
        >>> x = Num('1.32e-8')
        >>> x = Num('1.32e-8', isRelative=True)
        【错误案例】
        >>> t = Num(float('1.62'))  #不能以float或int形式给出数值
        >>> t = Num('1.62s')  #不能给出单位'''
        if numStr == None:
            return
        if type(numStr) != str:
            raise expressionInvalidException('用于创建数值的参数无效，数值只能以字符串形式给出')
        sci_exp = 0  #默认不使用科学记数法
        self.__num = float(numStr)
        for E in ['e', 'E']:
            if numStr.__contains__(E):
                strArr = numStr.split(E)
                sci_exp = int(strArr[1])  #获得指数
                numStr = strArr[0]  #只保留numStr的指数前部分
                break
        strArr = numStr.split('.')  #以小数点为界分割数值
        self.__d_front = getDigitFront(abs(float(strArr[0])))
        if len(strArr) == 1:
            self.__d_behind = 0
            #对于整数，有效数字位数即为小数点前位数
            self.__d_valid = self.__d_front
        else:
            self.__d_behind = len(strArr[1])
            self.__d_valid = self.__d_front + self.__d_behind
            #考虑小数点后无效0位数（排除诸如0.0000的情况）
            if self.__d_front == 0 and float(strArr[1]) != 0:
                for i in range(len(strArr[1])):
                    if strArr[1][i] != '0':
                        break
                    self.__d_valid -= 1
        if sci_exp != 0:  #对于科学记数法，进行后续处理
            self.__d_front += sci_exp
            if self.__d_front < 0:
                self.__d_front = 0
            self.__d_behind -= sci_exp
            if self.__d_behind < 0:
                self.__d_behind = 0
        self.__isRelative = isRelative
        
    def __newInstance(self):
        return Num(None)
        
    def __str__(self):
        '''获得数值的文本格式
        【返回值】
        str：数值文本。
        【应用举例】
        >>> x1 = Num('13.7')
        >>> x2 = Num('1.32e-8')
        >>> str(x1)
        '13.7'
        >>> str(x2)
        '1.32e-08'
        '''
        if self.__isRelative:
            return self.__getRelative() + r'%'
        outStr = None
        if self.__num == 0:
            outStr = ('%.' + str(self.__d_behind) + 'f') % self.__num
        elif (not self.__isRelative) and getBound(self) >= self.__sci_bound:  #判断是否需要使用科学记数法
            if fabs(self.__num) < 1e-8 and getBound(self) > self.__d_behind:  #若数字本身很小，且数字的首位比小数点后位数还大，说明该数字是0
                outStr = ('%.' + str(self.__d_behind) + 'f') % 0.00
            else:
                outStr, useSci = self.__sci()
        else:
            outStr = ('%.' + str(self.__d_behind) + 'f') % self.__num
        return outStr
    
    def latex(self, useBrackets=0):
        '''获得数值的LaTeX格式
        【参数说明】
        useBrackets（可选，int）：在输出数值的LaTeX形式时，何时加括号，只能选择0、1、2、3中的一个。useBrackets为0时，表示任何情况下都不加括号；为1时，表示输出数值为负数或科学记数法时加括号；为2时，表示仅在输出数值为负数的时候加括号；为3时，表示仅在输出数值为科学记数法时加括号。默认useBrackets=0。
        【返回值】
        str：数值的LaTeX格式文本。
        【应用举例】
        >>> x1 = Num('1.32e-8')
        >>> x2 = Num('-1.32e8')
        >>> x1.latex()
        1.32\times 10^{-8}
        >>> x1.latex(1)
        \left(1.32\times 10^{-8}\right)
        >>> x2.latex(2)
        \left(-1.32\times 10^{8}\right)
        >>> x2.latex(3)
        \left(-1.32\times 10^{8}\right)'''
        if self.__isRelative:
            return self.__getRelative() + r'\%'
        outStr = None
        useSci = False
        if self.__num == 0:
            outStr = ('%.' + str(self.__d_behind) + 'f') % self.__num
        elif (not self.__isRelative) and getBound(self) >= self.__sci_bound:  #判断是否需要使用科学记数法
            if fabs(self.__num) < 1e-8 and getBound(self) > self.__d_behind:  #若数字本身很小，且数字的首位比小数点后位数还大，说明该数字是0
                outStr = ('%.' + str(self.__d_behind) + 'f') % 0.00
                useBrackets = 0
            else:
                outStr, useSci = self.__sci(useLatex=True)
        else:
            outStr = ('%.' + str(self.__d_behind) + 'f') % self.__num
        if (useBrackets == 1) and (self < 0 or useSci):
            outStr = r'\left(%s\right)' % outStr
        elif (useBrackets == 2) and (self < 0):
            outStr = r'\left(%s\right)' % outStr
        elif (useBrackets == 3) and useSci:
            outStr = r'\left(%s\right)' % outStr
        return outStr
    
    def __getRelative(self, dec=False):
        '''生成相对比值
        【参数说明】
        dec（可选，bool）：是否已纯数字形式（int或float）给出相对比值。dec为True时，以纯数字形式给出；为False时，以数值（Num）形式给出。默认dec=False。
        【返回值】
        ①dec为True时，返回值为float类型的相对比值；
        ②dec为False时，返回值为Num类型的相对比值。
        '''
        rate = self.__num * 100
        if dec:
            if abs(rate) < 0.00295:
                return f(self.__num, 6)
            elif abs(rate) < 0.01:
                return f(self.__num, 5)
            elif abs(rate) < 0.0295:
                return f(self.__num, 5)
            elif abs(rate) < 0.1:
                return f(self.__num, 4)
            elif abs(rate) < 0.295:
                return f(self.__num, 4)
            elif abs(rate) < 1:
                return f(self.__num, 3)
            elif abs(rate) < 2.95:
                return f(self.__num, 3)
            elif abs(rate) < 10:
                return f(self.__num, 2)
            else:
                return f(self.__num, 2)
        else:
            if abs(rate) < 0.00295:
                return '%.4f' % f(rate, 4)
            elif abs(rate) < 0.01:
                return '%.3f' % f(rate, 3)
            elif abs(rate) < 0.0295:
                return '%.3f' % f(rate, 3)
            elif abs(rate) < 0.1:
                return '%.2f' % f(rate, 2)
            elif abs(rate) < 0.295:
                return '%.2f' % f(rate, 2)
            elif abs(rate) < 1:
                return '%.1f' % f(rate, 1)
            elif abs(rate) < 2.95:
                return '%.1f' % f(rate, 1)
            elif abs(rate) < 10:
                return '%d' % f(rate, 0)
            else:
                return '%d' % f(rate, 0)
        
    def __repr__(self):
        '''获得数值的文本格式
        【返回值】
        str：数值文本。
        【应用举例】
        >>> x1 = Num('13.7')
        >>> x2 = Num('1.32e-8')
        >>> repr(x1)
        13.7
        >>> repr(x2)
        1.32e-08
        '''
        return self.__str__()
    
    def toFloat(self):
        '''将当前数值转换成float
        【返回值】
        float：数值的float形式。
        '''
        return float(self.__num)
    
    def toInt(self):
        '''将当前数值转换成int
        【返回值】
        int：数值的int形式。'''
        return int(self.__num)
    
    def fix(self):
        '''数字修约
        【返回值】
        Num：修约后的Num数值。'''
        if self.__d_behind > 0:
            fixedNumber = f(self.__num, self.__d_behind)
        else:
            fixedNumber = f(self.__num, self.__d_valid - self.__d_front)
        fixed = Num(None)
        fixed.__num = fixedNumber
        fixed.__setDigit(self.__d_front, self.__d_behind, self.__d_valid)
        fixed.__isRelative = self.__isRelative
        return fixed
    
    def remainOneMoreDigit(self):
        '''设定多保留一位有效数字
        【应用案例】
        >>> p1, p2 = Num('13.66'), Num('13.58')
        >>> d = (p1-p2)/p1
        >>> d
        6e-03
        >>> d.remainOneMoreDigit()
        >>> d
        5.9e-03'''
        self.__d_valid += 1
        if self.__d_valid - self.__d_front >= 0:  #对于多保留一位后，小数点后有有效数字的数值，小数点后位数多一位
            self.__d_behind += 1   #（如35.6→35.63，137→137.0）


    def cutOneDigit(self):
        '''设定少保留一位有效数字
        【应用案例】
        >>> p1, p2 = Num('13.66'), Num('13.58')
        >>> d = (p1-p2)/p1
        >>> d
        6e-03
        >>> d.remainOneMoreDigit()
        >>> d
        5.9e-03
        >>> d.cutOneDigit()
        >>> d
        6e-03'''
        self.__d_valid -= 1
        if self.__d_valid - self.__d_front > 0:  #对于去除多保留的一位之前，小数点后有有效数字的数值，小数点后位数少一位
            self.__d_behind -= 1   #（如35.63→35.6，137.0→137）
    
    
    def __sciDigit(self):
        '''获得数值的科学记数法的指数'''
        if self.__num == 0:
            return 0
        elif getBound(self) >= self.__sci_bound:
            if self.__d_front > 0:  #对于首个有效位在小数点前的数值
                theory_digit = max(self.__d_valid, self.__d_front) - self.__d_behind  #理论小数点前位数
                if fabs(theory_digit - 1) >= self.__sci_bound:  #通过理论有效数字位数再次检验是否需要使用科学记数法
                    return (theory_digit - 1)
                else:  #若转换后的数字数量级过小，不使用科学记数法
                    return 0
            else:  #对于首个有效位在小数点后的数值
                theory_digit = self.__d_behind - self.__d_valid  #理论小数点后位数
                if fabs(theory_digit + 1) >= self.__sci_bound:
                    return -(theory_digit + 1)
                else:
                    return 0
        else:
            return 0
    
    def __sci(self, useLatex=False):
        '''生成当前数值的科学记数法格式的字符串'''
        if self.__d_front > 0:  #对于首个有效位在小数点前的数值
            theory_digit = max(self.__d_valid, self.__d_front) - self.__d_behind  #理论小数点前位数
            converted = self.__num / 10**(theory_digit - 1)
            if fabs(theory_digit - 1) >= self.__sci_bound:  #通过理论有效数字位数再次检验是否需要使用科学记数法
                if useLatex:
                    return (('%.' + str(self.__d_valid - 1) + 'f') % converted + r'\times 10^{%d}') % (theory_digit - 1), True
                else:
                    return (('%.' + str(self.__d_valid - 1) + 'f') % converted + 'e+%02d') % (theory_digit - 1), True
            else:  #若转换后的数字数量级过小，不使用科学记数法
                return ('%.' + str(self.__d_behind) + 'f') % self.__num, False
        else:  #对于首个有效位在小数点后的数值
            theory_digit = self.__d_behind - self.__d_valid  #理论小数点后位数
            converted = self.__num * 10**(theory_digit + 1)
            if fabs(theory_digit + 1) >= self.__sci_bound:
                if useLatex:
                    return ('%.' + str(self.__d_valid - 1) + r'f\times 10^{-%d}') % (converted, theory_digit + 1), True
                else:
                    return ('%.' + str(self.__d_valid - 1) + r'fe-%02d') % (converted, theory_digit + 1), True
            else:
                return ('%.' + str(self.__d_behind) + 'f') % self.__num, False
    
    def __neg__(self):
        n = Num(None)
        n.__num = -self.__num
        n.__setDigit(self.__d_front, self.__d_behind, self.__d_valid)
        return n
    
    def setSciBound(self, bound):
        '''设定使用科学记数法的边界条件
        【参数说明】
        bound（int）：使用科学计数法的指数边界，即数值小于等于10**(-bound)数量级，或大于等于10**bound数量级时，使用科学记数法；否则仍使用一般数字表示法。未设定边界时，默认bound=3。
        【应用举例】
        >>> d = Num('0.15')
        >>> d = d/1000
        >>> d
        1.5e-04
        >>> d.setSciBound(5)
        0.00015
        '''
        self.__sci_bound = bound
    
    def __setDigit(self, digit_front, digit_behind, digit_valid):
        '''设置有效数字位数'''
        self.__d_front = digit_front
        self.__d_behind = digit_behind
        self.__d_valid = digit_valid
        
    def setIsRelative(self, isRelative):
        '''设定是否为相对比（百分数形式）
        【参数说明】
        isRelative：是否为相对比。
        '''
        self.__isRelative = isRelative
        
    def __abs__(self):
        n = Num(None)
        n.__num = fabs(self.__num)
        n.__setDigit(self.__d_front, self.__d_behind, self.__d_valid)
        n.__lastIsPM = self.__lastIsPM
        return n
        
    def __gt__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num > obj
        else:
            return self.__num > obj.__num
    
    def __lt__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num < obj
        else:
            return self.__num < obj.__num
    
    def __ge__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num >= obj
        else:
            return self.__num >= obj.__num
    
    def __le__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num <= obj
        else:
            return self.__num <= obj.__num
        
    def __add__(self, obj):
        n = Num(None)
        n.__lastIsPM = True
        if type(obj) == int or type(obj) == float:  #数值与常数相加，不影响有效数字位数
            n.__num = self.__num + obj
            n.__setDigit(self.__d_front, self.__d_behind, self.__d_valid)
        elif type(obj) == Const:
            n.__num = self.__num + obj.value()
            n.__setDigit(self.__d_front, self.__d_behind, self.__d_valid)
        elif type(obj) == Num:  #数值相加，要考虑有效数字位数
            if obj.__num == 0:  #若与当前数值obj相加的数值为0，则相加结果为原数值self
                return self
            elif self.__num == 0:  #若与当前数值obj相加的数值不为0，而数值自身为0，则相加结果为当前数值obj
                return obj
            n.__num = self.__num + obj.__num
            if max(self.__d_front, obj.__d_front) > 0:  #对于首位在小数点前的数值
                n.__d_front = max(self.__d_front, obj.__d_front)  #取小数点前位数较大者作为小数点前位数
                n.__d_behind = min(self.__d_behind, obj.__d_behind)  #取小数点后位数较小者作为小数点后位数
                n.__d_valid = n.__d_front + n.__d_behind
                delta = max(self.__d_front - self.__d_valid, obj.__d_front - obj.__d_valid);
                #若存在某数的个位不是有效位的情况，减去小数点前有效零位中的较大者
                if (delta > 0):
                    n.__d_valid -= delta
            else:  #对于首位在小数点后的数值
                self_digit = self.__d_valid - self.__d_behind  #获得小数点后位数（负数）
                obj_digit = obj.__d_valid - obj.__d_behind #同上
                max_digit = max(self_digit, obj_digit)
                min_digitbehind = min(self.__d_behind, obj.__d_behind)
                n.__d_valid = min_digitbehind + max_digit
                n.__d_behind = min_digitbehind
                n.__d_front = 0
        else:
            return obj.__radd__(self)
        return n
    
    def __radd__(self, obj):
        return self.__add__(obj)
        
    def __sub__(self, obj):
        if type(obj) == int or type(obj) == float or type(obj) == Num:
            newObj = -obj
        elif type(obj) == Const:
            newObj = -obj.value()
        else:
            return obj.__rsub__(self)
        return self.__add__(newObj)
    
    def __rsub__(self, obj):
        if type(obj) == int or type(obj) == float or type(obj) == Num:
            new = -obj
        elif type(obj) == Const:
            new = -obj.value()
        else:
            return obj.__sub__(self)
        sub = self.__add__(new)
        sub.__num = -sub.__num
        return sub
    
    def __resetDigit(self):
        '''重设有效数字位数（适用于非加减、取负之外的全部运算，即只需要有效数字位数，不需要小数点前、后位数的情形）'''
        if not self.__lastIsPM:  #只有上一位是加减、取负运算，才能重新获取有效数字位数
            return
        usign = fabs(self.__num)
        if usign == 0:
            self.__d_valid = 1
            return
        firstUnit = floor(log10(usign * 1.000000000001)) + 1
        if self.__d_front > 0:  #若重设前的首位记为在小数点前（如11.37-11.32=0.05，self.__d_front=2）
            delta = self.__d_front - firstUnit  #重设前后有效数字位数差值为其首位的差值（11.37-11.32=0.05，self.__d_front=2，firstUnit=-1）
            d_valid = self.__d_valid - delta  # 4 - 3 = 1
        else:
            d_valid = self.__d_behind + firstUnit  #重设后有效数字位数为小数点后位数与首位的差值（0.0339-0.0343=-0.0004，self.__d_behind=4，firstUnit=-3）
        if d_valid < self.__d_valid:
            self.__d_valid = d_valid  #只有重设后的有效数字位数小于之前的有效数字位数（即相对偏差变大时），才更新有效数字位数
    
    def __mul__(self, obj):
        n = Num(None)
        self.__resetDigit()
        if type(obj) == int or type(obj) == float:  #数值与常数相乘，不影响有效数字位数
            n.__num = self.__num * obj
            n.__d_valid = self.__d_valid
        elif type(obj) == Const:
            n.__num = self.__num * obj.value()
            n.__d_valid = self.__d_valid
            if obj._Const__isHPercent:  #当被乘常数为100%时，将当前数值设定为相对比值
                n.__isRelative = True
        elif type(obj) == Num:  #数值相乘，要考虑有效数字位数
            obj.__resetDigit()
            n.__num = self.__num * obj.__num
            n.__d_valid = min(self.__d_valid, obj.__d_valid)  #最小有效数字位数原则
        else:
            return obj.__rmul__(self)
        usign = fabs(n.__num)
        n.__d_front = getDigitFront(usign)
        n.__d_behind = getDigitBehind(usign, n.__d_valid, n.__d_front)
        return n
    
    def __rmul__(self, obj):
        return self.__mul__(obj)
    
    def __truediv__(self, obj):
        n = Num(None)
        self.__resetDigit()
        if type(obj) == int or type(obj) == float or type(obj) == Const:  #数值与常数相乘，不影响有效数字位数
            if type(obj) == Const:
                n.__num = self.__num / obj.value()
            else:
                n.__num = self.__num / obj
            n.__d_valid = self.__d_valid
            usign = fabs(n.__num)
            n.__d_front = getDigitFront(usign)
            n.__d_behind = getDigitBehind(usign, n.__d_valid, n.__d_front)
        elif type(obj) == Num:  #数值相乘，要考虑有效数字位数
            obj.__resetDigit()
            n.__num = self.__num / obj.__num
            n.__d_valid = min(self.__d_valid, obj.__d_valid)  #最小有效数字位数原则
            usign = fabs(n.__num)
            n.__d_front = getDigitFront(usign)
            n.__d_behind = getDigitBehind(usign, n.__d_valid, n.__d_front)
        else:
            return obj.__rtruediv__(self)
        return n
    
    def __rtruediv__(self, obj):
        n = Num(None)
        self.__resetDigit()
        if type(obj) == int or type(obj) == float or type(obj) == Const:  #数值与常数相乘，不影响有效数字位数
            if type(obj) == Const:
                n.__num = obj.value() / self.__num
            else:
                n.__num = obj / self.__num
            n.__d_valid = self.__d_valid
            usign = fabs(n.__num)
            n.__d_front = getDigitFront(usign)
            n.__d_behind = getDigitBehind(usign, n.__d_valid, n.__d_front)
        elif type(obj) == Num:  #数值相乘，要考虑有效数字位数
            obj.__resetDigit()
            n.__num = obj.__num / self.__num
            n.__d_valid = min(self.__d_valid, obj.__d_valid)  #最小有效数字位数原则
            usign = fabs(n.__num)
            n.__d_front = getDigitFront(usign)
            n.__d_behind = getDigitBehind(usign, n.__d_valid, n.__d_front)
        else:
            return obj.__truediv__(self)
        return n
    
    def __pow__(self, b):
        n = Num(None)
        self.__resetDigit()
        if type(b) == Const:
            n.__num = self.__num ** b.value()
        else:
            n.__num = self.__num ** b
        n.__d_valid = self.__d_valid
        usign = fabs(n.__num)
        n.__d_front = getDigitFront(usign)
        n.__d_behind = getDigitBehind(usign, n.__d_valid, n.__d_front)
        return n
    
    def __rpow__(self, a):
        n = Num(None)
        self.__resetDigit()
        if type(a) == Const:
            n.__num = a.value() ** self.__num
        else:
            n.__num = a ** self.__num
        #指数（如pH）的小数点后位数（包括0）为所得数的有效数字位数
        n.__d_valid = self.__d_behind
        if n.__d_valid == 0:
            n.__d_valid = 1
        usign = fabs(n.__num)
        n.__d_front = getDigitFront(usign)
        n.__d_behind = getDigitBehind(usign, n.__d_valid, n.__d_front)
        return n
