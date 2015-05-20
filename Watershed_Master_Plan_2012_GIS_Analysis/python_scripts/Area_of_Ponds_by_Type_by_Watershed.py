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
ponds_table = os.path.join(task_dir, 'Stormwater_Control_Watersheds_Union')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset='Watershed_Polygons')

# Populate a dict keyed on watershed with value being another dict with keys
# commercial, residential, water_quality, and detention and values being
# area of each per watershed.
pond_program_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'PROGRAM_NAME', 'Shape_Area']
programs = ['Residential', 'Commercial']
cursor = arcpy.da.SearchCursor(in_table=ponds_table,
                               field_names=field_names)
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    subtypes = {}
    for program in programs:
        area = 0.0
        for row in cursor:
            if row[0] == ws_full_name and row[1] == program:
                area += row[2]
            subtypes[program] = sq_ft_to_acres(area)
        cursor.reset()
    pond_program_by_ws[watershed] = subtypes

# Populate a dict keyed on watershed, values another dict with keys for either
# water quality or detention pond and values area of each.
pond_type_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'IS_WQP', 'IS_DET', 'Shape_Area']
cursor = arcpy.da.SearchCursor(in_table=ponds_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    subtypes = {}
    wq_area = 0.0
    for row in cursor:
        if row[0] == ws_full_name and row[1] == 1:
            wq_area += row[3]
    subtypes['Water Quality'] = sq_ft_to_acres(wq_area)
    cursor.reset()
    det_area = 0.0
    for row in cursor:
        if row[0] == ws_full_name and row[2] == 1:
            det_area += row[3]
    subtypes['Detention'] = sq_ft_to_acres(det_area)
    pond_type_by_ws[watershed] = subtypes
    cursor.reset()

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Area_of_Ponds_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Residential (acres)',
              'Commercial (acres)',
              'Water Quality (acres)',
              'Detention (acres)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        res_area = pond_program_by_ws[watershed]['Residential']
        com_area = pond_program_by_ws[watershed]['Commercial']
        wq_area = pond_type_by_ws[watershed]['Water Quality']
        det_area = pond_type_by_ws[watershed]['Detention']
        writer.writerow([ws_full_name,
                         res_area,
                         com_area,
                         wq_area,
                         det_area])