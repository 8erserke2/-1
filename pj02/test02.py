# -*- coding: utf-8 -*-

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


if __name__ == "__main__":
    path = 'il9.txt'  # 数据文件路径
    data=np.loadtxt(path,delimiter='\t',skiprows=1,usecols=(4,))
    td=np.loadtxt(path,dtype=('str'),delimiter='\t',skiprows=1,usecols=(0,))
    print ('数据：\n', data)

    n=99

    y3=[]   #拟合价格
    y4=[]
    y9=[]
    z3=[]   #资产
    z4=[]
    z9=[]
    zz=[]
    f3=0    #进场点与方向
    f4=0
    f9=0    
    a3=0    #进场次数
    a4=0
    a9=0    
    a3x=0
    a3y=0
    a3z=0
    td1=[]
    td2=[]
    f3x=0
    f3y=0
    
    x=range(n+1)
    m=len(data)-n
    for i in range(m):
        y=data[i:i+n+1]
        p3=np.polyfit(x,y,3)
        p4=np.polyfit(x,y,4)
        p9=np.polyfit(x,y,9)
        t3=np.polyval(p3,n)
        t31=np.polyval(p3,n-1)
        t32=np.polyval(p3,n-2)
        t4=np.polyval(p4,n)
        t9=np.polyval(p9,n)
        y3.append(t3)
        y4.append(t4)
        y9.append(t9)
        if i>1:
            if t3>t31 and f3y<=0:
                if f3y==0:
                    zz.append(1)
                else:
                    zz.append(zz[-1]*(2-data[i+n]/data[n-f3y]))
                f3y=i
                td2.append(str(f3y)+'----'+td[i+n])
            if t3<t31 and f3y>=0:
                if f3y==0:
                    zz.append(1)
                else:
                    zz.append(zz[-1]*(data[i+n]/data[n+f3y]))
                f3y=-i
                td2.append(str(f3y)+'----'+td[i+n])
            f3x=0
            if t3>t31 and t31<=t32:
                f3x=1
                a3x=a3x+1
            elif t3<t31 and t31>=t32:
                f3x=-1
                a3x=a3x+1
            if t3>y3[i-1] and y3[i-1]<=y3[i-2]:
                td1.append('1----'+td[i+n])
                if f3x==1:
                    a3y=a3y+1
                if t3>t31:
                    a3z=a3z+1
                a3=a3+1
                if f3!=0:
                    z3.append(z3[-f3]*(2-data[i+n]/data[n-f3]))
                    f3=i
                else:
                    z3.append(1.0)
                    f3=i
            elif t3<y3[i-1] and y3[i-1]>=y3[i-2]:
                td1.append('-1----'+td[i+n])
                if f3x==-1:
                    a3y=a3y+1
                if t3<t31:
                    a3z=a3z+1
                a3=a3+1
                if f3!=0:
                    #print f3,i,z3,z3[f3]*(data[i+n]/data[n+f3])
                    z3.append(z3[f3]*(data[i+n]/data[n+f3]))
                    f3=-i
                else:
                    z3.append(1.0)
                    f3=-i
            elif f3>0:
                #print f3,i,z3,z3[f3]*(data[i+n]/data[n+f3])
                z3.append(z3[f3]*(data[i+n]/data[n+f3]))
            elif f3<0:
                z3.append(z3[-f3]*(2-data[i+n]/data[n-f3]))
            else:
                z3.append(1.0)
                
            if t4>y4[i-1] and y4[i-1]<=y4[i-2]:
                a4=a4+1
                if f4!=0:
                    z4.append(z4[-f4]*(2-data[i+n]/data[n-f4]))
                    f4=i
                else:
                    z4.append(1.0)
                    f4=i
            elif t4<y4[i-1] and y4[i-1]>=y4[i-2]:
                a4=a4+1
                if f4!=0:
                    z4.append(z4[f4]*(data[i+n]/data[n+f4]))
                    f4=-i
                else:
                    z4.append(1.0)
                    f4=-i
            elif f4>0:
                z4.append(z4[f4]*(data[i+n]/data[n+f4]))
            elif f4<0:
                z4.append(z4[-f4]*(2-data[i+n]/data[n-f4]))
            else:
                z4.append(1.0)

            if t9>y9[i-1] and y9[i-1]<=y9[i-2]:
                a9=a9+1
                if f9!=0:
                    z9.append(z9[-f9]*(2-data[i+n]/data[n-f9]))
                    f9=i
                else:
                    z9.append(1.0)
                    f9=i
            elif t9<y9[i-1] and y9[i-1]>=y9[i-2]:
                a9=a9+1
                if f9!=0:
                    z9.append(z9[f9]*(data[i+n]/data[n+f9]))
                    f9=-i
                else:
                    z9.append(1.0)
                    f9=-i
            elif f9>0:
                z9.append(z9[f9]*(data[i+n]/data[n+f9]))
            elif f9<0:
                z9.append(z9[-f9]*(2-data[i+n]/data[n-f9]))
            else:
                z9.append(1.0)
        else:  
            z3.append(1.)
            z4.append(1.)
            z9.append(1.)
    y0=data[n:]
    print ('拐点数3：\n', a3,a3x,a3y,a3z)
    print ('总收益3：\n', z3[m-1],np.power(z3[m-1],243.0/m)*100-100,zz[-1],np.power(zz[-1],243.0/m)*100-100)
    print ('拐点数4：\n', a4)
    print ('总收益4：\n', z4[m-1],np.power(z4[m-1],243.0/m)*100-100)
    print ('拐点数9：\n', a9)
    print ('总收益9：\n', z9[m-1],np.power(z9[m-1],243.0/m)*100-100)
    
    mpl.rcParams['font.sans-serif'] = [u'simHei']
    mpl.rcParams['axes.unicode_minus'] = False

    # 绘制1
    plt.figure(facecolor='w', figsize=(9, 6))
    plt.plot(y0[:100], 'r-', linewidth=2, label=u'真实数据')
    plt.plot(y3[:100], 'g-', linewidth=2, label=u'回归3')
    plt.grid(b=True)
    plt.show()

    # 绘制1
    plt.figure(facecolor='w', figsize=(9, 6))
    plt.plot(y3[:100], 'r-', linewidth=2, label=u'回归3')
    plt.plot(y4[:100], 'g-', linewidth=2, label=u'回归4')
    plt.plot(y9[:100], 'b-', linewidth=2, label=u'回归9')
    plt.grid(b=True)
    plt.show()

    # 绘制2
    plt.figure(facecolor='w', figsize=(9, 6))
    plt.plot(z3, 'r-', linewidth=2, label=u'回归3')
    plt.plot(z4, 'g-', linewidth=2, label=u'回归4')
    plt.plot(z9, 'b-', linewidth=2, label=u'回归9')
    plt.grid(b=True)
    plt.legend(loc='upper right')
    plt.title(u'收益率比较', fontsize=18)
    plt.show()
    
    print (len(td1), td1[:30])
    print (len(td2), td2[:30])
