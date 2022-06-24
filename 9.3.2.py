# -*- coding: utf-8 -*-
"""
从5分钟数据生成其它时间框架数据
"""

import pandas as pd

# K线转换（暂时忽略数据有缺失不连续的场景）, w:3=15分钟，6=30分钟，12=60分钟
def minx(data, w):
    newdata=data[:0]
    j=0
    k=-1
    for i in range(len(data)):
        if j!=0 and (data.iat[i,0]%10000==905 or data.iat[i,0]%10000==2105):
            j=0
        if j==0: 
            k=k+1
            newdata=newdata.append(data[i:i+1])
            j=1
        else:
            newdata.iat[k,0]=data.iat[i,0]
            newdata.iat[k,4]=data.iat[i,4]
            newdata.iat[k,5]+=data.iat[i,5]
            if newdata.iat[k,2]<data.iat[i,2]:
                newdata.iat[k,2]=data.iat[i,2]
            if newdata.iat[k,3]>data.iat[i,3]:
                newdata.iat[k,3]=data.iat[i,3]
            j=j+1
            if j==w:
                j=0
    return newdata

if __name__ == "__main__":
    name=['铜','铝','锌','镍','锡','螺纹']
    path = ['..\\data\\5m\\CUL9.txt','../data/5m/ALL9.txt','../data/5m/ZNL9.txt','../data/5m/NIL9.txt','../data/5m/SNL9.txt','../data/5m/RBL9.txt']  # 数据文件路径
    for i in range(6):
        xdata = pd.read_csv(path[i],sep=',',encoding='gbk',usecols=(1,2,3,4,5,6,))    # 读6列数据
        x=minx(xdata, 3)
        print (path[i]+'（'+name[i]+'）:')
        print ('表格原始形状：', xdata.shape)
        print ('15分钟表格形状：', x.shape)
        print ('前2行切片：\n', x[:2])
        print ('后2行切片：\n', x[-2:])
        print ('数据类型：\n', x.dtypes)
        x.to_csv(path[i].replace('5m','15m'))
        x=minx(xdata, 6)
        print ('30分钟表格形状：', x.shape)
        print ('前2行切片：\n', x[:2])
        print ('后2行切片：\n', x[-2:])
        x.to_csv(path[i].replace('5m','30m'))
        x=minx(xdata, 12)
        print ('60分钟表格形状：', x.shape)
        print ('前2行切片：\n', x[:2])
        print ('后2行切片：\n', x[-2:])
        x.to_csv(path[i].replace('5m','60m'))
        print ('\n')
