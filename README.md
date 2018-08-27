analyticlab（分析实验室）
====
analyticlab是一个实验数据计算、分析和计算过程展示的Python库，可应用于大学物理实验、分析化学等实验类学科以及大创、工艺流程等科技类竞赛的数据处理。该库包含以下5个部分：
* 数值运算（num、numitem模块）：按照有效数字运算规则的数值运算。
* 数理统计（numitem、twoitems模块）：包括偏差、误差、置信区间、协方差、相关系数、单个样本的显著性检验、两个样本的显著性检验。
* 离群值处理（outlier模块）：包括Nair检验、Grubbs检验、Dixon检验和偏度-峰度检验。
* 符号表达式合成（lsym、lsymitem模块）：根据符号和关系式，得到LaTeX格式的计算式。
* 测量及不确定度计算（measure包）：根据实验数据或其他不确定度报告中的数据、测量仪器/方法和测量公式，得出测量结果，包含测量值和不确定度。

模块定义
----
库中定义了9个类：
* Num：分析数值运算类，位于num模块。
* NumItem：分析数组类，位于numitem模块。
* LSym：LaTeX符号生成类，位于lsym模块。
* LSymItem：LaTeX符号组类，位于lsymitem模块。
* Const：常数类，位于const模块。
* LaTeX：公式集类，位于latexoutput模块。
* measure.Ins：测量仪器类，位于measure.ins模块。
* measure.BaseMeasure：基本测量类，位于measure.BaseMeasure模块。
* measure.Measure：测量类，位于measure.Measure模块。

7个函数模块：
* amath：对数值、符号、测量的求根、对数、三角函数运算。
* twoitems：两组数据的数理统计。
* outlier：离群值处理。
* latexoutput：数学公式、表格、LaTeX符号和不确定度等的输出。
* measure.std：计算标准偏差。
* measure.ACategory：计算A类不确定度。
* measure.BCategory：计算B类不确定度。

类的主要功能和绝大多数函数支持process（显示计算过程），通过在调用类方法或函数时，附加参数`process=True`实现。具体哪些类方法和函数支持process，可以查阅使用教程，或者通过help函数查询其说明文档。注意计算过程是以LaTeX格式输出的，因此计算过程展示功能只有在Jupyter Notebook环境下才能使用。如果只需要得到计算结果而不需要展示其过程，那么一般的Python3开发环境即可。

如何安装或更新
----
1.通过pip安装：
* `pip install analyticlab`

2.通过pip更新版本：
* `pip install analyticlab --upgrade`
<br>如果更新失败，可以尝试先卸载旧版本，再安装新版本：
* `pip uninstall analyticlab`
* `pip install analyticlab`

3.在pypi上下载analyticlab源代码并安装：
* 打开网址https://pypi.python.org/pypi/analyticlab
* 通过download下载tar.gz文件，解压到本地，通过cd指令切换到解压的文件夹内
* 通过`python setup.py install`实现安装

运行环境
----
analyticlab只能在Python 3.x环境下运行，不支持Python 2.x环境。要求系统已安装numpy、scipy、sympy、quantities库。可以在绝大多数Python平台下运行，但计算过程只有在Jupyter Notebook环境下才能显示出来。

参照标准文件
----
* GBT 8170-2008 数值修约规则与极限数值的表示和判定
* GBT 4883-2008 数据的统计处理和解释正态样本离群值的判断和处理
* JJF1059.1-2012 测量不确定度评定与表示
* CNAS-GL06 化学领域不确定度指南

