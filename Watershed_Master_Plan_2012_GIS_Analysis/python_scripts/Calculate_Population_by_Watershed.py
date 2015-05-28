import arcpy
import csv
import os

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Development_Patterns'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# For each watershed, sum populations of blocks within. Note: Dataset
# has been unioned with Use Ratio Policy turned on for the 'totpop'
# field.
pop_by_watershed = {}
in_table = os.path.join(task_dir, 'MSA_2010_Union')
field_names = ['WATERSHED_FULL_NAME', 'totpop']
cursor = arcpy.da.SearchCursor(in_table=in_table,
                               field_names=field_names)
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    pop_total = 0
    for row in cursor:
        if row[0] == ws_full_name:
            pop_total += row[1]
    pop_by_watershed[watershed] = pop_total
    cursor.reset()

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Population_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Total Population (2010)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        ws_pop = pop_by_watershed[watershed]
        writer.writerow([ws_full_name,
                         ws_pop])