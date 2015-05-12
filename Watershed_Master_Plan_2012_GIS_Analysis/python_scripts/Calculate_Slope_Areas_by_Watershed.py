import arcpy
import csv
import os

# Function to return acres from sq. ft.
def sq_ft_to_acres(x):
    return x / 43560.0

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Create a dict keyed by watershed name, values to be acres (total).
watershed_area = {}
# Search fields containing watershed name and Shape_Area.
watershed_table = '/Basemap/Watersheds_2012'
field_names = ['WATERSHED_FULL_NAME', 'Shape_Area']
cursor = arcpy.da.SearchCursor(in_table=watershed_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    # Replace underscores with spaces to work in the table.
    ws_full_name = watershed.replace("_", " ")
    for row in cursor:
        if row[0] == ws_full_name:
            watershed_area[watershed] = sq_ft_to_acres(row[1])
    cursor.reset()

# Create dict to be keyed on watershed name, values containing another dict
# keyed by [0, 1, 2, 3] corresponding to percent slope 0-15%, 15-25%,
# 25-35%, and 35-100% counts, respectively.
slope_values_by_ws = {}
slope_values = [0, 1, 2, 3]
# Search fields containing Value and Count for each raster.
field_names = ['Value', 'Count']
# Iterate over each watershed.
for watershed in watershed_names:
    ws_area = watershed_area[watershed]
    in_raster = 'Slope_' + watershed + '_Reclass'
    cursor = arcpy.da.SearchCursor(in_table=in_raster,
                                   field_names=field_names)
    slope_values_count = {}
    total_count = 0
    for slope_value in slope_values:
        for row in cursor:
            # Only sum the counts for a given value.
            if row[0] == slope_value:
                slope_values_count[row[0]] = row[1]
                total_count += row[1]
        cursor.reset()
    for slope_value in slope_values:
        x = slope_values_count[slope_value]
        slope_values_count[slope_value] = x * ws_area / total_count
    slope_values_by_ws[watershed] = slope_values_count

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Slope_Classification_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Total area (acres)',
              '0-15% slope (acres)',
              '15-25% slope (acres)',
              '25-35% slope (acres)',
              '> 35% slope (acres)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        ws_area = watershed_area[watershed]
        low_slope = slope_values_by_ws[watershed][0]
        med_slope = slope_values_by_ws[watershed][1]
        high_slope = slope_values_by_ws[watershed][2]
        vhigh_slope = slope_values_by_ws[watershed][3]
        writer.writerow([ws_full_name,
                         ws_area,
                         low_slope,
                         med_slope,
                         high_slope,
                         vhigh_slope])