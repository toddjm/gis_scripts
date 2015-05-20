import arcpy
import csv
import os

# Function to convert sq. ft. to acres.
def sq_ft_to_acres(x):
    return x / 43560.0

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Natural_Features'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Tables to be read in for this script.
plan_table = 'Planimetrics_2013_CopyFeatures'

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Extract planimetrics per watershed.
plan_layer = 'Plan_Layer'
arcpy.Delete_management(plan_layer)
arcpy.MakeFeatureLayer_management(plan_table, plan_layer)
for watershed in watershed_names:
    ws_polygon = os.path.join('Watershed_Polygons', watershed)
    out_name = os.path.join(task_dir, watershed + '_Planimetrics')
    arcpy.Clip_analysis(in_features=plan_layer,
                        clip_features=ws_polygon,
                        out_feature_class=out_name)
