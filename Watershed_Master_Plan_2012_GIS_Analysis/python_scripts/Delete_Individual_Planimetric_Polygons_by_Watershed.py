import arcpy
import csv
import os

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Natural_Features'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Get a list of feature classes with wildcard.
polygon_names = []
polygon_names = arcpy.ListFeatureClasses(feature_dataset=task_dir,
                                         wild_card='*_Planimetrics_Small')

# Delete polygons.
for polygon in polygon_names:
    arcpy.Delete_management(polygon)
