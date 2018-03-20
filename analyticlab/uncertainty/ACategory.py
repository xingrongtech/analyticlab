# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 10:15:25 2018

@author: xingrongtech
"""

from . import std
from ..amath import sqrt
from ..latexoutput import LaTeX
from ..numitem import NumItem
from ..lookup.Physics_tTable import phy_t
from ..lookup.RangeTable import v as rv
from ..lookup.RangeTable import C as rC

def Bessel(item, process=False, needValue=False, remainOneMoreDigit=False):
    '''贝塞尔公式法计算A类不确定度
    【参数说明】
    1.item（NumItem）：用于A类不确定度计算的样本数据。
    2.process（可选，bool）：是否获得计算过程。默认proces=False。
    3.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    4.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的A类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的A类不确定度和LaTeX类型的计算过程组成的元组。'''
    result = std.Bessel(item, remainOneMoreDigit) / len(item)**0.5
    if process:
        unitExpr = ''
        if item._NumItem__unit != None:
            unitExpr = item._NumItem__unit
        signal = item._NumItem__sym
        sciDigit = item._NumItem__sciDigit()
        if sciDigit == 0:
            p_mean = item.mean()
            sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).latex(1)) for xi in item._NumItem__arr])
            latex = LaTeX(r'u_{%s A}=\sqrt{\frac{1}{n(n-1)}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=\sqrt{\frac{1}{%d\times %d}\left[%s\right]}=%s{\rm %s}' % (signal, signal, signal, len(item), len(item)-1, sumExpr, result.latex(), unitExpr)) 
        else:
            d_arr = item * 10**(-sciDigit)
            p_mean = item.mean() * 10**(-sciDigit)
            sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).latex(1)) for xi in d_arr._NumItem__arr])
            latex = LaTeX(r'u_{%s A}=\sqrt{\frac{1}{n(n-1)}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=\sqrt{\frac{1}{%d \times %d}\left[%s\right]}\times 10^{%d}=%s{\rm %s}' % (signal, signal, signal, len(item), len(item)-1, sumExpr, sciDigit, result.latex(), unitExpr))
        if needValue:
            return result, latex
        else:
            return latex
    return result

def Range(item, process=False, needValue=False, remainOneMoreDigit=False):
    '''极差法计算A类不确定度
    【参数说明】
    1.item（NumItem）：用于A类不确定度计算的样本数据。
    2.process（可选，bool）：是否获得计算过程。默认proces=False。
    3.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    4.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的A类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的A类不确定度和LaTeX类型的计算过程组成的元组。'''
    result = std.Range(item, remainOneMoreDigit) / len(item)**0.5
    if process:
        unitExpr = ''
        if item._NumItem__unit != None:
            unitExpr = item._NumItem__unit
        signal = item._NumItem__sym
        p_max, p_min = max(item), min(item)
        C = rC(len(item))
        latex = LaTeX(r'u_{%s A}=\frac{R}{C\sqrt{n}}=\frac{%s-%s}{%s\times\sqrt{%s}}=%s{\rm %s}' % (signal, p_max.latex(), p_min.latex(2), C, len(item), result.latex(), unitExpr))
        if needValue:
            return result, latex
        else:
            return latex
    return result

def CollegePhysics(item, process=False, needValue=False, remainOneMoreDigit=False):
    '''大学物理实验中的A类不确定度计算
    【参数说明】
    1.item（NumItem）：用于A类不确定度计算的样本数据。
    2.process（可选，bool）：是否获得计算过程。默认proces=False。
    3.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    4.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的A类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的A类不确定度和LaTeX类型的计算过程组成的元组。'''
    result = phy_t(len(item)) * std.CollegePhysics(item, remainOneMoreDigit) / len(item)**0.5
    if process:
        unitExpr = ''
        if item._NumItem__unit != None:
            unitExpr = item._NumItem__unit
        signal = item._NumItem__sym
        sciDigit = item._NumItem__sciDigit()
        if sciDigit == 0:
            p_mean = item.mean()
            sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).latex(1)) for xi in item._NumItem__arr])
            latex = LaTeX(r'u_{%s A}=t_{n}\sqrt{\frac{1}{n(n-1)}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=%.2f \times\sqrt{\frac{1}{%d\times %d}\left[%s\right]}=%s{\rm %s}' % (signal, signal, signal, phy_t(len(item)), len(item), len(item)-1, sumExpr, result.latex(), unitExpr)) 
        else:
            d_arr = item * 10**(-sciDigit)
            p_mean = item.mean() * 10**(-sciDigit)
            sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).latex(1)) for xi in d_arr._NumItem__arr])
            latex = LaTeX(r'u_{%s A}=t_{n}\sqrt{\frac{1}{n(n-1)}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=%.2f \times\sqrt{\frac{1}{%d \times %d}\left[%s\right]}\times 10^{%d}=%s{\rm %s}' % (signal, signal, signal, phy_t(len(item)), len(item), len(item)-1, sumExpr, sciDigit, result.latex(), unitExpr))
        if needValue:
            return result, latex
        else:
            return latex
    return result

def CombSamples(items, method='auto', process=False, needValue=False, sym=None, unit=None, remainOneMoreDigit=False):
    '''合并样本的A类不确定度计算
    【参数说明】
    1.items（list<NumItem>）：用于A类不确定度计算的多个样本数据。
    2.method（可选，str）：使用何种方法计算每个样本的A类不确定度，从以下列表中取值：
    (1)'auto'：根据样本数量的大小，决定使用那种方法，即样本数量最大的组为9以上时，使用Bessel法；否则用极差法。
    (2)'Bessel'：使用贝塞尔公式法。
    (3)'Range'：使用极差法。
    (4)'CollegePhysics'：使用大学物理实验中的不确定度公式。
    3.process（可选，bool）：是否获得计算过程。默认proces=False。
    4.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    5.sym（可选，str）：合并样本的符号。默认sym=None。
    6.unit（可选，str）：合并样本的测量值单位。默认unit=None。
    7.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的合并样本的A类不确定度。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的合并样本的A类不确定度和LaTeX类型的计算过程组成的元组。'''
    m = len(items)
    if unit == None:
        unit = ''
    #计算各组样本的标准偏差
    if method == 'auto':
        if max([len(item) for item in items]) > 9:  #样本数量最大的组为9以上时，使用Bessel法
            s = [std.Bessel(item, remainOneMoreDigit=True) for item in items]
            method = 'Bessel'
        else:  #样本数量均不超过9时，使用极差法
            s = [std.Range(item, remainOneMoreDigit=True) for item in items]
            method = 'Range'
    elif method == 'Bessel':
        s = [std.Bessel(item, remainOneMoreDigit=True) for item in items]
    elif method == 'Range':
        s = [std.Range(item, remainOneMoreDigit=True) for item in items]
    elif method == 'CollegePhysics':
        s = [std.CollegePhysics(item, remainOneMoreDigit=True) for item in items]
    #根据所有样本的样本数量是否一致，判断使用哪个公式
    nSame = True
    n = len(items[0])
    for item in items:
        if len(item) != n:
            nSame = False
            break
    if nSame:
        nTotal = m*n
        sp = sqrt(sum([si**2 for si in s]) / m)
        if method == 'CollegePhysics':
            vSum = m*(n-1)
    else:
        nTotal = sum([len(item) for item in items])
        dSum = 0
        vSum = 0
        if method == 'Range':
            for i in range(m):
                v = rv(len(items[i]))
                dSum += v * s[i]**2
                vSum += v
            sp = sqrt(dSum / vSum)
        else:
            for i in range(m):
                v = len(items[i]) - 1
                dSum += v * s[i]**2
                vSum += v
            sp = sqrt(dSum / vSum)
    if method == 'CollegePhysics':
        result = phy_t(vSum+1) * sp / nTotal**0.5
    else:
        result = sp / nTotal**0.5
    if not remainOneMoreDigit:
        result.cutOneDigit()
    if process:
        resArr = []
        latex = LaTeX()
        if method == 'Range':
            for item in items:
                res = std.Range(item, remainOneMoreDigit=True)
                resArr.append(res)
                signal = item._NumItem__sym
                p_max, p_min = max(item), min(item)
                C = rC(len(item))
                latex.add(r's_{%s}=\frac{R}{C}=\frac{%s-%s}{%s}=%s{\rm %s}' % (signal, p_max.latex(), p_min.latex(2), C, res.latex(), unit))
        else:
            for item in items:
                res = std.Bessel(item, remainOneMoreDigit=True)
                resArr.append(res)
                signal = item._NumItem__sym
                sciDigit = item._NumItem__sciDigit()
                if sciDigit == 0:
                    p_mean = item.mean()
                    sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).latex(1)) for xi in item._NumItem__arr])
                    latex.add(r's_{%s}=\sqrt{\frac{1}{n-1}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=\sqrt{\frac{1}{%d}\left[%s\right]}=%s{\rm %s}' % (signal, signal, signal, len(item)-1, sumExpr, res.latex(), unit)) 
                else:
                    d_arr = item * 10**(-sciDigit)
                    p_mean = item.mean() * 10**(-sciDigit)
                    sumExpr = '+'.join([(r'%s^{2}' % (xi - p_mean).latex(1)) for xi in d_arr._NumItem__arr])
                    latex.add(r's_{%s}=\sqrt{\frac{1}{n-1}\sum\limits_{i=1}^n\left(%s_{i}-\overline{%s}\right)^{2}}=\sqrt{\frac{1}{%d}\left[%s\right]}\times 10^{%d}=%s{\rm %s}' % (signal, signal, signal, len(item)-1, sumExpr, sciDigit, res.latex(), unit))
        resItem = NumItem(resArr)
        sciDigit = resItem._NumItem__sciDigit()
        if sciDigit != 0:
            resItem = resItem * 10**(-sciDigit)
        if nSame:
            sumExpr = '+'.join([('%s^{2}' % res.latex(1)) for res in resItem])
            if sciDigit == 0:
                latex.add(r's_{p}=\sqrt{\frac{\sum\limits_{i=1}^m {s_{%s i}}^{2}}{m}}=\sqrt{\frac{%s}{%d}}=%s{\rm %s}' % (sym, sumExpr, m, sp.latex(), unit))
            else:
                latex.add(r's_{p}=\sqrt{\frac{\sum\limits_{i=1}^m {s_{%s i}}^{2}}{m}}=\sqrt{\frac{%s}{%d}}\times 10^{%d}=%s{\rm %s}' % (sym, sumExpr, m, sciDigit, sp.latex(), unit))
            if method == 'CollegePhysics':
                latex.add(r'u_{%s A}=\frac{t_{v+1}s_p}{\sqrt{mn}}=\frac{%.2f \times %s}{\sqrt{%s}}=%s{\rm %s}' % (sym, phy_t(vSum+1), sp.latex(2), nTotal, result.latex(), unit))
            else:
                latex.add(r'u_{%s A}=\frac{s_p}{\sqrt{mn}}=\frac{%s}{\sqrt{%s}}=%s{\rm %s}' % (sym, sp.latex(), nTotal, result.latex(), unit))
        else:
            sumExpr = ''
            if method == 'Range':
                for i in range(len(items)):
                    sumExpr += r'%s \times %s^{2}+' % (rv(len(items[i])), resItem[i].latex(1))
                vSumExpr = '+'.join(['%s' % rv(len(item)) for item in items])
            else:
                for i in range(len(items)):
                    sumExpr += r'%s \times %s^{2}+' % (len(items[i]) - 1, resItem[i].latex(1))
                vSumExpr = '+'.join(['%s' % (len(item) - 1) for item in items]) 
            sumExpr = sumExpr[:-1]
            if sciDigit == 0:
                latex.add(r's_{p}=\sqrt{\frac{\sum\limits_{i=1}^m \left(v_{i}s_{%s i}^{2}\right)}{\sum\limits_{i=1}^m v_{i}}}=\sqrt{\frac{%s}{%s}}=%s{\rm %s}' % (sym, sumExpr, vSumExpr, sp.latex(), unit))
            else:
                latex.add(r's_{p}=\sqrt{\frac{\sum\limits_{i=1}^m \left(v_{i}s_{%s i}^{2}\right)}{\sum\limits_{i=1}^m v_{i}}}=\sqrt{\frac{%s}{%s}}\times 10^{%d}=%s{\rm %s}' % (sym, sumExpr, vSumExpr, sciDigit, sp.latex(), unit))
            if method == 'CollegePhysics':
                latex.add(r'u_{%s A}=\frac{t_{v+1}s_p}{\sqrt{\sum\limits_{i=1}^m n_{i}}}=\frac{%s \times %s}{\sqrt{%s}}=%s{\rm %s}' % (sym, phy_t(vSum+1), sp.latex(2), nTotal, result.latex(), unit))
            else:
                latex.add(r'u_{%s A}=\frac{s_p}{\sqrt{\sum\limits_{i=1}^m n_{i}}}=\frac{%s}{\sqrt{%s}}=%s{\rm %s}' % (sym, sp.latex(), nTotal, result.latex(), unit))
        if needValue:
            return result, latex
        else:
            return latex
    return result