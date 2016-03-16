# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 16:00:30 2016

@author: paulinkenbrandt
"""

import numpy as np
import os
import arcpy
from arcpy import env
#import math

env.workspace = "M:\GIS\SnakeValley.gdb"#"CURRENT" #Set workspace as open map

#Functions 
def getfilename(path):
    # this function extracts the file name without file path or extension
    return path.split('\\').pop().split('/').pop().rsplit('.', 1)[0]

points = "sample"
buff = 0.05
outFeatureClass = "fishfndekmtadd"
# Number of rows and columns together with origin and opposite corner 
# determine the size of each cell 
numRows =  '50'
numColumns = '50'
S = 0.005
T = 10000
t = 100
Q = 100000
#Inputs
#points = arcpy.GetParameterAsText(0)
#Q = arcpy.GetParameterAsText(1)
#t = float(arcpy.GetParameterAsText(2))
#T = float(arcpy.GetParameterAsText(3)) #vertical multiplier
#S = float(arcpy.GetParameterAsText(4)) #horizontal multiplier
#buff = float(arcpy.GetParameterAsText(5))
#fileplace = arcpy.GetParameterAsText(5)

x, y = [], []

for row in arcpy.da.SearchCursor(points, ["SHAPE@XY"]):
    # Print x,y coordinates of each point feature
    x.append(row[0][0])
    y.append(row[0][1])    


desc = arcpy.Describe(points)
spatialref = desc.spatialReference 

meanx = np.average(x)
meany = np.average(y)


print(meanx)
print(meany)

miny = np.min(y)
minx = np.min(x)
maxy = np.max(y)
maxx = np.max(x)


# Set coordinate system of the output fishnet
env.outputCoordinateSystem = spatialref


# Set the origin of the fishnet
originCoordinate = str(minx-buff)+" "+str(miny-buff)

# Set the orientation
yAxisCoordinate = str(minx-buff)+" "+str(maxy+buff)

print(yAxisCoordinate)
print(originCoordinate)

# Enter 0 for width and height - these values will be calcualted by the tool
cellSizeWidth = '0'
cellSizeHeight = '0'

oppositeCoorner = str(maxx+buff)+" "+str(maxy+buff)

# Create a point label feature class 
labels = 'LABELS'

# Extent is set by origin and opposite corner - no need to use a template fc
templateExtent = points

# Each output cell will be a polygon
geometryType = 'POLYGON'

arcpy.CreateFishnet_management(outFeatureClass, originCoordinate, yAxisCoordinate, cellSizeWidth, cellSizeHeight, numRows, numColumns, oppositeCoorner, labels, templateExtent, geometryType)

grid_points = outFeatureClass+"_label"

gx, gy = [],[]

for row in arcpy.da.SearchCursor(grid_points, ["SHAPE@", "SHAPE@XY", "SHAPE@TRUECENTROID"]):
    # Print x,y coordinates of each point feature
    #
    gx.append(row[1][0])
    gy.append(row[1][1])    

uval = {}
f = {}
hval = {}
for j in range(len(x)):
    d = []    
    h = []
    u = []
    for i in range(len(gx)):
        
        d.append(np.sqrt(np.power((x[j]-gx[i]),2)+np.power((y[j]-gy[i]),2)))
        f[j] = d        
        u.append((np.power(d[i],2)*S)/(4*T*t))
        uval[j] = u
        qpart = (Q/(4.0*np.pi*T))
        lnpart = (-0.5772-np.log(u[i])+u[i]-(np.power(u[i],2)/(2.0*np.math.factorial(2)))+(np.power(u[i],3)/(3*np.math.factorial(3)))-(np.power(u[i],4)/(4*np.math.factorial(4))))
        h.append(qpart*lnpart)
        hval[j] = h
print(hval[0][1])
print(len(f))
# get xy from points
# get centroid of point set from xy
# get extent from proints
# add buffer to extent and use for fishnet extent
# create fishnet points from derived values

# calculate distance from fishnet points to well points
# use distance for each Thies calculation in well points
# (Q/(4piT))*[-0.5772-ln(u)+u-(u^2/2*2!)+(u^3/3*3!)-(u^4/4*4!)]
# create field in fishnet for each well point to designate drawdown from that point
# create field in fishnet that is the sum of all drawdowns
# interpolate fishnet points