# -*- coding: utf-8 -*-
"""
1.切片表示
将切片属性特征用于其它部分观察点的建模，这既符合传统技术分析的认识、也更有效地满足了现代方法的假设。
为了尽量有效地描述切片和后续观察点的关系，参考传统分析的观察思路，每个切片最终提供3个属性：
（1）切片尾部与观察点的距离
（2）切片方向（多/空）
（3）切片趋势长度（使用相对长度表达）
为了尽量充分和简明表达观察点的历史特征，对观察点引入不超过3个最近切片的属性，其中两个远切片不使用距离属性。
2.观察点表示
对于各个观察点，目标属性是近期未来的价格运动方向，识别标示方向的基准采用区域极值点。
观察点的自变量属性取其简单平滑后的3日收益率。
3.切片与样本集生成模块
（1）样本集生成函数
（2）切片属性计算与样本集调整函数
（3）极值点与目标属性生成函数
该模块实现代码参见log5.py。
3.切片与样本集生成模块
该模块实现代码参见9.5.1.py。
"""
import sys
sys.path.append("..")
import numpy as np
import pandas as pd   #导入pandas表格库
import sec94.log4 as log
from log5 import obserSet


if __name__ == "__main__":
    name=['铜','铝','锌','镍','锡','螺纹']
    path = ['..\\data\\dayx\\CUL9.txt','../data/dayx/ALL9.txt','../data/dayx/ZNL9.txt','../data/dayx/NIL9.txt','../data/dayx/SNL9.txt','../data/dayx/RBL9.txt']  # 数据文件路径
    pathb = ['5m','15m','30m','60m',]  # 数据文件路径
    i=0
    xdata = pd.read_csv(path[i],sep=',',encoding='gbk',usecols=(1,2,3,4,5,6,))    # 读6列数据到DataFrame
    
    print (path[i]+'（'+name[i]+'）:')
    print ('表格原始形状：', xdata.shape)
    print ('头部切片：\n', xdata.head())
    print ('尾部切片：\n', xdata[-5:])
    t=20
    w=11
    log.logb(xdata,t,w)
    print ('最终资产：\n', xdata[-1:][['time','op','stat','asset']])
    print ('年化收益率%\t交易次数\t次均收益率%：\n', log.yearRate(xdata))
    print ('夏普比率：\n', log.SharpeRatio(xdata))
    print ('重要回撤：\n', log.retrect(xdata,15))
    
    # 建立样本集
    zdata=obserSet(xdata)
    print ('样本集形状：', zdata.shape)
    print ('数据类型：\n', zdata.dtypes)
    print ('\n')

