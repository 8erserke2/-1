# -*- coding: utf-8 -*-
"""
5分钟数据整理
"""

import pandas as pd

#dataFrame清理
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
    path = ['..\\data\\5min\\CUL9.txt','../data/5min/ALL9.txt','../data/5min/ZNL9.txt','../data/5min/NIL9.txt','../data/5min/SNL9.txt','../data/5min/RBL9.txt']  # 数据文件路径
    for i in range(6):
        xdata = pd.read_csv(path[i],skiprows=3,skipfooter=1,sep='\t',encoding='gbk',usecols=(0,1,2,3,4,5,),names=['time','open','high','low','close','vol'])    # 读6列数据
        print (path[i]+'（'+name[i]+'）:')
        print ('表格原始形状：', xdata.shape)
        print ('数据类型：\n', xdata.dtypes)
        if i<4:
            clear(xdata,'','')  #它们不需要清除
        if i==4:
            clear(xdata,'','0905')  #假设锡需要清除0:00至9:00的数据(示意一下，实际上它应和铜等一样不需要清除)
        if i==5:
            clear(xdata,'2300','0905') #螺纹清除23:00——9:00间的无效数据，这是真实需要
        print ('表格整理后形状：', xdata.shape)
        print ('前2行切片：\n', xdata[:2])
        print ('后2行切片：\n', xdata[-2:])
        print ('数据类型：\n', xdata.dtypes)
        xdata.to_csv(path[i].replace('5min','5m'))
        print ('\n')


