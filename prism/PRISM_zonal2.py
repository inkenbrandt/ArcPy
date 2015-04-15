# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# PRISM_zonal2.py
# Created on: 2014-12-09 14:53:45.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: PRISM_zonal2 <Zone_field> <v_Name_> <Wildcard> <HUCS> <Downsampled> 
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Load required toolboxes
arcpy.ImportToolbox("Model Functions")

# Script arguments
Zone_field = arcpy.GetParameterAsText(0)
if Zone_field == '#' or not Zone_field:
    Zone_field = "ID" # provide a default value if unspecified

v_Name_ = arcpy.GetParameterAsText(1)
if v_Name_ == '#' or not v_Name_:
    v_Name_ = "C:\\GIS\\PRISM\\Table\\%Name%" # provide a default value if unspecified

Wildcard = arcpy.GetParameterAsText(2)
if Wildcard == '#' or not Wildcard:
    Wildcard = "a30*" # provide a default value if unspecified

HUCS = arcpy.GetParameterAsText(3)
if HUCS == '#' or not HUCS:
    HUCS = "U:\\GWP\\Groundwater\\PowderMt\\Powder_Mtn.gdb\\Watershed" # provide a default value if unspecified

Downsampled = arcpy.GetParameterAsText(4)
if Downsampled == '#' or not Downsampled:
    Downsampled = "C:\\GIS\\PRISM\\Downsampled" # provide a default value if unspecified

# Local variables:
Raster = Downsampled
Name = Downsampled

# Process: Iterate Rasters
arcpy.IterateRasters_mb(Downsampled, Wildcard, "", "NOT_RECURSIVE")

# Process: Zonal Statistics as Table
arcpy.gp.ZonalStatisticsAsTable_sa(HUCS, Zone_field, Raster, v_Name_, "DATA", "ALL")
