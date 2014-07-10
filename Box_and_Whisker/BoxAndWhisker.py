# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 09:44:39 2014


Box and Whisker

http://matplotlib.org/examples/pylab_examples/boxplot_demo2.html
http://matplotlib.org/examples/pylab_examples/boxplot_demo.html
http://stackoverflow.com/questions/16592222/matplotlib-group-boxplots
@author: paulinkenbrandt
"""

from pylab import * # the pylab module combines Pyplot (MATLAB type of plotting) with Numpy into a single namespace
import arcpy
import os

import numpy as np

# if observations are missing, label them as 0

path = os.getcwd() 


input = arcpy.GetParameterAsText(0)



arr = arcpy.da.TableToNumPyArray(input, ( arcpy.GetParameterAsText(1),arcpy.GetParameterAsText(6),arcpy.GetParameterAsText(7),arcpy.GetParameterAsText(8)), null_value=0)


nosamp = len(arr[arcpy.GetParameterAsText(7)]) # Determine number of samples in file


# Column Index for parameters
# Convert to meq/L

Geology = arr[arcpy.GetParameterAsText(1)]

#Geo1 = arcpy.GetParameterAsText(1)
#Geo2 = arcpy.GetParameterAsText(2)
#Geo3 = arcpy.GetParameterAsText(3)
Geo1 = arcpy.GetParameterAsText(2)
Geo2 = arcpy.GetParameterAsText(3)
Geo3 = arcpy.GetParameterAsText(4)
Geo4 = arcpy.GetParameterAsText(5)
p1 = arr[arcpy.GetParameterAsText(6)]
p2 = arr[arcpy.GetParameterAsText(7)]
p3 = arr[arcpy.GetParameterAsText(8)]

# function for setting the colors of the box plots pairs
def setBoxColors(bp):
    setp(bp['boxes'][0], color='blue')
    setp(bp['caps'][0], color='blue')
    setp(bp['caps'][1], color='blue')
    setp(bp['whiskers'][0], color='blue')
    setp(bp['whiskers'][1], color='blue')
    setp(bp['fliers'][0], color='blue')
    setp(bp['fliers'][1], color='blue')
    setp(bp['medians'][0], color='blue')

    setp(bp['boxes'][1], color='red')
    setp(bp['caps'][2], color='red')
    setp(bp['caps'][3], color='red')
    setp(bp['whiskers'][2], color='red')
    setp(bp['whiskers'][3], color='red')
    setp(bp['fliers'][2], color='red')
    setp(bp['fliers'][3], color='red')
    setp(bp['medians'][1], color='red')

    setp(bp['boxes'][2], color='green')
    setp(bp['caps'][4], color='green')
    setp(bp['caps'][5], color='green')
    setp(bp['whiskers'][4], color='green')
    setp(bp['whiskers'][5], color='green')
    setp(bp['fliers'][4], color='green')
    setp(bp['fliers'][5], color='green')
    setp(bp['medians'][2], color='green')
    
    setp(bp['boxes'][3], color='magenta')
    setp(bp['caps'][6], color='magenta')
    setp(bp['caps'][7], color='magenta')
    setp(bp['whiskers'][6], color='magenta')
    setp(bp['whiskers'][7], color='magenta')
    setp(bp['fliers'][6], color='magenta')
    setp(bp['fliers'][7], color='magenta')
    setp(bp['medians'][3], color='magenta')
    

A1 = []
for i in range(nosamp):
    if Geology[i] == Geo1:
        A1.append(p1[i])
A2 = []
for i in range(nosamp):
    if Geology[i] == Geo2:
        A2.append(p1[i])
A3 = []
for i in range(nosamp):
    if Geology[i] == Geo3:
        A3.append(p1[i])
A4 = []
for i in range(nosamp):
    if Geology[i] == Geo4:
        A4.append(p1[i])
B1 = []
for i in range(nosamp):
    if Geology[i] == Geo1:
        B1.append(p2[i])
B2 = []
for i in range(nosamp):
    if Geology[i] == Geo2:
        B2.append(p2[i])
B3 = []
for i in range(nosamp):
    if Geology[i] == Geo3:
        B3.append(p2[i])
B4 = []
for i in range(nosamp):
    if Geology[i] == Geo4:
        B4.append(p2[i])      
C1 = []
for i in range(nosamp):
    if Geology[i] == Geo1:
        C1.append(p3[i])
C2 = []
for i in range(nosamp):
    if Geology[i] == Geo2:
        C2.append(p3[i])
C3 = []
for i in range(nosamp):
    if Geology[i] == Geo3:
        C3.append(p3[i])
C4 = []
for i in range(nosamp):
    if Geology[i] == Geo4:
        C4.append(p3[i])
        
A = [A1,A2,A3,A4]
B = [B1,B2,B3,B4]
C = [C1,C2,C3,C4]

fig = figure()
ax = axes()
hold(True)

# first boxplot pair
bp = boxplot(A, positions = [1, 2, 3, 4], widths = 0.6)
setBoxColors(bp)

# second boxplot pair
bp = boxplot(B, positions = [6, 7, 8, 9], widths = 0.6)
setBoxColors(bp)

# thrid boxplot pair
bp = boxplot(C, positions = [11, 12, 13, 14], widths = 0.6)
setBoxColors(bp)

# set axes limits and labels
xlim(0,15)
#ylim(0,9)
ax.set_xticklabels([arcpy.GetParameterAsText(6), arcpy.GetParameterAsText(7), arcpy.GetParameterAsText(8)])
tspc = np.arange(2.5,14,5) 
ax.set_xticks(tspc)
ax.set_yscale('log')
ylabel('Concentration (mg/l)')
# draw temporary red and blue lines and use them to create a legend
hB, = plot([1,1],'b-')
hR, = plot([1,1],'r-')
hG, = plot([1,1],'g-')
hO, = plot([1,1],'m-')
legend((hB, hR, hG, hO),(Geo1+'  n = '+str(len(A1)), Geo2 + '  n = ' + str(len(A2)), Geo3 + '  n = ' + str(len(A3)), Geo4 + '  n = '+str(len(A4))),loc='upper center', bbox_to_anchor=(0.5, 1.4))
hB.set_visible(False)
hR.set_visible(False)
hG.set_visible(False)
hO.set_visible(False)
# Shink current axis by 20%
box = ax.get_position()

ax.set_position([box.x0, box.y0, box.width, box.height*0.78])


#text(1,max(A1)+100,'n= '+str(len(A1)), rotation=0, fontsize=8)
#text(2,max(A2)10000,'n= '+str(len(A2)), rotation=90, fontsize=8)
#text(3,max(A3)10000,'n= '+str(len(A3)), rotation=90, fontsize=8)
#text(4,max(A4)10000,'n= '+str(len(A4)), rotation=90, fontsize=8)

#text(6,max(B1)+100,'n= '+str(len(B1)), rotation=0, fontsize=8)
#text(7,max(B2)+4,'n= '+str(len(B2)), rotation=90, fontsize=8)
#text(8,max(B3)+4,'n= '+str(len(B3)), rotation=90, fontsize=8)
#text(9,max(B4)+4,'n= '+str(len(B4)), rotation=90, fontsize=8)


#text(11,max(C1)+100,'n= '+str(len(C1)), rotation=0, fontsize=8)
#text(12,max(C2)+4,'n= '+str(len(C2)), rotation=90, fontsize=8)
#text(13,max(C3)+4,'n= '+str(len(C3)), rotation=90, fontsize=8)
#text(14,max(C4)+4,'n= '+str(len(C4)), rotation=90, fontsize=8)


savefig(arcpy.GetParameterAsText(9))
show()
