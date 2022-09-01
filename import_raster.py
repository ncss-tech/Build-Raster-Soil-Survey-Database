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
        arcpy.AddMessage(theMsg)

    except:
        arcpy.AddMessage("Unhandled error in errorMsg method")

def UpdateMetadata(gdb, target, surveyInfo, iRaster):
    #
    # Used for non-ISO metadata
    #
    # Process:
    #     1. Read gSSURGO_MapunitRaster.xml
    #     2. Replace 'XX" keywords with updated information
    #     3. Write new file xxImport.xml
    #     4. Import xxImport.xml to raster
    #
    # Problem with ImportMetadata_conversion command. Started failing with an error.
    # Possible Windows 10 or ArcGIS 10.5 problem?? Later had to switch back because the
    # alternative ImportMetadata_conversion started for failing with the FY2018 rasters without any error.
    #
    # Search for keywords:  xxSTATExx, xxSURVEYSxx, xxTODAYxx, xxFYxx
    #
    try:
        arcpy.AddMessage("\tUpdating raster metadata...")
        arcpy.SetProgressor("default", "Updating raster metadata")

        # Set metadata translator file
        dInstall = arcpy.GetInstallInfo()
        installPath = dInstall["InstallDir"]
        prod = r"Metadata/Translator/ARCGIS2FGDC.xml"
        mdTranslator = os.path.join(installPath, prod)  # This file is not being used

        # Define input and output XML files
        mdImport = os.path.join(env.scratchFolder, "xxImport.xml")  # the metadata xml that will provide the updated info
        xmlPath = os.path.dirname(sys.argv[0])
        mdExport = os.path.join(xmlPath, "RSS_ClassRaster.xml") # original template metadata in script directory
        arcpy.AddMessage(" \nParsing gSSURGO template metadata file: " + mdExport)

        #arcpy.AddMessage(" \nUsing SurveyInfo: " + str(surveyInfo), 1)

        # Cleanup output XML files from previous runs
        if os.path.isfile(mdImport):
            os.remove(mdImport)

        # Get replacement value for the search words
        #
        stDict = StateNames()
        # st = os.path.basename(gdb)[8:-4]
        st = os.path.basename(outDB)[4:-4]

        if st in stDict:
            # Get state name from the geodatabase
            mdState = stDict[st]

        else:
            # Leave state name blank. In the future it would be nice to include a tile name when appropriate
            mdState = ""

        #arcpy.AddMessage(" \nUsing this string as a substitute for xxSTATExx: '" + mdState + "'", 1)

        # Set date strings for metadata, based upon today's date
        #
        d = datetime.date.today()
        today = str(d.isoformat().replace("-",""))

        #arcpy.AddMessage(" \nToday replacement string: " + today, 1)

        # Set fiscal year according to the current month. If run during January thru September,
        # set it to the current calendar year. Otherwise set it to the next calendar year.
        #
