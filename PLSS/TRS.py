import arcpy
import os

arcpy.env.workspace = arcpy.GetParameterAsText(4)
target =  arcpy.GetParameterAsText(0)
out_coordinate_system =  arcpy.SpatialReference(102059)

projfc = arcpy.env.scratchGDB + os.path.sep + "projfc"

arcpy.management.Project(target,projfc,out_coordinate_system)

join = arcpy.GetParameterAsText(1) #PLSSQQSec
join2 = arcpy.GetParameterAsText(2) #PLSSSec

pntcent = arcpy.env.scratchGDB + os.path.sep + "pntcent"

arcpy.FeatureToPoint_management(join,pntcent)
out = "PLSSjn1"
out2 = "PLSSjn2"
out4 = arcpy.GetParameterAsText(3)

out = arcpy.env.scratchGDB + os.path.sep + "out"
out2 = arcpy.env.scratchGDB + os.path.sep + "out2"
out3 = arcpy.env.scratchGDB + os.path.sep + "out3"

arcpy.analysis.SpatialJoin(projfc,join,out)
arcpy.analysis.SpatialJoin(out,join2,out2)
arcpy.analysis.Near(out2,pntcent,angle = "ANGLE")
arcpy.management.AddField(out2,"PLSS","TEXT","","","20")

print "joins complete"

# Calculate PLSS CAD field
intable = out2
fieldname = 'PLSS'
expression = 'quarterfill(!TNUM!,!RNUM!,!SNUM!,!QNUM!,!SECDIVNO!,!NEAR_ANGLE!)'
codeblock = '''
def quarterfill(tow, ran, sec, quad, x, a):
    g=x[0:2]
    h=x[2:4]
    m = {'NE':'a','NW':'b','SW':'c','SE':'d'}
    n = {1:'A',2:'B',3:'C',4:'D'}
    qq = m.get(g) or ''
    q = m.get(h) or ''
    j = n.get(quad) or ''
    if a > 90:
        qqq='d'
    elif a <-90:
        qqq='a'
    elif a < 90 and a > 0:
        qqq = 'c'
    elif a < 0 and a > -90:
        qqq = 'b'
    else:
        qqq = ''
    return '('+ str(j)+'-'+ str(int(tow)).rjust(2) + '-' + str(int(ran)).rjust(2)+')'+ str(int(sec)).rjust(2) + q + qq + qqq'''

arcpy.CalculateField_management(intable, fieldname, expression, "PYTHON_9.3", codeblock)

print 'cad complete'

#Add XY coordinates in decimal degree format
out3 = "PLSSProj"
out_coordinate_system =  arcpy.SpatialReference(4269)
arcpy.Project_management(out2,out3,out_coordinate_system)
arcpy.management.AddXY(out3)

out_coordinate_system =  arcpy.SpatialReference(102059)
arcpy.Project_management(out3,out4,out_coordinate_system)
arcpy.management.AddField(out4,"USGSStatID","TEXT","","","25")
print 'proj complete'

#Calculate Station ID field
intable = out4
fieldname = 'USGSStatID'
expression = 'decdeg(!POINT_X!,!POINT_Y!)'
codeblock = '''
def decdeg(x,y):
  degx = int(abs(x))
  degy = int(abs(y))
  tempx = 60* (abs(x) - degx)
  tempy = 60* (abs(y) - degy)
  minx = int(tempx)
  miny = int(tempy)
  secx = str(int(round(60*(tempx-minx),0))).zfill(2)
  secy = str(int(round(60*(tempy-miny),0))).zfill(2)
  return str(degy).zfill(2)+str(miny).zfill(2)+str(secy).zfill(2)+str(degx).zfill(2)+str(minx).zfill(2)+str(secx).zfill(2)'''

arcpy.CalculateField_management(intable, fieldname, expression, "PYTHON_9.3", codeblock)

#Delete intermediates
arcpy.Delete_management(projfc)
arcpy.Delete_management(pntcent)
arcpy.Delete_management(out)
arcpy.Delete_management(out2)
arcpy.Delete_management(out3)

arcpy.DeleteField_management(out4, "Join_Count;TARGET_FID;Join_Count_1;TARGET_FID_1;SECDIVID;FRSTDIVID;SECDIVNO;SECDIVSUF;SECDIVTYP;SECDIVTXT;ACRES;PLSSID;SECDIVLAB;SURVTYP;SURVTYPTXT;FRSTDIVID_1;TOWNSHIP;RANGE;SECTION;BASEMERIDIAN;FRSTDIVNO;FRSTDIVDUP;FRSTDIVTYP;FRSTDIVTXT;PLSSID_1;FRSTDIVLAB;SURVTYP_1;SURVTYPTXT_1;TNUM;RNUM;SNUM;QNUM;NEAR_FID;NEAR_DIST;NEAR_ANGLE")


print "Processing Complete"
