# Build-Raster-Soil-Survey-Database
Populate a gdb with SSURGO export to support raster soil survyes

This toolbox will only work with ArcGIS Desktop.

This toolbox will take the contents of a SSURGO export from NASIS and create a file geodatabase with the relationship classes built in order to generate SSURGO properties and interpretations using the Soil Data Development Toolbox.

In this toolbox is a folder named SSURGO_template_data.  In this folder there is:

1. a soil survey area (soilsa_a_ra000.shp) shapefile
2. a subfolder soil_ra000

DO NOT rename the subfolder as it follows the conventional SSURGO naming convention that the ArcGIS Desktop Build RSS toolbox requires.  You will see this folder has the contents of a typical SSURGO download, including a spatial and tabular folder as well as metadata.  The spatial folder has the typical files in a SSURGO download, however, all are empty with the exception of the soilsa_a_ra000.shp. These 2 versions of the soilsa_a_ra000.shp file are used to trick the tool into creating a valid gSSURGO database.

In order to execute the tool add the soilsa_a_ra000.shp from the SSURGO_template_data folder to a map document.  Add the toolbox in ArcToolbox.  
