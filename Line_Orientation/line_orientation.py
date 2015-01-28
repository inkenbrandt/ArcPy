# -*- coding: utf-8 -*-
__author__ = "Paul C. Inkenbrandt <paulinkenbrandt@utah.gov>"
__version__ = "0.0"


# Import required modules
import arcpy
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages



arcpy.AddMessage("All Modules Imported Successfully!")

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
arcpy.AddMessage("Spatial Extension is Available")

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# User Inputs #################################################################

# Elevation data
Elevation_Raster = arcpy.GetParameterAsText(0)
if Elevation_Raster == '#' or not Elevation_Raster:
    Elevation_Raster = "C:\\PROJECTS\\Pdwr_Mtn\\Pdwr_Mtn.gdb\\NED10" # provide a default value if unspecified

# Get name of Raster File and assign to variable fieldname
def getFileNameWithoutExtension(path):
  return path.split('\\').pop().split('/').pop().rsplit('.', 1)[0]
fieldname = getFileNameWithoutExtension(Elevation_Raster)

# Lines with orientations
Line_features = arcpy.GetParameterAsText(1)
if Line_features == '#' or not Line_features:
    Line_features = "C:\\PROJECTS\\Pdwr_Mtn\\Pdwr_Mtn.gdb\\Stream_Line.shp" # provide a default value if unspecified

# Location and name of Feature Class Where resulting segments will be stored
Output_Line_features = arcpy.GetParameterAsText(2)

# Place to put rose diagram 
pdf = PdfPages(arcpy.GetParameterAsText(8)+".pdf")
###############################################################################

# Straighten Lines
arcpy.SimplifyLine_cartography(Line_features, Output_Line_features, "POINT_REMOVE", float(arcpy.GetParameterAsText(3)),"FLAG_ERRORS", "NO_KEEP","NO_CHECK")
arcpy.AddMessage("Simplifying Lines complete")

# Create temporary input file for Split Line tool
tempFC = arcpy.env.scratchGDB + os.path.sep + "tempFC"
arcpy.CopyFeatures_management(Output_Line_features, tempFC)

# Overwrite Output lines with line segments     
arcpy.SplitLine_management(tempFC, Output_Line_features)
arcpy.Delete_management(tempFC)
arcpy.AddMessage("Splitting Lines Complete")

# Make a temporary feature class to hold line segment vertices
tempVert = arcpy.env.scratchGDB + os.path.sep + "tempVert"

# Process: Feature Vertices To Points
arcpy.FeatureVerticesToPoints_management(Output_Line_features, tempVert, "BOTH_ENDS")

# Process: Add XY Coordinates to points
arcpy.AddXY_management(tempVert)

# Process: Add Elevation Info to points
arcpy.sa.ExtractMultiValuesToPoints(tempVert, Elevation_Raster, "BILINEAR")
arcpy.AddMessage("Elevation Data Extracted")

