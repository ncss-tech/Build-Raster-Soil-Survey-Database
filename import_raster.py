#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Charles.Ferguson
#
# Created:     16/05/2022
# Copyright:   (c) Charles.Ferguson 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, sys, os

model_raster = arcpy.GetParameterAsText(0)
outDB = arcpy.GetParameterAsText(1)
state = arcpy.GetParameterAsText(2)

##set the snap raster environment
loc = sys.argv[0]
snap_dir = os.path.dirname(loc)
snap = os.path.join(snap_dir, "RSS_gSSURGO_snap.tif")
arcpy.AddMessage(snap)
arcpy.env.snapRaster = snap

##spatial reference
osr = arcpy.SpatialReference(5070)
arcpy.env.outputCoordinateSystem = osr

##resampling method
arcpy.env.resamplingMethod = "NEAREST"

desc = arcpy.Describe(model_raster)
cp = desc.catalogPath

RBdesc = arcpy.Describe(os.path.join(cp, "Band_1"))
if RBdesc.meanCellHeight != 10.0 or RBdesc.meanCellWidth != 10.0:
    arcpy.env.cellSize = 10


sr = desc.spatialReference
arcpy.AddMessage(sr.GCS.name)
if sr.GCS.name == "GCS_WGS_1984":
    tm = "WGS_1984_(ITRF00)_To_NAD_1983"
    arcpy.management.ProjectRaster(model_raster, outDB + os.sep + "temp_raster_10m_" + state, osr, "NEAREST", 10, tm, None, None, None )

elif sr.GCS.name == "GCS_North_American_1983":
    # no trannsformation needed
    arcpy.management.ProjectRaster(model_raster, outDB + os.sep + "temp_raster_10m_" + state, osr, "NEAREST", 10, None, None, None, None )

arcpy.management.CopyRaster(outDB + os.sep + "temp_raster_10m_" + state, outDB + os.sep + "MapunitRaster_10m_" + state, None, None, None, None, None, "32_BIT_UNSIGNED")

arcpy.management.Delete(outDB + os.sep + "temp_raster_10m_" + state)



