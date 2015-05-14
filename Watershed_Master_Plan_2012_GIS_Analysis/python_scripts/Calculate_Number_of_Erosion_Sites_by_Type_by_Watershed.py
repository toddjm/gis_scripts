import arcpy
import collections
import csv
import os

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Erosion'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Tables to be read in for this script.
sites_table = os.path.join(task_dir, 'Erosion_Sites_Watersheds_Intersect')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Populate a list from SITE_TYPE from erosion sites table.
field_names = ['SITE_TYPE']
site_type_names = []
# Set the cursor to search the feature class.
cursor = arcpy.da.SearchCursor(in_table=sites_table,
                               field_names=field_names)
for row in cursor:
    site_type_names.append(row[0])
# Collapse list to contain unique values.
site_type_names = collections.OrderedDict.fromkeys(site_type_names).keys()

# Compute number of erosion sites by type per watershed.
site_types_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'SITE_TYPE']
cursor = arcpy.da.SearchCursor(in_table=sites_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    site_cnt = {}
    for site in site_type_names:
        cnt = 0
        for row in cursor:
            if row[0] == ws_full_name and row[1] == site:
                cnt += 1
            site_cnt[site] = cnt
        cursor.reset()
    site_types_by_ws[watershed] = site_cnt

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Number_of_Erosion_Sites_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed']
    stn_list = sorted(site_type_names)
    header_list = ["Type " + str(i) + " (count)" for i in stn_list if i is not None]
    header += header_list
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        out_list = [site_types_by_ws[watershed][i] for i in stn_list]
        out_list = [ws_full_name] + out_list
        writer.writerow(out_list)