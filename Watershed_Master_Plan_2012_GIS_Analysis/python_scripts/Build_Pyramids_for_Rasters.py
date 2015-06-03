"""
Build pyramids for large set of rasters.

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

# Get raster names.
slope_raster_names = arcpy.ListRasters(wild_card='Slope_*_Reclass')

# Variables for building pyramids.
comp_qual = '75'
resample = 'NEAREST'
skip = 'SKIP_EXISTING'

# Iterate over each raster.
for raster in slope_raster_names:
    print 'Processing {0}'.format(raster)
    arcpy.BuildPyramids_management(in_raster_dataset=raster,
                                   resample_technique=resample,
                                   compression_quality=comp_qual,
                                   skip_existing=skip)
    print 'Pyramids built for {0}'.format(raster)