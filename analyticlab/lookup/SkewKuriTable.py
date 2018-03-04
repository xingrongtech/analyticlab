# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 08:41:33 2018

@author: xingrongtech
"""
from analyticlab.system.exceptions import tooMuchDataForTestException, tooLessDataForTestException
from analyticlab.system.numberformat import f

sTable = {}
sTable[0.95] = {8:0.99, 9:0.97, 10:0.95, 12:0.91, 15:0.85, 20:0.77, 25:0.71, 30:0.66, 35:0.62, 40:0.59, 45:0.56, 50:0.53, 60:0.49, 70:0.46, 80:0.43, 90:0.41, 100:0.39}
sTable[0.99] = {8:1.42, 9:1.41, 10:1.39, 12:1.34, 15:1.26, 20:1.15, 25:1.06, 30:0.98, 35:0.92, 40:0.87, 45:0.82, 50:0.79, 60:0.72, 70:0.67, 80:0.63, 90:0.60, 100:0.57}

kTable = {}
kTable[0.95] = {8:3.70, 9:3.86, 10:3.95, 12:4.05, 15:4.13, 20:4.17, 25:4.14, 30:4.11, 35:4.08, 40:4.05, 45:4.02, 50:3.99, 60:3.93, 70:3.88, 80:3.84, 90:3.80, 100:3.77}
kTable[0.99] = {8:4.53, 9:4.82, 10:5.00, 12:5.20, 15:5.30, 20:5.38, 25:5.29, 30:5.20, 35:5.11, 40:5.02, 45:4.94, 50:4.87, 60:4.73, 70:4.62, 80:4.52, 90:4.45, 100:4.37}

def b(confLevel, n, side=2):
    if n > 100:
        raise tooMuchDataForTestException('偏度-峰度检验最多只支持100个数据的检验')
    elif n < 8:
        raise tooLessDataForTestException('偏度-峰度检验')
    if side == 1:
        y = sTable[confLevel]
    elif side == 2:
        y = kTable[confLevel]
    if n in y:  #当表中有值时，直接取出值
        return y[n]
    else:  #当表中没有值时，使用插值法
        nl = n - min([n-k for k in sTable[confLevel].keys() if k<14])  #找出右侧的值
        nr = n + min([k-n for k in sTable[confLevel].keys() if k>14])  #找出左侧的值
        return f(y[nl] + (y[nr]-y[nl])/(nr-nl)*(n-nl), 2)  #给出插值结果