"""
Write csv file with miles reaches by score for each
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
task_dir = 'Erosion'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Tables to be read in for this script.
geo_table = os.path.join(task_dir, 'Geomorphic_Reaches_Watersheds_Intersect')
sites_table = os.path.join(task_dir, 'Erosion_Sites_Watersheds_Intersect')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Populate a list from DESCRIPTIV for geomorphic reaches table.
field_names = ['DESCRIPTIV']
score_names = []
# Set the cursor to search the feature class.
cursor = arcpy.da.SearchCursor(in_table=geo_table,
                               field_names=field_names)
for row in cursor:
    score_names.append(row[0])
# Collapse list to contain unique values.
score_names = collections.OrderedDict.fromkeys(score_names).keys()

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

# Create dict to be keyed on watershed name, values containing another dict
# keyed by score with values miles of reach per score.
miles_by_score_by_ws = {}
# Search fields containing watershed name, cu, and Shape_Area.
field_names = ['WATERSHED_FULL_NAME', 'DESCRIPTIV', 'Shape_Length']
cursor = arcpy.da.SearchCursor(in_table=geo_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    geo_length = {}
    for name in score_names:
        length = 0.0
        for row in cursor:
            # Only sum the areas for a given watershed and score name.
            if row[0] == ws_full_name and row[1] == name:
                length += row[2]
            geo_length[name] = ft_to_miles(length)
        cursor.reset()
    miles_by_score_by_ws[watershed] = geo_length

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Miles_of_Reaches_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed']
    sn_list = sorted(score_names)
    header_list = [i + " (miles)" for i in sn_list if i is not None]
    header += header_list
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        out_list = [miles_by_score_by_ws[watershed][i] for i in sn_list]
        out_list = [ws_full_name] + out_list
        writer.writerow(out_list)