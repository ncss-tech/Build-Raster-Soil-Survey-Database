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

import arcpy, sys

model_raster = arcpy.GetParameterAsText(0)
outDB = arcpy.GetParameterAsText(1)
state = arcpy.GetParameterAsText
loc = sys.argv[0]
snap_dir = os.path.dirname(loc)
raster = os.path.join(snap_dir, "RSS_gSSURGO_snap.tif")
arcpy.env.snapRaster = raster

arcpy.management.CopyRaster(model_raster, outDB + "MapunitRaster_10m_" + state)