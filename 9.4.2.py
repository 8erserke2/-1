# -*- coding: utf-8 -*-
"""
3.准海龟策略统计模块
（1）统计某时序对象在T和W各个参数组合条件下的趋势追踪效果函数
（2）单对象多时间框架统计控制程序（主控模块）
"""
import numpy as np
import pandas as pd 
import log4 as log

#（1）统计某时序对象在T和W各个参数组合条件下的趋势追踪效果函数
def logbTotal(data):
    ret=[]
    for t in range(15,61):
        for w in [t*3//8, t//2, t*5//8]:
            log.logb(data,t,w)
            yr=log.yearRate(data)
            ret.append([t, w, data.iat[-1,9], yr[0], log.SharpeRatio(data), yr[1], yr[2]])
    return pd.DataFrame(ret, columns=[u"开周期",u"平周期",u"总资产",u"年收益(%)",u"夏普比率",u"交易次数",u"次收益(%)",])

if __name__ == "__main__":
    name=['铜','铝','锌','镍','锡','螺纹']
    path = ['..\\data\\dayx\\CUL9.txt','../data/dayx/ALL9.txt','../data/dayx/ZNL9.txt','../data/dayx/NIL9.txt','../data/dayx/SNL9.txt','../data/dayx/RBL9.txt']  # 数据文件路径
    pathb = ['5m','15m','30m','60m',]  # 数据文件路径
    for i in range(1):
        xdata = pd.read_csv(path[i],sep=',',encoding='gbk',usecols=(1,2,3,4,5,6,)) 
        print (path[i]+'（'+name[i]+'）:')
        print ('表格原始形状：', xdata.shape)
        print ('头部切片：\n', xdata.head()) 
        print ('尾部切片：\n', xdata[-5:])
        x=logbTotal(xdata)
        print ('准海龟策略各周期效果统计：\n', x)
        x.to_csv(path[i].replace('.txt','2.csv'))
        print ('\n')

        for j in pathb:
            xdata = pd.read_csv(path[i].replace('dayx',j),sep=',',encoding='gbk',usecols=(1,2,3,4,5,6,)) 
            print (path[i].replace('dayx',j)+'（'+name[i]+'）:')
            print ('表格原始形状：', xdata.shape)
            print ('头部切片：\n', xdata.head())
            print ('尾部切片：\n', xdata[-5:])
            x=logbTotal(xdata)
            print ('准海龟策略各周期效果统计：\n', x)
            x.to_csv(path[i].replace('dayx',j).replace('.txt','2.csv'))
            print ('\n')
