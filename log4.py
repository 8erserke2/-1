# -*- coding: utf-8 -*-
"""
1.策略与统计模块
（1）单均线策略函数
按模拟交易规则对时序对象生成模拟交易资产序列。
模拟交易计算规则：
当移动平均价格转为上升时候，以次交易点开盘价，先前空单平仓，并开仓做多；
当移动平均价格转为下降时候，以次交易点开盘价，先前多单平仓，并开仓做空；
每次开仓以全额资产进场，开仓平仓手续费都按万分之一计算（不计杠杆即杠杆为1或100%保证金）；
每个交易点都以收盘价计算一下账面资产记录到模拟资产序列中（不考虑交易手续费）；
对于决策要在次节点进行交易的交易点，账面资产以按照前3条规则计算出的结果替代；
某个交易点账面资产不大于0终止模拟交易；
为了计算每个交易点账面资产，需要记录并使用之前的开仓价格；
为简化计算，一旦开仓，不考虑实际交易中的每日结算盈亏后的持仓主动与被动增减变化。
（2）准海龟策略函数
总的计算规则与上面相同，只对前两条入出场规则变更如下：
当收盘价高于之前T点的最高价时，以次交易点开盘价，先前空单平仓，并开仓做多；
当收盘价低于之前T天的最低价时，以次交易点开盘价，先前多单平仓，并开仓做空；
若持有空单，当收盘价高于之前W天的最高价时，以次交易点开盘价，先前空单平仓；
若持有多单，当收盘价低于之前W天的最低价时，以次交易点开盘价，先前多单平仓；
T>W，参考海龟策略，T取15—60，W取T的1/3—2/3区间。
标准的海龟交易法则T和W分别取20日和10日，在突破进场条件同时属于55日长期突破时候，W取20日。
（3）夏普比率计算函数
针对资产序列计算夏普比率。
（4）回撤统计函数
针对资产序列统计大幅回撤区段。
（5）年化收益率计算函数
针对资产序列计算年化收益率。
"""
import numpy as np
import pandas as pd

#（1）单均线策略函数
def loga(data, t):
    data['ma']=data['close'].rolling(window=t, center=False).mean()    #第6列，移动平均价格
    data['op']=6        #第7列， {"多开","反多","空开","反空","多平","空平","无"}; 交易操作类型（数字对应0~6）
    data['stat']=0      #第8列， {"空仓","持多","持空"};  持仓状态（数字对应0,1,2）
    data['asset']=1.0       #第9列，账面资产（初值为1，<=0爆仓）

    k=0     #之前持仓状况
    j=-1    #上一次交易操作位置
    a=1.0  #初始资产
    e=0.9999    #1-交易费率
    s=len(data)-1
    for i in range(t+1,s+1):
        if k!=1 and i!=s and data.iat[i,6]>data.iat[i-1,6] and data.iat[i-1,6]<=data.iat[i-2,6]:    #非持多均线上拐
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
        if k!=2 and i!=s and data.iat[i,6]<data.iat[i-1,6] and data.iat[i-1,6]>=data.iat[i-2,6]:    #非持空均线下拐
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
    if i<s: #爆仓
        data.loc[i+1:,9]=data.iat[i,9]
    return