# Add RASTERVALU field and populate with output from Extract Values to points
arcpy.AddField_management(tempVert,"RASTERVALU","FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(tempVert, "RASTERVALU", "!"+fieldname+"!", "PYTHON_9.3")

# Process: Summary Statistics
pivotStats = arcpy.env.scratchGDB + os.path.sep + "stats"
arcpy.Statistics_analysis(tempVert, pivotStats, "POINT_X FIRST;POINT_X LAST;POINT_Y FIRST;POINT_Y LAST;RASTERVALU FIRST;RASTERVALU LAST", "ORIG_FID")
arcpy.AddMessage("Calculated Statistics")

# Process: Add and calculate Trend Field
arcpy.AddField_management(pivotStats, "trend", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(pivotStats, "trend", "180 + math.atan2((!LAST_POINT_Y! - !FIRST_POINT_Y!),(!LAST_POINT_X! - !FIRST_POINT_X!)) * (180 / math.pi)", "PYTHON_9.3", "")
arcpy.AddMessage("Trend Calculated")

# Process: Add and calculate Distance Field
arcpy.AddField_management(pivotStats, "distance", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(pivotStats, "distance", "math.sqrt((!LAST_POINT_Y! - !FIRST_POINT_Y!)**2 + (!LAST_POINT_X! - !FIRST_POINT_X!)**2)", "PYTHON_9.3", "")
arcpy.AddMessage("Distance Calculated")

# Process: Add and calculate Plunge Field
arcpy.AddField_management(pivotStats, "plunge", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(pivotStats, "plunge", "math.atan2((!LAST_RASTERVALU! - !FIRST_RASTERVALU!), !distance!)*180/math.pi", "PYTHON_9.3", "")
arcpy.AddMessage("Plunge Calculated")

# Process: Join Table to Shapefile
arcpy.JoinField_management(Output_Line_features, "OBJECTID", pivotStats, "ORIG_FID", "")
arcpy.AddMessage("Fields Joined")

# Clean up intermediate files
arcpy.Delete_management(tempVert)
arcpy.Delete_management(arcpy.env.scratchGDB + os.path.sep + "pivot")
arcpy.Delete_management(pivotStats)
###############################################################################
## PLOTS!!! ##

# Rose Plot
makeroseplot = arcpy.GetParameterAsText(4) # Boolean for activating rose plot
if str(makeroseplot) == 'true':
    import itertools
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection    
    
    # Grab values from the output table to make plots
    arr = arcpy.da.TableToNumPyArray(Output_Line_features,('trend','plunge'),null_value=0)
    arcpy.AddMessage("Trend exported for plotting")
    
    ## ROSE DIAGRAM
    # http://stackoverflow.com/questions/16264837/how-would-one-add-a-colorbar-to-this-example
    # Plot concept by Joe Kington
    some_array_of_azimuth_directions = arr['trend']
    
    
    azi = arr['trend']
    z = [abs(arr['plunge'][i]) for i in range(len(arr['plunge']))]
    
    def rose(azimuths, z=None, ax=None, bins=30, bidirectional=False, 
             color_by=np.mean, **kwargs):
        """Create a "rose" diagram (a.k.a. circular histogram).  
    
        Parameters:
        -----------
            azimuths: sequence of numbers
                The observed azimuths in degrees.
            z: sequence of numbers (optional)
                A second, co-located variable to color the plotted rectangles by.
            ax: a matplotlib Axes (optional)
                The axes to plot on. Defaults to the current axes.
            bins: int or sequence of numbers (optional)
                The number of bins or a sequence of bin edges to use.
            bidirectional: boolean (optional)
                Whether or not to treat the observed azimuths as bi-directional
                measurements (i.e. if True, 0 and 180 are identical).
            color_by: function or string (optional)
                A function to reduce the binned z values with. Alternately, if the
                string "count" is passed in, the displayed bars will be colored by
                their y-value (the number of azimuths measurements in that bin).
            Additional keyword arguments are passed on to PatchCollection.
    
        Returns:
        --------
            A matplotlib PatchCollection
        """
        azimuths = np.asanyarray(azimuths)
        if color_by == 'count':
            z = np.ones_like(azimuths)
            color_by = np.sum
        if ax is None:
            ax = plt.gca()
        ax.set_theta_direction(-1)
        ax.set_theta_offset(np.radians(90))
        if bidirectional:
            other = azimuths + 180
            azimuths = np.concatenate([azimuths, other])
            if z is not None:
                z = np.concatenate([z, z])
        # Convert to 0-360, in case negative or >360 azimuths are passed in.
        azimuths[azimuths > 360] -= 360
        azimuths[azimuths < 0] += 360
        counts, edges = np.histogram(azimuths, range=[0, 360], bins=bins)
        if z is not None:
            idx = np.digitize(azimuths, edges)
            z = np.array([color_by(z[idx == i]) for i in range(1, idx.max() + 1)])
            z = np.ma.masked_invalid(z)
        edges = np.radians(edges)
        coll = colored_bar(edges[:-1], counts, z=z, width=np.diff(edges), 
                           ax=ax, **kwargs)
        return coll
    
    def colored_bar(left, height, z=None, width=0.8, bottom=0, ax=None, **kwargs):
        """A bar plot colored by a scalar sequence."""
        if ax is None:
            ax = plt.gca()
        width = itertools.cycle(np.atleast_1d(width))
        bottom = itertools.cycle(np.atleast_1d(bottom))
        rects = []
        for x, y, h, w in zip(left, bottom, height, width):
            rects.append(Rectangle((x,y), w, h))
        coll = PatchCollection(rects, array=z, **kwargs)
        ax.add_collection(coll)
        ax.autoscale()
        return coll
    
    
    plt.figure(figsize=(5,6))
    plt.subplot(111, projection='polar')
    coll = rose(azi, z=z, bidirectional=True)
    plt.xticks(np.radians(range(0, 360, 45)), 
               ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
    plt.colorbar(coll, orientation='horizontal')
    plt.rgrids()
    plt.xlabel('Dip (Degrees)')
    plt.title(arcpy.GetParameterAsText(5))
    pdf.savefig()    
    
# Stereo Plot
makeStereoplot = arcpy.GetParameterAsText(6) # Boolean for activating stereo plot
if str(makeStereoplot) == 'true':
    # from https://github.com/joferkington/mplstereonet    
    import mplstereonet
    plt.figure()
    fig, ax = mplstereonet.subplots()
    
    # data from output file; add 90 to adjust for strike
    strikes = [arr['trend'][i]+90 for i in range(len(arr['trend']))]
    dips = [abs(arr['plunge'][i]) for i in range(len(arr['plunge']))]
    
    cax = ax.density_contourf(strikes, dips, measurement='poles')
    
    ax.pole(strikes, dips)
    ax.grid(True)
    fig.colorbar(cax)
    plt.title(arcpy.GetParameterAsText(7))    
    pdf.savefig()   

# Save multipage pdf
if str(makeStereoplot) == 'true' or str(makeroseplot) == 'true':
    pdf.close()
    arcpy.AddMessage("Plot saved at " + arcpy.GetParameterAsText(8)+ ".pdf")