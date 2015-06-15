#--------------------------------------------------------------
# Purpose:     Creates custom quarter section grid labels.
#
# Author:      Ian Broad
# Website:     www.ianbroad.com
#
# Created:     04/21/2014
#--------------------------------------------------------------

import arcpy

arcpy.env.overwriteOutput = True

polygon = arcpy.GetParameterAsText(0)
labels = arcpy.GetParameterAsText(1)
q_grid = arcpy.GetParameterAsText(2)
output = arcpy.GetParameterAsText(3)

#Assigning labels
one, two, three, four = labels.split(", ")

mem_point = arcpy.CreateFeatureclass_management("in_memory", "mem_point", "POINT", "", "DISABLED", "DISABLED", polygon)
arcpy.AddField_management(mem_point, "GridLabel", "TEXT")

result = arcpy.GetCount_management(polygon)
count = int(result.getOutput(0))

arcpy.SetProgressor("step", "Creating Q Section Labels...", 0, count, 1)

insert_cursor = arcpy.da.InsertCursor(mem_point, ["SHAPE@XY", "GridLabel"])
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

        #Calculates approximate centroid of each quarter quarter section, it's ugly but good enough for now
        LLminDistance     = min(lowerLeft_distances)
        LRminDistance     = min(lowerRight_distances)
        ULminDistance     = min(upperLeft_distances)
        URminDistance     = min(upperRight_distances)

        top_left_X       = upperLeft_distances[ULminDistance][0]
        top_left_Y       = upperLeft_distances[ULminDistance][1]
        top_right_X      = upperRight_distances[URminDistance][0]
        top_right_Y      = upperRight_distances[URminDistance][1]

        bottom_left_X    = lowerLeft_distances[LLminDistance][0]
        bottom_left_Y    = lowerLeft_distances[LLminDistance][1]
        bottom_right_X   = lowerRight_distances[LRminDistance][0]
        bottom_right_Y   = lowerRight_distances[LRminDistance][1]

        top_half_X       = float((top_left_X + top_right_X)/2.0)
        top_half_Y       = float((top_left_Y + top_right_Y)/2.0)

        right_half_X     = float((top_right_X + bottom_right_X)/2.0)
        right_half_Y     = float((top_right_Y + bottom_right_Y)/2.0)

        left_half_X      = float((top_left_X + bottom_left_X)/2.0)
        left_half_Y      = float((top_left_Y + bottom_left_Y)/2.0)

        bottom_half_X    = float((bottom_left_X + bottom_right_X)/2.0)
        bottom_half_Y    = float((bottom_left_Y + bottom_right_Y)/2.0)

        one_X            = float((top_left_X + top_half_X)/2.0)
        one_Y            = float((top_left_Y + left_half_Y)/2.0)

        two_X            = float((top_right_X + top_half_X)/2.0)
        two_Y            = float((top_right_Y + right_half_Y)/2.0)

        three_X          = float((bottom_left_X + bottom_half_X)/2.0)
        three_Y          = float((bottom_left_Y + left_half_Y)/2.0)

        four_X           = float((bottom_right_X + bottom_half_X)/2.0)
        four_Y           = float((bottom_right_Y + right_half_Y)/2.0)

        insert_cursor.insertRow(((one_X, one_Y), one))
        insert_cursor.insertRow(((two_X, two_Y), two))
        insert_cursor.insertRow(((three_X, three_Y), three))
        insert_cursor.insertRow(((four_X, four_Y), four))

        arcpy.SetProgressorPosition()

    except Exception as e:
            print e.message

del insert_cursor
del search_cursor

arcpy.SpatialJoin_analysis(q_grid, mem_point, output, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CLOSEST")
arcpy.Delete_management(mem_point)

arcpy.ResetProgressor()
arcpy.GetMessages()