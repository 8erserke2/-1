# -*- coding: utf-8 -*-

import pandas as pd
import sys

sys.path.append("..")
import sec94.log4 as log


# 单20日均线+ATR指标
def logc(data):
    data['MA20']=data['close'].rolling(window=20, center=False).mean()  # 第6列20日均线
    data['op'] = 6  # 第7列， {"多开","反多","空开","反空","多平","空平","无"}; 操作类型（数字对应0~6）
    data['stat'] = 0  # 第8列， {"空仓","持多","持空"};  持仓状态（数字对应0,1,2）
    data['asset'] = 1.0  # 第9列，账面资产（交易前初值为1，<=0爆仓）

    # 计算ATR指标
    for i in range(0, len(data)):
        data.loc[data.index[i], 'TR'] = max((data['close'][i] - data['low'][i]),
                                                (data['high'][i] - data['close'].shift(-1)[i]),
                                                (data['low'][i] - data['close'].shift(-1)[i]))  # 第10列 计算TR
    data['ATR'] = data['TR'].rolling(12).mean()  # 第11列 计算ATR

    #寻找局部最高点，以及局部最低点
    data['max1'] = data[['open', 'close']].max(axis=1) # 第12列  以K线实体作为局部最大值的考量
    data['min1'] = data[['open', 'close']].min(axis=1)  # 第13列 以K线实体作为局部最小值的考量
    data.loc[(data['max1'].shift(1) > data['max1'])
            & (data['max1'].shift(1) > data['max1'].shift(2))
            & (data['max1'].shift(1) == data['max1'].rolling(10).max())
            & (data['max1'].shift(1) == data['max1'].shift(-5).rolling(10).max()), 'higher'] = 1 # 第14列 以前10天和后5天的值，来定义局部最高点
    data.loc[(data['min1'].shift(1) < data['min1'])
            & (data['min1'].shift(1) < data['min1'].shift(2))
            & (data['min1'].shift(1) == data['min1'].rolling(10).min())
            & (data['min1'].shift(1) == data['min1'].shift(-5).rolling(10).min()), 'downer'] = 1 # 第15列 以前10天和后5天的值，来定义局部最低点
    data['higher'] = data['higher'].shift(-1)  # 数据处理，缩进
    data['downer'] = data['downer'].shift(-1)  # 数据处理，缩进
    data.loc[data['higher'] == 1, 'high_price'] = data['max1']  # 第16列 最高点填入极值价格
    data.loc[data['downer'] == 1, 'low_price'] = data['min1']   # 第17列 最低点填入极值价格
    data['high_price_fill'] = data['high_price'].fillna(method='ffill') # 第18列 最高点数据填充处理
    data['low_price_fill'] = data['low_price'].fillna(method='ffill')   # 第19列 最低点数据填充处理


    k = 0  # 之前持仓状况
    j = -1  # 上一次操作位置
    a = 1.0  # 初始资产
    e = 0.9999  # 1-交易费率
    s = len(data) - 1

    for i in range(21,s+1):
        if k!=1 and i!=s and data.iat[i,6]>data.iat[i-1,6] and data.iat[i-1,6]<=data.iat[i-2,6] : #非持多均线上拐
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
        if k!=2 and i!=s and data.iat[i,6]<data.iat[i-1,6] and data.iat[i-1,6]>=data.iat[i-2,6] :   #非持空均线下拐
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
        if k==2 and i!=s and data.iat[i,19]<data.iat[i-1,19]-1.2*data.iat[i-1,11]:    #增加平仓条件，局部最低点，评价指标为价格低于前期最低价-1.2倍ATR
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
        if k==1 and i!=s and data.iat[i,18]>data.iat[i-1,18]+1.2*data.iat[i-1,11] :    #增加平仓条件，局部最高点，评价指标为价格高于前期最高价+1.2倍ATR
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

if __name__ == "__main__":
    name = ['铜', '铝', '锌', '镍', '锡', '螺纹']
    path = ['..\\data\\dayx\\CUL9.txt', '../data/dayx/ALL9.txt', '../data/dayx/ZNL9.txt', '../data/dayx/NIL9.txt',
            '../data/dayx/SNL9.txt', '../data/dayx/RBL9.txt']  # 日线数据文件路径
    pathb = ['5m', '15m', '30m', '60m', ]  # 数据文件路径
    i = 0  # 验证铜
    xdata = pd.read_csv(path[i], sep=',', encoding='gbk', usecols=(1, 2, 3, 4, 5, 6,))
    print(path[i] + '（' + name[i] + '）:')
    print('表格原始形状：', xdata.shape)
    logc(xdata)  # 海龟结合双均线策略
    print('单策略结果：')
    print('最终资产：\n', xdata[-1:][['time', 'op', 'stat', 'asset']])
    print('年化收益率%\t交易次数\t次均收益率%：\n', log.yearRate(xdata))
    print('夏普比率：\n', log.SharpeRatio(xdata))
    print('重要回撤：\n', log.retrect(xdata, 15))
    print(xdata)






