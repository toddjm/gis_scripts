import arcpy
import collections
import csv
import os

# Function to convert sq. ft. to acres.
def sq_ft_to_acres(x):
    return x / 43560.00

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Map_of_Watersheds'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Tables to be read in for this script.
land_use_table = os.path.join(task_dir, 'Land_Use_2012_Watersheds_Union_Join')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Populate a list from CURRENT_GENERAL_LAND_USE.
field_names = ['LU_Name']
land_use = []
# Set the cursor to search the feature class.
cursor = arcpy.da.SearchCursor(in_table=land_use_table,
                               field_names=field_names)
# Iterate over rows, append project stages list with values.
for row in cursor:
    land_use.append(row[0])
# Collapse list to contain unique values.
land_use = collections.OrderedDict.fromkeys(land_use).keys()

#print land_use
# Create dict to be keyed on watershed name, values containing another dict
# keyed by project stages with values equal to the count for each watershed.
land_use_by_ws = {}
# Search fields containing watershed name, cu, and Shape_Area.
field_names = ['WATERSHED_FULL_NAME', 'LU_Name', 'Shape_Area']
cursor = arcpy.da.SearchCursor(in_table=land_use_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    land_use_area = {}
    for use in land_use:
        area = 0.0
        for row in cursor:
            # Only sum the areas for a given watershed and LU.
            if row[0] == ws_full_name and row[1] == use:
                area += row[2]
            land_use_area[use] = sq_ft_to_acres(area)
        cursor.reset()
    land_use_by_ws[watershed] = land_use_area

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'LU_2012_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed']
    land_use_list = sorted(land_use)
    header_list = [i + " (acres)" for i in land_use_list if i is not None]
    header += header_list
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        out_list = [land_use_by_ws[watershed][i] for i in land_use_list]
        out_list = [ws_full_name] + out_list
        writer.writerow(out_list)