#--------------------------------------------------------------
# Purpose:     Creates a custom grid from an existing
#              polygon feature class.
#
# Author:      Ian Broad
# Website:     www.ianbroad.com
#
# Created:     08/18/2014
#--------------------------------------------------------------

import arcpy

arcpy.env.overwriteOutput = True

def vertical(TLX, TRX, TLY, TRY, BLX, BRX, BLY, BRY, divisions):

    count = 1.0
    while count < divisions:
        a         = float(TLX*((divisions-count)/divisions) + TRX*(count/divisions)) + float(overflow)
        b         = float(TLY*((divisions-count)/divisions) + TRY*(count/divisions)) + float(overflow)

        c         = float(BLX*((divisions-count)/divisions) + BRX*(count/divisions)) - float(overflow)
        d         = float(BLY*((divisions-count)/divisions) + BRY*(count/divisions)) - float(overflow)

        T2B       = arcpy.Array([arcpy.Point(a, b), arcpy.Point(c, d)])
        T2B_line  = arcpy.Polyline(T2B)

        insert_cursor.insertRow((T2B_line,))

        count += 1.0

def horizontal(TLX, TRX, TLY, TRY, BLX, BRX, BLY, BRY, divisions):

    count = 1.0
    while count < divisions:
        a         = float(TLX*((divisions-count)/divisions) + BLX*(count/divisions)) - float(overflow)
        b         = float(TLY*((divisions-count)/divisions) + BLY*(count/divisions)) - float(overflow)

        c         = float(TRX*((divisions-count)/divisions) + BRX*(count/divisions)) + float(overflow)
        d         = float(TRY*((divisions-count)/divisions) + BRY*(count/divisions)) + float(overflow)

        L2R       = arcpy.Array([arcpy.Point(a, b), arcpy.Point(c, d)])
        L2R_line  = arcpy.Polyline(L2R)

        insert_cursor.insertRow((L2R_line,))

        count += 1.0

polygon = arcpy.GetParameterAsText(0)
vertical_div = int(round(float(arcpy.GetParameterAsText(1))))
horizontal_div = int(round(float(arcpy.GetParameterAsText(2))))
output = arcpy.GetParameterAsText(3)
overflow = arcpy.GetParameterAsText(4)

if "in_memory" in output:
    mem_name = output.split("\\")[-1]
else:
    mem_name = "mem_line"

mem_line = arcpy.CreateFeatureclass_management("in_memory", mem_name, "POLYLINE", "", "DISABLED", "DISABLED", polygon)

result = arcpy.GetCount_management(polygon)
count = int(result.getOutput(0))

arcpy.SetProgressor("step", "Creating Custom Grid...", 0, count, 1)

insert_cursor = arcpy.da.InsertCursor(mem_line, ["SHAPE@"])
search_cursor = arcpy.da.SearchCursor(polygon, ["SHAPE@"])

for row in search_cursor:
    try:
        coordinateList = []
        lowerLeft_distances   = {}
        lowerRight_distances  = {}
        upperLeft_distances   = {}
        upperRight_distances  = {}

        for part in row[0]:
            for pnt in part:
                if pnt:
                    coordinateList.append((pnt.X, pnt.Y))

        #Finds the extent of each polygon
        polygonExtent = row[0].extent

        lowerLeft_coordinate = polygonExtent.lowerLeft
        lowerRight_coordinate = polygonExtent.lowerRight
        upperLeft_coordinate = polygonExtent.upperLeft
        upperRight_coordinate = polygonExtent.upperRight

        lowerLeft_point = arcpy.PointGeometry(lowerLeft_coordinate)
        lowerRight_point = arcpy.PointGeometry(lowerRight_coordinate)
        upperLeft_point = arcpy.PointGeometry(upperLeft_coordinate)
        upperRight_point = arcpy.PointGeometry(upperRight_coordinate)

        #Finds the vertex closest to each corner of the polygon extent
        for vertex in coordinateList:
            vertex_coordinates = arcpy.Point(vertex[0], vertex[1])
            vertex_point = arcpy.PointGeometry(vertex_coordinates)
            lowerLeft_distances[float(lowerLeft_point.distanceTo(vertex_point))] = (vertex[0], vertex[1])

        for vertex in coordinateList:
            vertex_coordinates = arcpy.Point(vertex[0], vertex[1])
            vertex_point = arcpy.PointGeometry(vertex_coordinates)
            lowerRight_distances[float(lowerRight_point.distanceTo(vertex_point))] = (vertex[0], vertex[1])

        for vertex in coordinateList:
            vertex_coordinates = arcpy.Point(vertex[0], vertex[1])
            vertex_point = arcpy.PointGeometry(vertex_coordinates)
            upperLeft_distances[float(upperLeft_point.distanceTo(vertex_point))] = (vertex[0], vertex[1])

        for vertex in coordinateList:
            vertex_coordinates = arcpy.Point(vertex[0], vertex[1])
            vertex_point = arcpy.PointGeometry(vertex_coordinates)
            upperRight_distances[float(upperRight_point.distanceTo(vertex_point))] = (vertex[0], vertex[1])

        #Calculates where quarter quarter sections would intersect polygon
        LLminDistance     = min(lowerLeft_distances)
        LRminDistance     = min(lowerRight_distances)
        ULminDistance     = min(upperLeft_distances)
        URminDistance     = min(upperRight_distances)

        top_left_X       = float(upperLeft_distances[ULminDistance][0])
        top_left_Y       = float(upperLeft_distances[ULminDistance][1])
        top_right_X      = float(upperRight_distances[URminDistance][0])
        top_right_Y      = float(upperRight_distances[URminDistance][1])

        bottom_left_X    = float(lowerLeft_distances[LLminDistance][0])
        bottom_left_Y    = float(lowerLeft_distances[LLminDistance][1])
        bottom_right_X   = float(lowerRight_distances[LRminDistance][0])
        bottom_right_Y   = float(lowerRight_distances[LRminDistance][1])

        arcpy.SetProgressorPosition()

        vertical(top_left_X, top_right_X, top_left_Y, top_right_Y, bottom_left_X, bottom_right_X, bottom_left_Y, bottom_right_Y, vertical_div)
        horizontal(top_left_X, top_right_X, top_left_Y, top_right_Y, bottom_left_X, bottom_right_X, bottom_left_Y, bottom_right_Y, horizontal_div)

    except Exception as e:
        print e.message

del insert_cursor
del search_cursor

if "in_memory" in output:
    arcpy.SetParameter(5, mem_line)
else:
    arcpy.CopyFeatures_management(mem_line, output)
    arcpy.Delete_management(mem_line)

arcpy.ResetProgressor()
arcpy.GetMessages()