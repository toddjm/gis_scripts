import arcpy
import csv
import os

# Function to covert feet to miles.
def ft_to_miles(x):
    return x / 5280.0

# Function to convert sq. ft. to acres.
def sq_ft_to_acres(x):
    return x / 43560.0

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Natural_Features'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Tables to be read in for this script.
creeks_table = os.path.join(task_dir, 'Creeks_2012')
floodplain_table = os.path.join(task_dir, 'Floodplain_2012_Union')
recharge_table = os.path.join(task_dir, 'Recharge_Zone_Union')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Create dict to be keyed on watershed name, values containing another dict
# keyed by DA thresholds with values equal to sum of creek lengths for each
# DA (in miles).
creek_lengths_by_DA = {}
drainage_thresholds = [64, 320, 640]
# Search fields containing watershed name, drainage_threshold, and Shape_Length.
field_names = ['WATERSHED_FULL_NAME', 'drainage_threshold', 'Shape_Length']
cursor = arcpy.da.SearchCursor(in_table=creeks_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    length_sum = {}
    for drainage_area in drainage_thresholds:
        length = 0.0
        for row in cursor:
            # Only sum the lengths for a given watershed and DA.
            if row[0] == ws_full_name and row[1] == drainage_area:
                length += row[2]
            # Insert key,value pair with length in miles.
            length_sum[drainage_area] = ft_to_miles(length)
        cursor.reset()
    creek_lengths_by_DA[watershed] = length_sum

# Compute acres of floodplain per watershed.
floodplain_area = {}
# Search fields containing watershed name and Shape_Area.
field_names = ['WATERSHED_FULL_NAME', 'Shape_Area']
cursor = arcpy.da.SearchCursor(in_table=floodplain_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    area_sum = 0.0
    for row in cursor:
        # Only sum the area of floodplain in a given watershed.
        if row[0] == ws_full_name:
            area_sum += row[1]
    floodplain_area[watershed] = sq_ft_to_acres(area_sum)
    cursor.reset()

# Compute acres of recharge zone per watershed.
recharge_area = {}
# Search fields containing watershed name and Shape_Area.
field_names = ['WATERSHED_FULL_NAME', 'Shape_Area']
cursor = arcpy.da.SearchCursor(in_table=recharge_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    area_sum = 0.0
    for row in cursor:
        # Only sum the area of floodplain in a given watershed.
        if row[0] == ws_full_name:
            area_sum += row[1]
    recharge_area[watershed] = sq_ft_to_acres(area_sum)
    cursor.reset()

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Natural_Features.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              '64-acre drainage (miles)',
              '320-acre drainage (miles)',
              '640-acre drainage (miles)',
              'Floodplain area (acres)',
              'Recharge area (acres)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        da_64 = creek_lengths_by_DA[watershed][64]
        da_320 = creek_lengths_by_DA[watershed][320]
        da_640 = creek_lengths_by_DA[watershed][640]
        fp_area = floodplain_area[watershed]
        rc_area = recharge_area[watershed]
        writer.writerow([ws_full_name,
                         da_64,
                         da_320,
                         da_640,
                         fp_area,
                         rc_area])