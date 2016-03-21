# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 12:32:51 2015

@author: paulinkenbrandt
"""

# -*- coding: utf-8 -*-
"""
Created on Thu May 29 10:57:49 2014

 Hydrochemistry - Construct Rectangular Piper plot

    Adopted from: Ray and Mukherjee (2008) Groundwater 46(6): 893-896 
    and from code found at:
    http://python.hydrology-amsterdam.nl/scripts/piper_rectangular.py

    Based on code by:
    B.M. van Breukelen <b.m.vanbreukelen@vu.nl>  
      
"""
#from pylab import * 
import arcpy
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from arcpy import env
from matplotlib.lines import Line2D
from collections import OrderedDict
#import matplotlib as mpl
#mpl.rcParams.update(mpl.rcParamsDefault)

env.workspace = "CURRENT" 

#Functions 
def getfilename(path):
    # this function extracts the file name without file path or extension
    return path.split('\\').pop().split('/').pop().rsplit('.', 1)[0]


#Inputs
resultstable = arcpy.GetParameterAsText(0)
meq = arcpy.GetParameterAsText(1)

typ,Elev = [],[]

try:
    ElevField = arcpy.GetParameterAsText(2)
    with arcpy.da.SearchCursor(resultstable,[ElevField]) as cursor:
        for row in cursor:
            if row[0] == None or row[0]=='' or np.isnan(row[0]):
                Elev.append(0)
            else:
                Elev.append(row[0])   
except ValueError:
    pass


try:      
    typField = arcpy.GetParameterAsText(3)
    with arcpy.da.SearchCursor(resultstable,[typField]) as cursor:                        
        for row in cursor:
            if row[0] > 0:
                typ.append(row[0])                
            else:
                typ.append('Sample')
    stationtypes = np.unique(typ)            
except:
    stationtypes = [''] 


piperTitle = arcpy.GetParameterAsText(4)
fileplace = arcpy.GetParameterAsText(5)



fieldnames = [u'Na', u'K', u'Ca', u'Mg', u'Cl', u'HCO3', u'CO3', u'SO4']

fieldlist = [f.name for f in arcpy.ListFields(resultstable)] #get fields from input table

# Check to see if all parameters are in table; 
# Create empty datasets for the missing parameters
for field in fieldnames: #loop through each field
    if field not in fieldlist:
        arcpy.AddMessage('WARNING! ' + field + ' not one of the columns, adding field' )
        arcpy.AddField_management(resultstable, field, "FLOAT", 6, "", "", field, "NULLABLE")
        with arcpy.da.UpdateCursor(resultstable,[field]) as cursor:
            for row in cursor:
                row[0] = '0'
                cursor.updateRow(row)

# Convert values in table fields to numpy arrays
# populate lists with values from the active table
Na, K, Ca, Mg, Cl, HCO3, CO3, SO4 = [],[],[],[],[],[],[],[]
constItems = [Na,K,Ca,Mg,Cl,HCO3,CO3,SO4]

data = {}

with arcpy.da.SearchCursor(resultstable,['Na', 'K', 'Ca', 'Mg', 'Cl', 'HCO3', 'CO3', 'SO4']) as cursor:
    for row in cursor:
        for i in range(len(row)):
            if row[i] == None or row[i]=='' or np.isnan(row[i]):
                constItems[i].append(0)
            else:
                constItems[i].append(row[i])


x, y = [],[]
with arcpy.da.SearchCursor(resultstable, "SHAPE@XY") as cursor:
    for row in cursor:
        x.append(row[0][0])
        y.append(row[0][1]) 

# Get spatial reference of input dataset
desc = arcpy.Describe(resultstable)
spatialref = desc.spatialReference 

nosamp = len(Cl) # Determine number of samples in file

#Conversion factors from mg/L to meq/L
d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}

# Checkbox; If checked, meq/L conversion is done
if str(meq) == 'true':
    # Column Index for parameters
    # Convert ion concentrations in mg/L to meq/L
    Cl = [Cl[i]*d['Cl'] for i in range(nosamp)]
    Mg = [Mg[i]*d['Mg'] for i in range(nosamp)]
    K = [K[i]*d['K'] for i in range(nosamp)]
    Ca = [Ca[i]*d['Ca'] for i in range(nosamp)]
    Na = [Na[i]*d['Na'] for i in range(nosamp)]
    HCO3 = [HCO3[i]*d['HCO3'] for i in range(nosamp)]
    CO3 = [CO3[i]*d['CO3'] for i in range(nosamp)]
    NaK = [Na[i]+K[i] for i in range(nosamp)] #Already Converted above
    SO4 = [SO4[i]*d['SO4'] for i in range(nosamp)]
    arcpy.AddMessage('Converting from mgL')
else:
    NaK = [Na[i]+K[i] for i in range(nosamp)]
    arcpy.AddMessage('No conversion')


#Sum Anions and Cations to determine charge balance
Anions = [Cl[i]+HCO3[i]+CO3[i]+SO4[i] for i in range(nosamp)]
Cations = [K[i]+Mg[i]+Na[i]+Ca[i] for i in range(nosamp)]
EC = [Anions[i]+Cations[i] for i in range(nosamp)]
BAL = [(Cations[i]-abs(Anions[i]))/(abs(Anions[i])+Cations[i]) for i in range(nosamp)]

#Print Charge Balance
for i in EC:
    arcpy.AddMessage('Anions + Cations = ' +str(i))

CaEC = [100*Ca[i]/(Cations[i]) for i in range(nosamp)]
MgEC = [100*Mg[i]/(Cations[i]) for i in range(nosamp)]
ClEC = [100*Cl[i]/(Anions[i]) for i in range(nosamp)]
SO4EC = [100*SO4[i]/(Anions[i]) for i in range(nosamp)]
NaKEC = [100*NaK[i]/(Cations[i]) for i in range(nosamp)]
SO4ClEC = [100*(SO4[i]+Cl[i])/(Anions[i]) for i in range(nosamp)]

# Change default settings for figures
plt.rc('savefig', dpi = 400)
plt.rc('xtick', labelsize = 10)
plt.rc('ytick', labelsize = 10)
plt.rc('font', size = 12)
plt.rc('legend', fontsize = 12)
plt.rc('figure', figsize = (14,5.5)) # defines size of Figure window orig (14,4.5)
plt.rc('svg', fonttype = 'svgfont')

markSize = 30
lineW = 0.5
xtickpositions = np.linspace(0,100,6) # desired xtickpositions for graphs

# Make Figure
fig = plt.figure()
# add title
fig.suptitle(piperTitle, x=0.20,y=.98, fontsize=14 )
# Colormap and Saving Options for Figure

if len(Elev)>0:
    vart = Elev
else:
    vart = [1]*nosamp
cNorm  = plt.Normalize(vmin=min(vart), vmax=max(vart))
cmap = plt.cm.coolwarm
#pdf = PdfPages(fileplace)

mrkrSymbl = ['v', '^', '+', 's', '.', 'o', '*', 'v', '^', '+', 's', ',', '.', 'o', '*','v', '^', '+', 's', ',', '.', 'o', '*', 'v', '^', '+', 's', ',', '.', 'o', '*']

# count variable for legend (n)
nstatTypes = [typ.count(i) for i in stationtypes]

typdict = {}
nstatTypesDict = {}
for i in range(len(stationtypes)):
    typdict[stationtypes[i]] = mrkrSymbl[i]
    nstatTypesDict[stationtypes[i]] = str(nstatTypes[i])

# CATIONS-----------------------------------------------------------------------------
# 2 lines below needed to create 2nd y-axis (ax1b) for first subplot
ax1 = fig.add_subplot(131)
ax1b = ax1.twinx()

ax1.fill([100,0,100,100],[0,100,100,0],color = (0.8,0.8,0.8))
ax1.plot([100, 0],[0, 100],'k')
ax1.plot([50, 0, 50, 50],[0, 50, 50, 0],'k--')
ax1.text(25,15, 'Na type')
ax1.text(75,15, 'Ca type')
ax1.text(25,65, 'Mg type')

if len(typ) > 0:
    for j in range(len(typ)):    
        ax1.scatter(CaEC[j], MgEC[j], s=markSize, c=vart[j], cmap= cmap, norm = cNorm, marker=typdict[typ[j]], linewidths = lineW)
else:
    ax1.scatter(CaEC, MgEC, s=markSize, c=vart, cmap= cmap, norm = cNorm, linewidths = lineW)

ax1.set_xlim(0,100)
ax1.set_ylim(0,100)
ax1b.set_ylim(0,100)
ax1.set_xlabel('<= Ca (% meq)')
ax1b.set_ylabel('Mg (% meq) =>')
plt.setp(ax1, yticklabels=[])

# next line needed to reverse x axis:
ax1.set_xlim(ax1.get_xlim()[::-1]) 

# ANIONS----------------------------------------------------------------------------
ax = fig.add_subplot(1,3,3)
ax.fill([100,100,0,100],[0,100,100,0],color = (0.8,0.8,0.8))
ax.plot([0, 100],[100, 0],'k')
ax.plot([50, 50, 0, 50],[0, 50, 50, 0],'k--')
ax.text(55,15, 'Cl type')
ax.text(5,15, 'HCO3 type')
ax.text(5,65, 'SO4 type')

if len(typ) > 0:
    for j in range(len(typ)):
        labs = typ[j] + " n= " + nstatTypesDict[typ[j]]
        if float(nstatTypesDict[typ[j]]) > 1:
            s = ax.scatter(ClEC[j], SO4EC[j], s=markSize, c=vart[j], cmap=cmap, norm =cNorm, marker=typdict[typ[j]], label=labs, linewidths = lineW)
        else:
            s = ax.scatter(ClEC[j], SO4EC[j], s=markSize, c=vart[j], cmap=cmap, norm =cNorm, marker=typdict[typ[j]], label=typ[j], linewidths = lineW)
else:
    s = ax.scatter(ClEC, SO4EC, s=markSize, c=vart, cmap=cmap, norm =cNorm, label='Sample', linewidths = lineW)

ax.set_xlim(0,100)
ax.set_ylim(0,100)
ax.set_xlabel('Cl (% meq) =>')
ax.set_ylabel('SO4 (% meq) =>')

# CATIONS AND ANIONS COMBINED ---------------------------------------------------------------
# 2 lines below needed to create 2nd y-axis (ax1b) for first subplot
ax2 = fig.add_subplot(132)
ax2b = ax2.twinx()

ax2.plot([0, 100],[10, 10],'k--')
ax2.plot([0, 100],[50, 50],'k--')
ax2.plot([0, 100],[90, 90],'k--')
ax2.plot([10, 10],[0, 100],'k--')
ax2.plot([50, 50],[0, 100],'k--')
ax2.plot([90, 90],[0, 100],'k--')

if len(typ) > 0:
    for j in range(len(typ)):    
        ax2.scatter(NaKEC[j], SO4ClEC[j], s=markSize, c=vart[j], cmap=cmap, norm =cNorm, marker=typdict[typ[j]], linewidths = lineW)
else:
    ax2.scatter(NaKEC, SO4ClEC, s=markSize, c=vart, cmap=cmap, norm =cNorm, linewidths = lineW)

ax2.set_xlim(0,100)
ax2.set_ylim(0,100)
ax2.set_xlabel('Na+K (% meq) =>')
ax2.set_ylabel('SO4+Cl (% meq) =>')
ax2.set_title('<= Ca+Mg (% meq)', fontsize = 12)
ax2b.set_ylabel('<= CO3+HCO3 (% meq)')
ax2b.set_ylim(0,100)

# next two lines needed to reverse 2nd y axis:
ax2b.set_ylim(ax2b.get_ylim()[::-1])

# Align plots
plt.subplots_adjust(left=0.05, bottom=0.35, right=0.95, top=0.90, wspace=0.4, hspace=0.0)    

#Legend-----------------------------------------------------------------------------------------

# Add colorbar below legend
#[left, bottom, width, height] where all quantities are in fractions of figure width and height


if len(Elev)>0:
    cax = fig.add_axes([0.25,0.10,0.50,0.02])    
    cb1 = plt.colorbar(s, cax=cax, cmap=cmap, norm=cNorm, orientation='horizontal') #use_gridspec=True
    cb1.set_label(arcpy.GetParameterAsText(2),size=8) 
    
if len(typ)>0:
    handles, labels = ax.get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))

    plt.legend(by_label.values(), by_label.keys(), loc='lower center', ncol=5, shadow=False, fancybox=True, bbox_to_anchor=(0.5, 0.6), scatterpoints=1)

#pdf.savefig()
#pdf.close()
plt.savefig(fileplace)
plt.close()
print "done"