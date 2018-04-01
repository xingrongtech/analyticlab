# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 08:41:19 2018

@author: xingrongtech
"""

import analyticlab
from .system.exceptions import expressionInvalidException, processStateWrongException
from IPython.display import display, Latex

class LaTeX(object):
    '''LaTeX为公式集类，该类用于储存一系列数学公式的LaTeX代码并输出公式。'''
    def __init__(self, line=None):
        '''初始化一个LaTeX公式集
        【参数说明】
        line（可选）：在初始化LaTeX公式集时，要加入的公式。默认line=None，即初始化时不加入公式。line可以是以下数据类型：
        (1)str：给出一行要加入公式的字符串。
        (2)list<str>：给出多行要加入公式的字符串列表。'''
        self.__lines = []
        if line != None:
            if type(line) == list:
                self.__lines += line
            elif type(line) == str:
                self.__lines += [line]
            else:
                raise expressionInvalidException('用于初始化公式集的参数无效')
      
    def add(self, line):
        '''添加一行或多行公式
        【参数说明】
        line：要加入的一行或多行公式。line可以是以下数据类型：
        (1)str：给出一行要加入公式的字符串。
        (2)LaTeX：将一个公式集追加到当前公式集。
        (3)list<str>：给出多行要加入公式的字符串列表。
        (4)list<LaTeX>：给出多个要追加的公式集。'''
        if type(line) == list:
            if type(line[0]) == str:
                self.__lines += line
            elif type(line[0]) == LaTeX:
                for oi in line:
                    self.__lines += oi.__lines
            else:
                raise expressionInvalidException('要添加公式的参数无效')
        elif type(line) == str:
            self.__lines += [line]
        elif type(line) == LaTeX:
            self.__lines += line.__lines
        else:
            raise expressionInvalidException('要添加公式的参数无效')
            
    def show(self):
        '''展示公式集'''
        slines = ['&'+li for li in self.__lines]
        lExpr = r'$\begin{align}' + ('\\\\ \n'.join(slines)) + r'\end{align}$'
        display(Latex(lExpr))
    
    def _repr_latex_(self):
        slines = ['&'+li for li in self.__lines]
        lExpr = r'$\begin{align}' + ('\\\\ \n'.join(slines)) + r'\end{align}$'
        return lExpr
    
    def addTable(self, table):
        '''添加一个简单格式的表格。表格的格式为m行n列，列宽由公式长度而定，公式居中。
        【参数说明】
        table（list<str>）：由表格各个单元格的内容（字符串格式）组成的二维列表，该列表的第一维度为行，第二维度为列。'''
        self.add(dispTable(table))
        
    def addLSym(self, lsym, resSym=None, resUnit=None):
        '''添加一个LSym计算过程（根据原始LSym是否有符号和对应数值，决定是否显示符号表达式、计算表达式和计算结果）
        【参数说明】
        1.lSym（LSym）：要展示的LaTeX符号。通过lSym，可以获得符号表达式、计算表达式和计算结果数值。
        2.resSym（可选，str）：计算结果的符号。当不给出符号时，生成的计算过程将只有代数表达式和数值表达式，而没有计算结果的符号。默认resSym=None。
        3.resUnit（可选，str）：计算结果的单位。当只展示符号表达式时，没必要给出计算结果的单位；若计算表达式和计算结果需要展示，则可选择是否给出resUnit。默认resUnit=None。'''
        self.add(dispLSym(lsym, resSym, resUnit))
        
    def addLSymItem(self, lSymItem, resSym=None, resUnit=None, headExpr='根据公式$%s$，得', showMean=True, meanExpr=None):
        '''添加一个LSymItem计算过程（包括符号表达式和计算表达式）
        【参数说明】
        1.lSymItem（LSymItem）：要展示的LaTeX符号组。通过lSymItem，可以获得符号表达式、计算表达式和计算结果数值。
        2.resSym（可选，str）：计算结果的符号。当不给出符号时，生成的计算过程将只有代数表达式和数值表达式，而没有计算结果的符号。默认resSym=None。
        3.resUnit（可选，str）：计算结果的单位。默认resUnit=None。
        4.headExpr（可选，str）：当符号表达式与计算表达式相分离时，对符号表达式进行语言修饰；当符号表达式与计算表达式在同一个等式中展示出来时，该参数无意义。默认headExpr='根据公式$%s$，得'。
        5.showMean（可选，bool）：是否展示符号组中各运算结果的均值及其运算过程。默认showMean=True。
        6.meanExpr（可选，str）：对均值的计算式进行语言修饰。默认meanExpr=None，即没有语言修饰。'''
        self.add(dispLSymItem(lSymItem, resSym, resUnit, headExpr, showMean, meanExpr))
        
    def addUnc(self, resUnc, resValue, resSym=None, resUnit=None, resDescription=None):
        '''添加不确定度的计算过程
        【参数说明】
        1.resUnc（Uncertainty或Measure）：最终测量结果的不确定度。
        2.resValue（Num）：最终测量结果的数值。
        3.resSym（可选，str）：最终测量结果的符号。当resUnc为Measure时，不需要给出，否则必须给出。默认resSym=None。
        4.resUnit（可选，str）：最终测量结果的单位。当resUnc为Measure时，不需要给出，否则必须给出。默认resUnit=None。
        5.resDescription（可选，str）：对最终测量结果的描述。默认resDescription=None。'''
        self.add(dispUnc(resUnc, resValue, resSym, resUnit, resDescription))
        
    def addRelErr(self, num, mu, sym=None, muSym=None, ESym='E_r'):
        '''添加相对误差的计算过程
        【参数说明】
        1.num和mu分别为测量值和真值。num、mu可以是以下数据类型：
        (1)Num：直接给出测量值、真值对应的数值
        (2)str：通过给出测量值、真值的字符串表达式，得到对应数值。
        (3)LSym：给出测量值、真值的LaTeX符号，得到对应数值。
        2.sym（可选，str）：测量值的符号。当测量值以LSym形式给出时，可不给出测量值符号，此时将使用num的符号作为测量值符号；否则必须给出符号。默认sym=None。
        3.muSym（可选，str）：真值的符号。当真值以LSym形式给出时，可不给出真值符号，此时将使用mu的符号作为真值符号；否则默认muSym为'\mu'。默认muSym=None。
        4.ESym（可选，str）：相对误差的符号。当给出相对误差的符号时，会在输出的表达式中加入相对误差符号那一项；当ESym为None时，没有那一项。默认ESym='E_r'。'''
        self.add(dispRelErr(num, mu, sym, muSym, ESym))

def dispTable(table):
    '''展示一个简单格式的表格。表格的格式为m行n列，列宽由公式长度而定，公式居中。
    【参数说明】
    table（list<str>）：由表格各个单元格的内容（字符串格式）组成的二维列表，该列表的第一维度为行，第二维度为列。
    【返回值】
    LaTeX：表格的公式集。
    【应用举例】
    lx=dispTable([['a/m', 'b/m', 'S/m^2'], ['1.36', '2.32', '9.91'], ['1.33', '2.35', '9.82'], ['1.35', '2.34', '9.92']])
    '''
    tex = r'\begin{array}{' + ('|'.join(['c']*len(table[0]))) + '}'
    for row in table:
        for j in range(len(row)):
            if type(row[j]) != str:
                if str(type(row[j])) == "<class 'analyticlab.num.Num'>":
                    row[j] = row[j].latex()
                elif str(type(row[j])) == "<class 'analyticlab.numitem.NumItem'>":
                    row[j] = ' & '.join([ci.latex() for ci in row[j]])
                elif type(row[j]) == float:
                    row[j] = '%g' % row[j]
                else:
                    row[j] = str(row[j])
        tex += r'\hline ' + (' & '.join([cell for cell in row])) + r'\\'
    tex += r'\hline\end{array}'
    return LaTeX(tex)
    
def dispLSym(lSym, resSym=None, resUnit=None):
    '''展示一个LSym计算过程（根据原始LSym是否有符号和对应数值，决定是否显示符号表达式、计算表达式和计算结果）
    【参数说明】
    1.lSym（LSym）：要展示的LaTeX符号。通过lSym，可以获得符号表达式、计算表达式和计算结果数值。
    2.resSym（可选，str）：计算结果的符号。当不给出符号时，生成的计算过程将只有代数表达式和数值表达式，而没有计算结果的符号。默认resSym=None。
    3.resUnit（可选，str）：计算结果的单位。当只展示符号表达式时，没必要给出计算结果的单位；若计算表达式和计算结果需要展示，则可选择是否给出resUnit。默认resUnit=None。
    【返回值】
    LaTeX：表格的公式集。'''
    if resUnit == None:
        resUnit = ''
    if resSym == None:
        resSymExpr = ''
    else:
        resSymExpr = resSym + '='
    if lSym._LSym__genSym and lSym._LSym__genCal:
        return LaTeX(r'%s%s=%s=%s{\rm %s}' % (resSymExpr, lSym.sym(), lSym.cal(), lSym.num().latex(), resUnit))
    elif lSym._LSym__genSym:
        return LaTeX(r'%s%s' % (resSymExpr, lSym.sym()))
    elif lSym._LSym__genCal:
        return LaTeX(r'%s%s=%s{\rm %s}' % (resSymExpr, lSym.cal(), lSym.num().latex(), resUnit))
        
def dispLSymItem(lSymItem, resSym=None, resUnit=None, headExpr='根据公式$%s$，得', showMean=True, meanExpr=None):
    '''展示一个LSymItem计算过程（包括符号表达式和计算表达式）
    【参数说明】
    1.lSymItem（LSymItem）：要展示的LaTeX符号组。通过lSymItem，可以获得符号表达式、计算表达式和计算结果数值。
    2.resSym（可选，str）：计算结果的符号。当不给出符号时，生成的计算过程将只有代数表达式和数值表达式，而没有计算结果的符号。默认resSym=None。
    3.resUnit（可选，str）：计算结果的单位。默认resUnit=None。
    4.headExpr（可选，str）：当符号表达式与计算表达式相分离时，对符号表达式进行语言修饰；当符号表达式与计算表达式在同一个等式中展示出来时，该参数无意义。默认headExpr='根据公式$%s$，得'。
    5.showMean（可选，bool）：是否展示符号组中各运算结果的均值及其运算过程。默认showMean=True。
    6.meanExpr（可选，str）：对均值的计算式进行语言修饰。默认meanExpr=None，即没有语言修饰。
    【返回值】
    LaTeX：表格的公式集。'''
    latex = LaTeX()
    if resUnit == None:
        resUnit = ''
    if analyticlab.lsymitem.LSymItem.sepSymCalc:
        latex.add((r'\text{' + headExpr + '}') % (resSym + '=' + lSymItem.getSepSym().sym()))
        if type(lSymItem._LSymItem__lsyms) == list:
            if resSym == None:
                for i in range(len(lSymItem)):
                    latex.add(r'%s=%s{\rm %s}' % (lSymItem[i].cal(), lSymItem[i].num().latex(), resUnit))
            else:
                for i in range(len(lSymItem)):
                    latex.add(r'{%s}_{%d}=%s=%s{\rm %s}' % (resSym, i+1, lSymItem[i].cal(), lSymItem[i].num().latex(), resUnit))
        else:
            if resSym == None:
                for ki in lSymItem._LSymItem__lsyms.keys():
                    latex.add(r'%s=%s{\rm %s}' % (lSymItem[ki].cal(), lSymItem[ki].num().latex(), resUnit))                
            else:
                for ki in lSymItem._LSymItem__lsyms.keys():
                    latex.add(r'{%s}_{%s}=%s=%s{\rm %s}' % (resSym, ki, lSymItem[ki].cal(), lSymItem[ki].num().latex(), resUnit))
    else:
        if type(lSymItem._LSymItem__lsyms) == list:
            if resSym == None:
                for i in range(len(lSymItem)):
                    latex.add(r'%s=%s=%s{\rm %s}' % (lSymItem[i].sym(), lSymItem[i].cal(), lSymItem[i].num().latex(), resUnit))
            else:
                for i in range(len(lSymItem)):
                    latex.add(r'{%s}_{%d}=%s=%s=%s{\rm %s}' % (resSym, i+1, lSymItem[i].sym(), lSymItem[i].cal(), lSymItem[i].num().latex(), resUnit))
        else:
            if resSym == None:
                for ki in lSymItem._LSymItem__lsyms.keys():
                    latex.add(r'%s=%s=%s{\rm %s}' % (lSymItem[ki].sym(), lSymItem[ki].cal(), lSymItem[ki].num().latex(), resUnit))                
            else:
                for ki in lSymItem._LSymItem__lsyms.keys():
                    latex.add(r'{%s}_{%s}=%s=%s=%s{\rm %s}' % (resSym, ki, lSymItem[ki].sym(), lSymItem[ki].cal(), lSymItem[ki].num().latex(), resUnit))
    if showMean and resSym != None:
        if type(lSymItem._LSymItem__lsyms) == list:
            mitem = analyticlab.numitem.NumItem([si.num() for si in lSymItem._LSymItem__lsyms], sym=resSym, unit=resUnit)
        else:
            mitem = analyticlab.numitem.NumItem([si.num() for si in lSymItem._LSymItem__lsyms.values()], sym=resSym, unit=resUnit)
        if meanExpr != None:
            latex.add((r'\text{' + meanExpr + '}') % mitem.mean(process=True)._LaTeX__lines[0])
        else:
            latex.add(mitem.mean(process=True))
    return latex
            
def dispUnc(resUnc, resValue, resSym=None, resUnit=None, resDescription=None):
    '''展示不确定度
    【参数说明】
    1.resUnc（Uncertainty或Measure）：最终测量结果的不确定度。
    2.resValue（Num）：最终测量结果的数值。
    3.resSym（可选，str）：最终测量结果的符号。当resUnc为Measure时，不需要给出，否则必须给出。默认resSym=None。
    4.resUnit（可选，str）：最终测量结果的单位。当resUnc为Measure时，不需要给出，否则必须给出。默认resUnit=None。
    5.resDescription（可选，str）：对最终测量结果的描述。默认resDescription=None。
    【返回值】
    LaTeX：表格的公式集。'''
    latex = LaTeX()
    res = resUnc._Uncertainty__res()
    if res == None:
        raise processStateWrongException()
    if str(type(resValue)) == "<class 'analyticlab.lsym.LSym'>":
        resValue = resValue.num()
    if str(type(resUnc)) =="<class 'analyticlab.uncertainty.unc.Uncertainty'>":
        #针对Uncertainty的不确定度输出
        measures = [mi[0] for mi in resUnc._Uncertainty__measures.values()]
        for i in range(len(measures)):
            latex.add(r'(%d)\text{对于%s：}' % (i+1, measures[i]._Measure__description))
            latex.add(measures[i].unc(process=True, remainOneMoreDigit=True))
        latex.add(r'\text{计算合成不确定度：}')
        if res['isRate']:
            uncValue = res['unc']._Num__getRelative(dec=True) * resValue
            latex.add(r'\frac{u_{%s}}{%s}=%s\\&\quad=%s\\&\quad=%s' % (resSym, resSym, res['uncLSym'].sym(), res['uncLSym'].cal(), res['unc'].latex()))
            latex.add(r'u_{%s}=\frac{u_{%s}}{%s}\cdot %s=%s\times %s=%s{\rm %s}' % (resSym, resSym, resSym, resSym, res['unc'].latex(), resValue.latex(), uncValue.latex(), resUnit))
        else:
            #给出不确定度计算定义式
            pExpr = '+'.join([r'\left(\cfrac{\partial %s}{\partial %s}\right)^2 u_{%s}^2' % (resSym, mi[0]._Measure__sym, mi[0]._Measure__sym) for mi in res['measures'].values()])
            pExpr = r'\sqrt{%s}' % pExpr
            latex.add(r'u_{%s}=%s\\&\quad=%s\\&\quad=%s\\&\quad=%s{\rm %s}' % (resSym, pExpr, res['uncLSym'].sym(), res['uncLSym'].cal(), res['unc'].latex(), resUnit))
        if res['isRate']:
            uNum = uncValue
        else:
            uNum = res['unc']
    elif str(type(resUnc)) =="<class 'analyticlab.uncertainty.measure.Measure'>":
        #针对Measure的不确定度输出
        uNum, proc = resUnc.unc(process=True, needValue=True, remainOneMoreDigit=True)
        latex.add(proc)
        resSym = resUnc._Measure__sym
        resUnit = resUnc._Measure__unit
    eqNum = resValue
    if res['K'] != None:
        uNum = res['K'] * uNum
        latex.add(r'u_{%s,%s}=%g u_{%s}=%s{\rm %s}' % (resSym, res['P'][1], res['K'], resSym, uNum.latex(), resUnit))
    des = ''
    if resDescription != None:
        des = resDescription
    sciDigit = eqNum._Num__sciDigit()
    if sciDigit == 0:
        uNum._Num__setDigit(eqNum._Num__d_front, eqNum._Num__d_behind, eqNum._Num__d_valid)
        finalExpr = r'\text{%s}%s=(%s \pm %s){\rm %s}' % (des, resSym, eqNum, uNum, resUnit)
    else:
        eqNum *= 10**(-sciDigit)
        uNum *= 10**(-sciDigit)
        uNum._Num__setDigit(eqNum._Num__d_front, eqNum._Num__d_behind, eqNum._Num__d_valid)
        finalExpr = r'\text{%s}%s=(%s \pm %s)\times 10^{%d}{\rm %s}' % (des, resSym, eqNum, uNum, sciDigit, resUnit)
    if res['K'] == None:
        finalExpr += r'\qquad {\rm P=0.6826}'
    else:
        finalExpr += r'\qquad {\rm P=%s}' % res['P'][0]
    latex.add(finalExpr)
    return latex

def dispRelErr(num, mu, sym=None, muSym=None, ESym='E_r'):
    '''展示相对误差
    【参数说明】
    1.num和mu分别为测量值和真值。num、mu可以是以下数据类型：
    (1)Num：直接给出测量值、真值对应的数值
    (2)str：通过给出测量值、真值的字符串表达式，得到对应数值。
    (3)LSym：给出测量值、真值的LaTeX符号，得到对应数值。
    2.sym（可选，str）：测量值的符号。当测量值以LSym形式给出时，可不给出测量值符号，此时将使用num的符号作为测量值符号；否则必须给出符号。默认sym=None。
    3.muSym（可选，str）：真值的符号。当真值以LSym形式给出时，可不给出真值符号，此时将使用mu的符号作为真值符号；否则不给出真值符号时，会用真值数值取代muSym。默认muSym=None。
    4.ESym（可选，str）：相对误差的符号。当给出相对误差的符号时，会在输出的表达式中加入相对误差符号那一项；当ESym为None时，没有那一项。默认ESym='E_r'。
    【返回值】
    LaTeX：相对误差的公式集。'''
    #当num不是Num数值类型时，将其转换为Num类型
    if type(num) == analyticlab.Num:
        pass
    elif type(num) == str:
        num = analyticlab.Num(num)
    elif type(num) == analyticlab.LSym:
        if sym == None:
            sym = num.sym()
        num = num.num()
    else:
        raise expressionInvalidException('数值num参数无效')
    #当mu不是Num数值类型时，将其转换为Num类型
    if type(mu) == analyticlab.Num:
        pass
    elif type(mu) == str:
        mu = analyticlab.Num(mu)
    elif type(mu) == analyticlab.LSym:
        if muSym == None:
            muSym = mu.sym()
        mu = mu.num()
    else:
        raise expressionInvalidException('真值mu参数无效')
    if muSym == None:
        muSym = num.latex()
    rel = abs(num - mu) / mu
    rel._Num__isRelative = True
    if ESym == None:
        return LaTeX(r'\cfrac{\left\lvert %s-%s \right\rvert}{%s}\times 100\%%=\cfrac{\left\lvert %s-%s \right\rvert}{%s}\times 100\%%=%s' % (sym, muSym, muSym, num.latex(), mu.latex(), mu.latex(), rel.latex()))
    else:
        return LaTeX(r'%s=\cfrac{\left\lvert %s-%s \right\rvert}{%s}\times 100\%%=\cfrac{\left\lvert %s-%s \right\rvert}{%s}\times 100\%%=%s' % (ESym, sym, muSym, muSym, num.latex(), mu.latex(), mu.latex(), rel.latex()))