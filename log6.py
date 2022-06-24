# -*- coding: utf-8 -*-
'''
建模、预测及评价
'''
import numpy as np
import pandas as pd
import sklearn.ensemble as ens
import matplotlib as mpl
import matplotlib.pyplot as plt

import sys
sys.path.append("..")
import sec94.log4 as log
from sec95.log5 import obserSet

#评价函数，预测修正后的资产计算，参数：data=全部数据表格、pos=训练集样本数=预测集首样本序号、dir=预测方向
def logp(data, pos, dir):
    data['py']=data['y']    #预测修正后的方向
    k=0     #之前持仓状况（0=空仓、1=持多、2=持空）
    j=-1    #上一次操作位置
    a=1.0  #初始资产
    e=0.9999    #1-交易费率
    s=len(data)-1
    cc=-1    #样本点计数器
    for i in range(t,s+1):
        if data.at[i,'obs']==1: #样本点
            cc=cc+1
            if cc>=pos:
                data.at[i,'py']=dir[cc-pos]
        if cc<pos: #训练段
            k=data.iat[i,8]
            if data.iat[i,7]<6:
                a=data.iat[i,9]
                if data.iat[i,7]<4:
                    j=i
                else:
                    j=-1
            continue
        if k!=1 and i!=s and (data.iat[i,7]<2 or data.at[i,'obs']==1 and dir[cc-pos]==0):    #非持多原策略做多或预测做多
            if k==0:    #之前空仓则多开
                k=1 
                data.iat[i,7]=0
                data.iat[i,8]=k
                a=a*e
                data.iat[i,9]=a
                j=i
                continue   
            if k==2:    #之前持空则反多
                k=1 
                data.iat[i,7]=1
                data.iat[i,8]=k
                a=a*(2-1.0*data.iat[i+1,1]/data.iat[j+1,1])*e*e
                data.iat[i,9]=a
                j=i
                if a<=0:
                    break
                continue   
        if k!=2 and i!=s and (data.iat[i,7]<4 and data.iat[i,7]>1 or data.at[i,'obs']==1 and dir[cc-pos]==1):    #非持空原策略做空或预测做空
            if k==0:    #之前空仓则空开
                k=2 
                data.iat[i,7]=2
                data.iat[i,8]=k
                a=a*e
                data.iat[i,9]=a
                j=i
                continue   
            if k==1:    #之前持多则反空
                k=2 
                data.iat[i,7]=3
                data.iat[i,8]=k
                a=a*(1.0*data.iat[i+1,1]/data.iat[j+1,1])*e*e
                data.iat[i,9]=a
                j=i
                if a<=0:
                    break
                continue   
        if k==2 and i!=s and data.iat[i,7]==5:    #持空原策略空平
            k=0 
            data.iat[i,7]=5
            data.iat[i,8]=k
            a=a*(2-1.0*data.iat[i+1,1]/data.iat[j+1,1])*e
            data.iat[i,9]=a
            j=-1
            if a<=0:
                break
            continue   
        if k==1 and i!=s and data.iat[i,7]==4:    #持多原策略多平
            k=0 
            data.iat[i,7]=4
            data.iat[i,8]=k
            a=a*(1.0*data.iat[i+1,1]/data.iat[j+1,1])*e
            data.iat[i,9]=a
            j=-1
            if a<=0:
                break
            continue   
        if k==1: #持多
            ta=a*(1.0*data.iat[i,4]/data.iat[j+1,1])
        elif k==2: #持空
            ta=a*(2-1.0*data.iat[i,4]/data.iat[j+1,1])
        else:
            ta=a
        data.iat[i,7]=6
        data.iat[i,8]=k
        data.iat[i,9]=ta
        if ta<=0:
            break
    if i<s:
        data.loc[i+1:,9]=data.iat[i,9]
    return

if __name__ == "__main__":
    name=['铜','铝','锌','镍','锡','螺纹']
    path = ['..\\data\\dayx\\CUL9.txt','../data/dayx/ALL9.txt','../data/dayx/ZNL9.txt','../data/dayx/NIL9.txt','../data/dayx/SNL9.txt','../data/dayx/RBL9.txt']  # 日线数据文件路径
    pathb = ['5m','15m','30m','60m',]  # 数据文件路径
    i=0 #验证铜
    xdata = pd.read_csv(path[i],sep=',',encoding='gbk',usecols=(1,2,3,4,5,6,))  
    print (path[i]+'（'+name[i]+'）:')
    print ('表格原始形状：', xdata.shape)
    t=20
    w=11
    log.logb(xdata,t,w)     #单一简化海龟策略模拟
    print ('单策略结果：')
    print ('最终资产：\n', xdata[-1:][['time','op','stat','asset']])
    print ('年化收益率%\t交易次数\t次均收益率%：\n', log.yearRate(xdata))
    print ('夏普比率：\n', log.SharpeRatio(xdata))
    print ('重要回撤：\n', log.retrect(xdata,15))8

    # 建立样本集
    zdata=obserSet(xdata)
    print ('样本集形状：', zdata.shape)
    s1=int(len(zdata)/2)     #训练集长度（取1半）
    s2=int(len(zdata)-s1)    #测试集长度
    #x1=zdata[['xa','xb','xc','xd','xe','xf','xsid','xlid']]
    x1=zdata[['xa','xb','xc','xsid','xlid']]    #取部分属性用于建模预测
    print (s1)
    x2=x1.values[s1:]   #测试集
    x1=x1.values[:s1]   #训练集
    y1=zdata['y'].values
    y2=y1[s1:]
    y1=y1[:s1]  #训练集目标属性
    rf=ens.RandomForestClassifier(n_estimators=99,oob_score=False)   #99棵树、无交叉验证
    rf.fit(x1,y1)   #建模
    z=rf.predict(x2)    #预测测试集
    print ('\n叠加预测测试后结果：')
    xdata['oldasset']=xdata['asset']
    logp(xdata,s1,z)
    print ('最终资产：\n', xdata[-1:][['time','op','stat','asset']])
    print ('年化收益率%\t交易次数\t次均收益率%：\n', log.yearRate(xdata))
    print ('夏普比率：\n', log.SharpeRatio(xdata))
    print ('重要回撤：\n', log.retrect(xdata,15))
    #xdata.to_csv(path[i].replace('.txt','obs.csv'))
    #print '训练集验证', rf.score(x1,y1)
    #print '测试集验证', rf.score(x2,y2)
    mpl.rcParams['font.sans-serif'] = [u'simHei']   #显示中文标签
    mpl.rcParams['axes.unicode_minus'] = False      #正常显示负号
    plt.figure(facecolor='w', figsize=(9, 6))
    plt.plot(xdata['oldasset'], 'r-', linewidth=2, label=u'预测前资产')
    plt.plot(xdata['asset'], 'g-', linewidth=2, label=u'预测后资产')
    plt.grid(b=True)
    plt.legend(loc='upper right')
    plt.title(u'准海龟策略/叠加预测比较', fontsize=18)
    plt.show()
    #xdata.plot()
    xdata[['oldasset','asset']].plot()


    

    
