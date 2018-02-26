analyticlab（分析实验室）是一个实验数据计算、分析和计算过程展示的库，可应用于大学物理实验、分析化学等实验类学科以及大创、工艺流程等科技类竞赛的数据处理。该库包含以下5个部分：
1.数值运算（num、numitem模块）：按照有效数字运算规则的数值运算。
2.数理统计（numitem、twoitems模块）：包括偏差、误差、置信区间、协方差、相关系数、单个样本的显著性检验、两个样本的显著性检验。
3.离群值处理（outlier模块）：包括Nair检验、Grubbs检验、Dixon检验和偏度-峰度检验。
4.符号表达式合成（lsym、lsymitem模块）：根据符号和关系式，得到LaTeX格式的计算式。
5.不确定度计算（uncertainty包）：根据实验数据、测量仪器和测量公式，计算不确定度。

库中定义了9个类：
1.Num：分析数值运算类，位于num模块。
2.NumItem：分析数组类，位于numitem模块。
3.LSym：LaTeX符号生成类，位于lsym模块。
4.LSymItem：LaTeX符号组类，位于lsymitem模块。
5.Const：常数类，位于const模块。
6.LaTeX：公式集类，位于latexoutput模块。
7.Ins：测量仪器类，位于uncertainty.ins模块。
8.Measure：测量类，位于uncertainty.measure模块。
9.Uncertainty：不确定度类，位于uncertainty.unc模块。

7个函数模块：
1.amath：对数值、符号、测量的求根、对数、三角函数运算。
2.twoitems：两组数据的数理统计。
3.outlier：离群值处理。
4.latexoutput：数学公式、表格、LaTeX符号和不确定度等的输出。
5.uncertainty.std：计算标准偏差。
6.uncertainty.ACategory：计算A类不确定度。
7.uncertainty.BCategory：计算B类不确定度。

类的主要功能和绝大多数函数支持process（显示计算过程），通过在调用类方法或函数时，附加参数process=True，将得到的计算过程传递给LaTeX公式集类，并通过调用公式集的show()方法来实现。哪些类方法和函数支持process，可以通过help函数查询其说明文档。注意计算过程是以LaTeX格式输出的，因此只有在Jupyter Notebook环境下，才能显示计算过程。

运行环境：
analyticlab只能在Python 3.x环境下运行，不支持Python 2.x环境。要求系统已安装scipy库。可以在绝大多数Python平台下运行，但计算过程只有在Jupyter Notebook环境下才能显示出来。

参照标准文件：
1.GBT 8170-2008 数值修约规则与极限数值的表示和判定
2.GBT 4883-2008 数据的统计处理和解释正态样本离群值的判断和处理
3.JJF1059.1-2012 测量不确定度评定与表示
4.CNAS-GL06 化学领域不确定度指南
