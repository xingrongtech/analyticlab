#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:25:06 2018

@author: xingrongtech
Referenced and modified by `markup` module, `quantities` package written by bjodah and apdavison
"""

import re
from quantities.quantity import Quantity

superscripts = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']
rad = Quantity(1., 'rad')
deg = Quantity(1., 'deg')

def superscript(val):
    items = re.split(r'\*{2}([\d]+)(?!\.)', val)
    ret = []
    while items:
        try:
            s = items.pop(0)
            e = items.pop(0)
            ret.append(s+''.join(superscripts[int(i)] for i in e))
        except IndexError:
            ret.append(s)
    return ''.join(ret)


def format_units_unicode(q):
    if type(q) != Quantity or len(q.dimensionality.items()) == 0:
        return ''
    res = str(q.dimensionality)
    res = superscript(res)
    res = res.replace('**', '^').replace('*','·').replace('deg', '°')
    return res

def format_units_latex(q, paren=False):
    '''
    Replace the units string provided with an equivalent latex string.

    Exponentiation (m**2) will be replaced with superscripts (m^{2})

    Multiplication (*) are replaced with the symbol specified by the mult argument.
    By default this is the latex \cdot symbol.  Other useful
    options may be '' or '*'.

    If paren=True, encapsulate the string in '\left(' and '\right)'

    The result of format_units_latex is encapsulated in $.  This allows the result
    to be used directly in Latex in normal text mode, or in Matplotlib text via the
    MathText feature.

    Restrictions:
    This routine will not put CompoundUnits into a fractional form.
    '''
    if type(q) != Quantity or len(q.dimensionality.items()) == 0:
        return ''
    res = str(q.dimensionality)
    if res.startswith('(') and res.endswith(')'):
        # Compound Unit
        compound = True
    else:
        # Not a compound unit
        compound = False
        # Replace division (num/den) with \frac{num}{den}
        #res = re.sub(r'(?P<num>.+)/(?P<den>.+)',r'\\frac{\g<num>}{\g<den>}',res)
    # Replace exponentiation (**exp) with ^{exp}
    res = re.sub(r'\*{2,2}(?P<exp>\d+)',r'^{\g<exp>}',res)
    # Remove multiplication signs
    res = re.sub(r'\*',r' \cdot ',res)
    res = res.replace('deg', r'{^\circ}')
    if paren and not compound:
        res = r'\left(%s\right)' % res
    res = r'{\rm %s}' % res
    return res