##        if d.month > 9:
##            fy = "FY" + str(d.year + 1)
##
##        else:
##            fy = "FY" + str(d.year)

        # As of July 2020, switch gSSURGO version format to YYYYMM
        # fy = d.strftime('%Y%m')
        now = datetime.datetime.now()
        syr = str(now.year)
        smonth = str(now.month)
        if len(smonth) ==1:
            smonth = smonth.zfill(2)
        fy = syr + smonth

        #arcpy.AddMessage(" \nFY replacement string: " + str(fy), 1)

        # Process gSSURGO_MapunitRaster.xml from script directory
        tree = ET.parse(mdExport)
        root = tree.getroot()

        # new citeInfo has title.text, edition.text, serinfo/issue.text
        citeInfo = root.findall('idinfo/citation/citeinfo/')

        if not citeInfo is None:
            # Process citation elements
            # title, edition, issue
            #
            for child in citeInfo:
                arcpy.AddMessage("\t\t" + str(child.tag))

                if child.tag == "title":
                    if child.text.find('xxSTATExx') >= 0:
                        newTitle = "MapunitRaster " + str(iRaster) + "m - " + mdState
                        # newTitle = "Map Unit Raster " + str(iRaster) + "m - " + mdState
                        #arcpy.AddMessage("\t\tUpdating title to: " + newTitle, 1)
                        #child.text = child.text.replace('xxSTATExx', mdState)
                        child.text = newTitle

                    elif mdState != "":
                        child.text = child.text + " " + str(iRaster) + "m - " + mdState

                    else:
                        child.text = "MapunitRaster " + str(iRaster) + "m"

                elif child.tag == "edition":
                    if child.text == 'xxFYxx':
                        #arcpy.AddMessage("\t\tReplacing xxFYxx", 1)
                        child.text = fy

                elif child.tag == "serinfo":
                    for subchild in child.iter('issue'):
                        if subchild.text == "xxFYxx":
                            #arcpy.AddMessage("\t\tReplacing xxFYxx", 1)
                            subchild.text = fy

        # Update place keywords
        ePlace = root.find('idinfo/keywords/place')

        if not ePlace is None:
            arcpy.AddMessage("\t\tplace keywords")

            for child in ePlace.iter('placekey'):
                if child.text == "xxSTATExx":
                    #arcpy.AddMessage("\t\tReplacing xxSTATExx", 1)
                    child.text = mdState

                elif child.text == "xxSURVEYSxx":
                    #arcpy.AddMessage("\t\tReplacing xxSURVEYSxx", 1)
                    child.text = mdState

        # Update credits
        eIdInfo = root.find('idinfo')
        if not eIdInfo is None:
            arcpy.AddMessage("\t\tcredits")

            for child in eIdInfo.iter('datacred'):
                sCreds = child.text

                if sCreds.find("xxSTATExx") >= 0:
                    #arcpy.AddMessage("\t\tcredits " + mdState, 0)
                    child.text = child.text.replace("xxSTATExx", mdState)
                    #arcpy.AddMessage("\t\tReplacing xxSTATExx", 1)

                if sCreds.find("xxFYxx") >= 0:
                    #arcpy.AddMessage("\t\tcredits " + fy, 0)
                    child.text = child.text.replace("xxFYxx", fy)
                    #arcpy.AddMessage("\t\tReplacing xxFYxx", 1)

                if sCreds.find("xxTODAYxx") >= 0:
                    #arcpy.AddMessage("\t\tcredits " + today, 0)
                    child.text = child.text.replace("xxTODAYxx", today)
                    #arcpy.AddMessage("\t\tReplacing xxTODAYxx", 1)

        idPurpose = root.find('idinfo/descript/purpose')

        if not idPurpose is None:
            arcpy.AddMessage("\t\tpurpose")

            ip = idPurpose.text

            if ip.find("xxFYxx") >= 0:
                idPurpose.text = ip.replace("xxFYxx", fy)
                #arcpy.AddMessage("\t\tReplacing xxFYxx", 1)

        # Update process steps
        eProcSteps = root.findall('dataqual/lineage/procstep')

        if not eProcSteps is None:
            arcpy.AddMessage("\t\tprocess steps")
            for child in eProcSteps:
                for subchild in child.iter('procdesc'):
                    #arcpy.AddMessage("\t\t" + subchild.tag + "\t" + subchild.text, 0)
                    procText = subchild.text

                    if procText.find('xxTODAYxx') >= 0:
                        subchild.text = subchild.text.replace("xxTODAYxx", d.strftime('%Y-%m-%d'))

                    if procText.find("xxSTATExx") >= 0:
                        subchild.text = subchild.text.replace("xxSTATExx", mdState)
                        #arcpy.AddMessage("\t\tReplacing xxSTATExx", 1)

                    if procText.find("xxFYxx") >= 0:
                        subchild.text = subchild.text.replace("xxFYxx", fy)
                        #arcpy.AddMessage("\t\tReplacing xxFYxx", 1)

        #arcpy.AddMessage(" \nSaving template metadata to " + mdImport, 1)

        #  create new xml file which will be imported, thereby updating the table's metadata
        tree.write(mdImport, encoding="utf-8", xml_declaration=None, default_namespace=None, method="xml")

        # import updated metadata to the geodatabase table
        # Using three different methods with the same XML file works for ArcGIS 10.1
        #
        #arcpy.AddMessage(" \nImporting metadata " + mdImport + " to " + target, 1)
        arcpy.MetadataImporter_conversion(mdImport, target)  # This works. Raster now has metadata with 'XX keywords'. Is this step neccessary to update the source information?

        if not arcpy.Exists(target):
            raise errorMsg + "Missing xml file to import as metadata: " + target

        arcpy.AddMessage(" \nUpdating metadata for " + target + " using file: " + mdImport)
        arcpy.ImportMetadata_conversion(mdImport, "FROM_FGDC", target, "DISABLED")  # Tool Validate problem here
        #arcpy.MetadataImporter_conversion(target, mdImport) # Try this alternate tool with Windows 10.

        # delete the temporary xml metadata file
        if os.path.isfile(mdImport):
            os.remove(mdImport)
            #pass

        # delete metadata tool logs
        logFolder = os.path.dirname(env.scratchFolder)
        logFile = os.path.basename(mdImport).split(".")[0] + "*"

        currentWS = env.workspace
        env.workspace = logFolder
        logList = arcpy.ListFiles(logFile)

        for lg in logList:
            arcpy.Delete_management(lg)

        env.workspace = currentWS

        # return True

    # except errorMsg(), e:
    #     # Example: raise MyError, "This is an error message"
    #     arcpy.AddMessage(str(e), 2)
    #     return False

    except Exception as e:
        arcpy.AddMessage(e)

        
