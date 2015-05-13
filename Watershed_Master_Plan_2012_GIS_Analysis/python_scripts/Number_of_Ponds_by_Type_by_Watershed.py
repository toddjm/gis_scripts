import arcpy
import csv
import os

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
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')
print watershed_names

# Populate a dict keyed on watershed with value being another dict with keys
# commercial, residential, water_quality, and detention and values being
# count of each per watershed.
pond_program_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'PROGRAM_NAME']
programs = ['Residential', 'Commercial']
cursor = arcpy.da.SearchCursor(in_table=ponds_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    subtypes = {}
    for program in programs:
        cnt = 0
        for row in cursor:
            if row[0] == ws_full_name and row[1] == program:
                cnt += 1
            subtypes[program] = cnt
        cursor.reset()
    pond_program_by_ws[watershed] = subtypes

print pond_program_by_ws

pond_type_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'IS_WQP', 'IS_DET']
cursor = arcpy.da.SearchCursor(in_table=ponds_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    subtypes = {}
    wq_cnt = 0
    for row in cursor:
        if row[0] == ws_full_name and row[1] == 1:
            wq_cnt += 1
        print wq_cnt
        subtypes['Water Quality'] = wq_cnt
        cursor.reset()
    pond_type_by_ws[watershed] = subtypes

print pond_type_by_ws
# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Number_of_Ponds_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Residential (count)',
              'Commercial (count)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        res_cnt = pond_program_by_ws[watershed]['Residential']
        com_cnt = pond_program_by_ws[watershed]['Commercial']
        writer.writerow([ws_full_name,
                         res_cnt,
                         com_cnt])