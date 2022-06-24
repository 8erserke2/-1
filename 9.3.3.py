# -*- coding: utf-8 -*-
"""
日K线数据整理
"""

import pandas as pd

#清理
def clear(data, ta, tb):
    data['time']=data['time'].str.replace('-','')
    data['time']=data['time'].str.replace('/','')
    data['time']=data['time'].str.replace(':','')
    if ta>'':
        data.drop(data[data.time.str[9:]>ta].index, inplace=True)
    if tb>'':
        data.drop(data[data.time.str[9:]<tb].index, inplace=True)

if __name__ == "__main__":
    name=['铜','铝','锌','镍','锡','螺纹']
    path = ['..\\data\\day\\CUL9.txt','../data/day/ALL9.txt','../data/day/ZNL9.txt','../data/day/NIL9.txt','../data/day/SNL9.txt','../data/day/RBL9.txt']  # 数据文件路径
    for i in range(6):
        xdata = pd.read_csv(path[i],skiprows=3,skipfooter=1,sep='\t',encoding='gbk',usecols=(0,1,2,3,4,5,),names=['time','open','high','low','close','vol']) 
        print (path[i]+'（'+name[i]+'）:')
        print ('表格原始形状：', xdata.shape)
        clear(xdata,'','')  #它们不需要清除
        print ('表格过滤后形状：', xdata.shape)
        print ('前2行切片：\n', xdata[:2])
        print ('后2行切片：\n', xdata[-2:])
        print ('数据类型：\n', xdata.dtypes)
        xdata.to_csv(path[i].replace('day','dayx'))
        print ('\n')