def StateNames():
    # Create dictionary object containing list of state abbreviations and their names that
    # will be used to name the file geodatabase.
    # For some areas such as Puerto Rico, U.S. Virgin Islands, Pacific Islands Area the
    # abbrevation is

    # NEED TO UPDATE THIS FUNCTION TO USE THE LAOVERLAP TABLE AREANAME. AREASYMBOL IS STATE ABBREV
    
    valid = ['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'PRUSVI', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
    
    try:
        stDict = dict()
        stDict["AL"] = "Alabama"
        stDict["AK"] = "Alaska"
        stDict["AS"] = "American Samoa"
        stDict["AZ"] = "Arizona"
        stDict["AR"] = "Arkansas"
        stDict["CA"] = "California"
        stDict["CO"] = "Colorado"
        stDict["CT"] = "Connecticut"
        stDict["DC"] = "District of Columbia"
        stDict["DE"] = "Delaware"
        stDict["FL"] = "Florida"
        stDict["GA"] = "Georgia"
        stDict["HI"] = "Hawaii"
        stDict["ID"] = "Idaho"
        stDict["IL"] = "Illinois"
        stDict["IN"] = "Indiana"
        stDict["IA"] = "Iowa"
        stDict["KS"] = "Kansas"
        stDict["KY"] = "Kentucky"
        stDict["LA"] = "Louisiana"
        stDict["ME"] = "Maine"
        stDict["MD"] = "Maryland"
        stDict["MA"] = "Massachusetts"
        stDict["MI"] = "Michigan"
        stDict["MN"] = "Minnesota"
        stDict["MS"] = "Mississippi"
        stDict["MO"] = "Missouri"
        stDict["MT"] = "Montana"
        stDict["NE"] = "Nebraska"
        stDict["NV"] = "Nevada"
        stDict["NH"] = "New Hampshire"
        stDict["NJ"] = "New Jersey"
        stDict["NM"] = "New Mexico"
        stDict["NY"] = "New York"
        stDict["NC"] = "North Carolina"
        stDict["ND"] = "North Dakota"
        stDict["OH"] = "Ohio"
        stDict["OK"] = "Oklahoma"
        stDict["OR"] = "Oregon"
        stDict["PA"] = "Pennsylvania"
        stDict["PRUSVI"] = "Puerto Rico and U.S. Virgin Islands"
        stDict["RI"] = "Rhode Island"
        stDict["SC"] = "South Carolina"
        stDict["SD"] ="South Dakota"
        stDict["TN"] = "Tennessee"
        stDict["TX"] = "Texas"
        stDict["UT"] = "Utah"
        stDict["VT"] = "Vermont"
        stDict["VA"] = "Virginia"
        stDict["WA"] = "Washington"
        stDict["WV"] = "West Virginia"
        stDict["WI"] = "Wisconsin"
        stDict["WY"] = "Wyoming"
        return stDict

    except:
        arcpy.AddError("\tFailed to create list of state abbreviations (CreateStateList)", 2)
        return stDict

import arcpy, sys, os, traceback, datetime, shutil
from arcpy import env
import xml.etree.cElementTree as ET


try:

    model_raster = arcpy.GetParameterAsText(0)
    outDB = arcpy.GetParameterAsText(1)
    state = arcpy.GetParameterAsText(2)

    ##set the snap raster environment
    loc = sys.argv[0]
    snap_dir = os.path.dirname(loc)
    
    table_dir = os.path.join(snap_dir, "SSURGO_template_data","soil_ra000","tabular")
    snap = os.path.join(snap_dir, "RSS_gSSURGO_snap.tif")
    # arcpy.AddMessage(snap)
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

    rasters = [outDB + os.sep + "temp_raster_10m_" + state, outDB + os.sep + "MapunitRaster_10m_" + state]
    for r in rasters:
        if arcpy.Exists(r):
            arcpy.management.Delete(r)

    sr = desc.spatialReference
    # arcpy.AddMessage(sr.GCS.name)
    if sr.GCS.name == "GCS_WGS_1984":
        tm = "WGS_1984_(ITRF00)_To_NAD_1983"
        arcpy.management.ProjectRaster(model_raster, outDB + os.sep + "temp_raster_10m_" + state, osr, "NEAREST", 10, tm, None, None, None )

    elif sr.GCS.name == "GCS_North_American_1983":
        # no trannsformation needed
        arcpy.management.ProjectRaster(model_raster, outDB + os.sep + "temp_raster_10m_" + state, osr, "NEAREST", 10, None, None, None, None )

            
    arcpy.management.CopyRaster(outDB + os.sep + "temp_raster_10m_" + state, outDB + os.sep + "MapunitRaster_10m_" + state, None, None, None, None, None, "32_BIT_UNSIGNED")

    arcpy.management.Delete(outDB + os.sep + "temp_raster_10m_" + state)
    
    outputRaster = outDB + os.sep + "MapunitRaster_10m_" + state
    surveyInfo = ''
    iRaster = 10
    UpdateMetadata(outDB, outputRaster, surveyInfo, iRaster)
    
    # i = state.s.rfind("_")
    # stabb = out[i-2:i]
    # db_dir= os.path.dirname(outDB)
    # tiff_pkg = os.path.join(db_dir, "RSS_" + state[:2])
    # os.mkdir(tiff_pkg)
    # dirs = ['spatial', 'tabular']
    # for d in dirs:
    #     os.mkdir(os.path.join(tiff_pkg, d))
    
    # arcpy.management.CopyRaster(outDB + os.sep + "MapunitRaster_10m_" + state, os.path.join(tiff_pkg, "spatial", "MapunitRaster_10m_" + state + '.tif' ), None, None, None, None, None, "32_BIT_UNSIGNED")
    
    # os.chdir(table_dir)
    # for table in os.listdir(table_dir):
    #     if not table.startswith("."):
    #         dest = os.path.join(tiff_pkg, 'tabular',  table)
    #         shutil.copy(table, dest)
    

except Exception as e:
    arcpy.AddError(e)
    


