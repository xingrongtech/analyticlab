# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 22:02:20 2018

@author: wzv100
"""

from math import sqrt
from analyticlab import amath
from analyticlab.latexoutput import LaTeX
from analyticlab.lookup.FTable import F
from analyticlab.lookup.tTable import t
from analyticlab.system import unitTreat
from analyticlab.system.statformat import statFormat, getMaxDeltaDigit
from analyticlab.system.exceptions import itemNotSameLengthException

def cov(X, Y, process=False, processWithMean=True, needValue=False, dec=False, remainOneMoreDigit=False):
    '''获得两组数据的协方差
    【参数说明】
    1.X（NumItem）：甲组数据。
    2.Y（NumItem）：乙组数据。
    3.process（可选，bool）：是否获得计算过程，默认process=False。
    4.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    5.dec（可选，bool）：是否已纯数字形式（int或float）给出样本均值。dec为True时，以纯数字形式给出；为False时，以数值（Num）形式给出。注意当dec=True时，process将会无效。默认dec=False。
    6.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①dec为True时，返回值为float类型的纯数字协方差；
    ②dec为False时：
    A.process为False时，返回值为Num类型的协方差。
    B.process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    C.process为True且needValue为True时，返回值为Num类型的协方差和LaTeX类型的计算过程组成的元组。
    【应用举例】
    >>> d1 = NumItem('10.69 10.67 10.74 10.72')
    >>> d2 = NumItem('5.38e-7 5.34e-7 5.37e-7 5.33e-7')
    >>> cov(d1, d2, remainOneMoreDigit=True)
    6.7e-12
    '''
    rX, rY = X._NumItem__arr, Y._NumItem__arr
    if len(rX) != len(rY):
        raise itemNotSameLengthException('进行协方差运算的两组数据长度必须一致')
    n = len(X)
    meanX, meanY = X.mean(), Y.mean()
    dsum = 0
    for i in range(n):
        dsum += (rX[i]._Num__num - meanX._Num__num) * (rY[i]._Num__num - meanY._Num__num)
    if dec:
    	return dsum / (n - 1)
    else:
        if process and processWithMean:
            meanX, lsub1 = X.mean(process=True, needValue=True)
            meanY, lsub2 = Y.mean(process=True, needValue=True)
        res = dsum / (n - 1)
        result = statFormat(min(getMaxDeltaDigit(X, meanX), getMaxDeltaDigit(Y, meanY)), res)
        if remainOneMoreDigit:
            result.remainOneMoreDigit()
        if process:
            latex = LaTeX()
            if processWithMean:
                latex.add([lsub1, lsub2])
            symX, symY = X._NumItem__sym, Y._NumItem__sym
            sumExpr = ''
            unitExpr = r'{\rm %s}' % unitTreat.mul(X._NumItem__unit, Y._NumItem__unit)
            sciDigit = max(X._NumItem__sciDigit(), Y._NumItem__sciDigit())
            if sciDigit == 0:
                for i in range(n):
                    sumExpr += r'%s\times%s+' % ((X[i] - meanX).latex(1), (Y[i] - meanY).latex(1))
                sumExpr = sumExpr[:-1]
                latex.add(r's(%s,%s)=\frac{1}{n-1}\sum\limits_{i=1}^n [(%s_{i}-\overline{%s})(%s_{i}-\overline{%s})]=\frac{1}{%d}\left[%s\right]=%s' % (symX, symY, symX, symX, symY, symY, n-1, sumExpr, result.latex() + unitExpr))
            else:
                dX = X * 10**(-sciDigit)
                dY = Y * 10**(-sciDigit)
                dmeanX = meanX * 10**(-sciDigit)
                dmeanY = meanY * 10**(-sciDigit)
                for i in range(n):
                    sumExpr += r'%s\times%s+' % ((dX[i] - dmeanX).latex(1), (dY[i] - dmeanY).latex(1))
                sumExpr = sumExpr[:-1]
                latex.add(r's(%s,%s)=\frac{1}{n-1}\sum\limits_{i=1}^n [(%s_{i}-\overline{%s})(%s_{i}-\overline{%s})]=\frac{1}{%d}\left[%s\right]\times 10^{%d}=%s' % (symX, symY, symX, symX, symY, symY, n-1, sumExpr, sciDigit*2, result.latex() + unitExpr))
            if needValue:
                return result, latex
            else:
                return latex
        return result

def corrCoef(X, Y, process=False, needValue=False, remainOneMoreDigit=False):
    '''获得两组数据的相关系数
    【参数说明】
    1.X（NumItem）：甲组数据。
    2.Y（NumItem）：乙组数据。
    3.process（可选，bool）：是否获得计算过程，默认process=False。
    4.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    5.remainOneMoreDigit（可选，bool）：结果是否多保留一位有效数字。默认remainOneMoreDigit=False。
    【返回值】
    ①process为False时，返回值为Num类型的相关系数。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为Num类型的相关系数和LaTeX类型的计算过程组成的元组。
    【应用举例】
    >>> d1 = NumItem('10.69 10.67 10.74 10.72')
    >>> d2 = NumItem('5.38e-7 5.34e-7 5.37e-7 5.33e-7')
    >>> corrCoef(d1, d2, remainOneMoreDigit=True)
    0.086
    '''
    if process:
        latex = LaTeX()
        sXY, lsub1 = cov(X, Y, process, processWithMean=False, needValue=True, remainOneMoreDigit=True)
        sX, lsub2 = X.staDevi(process, needValue=True, remainOneMoreDigit=True)
        sY, lsub3 = Y.staDevi(process, needValue=True, remainOneMoreDigit=True)
        latex.add([lsub1, lsub2, lsub3])
    else:
        sXY = cov(X, Y, remainOneMoreDigit=True)
        sX, sY = X.staDevi(remainOneMoreDigit=True), Y.staDevi(remainOneMoreDigit=True)
    result = sXY / (sX * sY)
    if not remainOneMoreDigit:
        result.cutOneDigit()
    if process:
        symX, symY = X._NumItem__sym, Y._NumItem__sym
        latex.add(r'r(%s,%s)=\frac{s(%s,%s)}{s_{%s}s_{%s}}=\frac{%s}{%s\times %s}=%s' % (symX, symY, symX, symY, symX, symY, sXY.latex(), sX.latex(2), sY.latex(2), result.latex()))
        if needValue:
            return result, latex
        else:
            return latex
    return result

def sigDifference(X, Y, confLevel=0.95, process=False, needValue=False):
    '''检测两组数据是否有显著性差异
    【参数说明】
    1.X（NumItem）：甲组数据。
    2.Y（NumItem）：乙组数据。
    3.confLevel（可选，float）：置信水平，建议选择0.6826、0.90、0.95、0.98、0.99中的一个（选择推荐值意外的值会使程序变慢），默认confLevel=0.95。
    4.process（可选，bool）：是否获得计算过程，默认process=False。
    5.needValue（可选，bool）：当获得计算过程时，是否返回计算结果。默认needValue=False。
    【返回值】
    bool：有显著性差异为True，无显著性差异为False
    ①process为False时，返回值为bool。
    ②process为True且needValue为False时，返回值为LaTeX类型的计算过程。
    ③process为True且needValue为True时，返回值为bool和LaTeX类型的计算过程组成的元组。
    【应用举例】
    >>> Al_1 = NumItem('10.69 10.67 10.74 10.72')
    >>> Al_2 = NumItem('10.76 10.68 10.73 10.74')
    >>> hasDifference = sigDifference(Al_1, Al_2)
    >>> print('两组数据是否有显著性差异：%s' % (Al_1, Al_2, hasDifference))
    两组数据是否有显著性差异：False
    '''
    #先进行F检验：比较两组的精密度
    item = (X, Y)
    s = (X.staDevi(dec=True), Y.staDevi(dec=True))
    if s[0] > s[1]:
        maxid, minid = 0, 1
    else:
        maxid, minid = 1, 0
    n_min = len(item[minid]._NumItem__arr)
    n_max = len(item[maxid]._NumItem__arr)
    FCal = s[maxid]**2 / s[minid]**2
    sDifferent = (FCal >= F(confLevel, n_min-1, n_max-1))
    if process:
        symX, symY = X._NumItem__sym, Y._NumItem__sym
        latex = LaTeX(r'\bbox[gainsboro, 2px]{\text{【通过F检验，比较两组的精密度】}}')
        p_meanX, p_meanY = X.mean(), Y.mean()
        p_sX, lsub1 = X.staDevi(process=True, needValue=True, remainOneMoreDigit=True)
        p_sY, lsub2 = Y.staDevi(process=True, needValue=True, remainOneMoreDigit=True)
        latex.add([lsub1, lsub2])
        #比较方差大小
        if (p_sX >= p_sY):
            latex.add(r'\text{其中}s_{%s}>s_{%s}\text{，故}s_{\rm max}=s_{%s}\text{，}s_{\rm min}=s_{%s}' % (symX, symY, symX, symY))
            latex.add(r'F=\frac{s_{\rm max}^2}{s_{\rm min}^2}=\frac{{%s}^2}{{%s}^2}=%.3f' % (p_sX.latex(1), p_sY.latex(1), FCal))
        else:
            latex.add(r'\text{其中}s_{%s}<s_{%s}\text{，故}s_{\rm max}=s_{%s}\text{，}s_{\rm min}=s_{%s}' % (symX, symY, symY, symX))
            latex.add(r'F=\frac{s_{\rm max}^2}{s_{\rm min}^2}=\frac{{%s}^2}{{%s}^2}=%.3f' % (p_sY.latex(1), p_sX.latex(1), FCal))
        latex.add(r'P=1-\frac{\alpha}{2}=%g\text{，}n_{\rm min}=%d\text{，}n_{\rm max}=%d\text{，查表得：}F_{1-\alpha/2}(n_{\rm min}-1,n_{\rm max}-1)=F_{%g}(%d,%d)=%.3f' % (confLevel, n_min, n_max, confLevel, n_min-1, n_max-1, F(confLevel, n_min-1, n_max-1)))
    if sDifferent:
        if process:
            latex.add(r'F>F_{%g}(%d,%d)\text{，表明两组测量结果的方差有显著性差异，即两组数据采用了精密度不同的两种测量方法}' % (confLevel, n_min-1, n_max-1))
            if needValue:
                return True, latex
            else:
                return latex
        return True
    else:
        #再进行t检验：比较两组的平均值，是否有显著差异
        nX, nY = len(X._NumItem__arr), len(Y._NumItem__arr)
        sp = sqrt(((nX-1)*s[0]**2 + (nY-1)*s[1]**2) / (nX+nY-2))
        tCal = abs(X.mean(dec=True) - Y.mean(dec=True)) / sp * sqrt((nX*nY)/(nX+nY))
        tv = t(confLevel, nX+nY-2)
        if process:
            latex.add(r'F<F_{%g}(%d,%d)\text{，表明两组测量结果的方差无显著性差异}' % (confLevel, n_min-1, n_max-1))
            latex.add(r'\bbox[gainsboro, 2px]{\text{【通过t检验，比较两组的均值】}}')
            p_sp = amath.sqrt(((nX-1)*p_sX**2 + (nY-1)*p_sY**2) / (nX+nY-2))
            latex.add(r's_{p}=\sqrt{\frac{(n_{%s}-1)s_{%s}^2+(n_{%s}-1)s_{%s}^2}{n_{%s}+n_{%s}-2}}=\sqrt{\frac{(%d-1)\times {%s}^2+(%d-1)\times {%s}^2}{%d+%d-2}}=%s' % (symX, symX, symY, symY, symX, symY, nX, p_sX.latex(1), nY, p_sY.latex(1), nX, nY, p_sp.latex()))
            latex.add(r't=\frac{\left\lvert \overline{%s}-\overline{%s}\right\rvert}{s_{p}}\sqrt{\frac{n_{%s}n_{%s}}{n_{%s}+n_{%s}}}=\frac{\left\lvert %s-%s\right\rvert}{%s}\times\sqrt{\frac{%d\times %d}{%d+%d}}=%.3f' % (symX, symY, symX, symY, symX, symY, p_meanX.latex(), p_meanY.latex(2), p_sp.latex(), nX, nY, nX, nY, tCal))
            latex.add(r'P=1-\frac{\alpha}{2}=%g，n_{%s}=%d，n_{%s}=%d\text{，查表得：}t_{1-\alpha/2}(n_{%s}+n_{%s}-2)=t_{%g}(%d)=%.3f' % (confLevel, symX, nX, symY, nY, symX, symY, confLevel, nX+nY-2, t(confLevel, nX+nY-2)))
            if tCal >= tv:
                latex.add(r't>t_{%g}(%d)\text{，说明两组测量结果的均值有明显差异，不属于同一群体，两者之间存在系统误差}' % (confLevel, nX+nY-2))
            else:
                latex.add(r't<t_{%g}(%d)\text{，说明两组测量结果的均值无明显差异，属于同一群体，两者之间的误差是由偶然误差引起的}' % (confLevel, nX+nY-2))
            if needValue:
                return tCal >= tv, latex
            else:
                return latex
        return tCal > tv
