"""
Write a csv file with a count of parcels by age
for each watershed.

"""
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

# Tables to be read in for this script.
dev_table = os.path.join(task_dir, 'TCAD_Watersheds_Union')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Compute number parcels by age group per watershed.
cnt_dev_age_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'YEAR_BUILT']
cursor = arcpy.da.SearchCursor(in_table=dev_table,
                               field_names=field_names)
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    cnt_old = 0
    cnt_med = 0
    cnt_new = 0
    cnt_by_age = {}
    for row in cursor:
        if row[0] == ws_full_name:
            if row[1] > 0 and row[1] < 1974:
                cnt_old += 1
            elif row[1] >= 1974 and row[1] <= 1991:
                cnt_med += 1
            elif row[1] > 1991:
                cnt_new += 1
    cursor.reset()
    cnt_by_age['old'] = cnt_old
    cnt_by_age['med'] = cnt_med
    cnt_by_age['new'] = cnt_new
    cnt_dev_age_by_ws[watershed] = cnt_by_age

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Number_of_Parcels_by_Age_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Development Age pre-1974 (count)',
              'Development Age 1974-1991 (count)',
              'Development Age post-1991 (count)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        cnt_old = cnt_dev_age_by_ws[watershed]['old']
        cnt_med = cnt_dev_age_by_ws[watershed]['med']
        cnt_new = cnt_dev_age_by_ws[watershed]['new']
        writer.writerow([ws_full_name,
                         cnt_old,
                         cnt_med,
                         cnt_new])