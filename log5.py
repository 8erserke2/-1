# -*- coding: utf-8 -*-
"""
3.切片与样本集生成模块
包含一个样本集生成函数和测试主程序，其功能包括：
（1）样本集筛选
（2）观察点属性计算
（3）网格属性计算
（4）切片属性计算与观察点集调整
（5）极值点、目标属性计算与观察点集调整
"""
import sys
sys.path.append("..")
import numpy as np
import pandas as pd
import sec94.log4 as log

#（1）样本集生成函数
def obserSet(data):
    data['std']=data['close'].rolling(window=120, center=False).std()    # 120线标准差
    data['maxt']=data['close'].rolling(window=15, center=True).max()    # 局部15点最大值
    data['mint']=data['close'].rolling(window=15, center=True).min()    # 局部15点最小值
    data['ma']=data['close'].rolling(window=5, center=False).mean()    # 移动平均价格
    data['ma']=data['ma'].pct_change()  #移动均价收益率
    data['obs']=0   # 有效观察点标记（1有效）
    data['xa']=0.0    # 当日收益率
    data['xb']=0.0    # 昨日收益率
    data['xc']=0.0    # 前日收益率
    data['xd']=0.0    # 临切（左侧相邻切片）距离
    data['xe']=0.0    # 临切方向（0=做多、1=做空）
    data['xf']=0.0    # 临切幅度
    data['xg']=0.0    # 隔切方向
    data['xh']=0.0    # 隔切幅度
    data['xi']=0.0    # 远切方向
    data['xj']=0.0    # 远切幅度
    data['xsid']=0.0    # 短网格id
    data['xlid']=0.0    # 长网格id
    data['y']=0     # 观察点方向（目标属性)
    data['ma5']=data['close'].rolling(window=5, center=False).mean()    #5日均价
    data['ma10']=data['close'].rolling(window=10, center=False).mean()    #10日均价
    data['ma20']=data['close'].rolling(window=20, center=False).mean()    #20日均价
    data['ma60']=data['close'].rolling(window=60, center=False).mean()    #60日均价
    data['ma120']=data['close'].rolling(window=120, center=False).mean()    #120日均价
    sec=[]
    s=len(data)
    k=-1
    for i in range(s):
        if data.iat[i,7]==0:    #多开
            k=i
            continue
        if data.iat[i,7]==2:    #空开
            k=i
            continue
        if data.iat[i,7]==4:    #多平
            sec.append([0,(data.iat[i+1,1]-data.iat[k+1,1]),i])
            if len(sec)==4:
                sec.pop(0)
            k=-1
            continue
        if data.iat[i,7]==5:    #空平
            sec.append([1,-(data.iat[i+1,1]-data.iat[k+1,1]),i])
            if len(sec)==4:
                sec.pop(0)
            k=-1
            continue
        if data.iat[i,7]==1:    #反多
            sec.append([1,-(data.iat[i+1,1]-data.iat[k+1,1]),i])
            if len(sec)==4:
                sec.pop(0)
            k=i
            continue
        if data.iat[i,7]==3:    #反空
            sec.append([0,(data.iat[i+1,1]-data.iat[k+1,1]),i])
            if len(sec)==4:
                sec.pop(0)
            k=i
            continue
        if data.iat[i,8]!=0:    #切片内跳过
            continue;
        if i<120 or len(sec)<3: #序列初段数据不全跳过
            continue
        if not(data.at[i,'ma5']>data.at[i-1,'ma5'] and data.at[i-1,'ma5']<=data.at[i-2,'ma5'] or data.at[i,'ma5']<data.at[i-1,'ma5'] and data.at[i-1,'ma5']>=data.at[i-2,'ma5']):   
            continue;   #5日均线不拐跳过
        # 左侧有3个切片的观察点
        data.at[i,'obs']=1
        data.at[i,'xa']=data.at[i,'ma']
        data.at[i,'xb']=data.at[i-1,'ma']
        data.at[i,'xc']=data.at[i-2,'ma']
        data.at[i,'xd']=i-sec[2][2]
        data.at[i,'xe']=sec[2][0]
        data.at[i,'xf']=sec[2][1]/data.at[i,'std']
        data.at[i,'xg']=sec[1][0]
        data.at[i,'xh']=sec[1][1]/data.at[i,'std']
        data.at[i,'xi']=sec[0][0]
        data.at[i,'xj']=sec[0][1]/data.at[i,'std']
        if data.at[i,'ma60']>data.at[i,'ma120']:
            data.at[i,'xlid']=data.at[i,'xlid']+12
        if data.at[i,'ma120']>data.at[i-1,'ma120']:
            data.at[i,'xlid']=data.at[i,'xlid']+6
        if data.at[i,'ma60']>data.at[i-1,'ma60']:
            data.at[i,'xlid']=data.at[i,'xlid']+3
        if data.at[i,'ma5']>data.at[i,'ma120']:
            data.at[i,'xlid']=data.at[i,'xlid']+1
        if data.at[i,'ma5']>data.at[i,'ma60']:
            data.at[i,'xlid']=data.at[i,'xlid']+1
        if data.at[i,'ma10']>data.at[i,'ma20']:
            data.at[i,'xsid']=data.at[i,'xsid']+12
        if data.at[i,'ma20']>data.at[i-1,'ma20']:
            data.at[i,'xsid']=data.at[i,'xsid']+6
        if data.at[i,'ma10']>data.at[i-1,'ma10']:
            data.at[i,'xsid']=data.at[i,'xsid']+3
        if data.at[i,'ma5']>data.at[i,'ma10']:
            data.at[i,'xsid']=data.at[i,'xsid']+1
        if data.at[i,'ma5']>data.at[i,'ma20']:
            data.at[i,'xsid']=data.at[i,'xsid']+1
    k=-1
    a=range(s)[::-1]
    for i in a:
        if k==-1:
            data.at[i,'obs']=0
        else:
            data.at[i,'y']=k
        if data.at[i,'maxt']==data.iat[i,4]:
            k=0
            continue
        if data.at[i,'mint']==data.iat[i,4]:
            k=1
            continue
    return data.loc[data['obs']==1]

if __name__ == "__main__":
    name=['铜','铝','锌','镍','锡','螺纹']
    path = ['..\\data\\dayx\\CUL9.txt','../data/dayx/ALL9.txt','../data/dayx/ZNL9.txt','../data/dayx/NIL9.txt','../data/dayx/SNL9.txt','../data/dayx/RBL9.txt']  # 数据文件路径
    pathb = ['5m','15m','30m','60m',]  # 数据文件路径
    i=0
    xdata = pd.read_csv(path[i],sep=',',encoding='gbk',usecols=(1,2,3,4,5,6,)) 
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
