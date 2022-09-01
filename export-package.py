# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 13:25:46 2022

@author: Charles.Ferguson
"""

import os, arcpy, shutil

inDB = arcpy.GetParameterAsText(0)
inRaster =  arcpy.GetParameterAsText(1)
inTemplate = arcpy.GetParameterAsText(2)

i = inDB.rfind("_")
state = inDB[i+1:i+3]

theRaster = os.path.join(inDB, inRaster)
db_dir= os.path.dirname(inDB)
tiff_pkg = os.path.join(db_dir, "RSS_" + state[:2])
os.mkdir(tiff_pkg)
dirs = ['spatial', 'tabular']
for d in dirs:
    os.mkdir(os.path.join(tiff_pkg, d))

arcpy.AddMessage('\n\tExporting ' + os.path.join(inDB, inRaster + ' to .tif format\n'))
arcpy.management.CopyRaster(inDB + os.sep + inRaster, os.path.join(tiff_pkg, "spatial", inRaster + '.tif' ), None, None, None, None, None, "32_BIT_UNSIGNED")


req = ['ccancov.txt', 'ccrpyd.txt', 'cdfeat.txt', 'cecoclas.txt', 'ceplants.txt', 'cerosnac.txt', 'cfprod.txt', 'cfprodo.txt', 'cgeomord.txt', 'chaashto.txt', 'chconsis.txt', 'chdsuffx.txt', 'chfrags.txt', 'chorizon.txt', 'chpores.txt', 'chstr.txt', 'chstrgrp.txt', 'chtexgrp.txt', 'chtexmod.txt', 'chtext.txt', 'chtextur.txt', 'chunifie.txt', 'chydcrit.txt', 'cinterp.txt', 'cmonth.txt', 'comp.txt', 'cpmat.txt', 'cpmatgrp.txt', 'cpwndbrk.txt', 'crstrcts.txt', 'csfrags.txt', 'csmoist.txt', 'csmorgc.txt', 'csmorhpp.txt', 'csmormr.txt', 'csmorss.txt', 'cstemp.txt', 'ctext.txt', 'ctreestm.txt', 'ctxfmmin.txt', 'ctxfmoth.txt', 'ctxmoicl.txt', 'distimd.txt', 'distlmd.txt', 'distmd.txt', 'lareao.txt', 'legend.txt', 'ltext.txt', 'mapunit.txt', 'msdomdet.txt', 'msdommas.txt', 'msidxdet.txt', 'msidxmas.txt', 'msrsdet.txt', 'msrsmas.txt', 'mstab.txt', 'mstabcol.txt', 'muaggatt.txt', 'muareao.txt', 'mucrpyd.txt', 'mutext.txt', 'README.txt', 'sacatlog.txt', 'sainterp.txt', 'sdvalgorithm.txt', 'sdvattribute.txt', 'sdvfolder.txt', 'sdvfolderattribute.txt', 'version.txt']
tabDir = os.path.join(inTemplate, 'tabular')
tabs = [os.path.join(tabDir, t) for t in os.listdir(tabDir) if t in req]

for t in tabs:
    arcpy.AddMessage('\tCopying ' + os.path.basename(t[:-4]) + ' table' )
    shutil.copy(t, os.path.join(tiff_pkg, dirs[1]))
    