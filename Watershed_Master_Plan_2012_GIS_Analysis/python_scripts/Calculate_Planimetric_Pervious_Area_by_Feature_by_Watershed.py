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
task_dir = 'Planimetrics_Features_Union_Watersheds'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# List of pervious area features.
pc_features = ['Courtyard',
               'Edge_of_Trail',
               'Golf_Course',
               'Gravel_Sandpit',
               'Open_Space',
               'Open_Storage',
               'Quarry',
               'Remaining_Pervious_LT_100',
               'Remaining_Pervious_GT_100_LT_150',
               'Remaining_Pervious_GT_150_LT_500',
               'Remaining_Pervious_GT_500_LT_5000',
               'Remaining_Pervious_GT_5000',
               'Unpaved_Athletic_Field']

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Sum area for each PC feature on a per-watershed basis.
pc_area_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'SHAPE_Area']
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    pc_area = {}
    for feature in pc_features:
        in_table = feature + '_Watersheds_Union'
        cursor = arcpy.da.SearchCursor(in_table=in_table,
                                       field_names=field_names)
        area = 0.0
        for row in cursor:
            if row[0] == ws_full_name:
                area += row[1]
        cursor.reset()
        pc_area[feature] = sq_ft_to_acres(area)
    pc_area_by_ws[watershed] = pc_area

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'PC_Area_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed']
    pc_features_list = sorted(pc_features)
    header_list = [i + " (acres)" for i in pc_features_list if i is not None]
    header += header_list
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        out_list = [pc_area_by_ws[watershed][i] for i in pc_features_list]
        out_list = [ws_full_name] + out_list
        writer.writerow(out_list)