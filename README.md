# Build-Raster-Soil-Survey-Database
Populate a gdb with SSURGO export to support raster soil survyes

This toolbox will only work with ArcGIS Desktop.

This toolbox will take the contents of a SSURGO export from NASIS and create a file geodatabase with the relationship classes built in order to generate SSURGO properties and interpretations using the Soil Data Development Toolbox.

In this toolbox is a folder named SSURGO_template_data.  In this folder there is:

1. a soil survey area (soilsa_a_ra000.shp) shapefile
2. a subfolder soil_ra000

DO NOT rename the subfolder as it follows the conventional SSURGO naming convention that the ArcGIS Desktop Build RSS toolbox requires.  You will see this folder has the contents of a typical SSURGO download, including a spatial and tabular folder as well as metadata.  The spatial folder has the typical files in a SSURGO download, however, all are empty with the exception of the soilsa_a_ra000.shp. These 2 versions of the soilsa_a_ra000.shp file are used to trick the tool into creating a valid gSSURGO database.

In order to execute the tool
1. add the contents (tabular files) from your SSURGO export into the SSURGO_template_data > soil_ra000 > tabular folder
2. add the soilsa_a_ra000.shp from the SSURGO_template_data folder to a map document.
3. Add the toolbox in ArcToolbox.
4. Open the tool
5. In the SSURGO downloads, point to the SSURGO_template_data folder, which has the soil_ra000 folder containg empty shapefiles (except for the survey area because we need an areasymbol) in the spatial folder, and the tabular folder (with the files from your SSURGO export in step 1).
6. In the Survey Boundary Layer parameter, point to the soilsa_a_ra000 you added in step 2
7. The input SSURGO Datasets parameter should auto populate with the soil_ra000 folder, make sure it is selected
8. For the Output Geodatabse parameter, navigate to where you want to write the gdb to disk, give it a name and be sure to add .gdb as an extension.  Note standards dictate the database name must be a state abbreviation (CA.gdb), but it can be renamed whenever you'd like.
9. Ignore the remaining parameters.
10. When the tool finishes, right-click on the newly created geodatabse and import your raster.
11. Test the database by running a property or interpretation from the Soil Data Development Toolbox. 
12. Note: delete any layer files/tables that are created in step 11 and compact the database before uploading to the NRCS Datagateway      
