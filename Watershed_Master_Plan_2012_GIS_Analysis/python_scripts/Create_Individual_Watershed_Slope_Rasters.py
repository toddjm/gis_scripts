import arcpy
import os

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# Get watershed names from listing polygons in the
# Watershed_Polygons feature dataset. Iterate over watersheds.
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')
in_raster = 'Slope'
for wn in watershed_names:
    in_mask = '/Watershed_Polygons' + '/' + wn
    print 'Processing {0}'.format(wn)
    out_extract_by_mask = arcpy.sa.ExtractByMask(in_raster, in_mask)
    out_file = 'Slope_' + wn
    out_extract_by_mask.save(out_file)



