# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 20:04:16 2018

@author: xingrongtech
"""

from sympy import Symbol
from ..amath import sqrt
from ..num import Num
from ..numitem import NumItem
from ..lsym import LSym
from ..lsymitem import LSymItem
from ..latexoutput import LaTeX
from ..uncertainty import ACategory, BCategory, unc
from ..system.exceptions import expressionInvalidException

class Measure(unc.Uncertainty):
    '''Measure为测量类，该类通过给出一组直接测量的数据以及测量该数据所使用的仪器，从而计算单个测量的标准不确定度。'''
    AMethod = 'auto'  #静态属性，控制A类不确定度如何计算
    
    __value = None
    
    def __init__(self, data, instrument=None, sym=None, unit=None, description=None):
        '''初始化一个Measure测量
        【参数说明】
        1.data：测量数据，可以是单个测量值、一个样本或多个样本，是用于计算A类不确定度的依据。data可以是以下数据类型：
        (1)单个测量值：
        ①Num：直接给出单个测量值的Num数值；
        ②str：通过给出数值的字符串表达式，得到对应的Num数值。
        ③LSym：若LaTeX符号中有数值（即创建LSym时，sNum为str或Num类型），则可以通过给出LSym，得到LSym中的Num数值。
        (2)一个样本：
        ①NumItem：直接给出样本的NumItem数组；
        ②str：对于还没有转换成Num的数值，将数值以空格隔开，表示成字符串表达式，以此生成样本的NumItem数组；
        ③list<Num>：对于已经转换成Num的数值，将数值用list表示出，以此生成样本的NumItem数组；
        ④list<LSym>：若LaTeX符号中有数值（即创建LSym时，sNum为str或Num类型），则可以通过给出LSym的列表，得到每个LSym中的Num数值，以此生成样本的NumItem数组；
        ⑤LSymItem：通过给出LSymItem，得到LSymItem中对应的Num数值作为样本数据。
        (3)多个样本：
        ①list<NumItem>：直接给出每个样本的NumItem数组，得到多个样本数组；
        ②list<str>：列表中的每个str生成一个样本数组，从而得到多个样本数组；
        ③list<LSymItem>：通过给出LSymItem，得到每个LSymItem中对应的Num数值作为每个样本的数据，从而得到多个样本数组。
        2.instrument（可选，Instrument）：测量仪器，是获得测量结果单位、用于计算B类不确定的依据。当测量仪器为None时，将不会计算B类不确定度。默认instrument=None。
        3.sym（可选，str）：测量的符号。当用于导入的data中有sym（比如LSym、LSymItem、NumItem），且参数sym为None时，将使用data中的sym，否则使用参数sym作为符号。默认sym=None。
        4.unit（可选，str）：测量的单位。当给定测量仪器时，使用测量仪器的单位，否则使用参数unit。默认unit=None。
        5.description（可选，str）：在展示不确定度时，作为对测量的语言描述。默认description=None。'''
        self.__data = None
        self.__description = description
        self.__instrument = instrument
        if instrument == None:
            self.__unit = unit
        else:
            self.__unit = instrument.unit
        if type(data) == Num or type(data) == LSym:
            self.__uA = None  #单个测量值、空值没有A类不确定度
            if type(data) == Num:
                self.__value = data
            elif type(data) == LSym:
                self.__value = data.num()
                if sym == None:
                    sym = data.sym()
        elif type(data) == LSymItem:
            self.__uA = 'single'
            if type(data._LSymItem__lsyms) == list:
                dd = data._LSymItem__lsyms
            else:
                dd = data._LSymItem__lsyms.values()
            self.__data = NumItem([d._LSym__sNum for d in dd], sym=data._LSymItem__symText, unit=self.__unit)
        elif type(data) == str:
            isItem = (data.find(' ') >= 0)
            if isItem:
                self.__uA = 'single'
                self.__data = NumItem(data)
                if sym != None:
                    self.__data._NumItem__sym = '{' + sym + '}'
            else:
                self.__uA = None
                self.__value = Num(data)
        elif type(data) == NumItem:
            self.__uA = 'single'
            self.__data = data
            self.__data._NumItem__unit = self.__unit
        elif type(data) == list:
            self.__uA = 'comb'
            if len(data) == 0:
                raise expressionInvalidException('用于创建测量的参数无效')
            elif type(data[0]) == str:
                self.__data = [NumItem(d, sym=sym) for d in data]
            elif type(data[0]) == NumItem:
                self.__data = data
            elif type(data[0]) == LSymItem:
                self.__data = []
                for i in range(len(data)):
                    if type(data[i]._LSymItem__lsyms) == list:
                        lsymList = data[i]._LSymItem__lsyms
                    else:
                        lsymList = data[i]._LSymItem__lsyms.values()
                    data_i = NumItem([d._LSym__sNum for d in lsymList], sym=data[i]._LSymItem__symText, unit=self.__unit)
                    self.__data.append(data_i)
            elif type(data[0]) == Num:
                self.__data = NumItem(data, sym=sym, unit=self.__unit)
            elif type(data[0]) == LSym:
                self.__data = NumItem([d.num() for d in data], sym=sym, unit=self.__unit)
            else:
                raise expressionInvalidException('用于创建测量的参数无效')
            self.__value = NumItem([d.mean() for d in self.__data]).mean()
        else:
            raise expressionInvalidException('用于创建测量的参数无效')
        if type(self.__data) == NumItem:
            self.__value = self.__data.mean()
            if sym == None:
                self.__sym = self.__data._NumItem__sym
            else:
                self.__sym = '{' + sym + '}'
                self.__data._NumItem__sym = self.__sym
        else:
            self.__sym = '{' + sym + '}'
        self._Uncertainty__symbol = Symbol(self.__sym, real=True)
        self._Uncertainty__measures = {}
        self._Uncertainty__lsyms = {}
        self._Uncertainty__consts = {}
    
    def unc(self, process=False, needValue=False, remainOneMoreDigit=False):
        '''获得标准不确定度
        【参数说明】
        1.process（可选，bool）：是否展示计算过程。默认proces=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        3.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
        【返回值】
        Num：标准不确定度数值。'''
        oneMoreDigit = remainOneMoreDigit or (self.__uA != None and self.__instrument != None)
        if self.__uA != None:  #判断是否需要计算A类不确定度
            if self.__uA == 'single':
                if Measure.AMethod == 'auto':
                    if len(self.__data) > 9:  #样本数量最大的组为9以上时，使用Bessel法
                        uA = ACategory.Bessel(self.__data, process, True, oneMoreDigit)
                    else:
                        uA = ACategory.Range(self.__data, process, True, oneMoreDigit)
                elif Measure.AMethod == 'Bessel':
                    uA = ACategory.Bessel(self.__data, process, True, oneMoreDigit)
                elif Measure.AMethod == 'Range':
                    uA = ACategory.Range(self.__data, process, True, oneMoreDigit)
                elif Measure.AMethod == 'CollegePhysics':
                    uA = ACategory.CollegePhysics(self.__data, process, True, oneMoreDigit)
            elif self.__uA == 'comb':
                uA = ACategory.CombSamples(self.__data, Measure.AMethod, process, True, self.__sym, self.__unit, oneMoreDigit)
        if self.__instrument != None:  #判断是否需要计算B类不确定度
            uB = BCategory.b(self.__instrument, self.__sym, process, True, oneMoreDigit)
        if process:
            latex = LaTeX()
            if self.__uA != None:
                latex.add(uA[1])
                uA = uA[0]
            if self.__instrument != None:
                latex.add(uB[1])
                uB = uB[0]
        if self.__uA != None and self.__instrument != None:
            u = sqrt(uA**2 + uB**2)
            if not remainOneMoreDigit:
                u.cutOneDigit()
            if process:
                latex.add(r'u_{%s}=\sqrt{{u_{%s A}}^{2}+{u_{%s B}}^{2}}=\sqrt{%s^{2}+%s^{2}}=%s{\rm %s}' % (self.__sym, self.__sym, self.__sym, uA.latex(1), uB.latex(1), u.latex(), self.__unit))
        elif self.__uA != None:
            u = uA
            if not remainOneMoreDigit:
                u.cutOneDigit()
            if process:
                latex.add(r'u_{%s}=u_{%s A}=%s{\rm %s}' % (self.__sym, self.__sym, u.latex(), self.__unit))
        elif self.__instrument != None:
            u = uB
            if not remainOneMoreDigit:
                u.cutOneDigit()
            if process:
                latex.add(r'u_{%s}=u_{%s B}=%s{\rm %s}' % (self.__sym, self.__sym, u.latex(), self.__unit))
        if self._Uncertainty__K != None:
            P = unc.KTable[self._Uncertainty__K]
            u = u * self._Uncertainty__K
            if not remainOneMoreDigit:
                u.cutOneDigit()
            if process:
                latex.add(r'u_{%s,%s}=%g u_{%s}=%s{\rm %s}' % (self.__sym, P[1], self._Uncertainty__K, self.__sym, u.latex(), self.__unit))
        if process:
            if needValue:
                return u, latex
            else:
                return latex
        return u
            
    def uncLSym(self):
        '''获得标准不确定度公式的LaTeX符号
        【返回值】
        LSym：标准不确定度公式的LaTeX符号。'''
        return LSym('u_{%s}' % self.__sym, self.unc())
    
    def equ(self):
        '''获得计算结果
        【返回值】
        Num：计算结果数值。'''
        return self.__value
    
    def equLSym(self):
        '''获得计算式的LaTeX符号
        【返回值】
        LSym：计算式的LaTeX符号。'''
        return LSym(self.__sym, self.__value)