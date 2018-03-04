# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 08:41:19 2018

@author: xingrongtech
"""

import analyticlab
from IPython.display import display, Math
from analyticlab.system.exceptions import expressionInvalidException

class LaTeX():
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
        lExpr = r'\begin{align}' + (r'\\'.join(slines)) + r'\end{align}'
        display(Math(lExpr))

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
        tex += r'\hline' + (' & '.join([cell for cell in row])) + r'\\'
    tex += r'\hline\end{array}'
    return LaTeX(tex)
    
def dispLSym(lSym, resSym, resUnit=None):
    '''展示一个LSym计算过程（根据原始LSym是否有符号和对应数值，决定是否显示符号表达式、计算表达式和计算结果）
    【参数说明】
    1.lSym（LSym）：要展示的LaTeX符号。通过lSym，可以获得符号表达式、计算表达式和计算结果数值。
    2.resSym（str）：计算结果的符号。
    3.resUnit（可选，str）：计算结果的单位。当只展示符号表达式时，没必要给出计算结果的单位；若计算表达式和计算结果需要展示，则可选择是否给出resUnit。默认resUnit=None。
    【返回值】
    LaTeX：表格的公式集。'''
    if lSym._LSym__genSym and lSym._LSym__genCal:
        return LaTeX(r'%s=%s=%s=%s{\rm %s}' % (resSym, lSym.sym(), lSym.cal(), lSym.num().latex(), resUnit))
    elif lSym._LSym__genSym:
        return LaTeX(r'%s=%s' % (resSym, lSym.sym()))
    elif lSym._LSym__genCal:
        return LaTeX(r'%s=%s=%s{\rm %s}' % (resSym, lSym.cal(), lSym.num().latex(), resUnit))
        
def dispLSymItem(lSymItem, resSym, resUnit=None, headExpr='根据公式$%s$，得', showMean=True, meanExpr=None):
    '''展示一个LSymItem计算过程（包括符号表达式和计算表达式）
    【参数说明】
    1.lSymItem（LSymItem）：要展示的LaTeX符号组。通过lSymItem，可以获得符号表达式、计算表达式和计算结果数值。
    2.resSym（str）：计算结果的符号。
    3.resUnit（可选，str）：计算结果的单位。默认resUnit=None。
    4.headExpr（可选，str）：当符号表达式与计算表达式相分离时，对符号表达式进行语言修饰；当符号表达式与计算表达式在同一个等式中展示出来时，该参数无意义。默认headExpr='根据公式$%s$，得'。
    5.showMean（可选，bool）：是否展示符号组中各运算结果的均值及其运算过程。默认showMean=True。
    6.meanExpr（可选，str）：对均值的计算式进行语言修饰。默认meanExpr=None，即没有语言修饰。
    【返回值】
    LaTeX：表格的公式集。'''
    latex = LaTeX()
    if analyticlab.lsymitem.LSymItem.sepSymCalc:
        latex.add((r'\text{' + headExpr + '}') % (resSym + '=' + lSymItem.getSepSym().sym()))
        for i in range(len(lSymItem)):
            latex.add(r'{%s}_{%d}=%s=%s{\rm %s}' % (resSym, i+1, lSymItem[i].cal(), lSymItem[i].num().latex(), resUnit))
    else:
        for i in range(len(lSymItem)):
            latex.add(r'{%s}_{%d}=%s=%s=%s{\rm %s}' % (resSym, i+1, lSymItem[i].sym(), lSymItem[i].cal(), lSymItem[i].num().latex(), resUnit))
    if showMean:
        mitem = analyticlab.numitem.NumItem([si.num() for si in lSymItem], sym=resSym, unit=resUnit)
        if meanExpr != None:
            latex.add((r'\text{' + meanExpr + '}') % mitem.mean(process=True)._LaTeX__lines[0])
        else:
            latex.add(mitem.mean(process=True))
    return latex
            
def dispUnc(measures, resUnc, resValue, resSym, resUnit, resDescription=None):
    '''输出不确定度
    【参数说明】
    1.measures（list<Measure>）：由构成不确定度的全部测量（Measure）组成的数组。
    2.resUnc（Uncertainty或Measure）：最终测量结果的不确定度。
    3.resValue（Num）：最终测量结果的数值。
    4.resSym（str）：最终测量结果的符号。
    5.resUnit（str）：最终测量结果的单位。
    6.resDescription（可选，str）：对最终测量结果的描述。默认resDescription=None。
    【返回值】
    LaTeX：表格的公式集。'''
    latex = LaTeX()
    for i in range(len(measures)):
        latex.add(r'(%d)\text{对于%s：}' % (i+1, measures[i]._Measure__description))
        latex.add(measures[i].unc(process=True))
    res = resUnc._Uncertainty__res()
    if str(type(resValue)) == "<class 'analyticlab.lsym.LSym'>":
        resValue = resValue.num()
    latex.add(r'\text{计算合成不确定度：}')
    if res['isRate']:
        uncValue = res['unc']._Num__getRelative(dec=True) * resValue
        latex.add(r'\frac{u_{%s}}{%s}=%s=%s=%s' % (resSym, resSym, res['uncLSym'].sym(), res['uncLSym'].cal(), res['unc'].latex()))
        latex.add(r'u_{%s}=\frac{u_{%s}}{%s}\cdot %s=%s\times %s=%s{\rm %s}' % (resSym, resSym, resSym, resSym, res['unc'].latex(), resValue.latex(), uncValue.latex(), resUnit))
    else:
        latex.add(r'u_{%s}=%s=%s=%s{\rm %s}' % (resSym, res['uncLSym'].sym(), res['uncLSym'].cal(), res['unc'].latex(), resUnit))
    des = ''
    eqNum = resValue
    if res['isRate']:
        uNum = uncValue
    else:
        uNum = res['unc']
    if res['K'] != None:
        uNum = res['K'] * uNum
        latex.add(r'u_{%s,%s}=%g u_{%s}=%s{\rm %s}' % (resSym, res['P'][1], res['K'], resSym, uNum.latex(), resUnit))
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