from time import clock
from analyticlab import twoitems, outlier
from analyticlab.numitem import NumItem
from analyticlab.lsymitem import LSymItem
from analyticlab.uncertainty import ACategory, BCategory, ins
from analyticlab.uncertainty.measure import Measure

Al_real = '10.70'
Al = NumItem('10.69 10.26 10.71 10.72', Al_real, sym='m_{1}', unit='g')
Al_1 = NumItem('10.69 10.67 10.74 10.72', Al_real, sym='m_{2}', unit='g')
Al_2 = NumItem('10.76 10.68 10.73 10.74', Al_real, sym='m_{3}', unit='g')
Al_3 = NumItem("3.13 3.49 4.01 4.48 4.61 4.76 4.98 5.25 5.32 5.39 5.42 5.57 5.59 5.59 5.63 5.63 5.65 5.66 5.67 5.69 5.71 6.00 6.03 6.12 6.76", unit='g')
Al_4 = NumItem('13.52 13.56 13.55 13.54 13.12 13.54', sym = 'm_{4}', unit='g')
Al_5 = NumItem('13.52 13.56 13.55 13.54 13.12 13.54 13.58 13.53 13.74 13.56 13.51', unit='g')

ttotal = 0

def bUnc(process=False):
    d = LSymItem('d', '1.63 1.68 1.66 1.62')
    md = Measure(d, ins.刻度尺_毫米_1)
    return md.unc(process)

def test(func, expr):
    start = clock()
    for i in range(1000):
        p = func()
    end = clock()
    global ttotal
    ttotal += (end-start);
    print('%.6fms' % (end-start), expr, p)

test(lambda: Al.absErr(), '绝对误差')
test(lambda: Al.relErr(), '相对误差')
test(lambda: Al.isum(), '求和')
test(lambda: Al.mean(), '平均值')
test(lambda: Al.devi(), '偏差')
test(lambda: Al.staDevi(), '标准偏差')
test(lambda: Al.relStaDevi(), '相对标准偏差')
test(lambda: Al.relDevi(), '相对偏差')
test(lambda: Al.avgDevi(), '平均偏差')
test(lambda: Al.relAvgDevi(), '相对平均偏差')
test(lambda: Al.samConfIntv(), '双侧置信区间')
test(lambda: Al.samConfIntv(confLevel=0.6826, side='left'), '左侧置信区间')
test(lambda: Al.samConfIntv(confLevel=0.6826, side='right'), '右侧置信区间')
test(lambda: Al.tTest(), 't检验')
test(lambda: twoitems.cov(Al_1, Al_2), '协方差')
test(lambda: twoitems.corrCoef(Al_1, Al_2), '相关系数')
test(lambda: twoitems.sigDifference(Al_1, Al_2), '两组数据的显著性差异')
test(lambda: outlier.Nair(Al_3, 0.65, side='up'), 'Nair检验')
test(lambda: outlier.Grubbs(Al_4), 'Grubbs检验')
test(lambda: outlier.Dixon(Al_5), 'Dixon检验')
test(lambda: outlier.SkewKuri(Al_5), '偏度-峰度检验')
test(lambda: ACategory.Bessel(Al), 'A类不确定度-Bessel法')
test(lambda: ACategory.Range(Al), 'A类不确定度-极差法')
test(lambda: ACategory.CollegePhysics(Al), 'A类不确定度-大学物理实验')
test(lambda: ACategory.CombSamples([Al,Al_1,Al_2,Al_4], sym='m', unit='g', method='CollegePhysics'), 'A类不确定度-组合不确定度')
test(bUnc, 'B类不确定度')

print('总计用时：%.6fms' % ttotal)