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


# Input file - should be a selection from a table (table view parameter)
input = arcpy.GetParameterAsText(0)

# Fields that you need in your table for this to work
# Units must be mg/l
# the get parameter is the Type Field

if arcpy.GetParameterAsText(1)<>'' and arcpy.GetParameterAsText(2)<>'':
    try:
        arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg',arcpy.GetParameterAsText(1),arcpy.GetParameterAsText(2) ), null_value=0)
    except RuntimeError:
        arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg'), null_value=0)

elif arcpy.GetParameterAsText(1)<>'' and arcpy.GetParameterAsText(2)=='':
    try:
        arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg',arcpy.GetParameterAsText(1)), null_value=0)
    except RuntimeError:
        arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg'), null_value=0)

elif arcpy.GetParameterAsText(1)=='' and arcpy.GetParameterAsText(2)<>'':
    try:
        arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg',arcpy.GetParameterAsText(2)), null_value=0)
    except RuntimeError:
        arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg'), null_value=0)

else:
    arr = arcpy.da.TableToNumPyArray(input, ('Cl', 'HCO3','CO3', 'SO4','Na','K','Ca','Mg'), null_value=0)

nosamp = len(arr['Cl']) # Determine number of samples in file

# Multipliers to convert from mg/l to meq/l
d = {'Ca':0.04990269, 'Mg':0.082287595, 'Na':0.043497608, 'K':0.02557656, 'Cl':0.028206596, 'HCO3':0.016388838, 'CO3':0.033328223, 'SO4':0.020833333, 'NO2':0.021736513, 'NO3':0.016129032}

# Convert to meq/L and assign to variables
Cl = [arr['Cl'][i]*d['Cl'] for i in range(nosamp)]
Mg = [arr['Mg'][i]*d['Mg'] for i in range(nosamp)]
K = [arr['K'][i]*d['K'] for i in range(nosamp)]
Ca = [arr['Ca'][i]*d['Ca'] for i in range(nosamp)]
Na = [arr['Na'][i]*d['Na'] for i in range(nosamp)]
HCO3 = [arr['HCO3'][i]*d['HCO3'] for i in range(nosamp)]
CO3 = [arr['CO3'][i]*d['CO3'] for i in range(nosamp)]
NaK = [Na[i]+K[i] for i in range(nosamp)]
SO4 = [arr['SO4'][i]*d['SO4'] for i in range(nosamp)]

try:
    Elev = arr[arcpy.GetParameterAsText(1)]
except ValueError:
    Elev =[]
try:
    typ = arr[arcpy.GetParameterAsText(2)]
except ValueError:
    typ = ['nope']*nosamp
# mass balance calculations
Anions = [Cl[i]+HCO3[i]+CO3[i]+SO4[i] for i in range(nosamp)]
Cations = [K[i]+Mg[i]+Na[i]+Ca[i] for i in range(nosamp)]
EC = [Anions[i]+Cations[i] for i in range(nosamp)]

# Various station types (optional input)
typ1 = arcpy.GetParameterAsText(3)
typ2 = arcpy.GetParameterAsText(4)
typ3 = arcpy.GetParameterAsText(5)
typ4 = arcpy.GetParameterAsText(6)

# Assign blank types - this is needed for the symbology and figure display
if typ1 is None:
    typ1='None'
elif typ1 == '':
    typ1='None'
if typ2 is None:
    typ1 = 'None '
elif typ2 == '':
    typ2='None'
if typ3 is None:
    typ3 = 'None '
elif typ3 == '':
    typ3='None'
if typ4 is None:
    typ4 = 'None '
elif typ4 == '':
    typ4='None'    
    
# Change default settings for figures
plt.rc('savefig', dpi = 300)
plt.rc('xtick', labelsize = 10)
plt.rc('ytick', labelsize = 10)
plt.rc('font', size = 12)
plt.rc('legend', fontsize = 12)
plt.rc('figure', figsize = (14,5.5)) # defines size of Figure window orig (14,4.5)

markersize = 12
linewidth = 2
xtickpositions = np.linspace(0,100,6) # desired xtickpositions for graphs

# Make Figure
fig=plt.figure()
# add title
fig.suptitle(arcpy.GetParameterAsText(7), x=0.20,y=.98, fontsize=14 )
# Colormap and Saving Options for Figure

if len(Elev)>0:
    vart = Elev
else:
    vart = [1]*nosamp
cNorm  = plt.Normalize(vmin=min(vart), vmax=max(vart))
cmap = plt.cm.coolwarm
pdf = PdfPages(arcpy.GetParameterAsText(8))

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

