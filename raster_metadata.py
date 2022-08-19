# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 09:57:10 2022

@author: Charles.Ferguson
"""
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
        PrintMsg("\tUpdating raster metadata...")
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
        #PrintMsg(" \nParsing gSSURGO template metadata file: " + mdExport, 1)

        #PrintMsg(" \nUsing SurveyInfo: " + str(surveyInfo), 1)

        # Cleanup output XML files from previous runs
        if os.path.isfile(mdImport):
            os.remove(mdImport)

        # Get replacement value for the search words
        #
        stDict = StateNames()
        # st = os.path.basename(gdb)[8:-4]
        st = os.path.basename(outputWS)[4:-4]

        if st in stDict:
            # Get state name from the geodatabase
            mdState = stDict[st]

        else:
            # Leave state name blank. In the future it would be nice to include a tile name when appropriate
            mdState = ""

        #PrintMsg(" \nUsing this string as a substitute for xxSTATExx: '" + mdState + "'", 1)

        # Set date strings for metadata, based upon today's date
        #
        d = datetime.date.today()
        today = str(d.isoformat().replace("-",""))

        #PrintMsg(" \nToday replacement string: " + today, 1)

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
            nth = smonth.zfill(2)
        fy = syr + smonth

        #PrintMsg(" \nFY replacement string: " + str(fy), 1)

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
                PrintMsg("\t\t" + str(child.tag), 0)

                if child.tag == "title":
                    if child.text.find('xxSTATExx') >= 0:
                        newTitle = "MapunitRaster " + str(iRaster) + "m - " + mdState
                        # newTitle = "Map Unit Raster " + str(iRaster) + "m - " + mdState
                        #PrintMsg("\t\tUpdating title to: " + newTitle, 1)
                        #child.text = child.text.replace('xxSTATExx', mdState)
                        child.text = newTitle

                    elif mdState != "":
                        child.text = child.text + " " + str(iRaster) + "m - " + mdState

                    else:
                        child.text = "MapunitRaster " + str(iRaster) + "m"

                elif child.tag == "edition":
                    if child.text == 'xxFYxx':
                        #PrintMsg("\t\tReplacing xxFYxx", 1)
                        child.text = fy

                elif child.tag == "serinfo":
                    for subchild in child.iter('issue'):
                        if subchild.text == "xxFYxx":
                            #PrintMsg("\t\tReplacing xxFYxx", 1)
                            subchild.text = fy

        # Update place keywords
        ePlace = root.find('idinfo/keywords/place')

        if not ePlace is None:
            PrintMsg("\t\tplace keywords", 0)

            for child in ePlace.iter('placekey'):
                if child.text == "xxSTATExx":
                    #PrintMsg("\t\tReplacing xxSTATExx", 1)
                    child.text = mdState

                # elif child.text == "xxSURVEYSxx":
                #     #PrintMsg("\t\tReplacing xxSURVEYSxx", 1)
                #     child.text = mdState

        # Update credits
        eIdInfo = root.find('idinfo')
        if not eIdInfo is None:
            PrintMsg("\t\tcredits", 0)

            for child in eIdInfo.iter('datacred'):
                sCreds = child.text

                if sCreds.find("xxSTATExx") >= 0:
                    #PrintMsg("\t\tcredits " + mdState, 0)
                    child.text = child.text.replace("xxSTATExx", mdState)
                    #PrintMsg("\t\tReplacing xxSTATExx", 1)

                if sCreds.find("xxFYxx") >= 0:
                    #PrintMsg("\t\tcredits " + fy, 0)
                    child.text = child.text.replace("xxFYxx", fy)
                    #PrintMsg("\t\tReplacing xxFYxx", 1)

                if sCreds.find("xxTODAYxx") >= 0:
                    #PrintMsg("\t\tcredits " + today, 0)
                    child.text = child.text.replace("xxTODAYxx", today)
                    #PrintMsg("\t\tReplacing xxTODAYxx", 1)

        idPurpose = root.find('idinfo/descript/purpose')

        if not idPurpose is None:
            PrintMsg("\t\tpurpose", 0)

            ip = idPurpose.text

            if ip.find("xxFYxx") >= 0:
                idPurpose.text = ip.replace("xxFYxx", fy)
                #PrintMsg("\t\tReplacing xxFYxx", 1)

        # Update process steps
        eProcSteps = root.findall('dataqual/lineage/procstep')

        if not eProcSteps is None:
            PrintMsg("\t\tprocess steps", 0)
            for child in eProcSteps:
                for subchild in child.iter('procdesc'):
                    #PrintMsg("\t\t" + subchild.tag + "\t" + subchild.text, 0)
                    procText = subchild.text

                    if procText.find('xxTODAYxx') >= 0:
                        subchild.text = subchild.text.replace("xxTODAYxx", d.strftime('%Y-%m-%d'))

                    if procText.find("xxSTATExx") >= 0:
                        subchild.text = subchild.text.replace("xxSTATExx", mdState)
                        #PrintMsg("\t\tReplacing xxSTATExx", 1)

                    if procText.find("xxFYxx") >= 0:
                        subchild.text = subchild.text.replace("xxFYxx", fy)
                        #PrintMsg("\t\tReplacing xxFYxx", 1)

        #PrintMsg(" \nSaving template metadata to " + mdImport, 1)

        #  create new xml file which will be imported, thereby updating the table's metadata
        tree.write(mdImport, encoding="utf-8", xml_declaration=None, default_namespace=None, method="xml")

        # import updated metadata to the geodatabase table
        # Using three different methods with the same XML file works for ArcGIS 10.1
        #
        #PrintMsg(" \nImporting metadata " + mdImport + " to " + target, 1)
        arcpy.MetadataImporter_conversion(mdImport, target)  # This works. Raster now has metadata with 'XX keywords'. Is this step neccessary to update the source information?

        if not arcpy.Exists(target):
            raise MyError, "Missing xml file to import as metadata: " + target

        PrintMsg(" \nUpdating metadata for " + target + " using file: " + mdImport, 1)
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

        return True

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return False

    except:
        errorMsg()
        False
        
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
        PrintMsg("\tFailed to create list of state abbreviations (CreateStateList)", 2)
        return stDict