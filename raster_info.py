#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Charles.Ferguson
#
# Created:     25/05/2022
# Copyright:   (c) Charles.Ferguson 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy

r =r'D:\GIS\PROJECT_21\GSOCS\conus_lu_crop.tif'

desc = arcpy.Describe(r)

sr = desc.spatialReference

gcs = sr.GCS

print(gcs.name)
print(sr.GCSName)
print(sr.PCSCode)