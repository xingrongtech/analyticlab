* LaTeX类：改进换行机制，使之在不适用align的情况下，能够支持HTML-CSS、FastHTML, MathML的公式换行
* unit类：新增unit类，实现单位换算，建议使用sympy.Symbol实现，并通过repDict实现一些单位的替换（如kg*m/s**2替换成N）
* 不确定度部分：支持最小二乘法的不确定度计算
Num类：解决Num运算中诸如(1.00+0.69+0.63+1.02)/4=0.834的有效位判断错误的问题
