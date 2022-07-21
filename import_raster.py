#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Charles.Ferguson
#
# Created:     16/05/2022
# Copyright:   (c) Charles.Ferguson 2022
# Licence:     <your licence>

## original intent was to just use copy raster with arcpy.env settings all set to
## be used by the tool.  These included snap raster, output coordinate systems,
## cell size, geographic transformations, resampling method.  this did not work,
## the cell alignment (snapping was off).  Below the input raster is reprojected
## (whether it needs it or not) then the copy raster tool is used.  The copy raster
## tool is the only tool that allows for pixel type transformation.
#-------------------------------------------------------------------------------

def errorMsg():
    try:
        excInfo = sys.exc_info()
        tb = excInfo[2]
        tbinfo = traceback.format_tb(tb)[0]
        theMsg = tbinfo + " \n" + str(sys.exc_type)+ ": " + str(sys.exc_value) + " \n"
        arcpy.AddMessage(theMsg, 2)

    except:
        arcpy.AddMessage("Unhandled error in errorMsg method", 2)



import arcpy, sys, os, traceback


try:

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


    # state = os.path.basename(outDB)[-6:-4]

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

except:
    errorMsg()


