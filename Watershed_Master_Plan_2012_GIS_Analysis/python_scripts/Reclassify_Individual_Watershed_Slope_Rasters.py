"""
Read raster data and reclassify values.
"""
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

# Get raster names (note wildcard).
slope_raster_names = arcpy.ListRasters(wild_card='Slope_*')
# Set remap ranges here: 0-15% -> 0, 15-25% -> 1, 25-35% ->2, and
# 35-100 -> 3.
remap = arcpy.sa.RemapRange([[0, 15, 0],
                            [15, 25, 1],
                            [25, 35, 2],
                            [35, 100, 3]])
reclass_field = 'VALUE'
for raster in slope_raster_names:
    print 'Processing {0}'.format(raster)
    out_reclassify = arcpy.sa.Reclassify(raster,
                                         reclass_field,
                                         remap,
                                         'NODATA')
    out_file = raster + '_Reclass'
    out_reclassify.save(out_file)