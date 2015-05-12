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

watershed_names = ['Barton_Creek',
                   'Lake_Creek',
                   'Lake_Travis',
                   'South_Brushy_Creek']

in_raster = 'Tree_Canopy_Raster'
for wn in watershed_names:
    in_mask = '/Watershed_Polygons' + '/' + wn
    print 'Processing {0}'.format(wn)
    out_extract_by_mask = arcpy.sa.ExtractByMask(in_raster, in_mask)
    out_file = 'Tree_Canopy_' + wn
    out_extract_by_mask.save(out_file)



