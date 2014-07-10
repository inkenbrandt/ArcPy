"""Created on Thu Jun 26 11:11:42 2014
@author: paulinkenbrandt"""

from pylab import * 
import arcpy
import numpy as np
import pandas as pd
import datetime
import matplotlib.colors as clrs


input = "PIEZO.dbf"

# field names must match input fields
arr = arcpy.da.TableToNumPyArray(input, ('PiezoID','DateTIME','WaterDepth'), skip_nulls = True)

piezo = arr['PiezoID']


newday = [(datetime.datetime.strptime(arr['DateTIME'][i],'%m/%d/%Y')) for i in range(len(piezo))]
    # assign water level as z
z = [(arr['WaterDepth'][i]) for i in range(len(piezo))]

# define year variable as y and convert from datetime format
y = [int(newday[i].strftime('%Y')) for i in range(len(newday))]

# define day variable as x and convert from datetime format
x = [int(newday[i].strftime('%j')) for i in range(len(newday))]

arrin = zip(piezo,newday,x,y,z)
df = pd.DataFrame(arrin, columns = ['piezo','date','day','year','wl'])

df.sort(columns=['piezo','date'], inplace=True)
df.set_index(keys=['piezo'],drop=False,inplace=True)

# Define Extreme Values for all datasets
xmin = min(x)
xmax = max(x)
ymin = min(y)
ymax = max(y)

cNorm  = clrs.Normalize(vmin=min(z), vmax=max(z))
cmap = plt.cm.jet


g = df.groupby('piezo')

for name, group in g:
    x = group['day']
    y = group['year']
    z = group['wl']
    plt.figure()    
    lines = plt.scatter(x,y,c=z ,marker = '|', cmap = cmap, norm = cNorm, s=5050)
    plt.setp(lines, linewidth = 4.0)
    m=cm.ScalarMappable(cmap=cmap,norm=cNorm)
    m.set_array(z)
    cb1 = plt.colorbar(m) 
    cb1.set_label('Water Level (ft)',size=9)
    plt.title(name)    
    plt.xlabel('month', size= 9)
    plt.ylabel('year', size = 9)
    plt.xticks(arange(1,361,30), [1,2,3,4,5,6,7,8,9,10,11,12], rotation=30, size='x-small')
    plt.yticks(arange(ymin,ymax+1,1),arange(ymin,ymax+1,1),size='x-small')
    plt.ylim(ymin-1,ymax+1)
    plt.xlim(xmin,xmax)
    plt.savefig(name +".pdf",format='pdf')
    plt.close()