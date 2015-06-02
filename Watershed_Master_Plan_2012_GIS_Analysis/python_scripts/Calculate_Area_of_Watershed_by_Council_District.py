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

# The districts feature class is processed by the user with the
# Make Feature Layer tool with the Use Ratio Policy set for the shape
# length and shape area fields. The resulting layer is unioned with the
# watersheds feature class. Finally, the output feature class is edited
# and entries with FID identifiers that are non-positive (i.e. = -1) have
# been removed.
district_table = os.path.join(task_dir, 'Districts_Watersheds_Union')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Populate a list from DISTRICT_NAME.
field_names = ['COUNCIL_DISTRICT']
district_names = []
# Set the cursor to search the feature class.
cursor = arcpy.da.SearchCursor(in_table=district_table,
                               field_names=field_names)
# Iterate over rows, append district names list with values.
for row in cursor:
    district_names.append(row[0])
# Collapse list to contain unique values.
district_names = collections.OrderedDict.fromkeys(district_names).keys()

# Create dict to be keyed on watershed name, values containing another dict
# keyed by district name with values equal to the area for each watershed in
# that district.
ws_area_by_district = {}
# Search fields containing watershed name, district name, and Shape_Area.
field_names = ['WATERSHED_FULL_NAME', 'COUNCIL_DISTRICT', 'Shape_Area']
cursor = arcpy.da.SearchCursor(in_table=district_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    ws_area = {}
    for district in district_names:
        area = 0.0
        for row in cursor:
            # Only sum the areas for a given watershed and LU.
            if row[0] == ws_full_name and row[1] == district:
                area += row[2]
            ws_area[district] = sq_ft_to_acres(area)
        cursor.reset()
    ws_area_by_district[watershed] = ws_area

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Watershed_Area_by_District.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed']
    district_name_list = sorted(district_names)
    header_list = ["District " + str(i) +
                   " (acres)" for i in district_name_list if i is not None]
    header += header_list
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        out_list = [ws_area_by_district[watershed][i] for i in district_name_list]
        out_list = [ws_full_name] + out_list
        writer.writerow(out_list)