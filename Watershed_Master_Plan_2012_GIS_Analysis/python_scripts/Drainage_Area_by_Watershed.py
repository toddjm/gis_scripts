import arcpy
import csv
import os

# Convert sq. ft. to acres.
def sq_ft_to_acres(x):
    return x / 43560.0

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Infrastructure'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Tables to be read in for this script.
da_table = os.path.join(task_dir, 'Drainage_Areas_Watersheds_Union')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Populate a dict keyed on watershed with value being another dict with keys
# commercial, residential, water_quality, and detention and values being
# count of each per watershed.
da_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'Shape_Area']
cursor = arcpy.da.SearchCursor(in_table=da_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    area = 0.0
    for row in cursor:
        if row[0] == ws_full_name:
            area += row[1]
    cursor.reset()
    da_by_ws[watershed] = sq_ft_to_acres(area)

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Drainage_Area_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Drainage Area (acres)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        da_area = da_by_ws[watershed]
        writer.writerow([ws_full_name,
                         da_area])