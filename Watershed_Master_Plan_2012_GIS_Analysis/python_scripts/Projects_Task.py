import arcpy
import collections
import csv
import os

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Projects'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Tables to be read in for this script.
projects_table = os.path.join(task_dir, 'CIP_Projects_Watersheds_Union')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Populate a list from PROJECT_STAGE.
field_names = ['PROJECT_STAGE']
project_stages = []
# Set the cursor to search the feature class.
cursor = arcpy.da.SearchCursor(in_table=projects_table,
                               field_names=field_names)
# Iterate over rows, append project stages list with values.
for row in cursor:
    project_stages.append(row[0])
# Collapse list to contain unique values.
project_stages = collections.OrderedDict.fromkeys(project_stages).keys()


# Create dict to be keyed on watershed name, values containing another dict
# keyed by project stages with values equal to the count for each watershed.
projects_by_ws = {}
# Search fields containing watershed name, drainage_threshold, and Shape_Length.
field_names = ['WATERSHED_FULL_NAME', 'PROJECT_STAGE']
cursor = arcpy.da.SearchCursor(in_table=projects_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    stage_count = {}
    for stage in project_stages:
        cnt = 0
        for row in cursor:
            # Only sum the lengths for a given watershed and DA.
            if row[0] == ws_full_name and row[1] == stage:
                cnt += 1
            stage_count[stage] = cnt
        cursor.reset()
    projects_by_ws[watershed] = stage_count

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'CIP_Projects.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed']
    stages_list = sorted(project_stages)
    header_list = [i for i in stages_list if i is not None]
    header += header_list
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        out_list = [projects_by_ws[watershed][i] for i in stages_list]
        out_list = [ws_full_name] + out_list
        writer.writerow(out_list)