#（2）准海龟策略函数
def logb(data, t, w):
    data['maxt']=data['close'].rolling(window=t, center=False).max()    #第6列，开仓周期最大值
    data['op']=6        #第7列， {"多开","反多","空开","反空","多平","空平","无"}; 操作类型（数字对应0~6）
    data['stat']=0      #第8列， {"空仓","持多","持空"};  持仓状态（数字对应0,1,2）
    data['asset']=1.0       #第9列，账面资产（交易前初值为1，<=0爆仓）
    data['maxw']=data['close'].rolling(window=w, center=False).max()    #第10列，平仓周期最大值
    data['mint']=data['close'].rolling(window=t, center=False).min()    #第11列，开仓周期最小值
    data['minw']=data['close'].rolling(window=w, center=False).min()    #第12列，平仓周期最小值

    k=0     #之前持仓状况
    j=-1    #上一次操作位置
    a=1.0  #初始资产
    e=0.9999    #1-交易费率
    s=len(data)-1
    for i in range(t,s+1):
        if k!=1 and i!=s and data.iat[i,4]>data.iat[i-1,6]: #非持多t日上突
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
        if k!=2 and i!=s and data.iat[i,4]<data.iat[i-1,11]:    #非持空t日下突
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
        if k==2 and i!=s and data.iat[i,4]>data.iat[i-1,10]:    #持空w日上突
            #之前持空则平仓
            k=0 
            data.iat[i,7]=5
            data.iat[i,8]=k
            a=a*(2-1.0*data.iat[i+1,1]/data.iat[j+1,1])*e
            data.iat[i,9]=a
            j=-1
            if a<=0:
                break
            continue   
        if k==1 and i!=s and data.iat[i,4]<data.iat[i-1,12]:    #持多w日下突
            #之前持多则平仓
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
    if i<s: #爆仓
        data.loc[i+1:,9]=data.iat[i,9]
    return

#（3）夏普比率计算函数（按日收益率序列计算）
def SharpeRatio(data):
    if data.iat[0,0]>99999999:  #日内次高频
        t=data[['time','asset']].loc[data['time']%10000==1500]
    else:
        t=data[['time','asset']]
    t.insert(2,'ret',t['asset'].pct_change())
    return t['ret'].mean()/t['ret'].std()*np.sqrt(243)

#（4）大幅回撤统计函数(资产值在第9列，back=回撤百分比)
def retrect(data, back): #计算back以上回撤的幅度和区间
    ret=[]
    s=0     #历史最高位置
    e=0     #最高后最低位置
    for i in range(len(data)):
        if data.iat[i,9]>data.iat[s,9]:
            if data.iat[e,9]<data.iat[s,9]*(1-0.01*back):
                 ret.append([data.iat[s,0],data.iat[e,0],e-s,100-100*data.iat[e,9]/data.iat[s,9]])
            s=i
            e=i
            continue
        if data.iat[i,9]<data.iat[e,9]:
            e=i
    return pd.DataFrame(ret, columns=["start","end","width","back(%)",])

#（5）年化收益率计算函数(资产值在第9列)，返回年化收益率，交易次数，次均收益率
def yearRate(data):
    if data.iat[-1,9]<=0:
        return "爆仓无效"
    c=len(data['op'].loc[data['op']<4]) #进场开仓次数
    j=data.iat[0,0]
    k=data.iat[-1,0]
    if j>99999999:
        j=j//10000
        k=k//10000
    x1=j//10000+(j%10000)//100/12.0+(j%100)/360.0
    j=k
    x2=j//10000+(j%10000)//100/12.0+(j%100)/360.0
    return [np.power(data.iat[-1,9],1/(x2-x1))*100-100, c, np.power(data.iat[-1,9],1.0/c)*100-100]
    
if __name__ == "__main__":
    name=['铜','铝','锌','镍','锡','螺纹']
    path = ['..\\data\\dayx\\CUL9.txt','../data/dayx/ALL9.txt','../data/dayx/ZNL9.txt','../data/dayx/NIL9.txt','../data/dayx/SNL9.txt','../data/dayx/RBL9.txt']  # 数据文件路径
    i=0
    xdata = pd.read_csv(path[i],sep=',',encoding='gbk',usecols=(1,2,3,4,5,6,))    # 读6列数据到DataFrame
    print (path[i]+'（'+name[i]+'）:')
    print ('表格原始形状：', xdata.shape)
    print ('头部切片：\n', xdata.head())
    print ('尾部切片：\n', xdata[-5:])
    loga(xdata, 20)
    print ('单均线策略最终资产：\n', xdata[-1:][['time','op','stat','asset']])
    print ('年化收益率%\t交易次数\t次均收益率%：\n', yearRate(xdata))
    print ('夏普比率：\n', SharpeRatio(xdata))
    print ('重要回撤：\n', retrect(xdata,20))
    print ('\n')

