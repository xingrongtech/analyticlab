# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 20:04:16 2018

@author: xingrongtech
"""

from sympy import Symbol
from quantities.quantity import Quantity
from . import ACategory, BCategory, measure
from .ins import Ins
from ..amath import sqrt
from ..num import Num
from ..numitem import NumItem
from ..lsym import LSym
from ..lsymitem import LSymItem
from ..latexoutput import LaTeX
from ..system.exceptions import expressionInvalidException
from ..system.unit_open import openUnit, closeUnit
from ..system.text_unicode import usub
from ..system.format_units import format_units_unicode, format_units_latex

class BaseMeasure(measure.Measure):
    '''BaseMeasure为直接测量类，该类通过给出一组直接测量的数据以及测量该数据所使用的仪器或方法，从而计算单个直接测量的不确定度。'''
    AMethod = 'auto'  #静态属性，控制A类不确定度如何计算
    __value = None
    __staUnc = None
    __q = 1
    __data = None
    __linearfit_data = None
    useRelUnc = False  #决定由str、latex生成的测量结果中，不确定度是否使用相对不确定度表示
    
    def __init__(self, data, instrument=None, unit=None, sym=None, description=None):
        '''初始化一个BaseMeasure直接测量
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
        3.unit（可选，str）：测量的单位。给出unit时，会优先使用unit的单位；若没有给出unit，则当给定测量仪器时，使用测量仪器的单位；若未给出测量仪器的单位，则当data中有单位（比如Num、LSym、NumItem、LSymItem，或list<Num>、list<LSym>、list<NumItem>、list<LSymItem>中首个元素）则使用data中的单位，否则没有单位。默认unit=None。
        4.sym（可选，str）：符号。一般情况下不需要给出，当需要展示计算过程时，最好给出。当sym未给出时，若data以NumItem形式给出且包含sym，则使用data的sym，否则没有sym。默认sym=None。
        5.description（可选，str）：在展示测量（含测量值和不确定度）时，作为对测量的语言描述。默认description=None。'''
        self.__instrument = instrument
        if unit != None:
            self.__q = Quantity(1., unit) if type(unit) == str else unit
            if instrument != None:
                instrument.q = self.__q
        elif instrument != None and instrument.q != None:
            self.__q = instrument.q
        if type(data) == Num or type(data) == LSym:
            self.__uA = None  #单个测量值、空值没有A类不确定度
            if type(data) == Num:
                self.__value = data
                if type(self.__q) != Quantity:
                    self.__q = data._Num__q
            elif type(data) == LSym:
                self.__value = data.num()
                if type(self.__q) != Quantity:
                    self.__q = data.num()._Num__q
                if sym == None:
                    sym = data.sym()
        elif type(data) == LSymItem:
            self.__uA = 'single'
            self.__data = NumItem(data)
            if type(self.__q) != Quantity:
                self.__q = data._LSymItem__q
        elif type(data) == str:
            isItem = (data.find(' ') >= 0)
            if isItem:
                self.__uA = 'single'
                self.__data = NumItem(data)
                if type(self.__q) != int:
                    self.__data._NumItem__q = self.__q
            else:
                self.__uA = None
                self.__value = Num(data)
                if type(self.__q) != int:
                    self.__value._Num__q = self.__q
        elif type(data) == NumItem:
            self.__uA = 'single'
            self.__data = data
            if type(self.__q) != Quantity:
                self.__q = data._NumItem__q
            else:
                data._NumItem__q = self.__q
                data._NumItem__qUpdate()
        elif type(data) == list:
            self.__uA = 'comb'
            if len(data) == 0:
                raise expressionInvalidException('用于创建测量的参数无效')
            elif type(data[0]) == str:
                self.__data = [NumItem(di) for di in data]
                if type(self.__q) != int:
                    for di in self.__data:
                        di._NumItem__q = self.__q
                        di._NumItem__qUpdate()
            elif type(data[0]) == NumItem:
                self.__data = data
                if type(self.__q) != Quantity:
                    self.__q = self.__data[0]._NumItem__q
                else:
                    if sym == None:
                        for di in self.__data:
                            di._NumItem__q = self.__q
                            di._NumItem__qUpdate()
                    else:
                        for di in self.__data:
                            di._NumItem__q = self.__q
                            di._NumItem__qUpdate()
                            di._NumItem__sym = sym
            elif type(data[0]) == LSymItem:
                self.__data = [NumItem(di) for di in data]
                if type(self.__q) != Quantity:
                    self.__q = self.__data[0]._NumItem__q
                else:
                    for di in self.__data:
                        di._NumItem__q = self.__q
                        di._NumItem__qUpdate()
            elif type(data[0]) == Num or type(data[0]) == LSym:
                self.__data = NumItem(data)
                if type(self.__q) != Quantity:
                    self.__q = self.__data._NumItem__q
                else:
                    self.__data._NumItem__q = self.__q
                    self.__data._NumItem__qUpdate()
            else:
                raise expressionInvalidException('用于创建直接测量的参数无效')
            self.__value = NumItem([d.mean() for d in self.__data]).mean()
        else:
            raise expressionInvalidException('用于创建直接测量的参数无效')
        if type(self.__data) == NumItem:
            self.__value = self.__data.mean()
            if sym == None:
                self.__sym = self.__data._NumItem__sym
            else:
                self.__sym = '{%s}' % sym
                self.__data._NumItem__sym = self.__sym
        else:
            if sym == None:
                self.__sym = '{x_{%d}}' % id(self)
            else:
                self.__sym = '{%s}' % sym
            if self.__uA == 'comb':
                for i in range(len(self.__data)):
                    self.__data[i]._NumItem__sym = '{%s_{%d}}' % (self.__sym, i+1)
        self._Measure__symbol = Symbol(self.__sym, real=True)
        if unit != None:
            self.__value._Num__q = self.__q
            if instrument != None:
                instrument.q = self.__q
        if measure.Measure.process:
            self._Measure__vl = LSym(self.__sym, self.__value)
        else:
            self._Measure__vl = self.__value
        if description == None:
            self.__description = self.__sym
        else:
            self.__description = description
        self._Measure__baseMeasures = {}
        self._Measure__measures = {}
        self._Measure__lsyms = {}
        self._Measure__consts = {}
        self.__staUnc = self.__calStaUnc()
        self.useRelUnc = False
        
    def fromReport(report, unit=None, sym=None, distribution=1, description=None, **param):
        '''从不确定度报告中获得BaseMeasure
        【参数说明】
        1.report（str）：形如`114.818(3)`的不确定度报告。
        2.distribution（可选，int）：分布类型，从以下列表中取值。默认distribution=Ins.rectangle。
        ①Ins.norm：正态分布；
        ②Ins.rectangle：矩形分布；
        ③Ins.triangle：三角分布；
        ④Ins.arcsin：反正弦分布；
        ⑤Ins.twopoints：两点分布；
        ⑥Ins.trapezoid：梯形分布，此分布下需要通过附加参数beta给出β值。
        3.unit（可选，str）：测量的单位。默认unit=None。
        4.sym（可选，str）：符号。一般情况下不需要给出，当需要展示计算过程时，最好给出。默认sym=None。
        5.description（可选，str）：在展示测量（含测量值和不确定度）时，作为对测量的语言描述。默认description=None。'''
        rlist = report[:-1].split('(')
        v = rlist[0]
        zero_behind = len(v.split('.')[1])-len(rlist[1])  #小数点后空零的数量 
        half_width = '0.' + zero_behind*'0' + rlist[1]
        if len(param) == 0:
            rIns = Ins(half_width, distribution, unit)
        else:
            rIns = Ins(half_width, distribution, unit, beta=param['beta'])
        return BaseMeasure(v, rIns, sym=sym, description=description)
    
    def value(self, process=False, needValue=False):
        '''获得测量值
        【参数说明】
        1.process（可选，bool）：是否展示计算过程。默认proces=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        【返回值】
        ①process为False时，返回值为Num类型的测量值。
        ②process为True且needValue为False时，返回值为LaTeX类型的计算过错。
        ③process为True且needValue为True时，返回值为Num类型的测量值及其LaTeX类型的计算过程组成的元组。
        Num：测量值。'''
        if process:
            if self.__uA == 'single':
                return self.__data.mean(True, needValue)
            elif self.__uA == 'comb':
                m = len(self.__data)
                #根据所有样本的样本数量是否一致，判断使用哪个公式
                nSame = True
                n = len(self.__data[0])
                for di in self.__data:
                    if len(di._NumItem__arr) != n:
                        nSame = False
                        break
                sciDigit = max([di._NumItem__sciDigit() for di in self.__data], key=lambda digit: abs(digit))
                large_brac = max([len([x for x in di._NumItem__arr if x < 0]) for di in self.__data]) > 0
                sub_sumExpr = []
                if sciDigit == 0:
                    for di in self.__data:
                        plusExpr = '+'.join([n.dlatex(2) for n in di._NumItem__arr])
                        if len([x for x in di._NumItem__arr if x < 0]) == 0:
                            sub_sumExpr.append(r'\left(%s\right)' % plusExpr)
                        else:
                            sub_sumExpr.append(r'\left[%s\right]' % plusExpr)
                    if large_brac:
                        sumExpr = r'\left \{ %s \right \}' % '+'.join(sub_sumExpr)
                    else:
                        sumExpr = r'\left[ %s \right]' % '+'.join(sub_sumExpr)
                else:
                    for di in self.__data:
                        diArr = di * 10**(-sciDigit)
                        plusExpr = '+'.join([n.dlatex(2) for n in diArr._NumItem__arr])
                        if len([x for x in diArr._NumItem__arr if x < 0]) == 0:
                            sub_sumExpr.append(r'\left(%s\right)' % plusExpr)
                        else:
                            sub_sumExpr.append(r'\left[%s\right]' % plusExpr)
                    if large_brac:
                        sumExpr = r'\left \{ %s \right \}\times 10^{%d}' % ('+'.join(sub_sumExpr), sciDigit)
                    else:
                        sumExpr = r'\left[ %s \right]\times 10^{%d}' % ('+'.join(sub_sumExpr), sciDigit)
                if nSame:
                    formula = r'\cfrac{1}{mn}\sum\limits_{i=1}^m\sum\limits_{j=1}^n %s_{ij}' % self.__sym
                    meanExpr = r'\cfrac{1}{%d \times %d}%s' % (m, n, sumExpr)
                else:
                    formula = r'\cfrac{1}{\sum_{i=1}^m n_i}\sum\limits_{i=1}^{m}\sum\limits_{j=1}^{n_i} %s_{ij}' % self.__sym
                    n_sumExpr = '+'.join([str(len(di._NumItem__arr)) for di in self.__data])
                    meanExpr = r'\cfrac{1}{%s}%s' % (n_sumExpr, sumExpr)
                latex = LaTeX(r'\overline{%s}=%s=%s=%s' % (self.__sym, formula, meanExpr, self.__value.latex()))
                if needValue:
                    return self.__value, latex
                else:
                    return latex
        else:
            return self.__value
    
    def __calStaUnc(self):
        '''计算标准不确定度'''
        if self.__uA != None:  #判断是否需要计算A类不确定度
            if self.__uA == 'single':
                if BaseMeasure.AMethod == 'auto':
                    if len(self.__data) > 9:  #样本数量最大的组为9以上时，使用Bessel法
                        uA = ACategory.Bessel(self.__data)
                    else:
                        uA = ACategory.Range(self.__data)
                elif BaseMeasure.AMethod == 'Bessel':
                    uA = ACategory.Bessel(self.__data)
                elif BaseMeasure.AMethod == 'Range':
                    uA = ACategory.Range(self.__data)
                elif BaseMeasure.AMethod == 'CollegePhysics':
                    uA = ACategory.CollegePhysics(self.__data)
            elif self.__uA == 'comb':
                uA = ACategory.CombSamples(self.__data)
        if self.__instrument != None:  #判断是否需要计算B类不确定度
            uB = BCategory.b(self.__instrument)
        if self.__uA != None and self.__instrument != None:
            closeUnit()
            u = sqrt(uA**2 + uB**2)
            u._Num__q = self.__q
            openUnit()
        elif self.__uA != None:
            u = uA
        elif self.__instrument != None:
            u = uB
        return u
    
    def unc(self, process=False, needValue=False, remainOneMoreDigit=False):
        '''获得不确定度
        【参数说明】
        1.process（可选，bool）：是否展示计算过程。默认proces=False。
        2.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
        3.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
        【返回值】
        Num：标准不确定度数值。'''
        if process:
            oneMoreDigit = remainOneMoreDigit or (self.__uA != None and self.__instrument != None)
            if self.__uA != None:  #判断是否需要计算A类不确定度
                if self.__uA == 'single':
                    if BaseMeasure.AMethod == 'auto':
                        if len(self.__data) > 9:  #样本数量最大的组为9以上时，使用Bessel法
                            uA = ACategory.Bessel(self.__data, True, True, oneMoreDigit)
                        else:
                            uA = ACategory.Range(self.__data, True, True, oneMoreDigit)
                    elif BaseMeasure.AMethod == 'Bessel':
                        uA = ACategory.Bessel(self.__data, True, True, oneMoreDigit)
                    elif BaseMeasure.AMethod == 'Range':
                        uA = ACategory.Range(self.__data, True, True, oneMoreDigit)
                    elif BaseMeasure.AMethod == 'CollegePhysics':
                        uA = ACategory.CollegePhysics(self.__data, True, True, oneMoreDigit)
                elif self.__uA == 'comb':
                    uA = ACategory.CombSamples(self.__data, BaseMeasure.AMethod, True, True, self.__sym, oneMoreDigit)
            if self.__instrument != None:  #判断是否需要计算B类不确定度
                uB = BCategory.b(self.__instrument, self.__sym, process, True, oneMoreDigit)
            latex = LaTeX()
            if self.__uA != None:
                latex.add(uA[1])
                uA = uA[0]
            if self.__instrument != None:
                latex.add(uB[1])
                uB = uB[0]
            if self.__uA != None and self.__instrument != None:
                closeUnit()
                u = sqrt(uA**2 + uB**2)
                u._Num__q = self.__q
                openUnit()
                if not remainOneMoreDigit:
                    u.cutOneDigit()
                latex.add(r'u_{%s}=\sqrt{{u_{%s A}}^{2}+{u_{%s B}}^{2}}=\sqrt{%s^{2}+%s^{2}}=%s' % (self.__sym, self.__sym, self.__sym, uA.dlatex(1), uB.dlatex(1), u.latex()))
            elif self.__uA != None:
                u = uA
                if not remainOneMoreDigit:
                    u.cutOneDigit()
                latex.add(r'u_{%s}=u_{%s A}=%s' % (self.__sym, self.__sym, u.latex()))
            elif self.__instrument != None:
                u = uB
                if not remainOneMoreDigit:
                    u.cutOneDigit()
                latex.add(r'u_{%s}=u_{%s B}=%s' % (self.__sym, self.__sym, u.latex()))
            if self._Measure__K != None:
                P = measure.KTable[self._Measure__K]
                u = u * self._Measure__K
                if not remainOneMoreDigit:
                    u.cutOneDigit()
                latex.add(r'u_{%s,%s}=%g u_{%s}=%s' % (self.__sym, P[1], self._Measure__K, self.__sym, u.latex()))
            if needValue:
                return u, latex
            else:
                return latex
        else:
            uc = self.__staUnc
            if self._Measure__K != None:
                uc = uc * self._Measure__K
            if remainOneMoreDigit:
                uc.remainOneMoreDigit()
            return uc
            
    def uncLSym(self):
        '''获得不确定度公式的LaTeX符号
        【返回值】
        LSym：不确定度公式的LaTeX符号。'''
        assert measure.Measure.process, 'Measure.process为False时，无法获取LSym'
        return LSym('u_{%s}' % self.__sym, self.unc())
    
    def __str__(self):
        '''获得测量值和不确定度的字符串形式
        【返回值】
        str：(测量值±不确定度)，如已给出单位，会附加单位'''
        unitExpr = format_units_unicode(self.__q)
        val = self.value()
        u = self.unc()
        sciDigit = val._Num__sciDigit()
        if self.useRelUnc:
            ur = u / val
            ur.setIsRelative(True)
            expr = r'%s(1±%s)%s' % (val.strNoUnit(), ur, unitExpr)
        else:
            if sciDigit == 0:
                u._Num__setDigit(val._Num__d_front, val._Num__d_behind, val._Num__d_valid)
                while float(u.strNoUnit()) == 0:
                    u.remainOneMoreDigit()
                expr = r'%s±%s' % (val.strNoUnit(), u.strNoUnit())
                if unitExpr != '':
                    expr = '(%s)%s' % (expr, unitExpr)
            else:
                val *= 10**(-sciDigit)
                u *= 10**(-sciDigit)
                u._Num__setDigit(val._Num__d_front, val._Num__d_behind, val._Num__d_valid)
                while float(u.strNoUnit()) == 0:
                    u.remainOneMoreDigit()
                expr = r'(%s±%s)×10%s%s' % (val.strNoUnit(), u.strNoUnit(), usub(sciDigit), unitExpr)
        return expr
        
    def __repr__(self):
        '''获得测量值和不确定度的字符串形式
        【返回值】
        str：(测量值±不确定度)，如已给出单位，会附加单位'''
        return self.__str__()
    
    def latex(self):
        unitExpr = format_units_latex(self.__q)
        val = self.value()
        u = self.unc()
        sciDigit = val._Num__sciDigit()
        if self.useRelUnc:
            ur = u / val
            ur.setIsRelative(True)
            expr = r'%s\left(1 \pm %s\right)%s' % (val.strNoUnit(), ur.dlatex(), unitExpr)
        else:
            if sciDigit == 0:
                u._Num__setDigit(val._Num__d_front, val._Num__d_behind, val._Num__d_valid)
                while float(u.strNoUnit()) == 0:
                    u.remainOneMoreDigit()
                expr = r'\left(%s \pm %s\right)%s' % (val.strNoUnit(), u.strNoUnit(), unitExpr)
            else:
                val *= 10**(-sciDigit)
                u *= 10**(-sciDigit)
                u._Num__setDigit(val._Num__d_front, val._Num__d_behind, val._Num__d_valid)
                while float(u.strNoUnit()) == 0:
                    u.remainOneMoreDigit()
                expr = r'\left(%s \pm %s\right)\times 10^{%d}%s' % (val.strNoUnit(), u.strNoUnit(), sciDigit, unitExpr)
        return expr
    
    def _repr_latex_(self):
        return r'$\begin{align}%s\end{align}$' % self.latex()