for i in range(nosamp):
    if typ1 in typ[i]:    
        ax1.scatter(100*Ca[i]/(EC[i]), 100*Mg[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='v')
    if typ2 in typ[i]:
        ax1.scatter(100*Ca[i]/(EC[i]), 100*Mg[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='^')
    if typ3 in typ[i]:
        ax1.scatter(100*Ca[i]/(EC[i]), 100*Mg[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='+')
    if typ4 in typ[i]:
        ax1.scatter(100*Ca[i]/(EC[i]), 100*Mg[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='s')
    elif (typ1 not in typ[i]) and (typ2 not in typ[i]) and (typ3 not in typ[i]) and (typ4 not in typ[i]): 
        ax1.scatter(100*Ca[i]/(EC[i]), 100*Mg[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='.')
        
ax1.set_xlim(0,100)
ax1.set_ylim(0,100)
ax1b.set_ylim(0,100)
ax1.set_xlabel('<= Ca (% meq)')
ax1b.set_ylabel('Mg (% meq) =>')
plt.setp(ax1, yticklabels=[])

# next line needed to reverse x axis:
ax1.set_xlim(ax1.get_xlim()[::-1]) 


# ANIONS----------------------------------------------------------------------------
plt.subplot(1,3,3)
plt.fill([100,100,0,100],[0,100,100,0],color = (0.8,0.8,0.8))
plt.plot([0, 100],[100, 0],'k')
plt.plot([50, 50, 0, 50],[0, 50, 50, 0],'k--')
plt.text(55,15, 'Cl type')
plt.text(5,15, 'HCO3 type')
plt.text(5,65, 'SO4 type')

for i in range(nosamp):
    if typ1 in typ[i]:
        plt.scatter(100*Cl[i]/(EC[i]), 100*SO4[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='v')
    if typ2 in typ[i]:
        plt.scatter(100*Cl[i]/(EC[i]), 100*SO4[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='^')
    if typ3 in typ[i]:
        plt.scatter(100*Cl[i]/(EC[i]), 100*SO4[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='+')
    if typ4 in typ[i]:
        plt.scatter(100*Cl[i]/(EC[i]), 100*SO4[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='s')
    elif (typ1 not in typ[i]) and (typ2 not in typ[i]) and (typ3 not in typ[i]) and (typ4 not in typ[i]): 
        plt.scatter(100*Cl[i]/(EC[i]), 100*SO4[i]/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm,marker='.')

plt.xlim(0,100)
plt.ylim(0,100)
plt.xlabel('Cl (% meq) =>')
plt.ylabel('SO4 (% meq) =>')


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

# designate variable for legend
s = []
hB, = plt.plot(1,1,'v')
hR, = plt.plot(1,1,'^')
hG, = plt.plot(1,1,'+')
hP, = plt.plot(1,1,'s')
hZ, = plt.plot(1,1,'.')

for i in range(nosamp):
    if typ1 in typ[i]:    
        ax2.scatter(100*NaK[i]/(EC[i]), 100*(SO4[i]+Cl[i])/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm, marker='v')
        s.append(hB)
    if typ2 in typ[i]:
        ax2.scatter(100*NaK[i]/(EC[i]), 100*(SO4[i]+Cl[i])/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm, marker='^')
        s.append(hR)
    if typ3 in typ[i]:   
        ax2.scatter(100*NaK[i]/(EC[i]), 100*(SO4[i]+Cl[i])/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm, marker='+')
        s.append(hG)
    if typ4 in typ[i]:
        ax2.scatter(100*NaK[i]/(EC[i]), 100*(SO4[i]+Cl[i])/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm, marker='s')
        s.append(hP)
    elif (typ1 not in typ[i]) and (typ2 not in typ[i]) and (typ3 not in typ[i]) and (typ4 not in typ[i]):
        ax2.scatter(100*NaK[i]/(EC[i]), 100*(SO4[i]+Cl[i])/(EC[i]),c=vart[i], cmap=cmap, norm =cNorm, marker='.')
        s.append(hZ)
        
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

# count variable for legend (n)
typ1c = s.count(hB)
typ2c = s.count(hR)
typ3c = s.count(hG)
typ4c = s.count(hP)
othrc = len(s)-(typ1c+typ2c+typ3c)



if othrc == len(s):
    # remove duplicates and sort
    s = sorted(list(set(s)))    
    d = {hB:typ1 + '  (n = '+ str(typ1c) + ')',hR:typ2 + '  (n = '+ str(typ2c) + ')',hG:typ3 + '  (n = '+ str(typ3c) + ')',hP:typ4 + '  (n = '+ str(typ4c) + ')',hZ:'Samples'+ '  (n = '+ str(othrc) + ')'}
else:
    # remove duplicates and sort
    s = sorted(list(set(s)))    
    d = {hB:typ1 + '  (n = '+ str(typ1c) + ')',hR:typ2 + '  (n = '+ str(typ2c) + ')',hG:typ3 + '  (n = '+ str(typ3c) + ')',hP:typ4 + '  (n = '+ str(typ4c) + ')',hZ:'Other'+ '  (n = '+ str(othrc) + ')'}

b = [d[s[i]] for i in range(len(s))]

# Add colorbar below legend
#[left, bottom, width, height] where all quantities are in fractions of figure width and height

if len(Elev)<>0:
    cax = fig.add_axes([0.25,0.10,0.50,0.02])    
    cb1 = plt.colorbar(cax=cax, cmap=cmap, norm=cNorm, orientation='horizontal') #use_gridspec=True
    cb1.set_label(arcpy.GetParameterAsText(1),size=8)
    plt.legend(s,b, loc='lower center', ncol=5, shadow=False, fancybox=True, bbox_to_anchor=(0.5, 0.6))

else:
    plt.legend(s,b, loc='lower center', ncol=5, shadow=False, fancybox=True, bbox_to_anchor=(0.5, -0.4))



# Hide points made to create legend
hB.set_visible(False)
hR.set_visible(False)
hG.set_visible(False)
hP.set_visible(False)
hZ.set_visible(False)
    

                             
pdf.savefig()
pdf.close()

print "done"