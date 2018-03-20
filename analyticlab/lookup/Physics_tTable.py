# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 10:56:28 2018

@author: xingrongtech
"""

table = [1.84, 1.32, 1.20, 1.14, 1.11, 1.09, 1.08, 1.07, 1.06, 1.05, 1.05, 1.04, 1.04, 1.04, 1.03]

def phy_t(n):
    if n <= 16:
        return table[n-2]
    elif n < 30:
        return 1.03
    elif n < 40:
        return 1.02;
    elif n < 200:
        return 1.01;
    else:
        return 1.00;