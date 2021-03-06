"""
Write a csv file with miles of drainage pipe per
watershed.

"""
import arcpy
import collections
import csv
import os

def ft_to_miles(x):
    """
    Return miles given feet.
    """
    return x / 5280.0

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Infrastructure'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# The drainage pipe feature class is processed by the user with the
# Make Feature Layer tool with the Use Ratio Policy set for the shape
# length and shape area fields. The resulting layer is intersected with the
# watersheds feature class. Finally, the output feature class is edited
# and entries with FID identifiers that are non-positive (i.e. = -1) have
# been removed.
pipe_table = os.path.join(task_dir, 'Drainage_Pipe_Watersheds_Intersect')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Compute number of linear feet of drainage pipe (active) per watershed.
# Note: Dataset has been intersected with Use Ratio Policy turned on
# for the 'Shape_Length' field.
pipe_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'STATUS', 'Shape_Length']
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    cursor = arcpy.da.SearchCursor(in_table=pipe_table,
                                   field_names=field_names)
    len_total = 0.0
    for row in cursor:
        if row[0] == ws_full_name and row[1] == 'ACTIVE':
            len_total += row[2]
    pipe_by_ws[watershed] = ft_to_miles(len_total)
    cursor.reset()

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Miles_of_Storm_Drains_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Storm Drains (miles)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        pipe_length = pipe_by_ws[watershed]
        writer.writerow([ws_full_name,
                         pipe_length])