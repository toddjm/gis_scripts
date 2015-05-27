import arcpy
import csv
import os

# Function to convert sq. ft. to acres.
def sq_ft_to_acres(x):
    return x / 43560.0

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Planimetrics_Features_Union_Watersheds'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# List of impervious area features.
ic_features = ['Above_Ground',
               'Airport_Runway_Taxiway',
               'Bridge',
               'Compacted_Soil',
               'Covered',
               'Dam',
               'Dock',
               'Edge_of_Paved_Alley',
               'Edge_of_Paved_Road',
               'Edge_of_Pavement',
               'Edge_of_Unpaved_Road',
               'In_Ground',
               'Median',
               'Misc',
               'Other_Landmark',
               'Patio',
               'Paved',
               'Paved_Ditch',
               'Paved_Parking',
               'Recreation_Court_Ball_Field',
               'Sidewalk',
               'Structure',
               'Tank',
               'Uncovered',
               'Unpaved',
               'Unpaved_Parking']

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Sum area for each IC feature on a per-watershed basis.
ic_area_by_ws = {}
field_names = ['WATERSHED_FULL_NAME', 'SHAPE_Area']
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    ic_area = {}
    for feature in ic_features:
        in_table = feature + '_Watersheds_Union'
        cursor = arcpy.da.SearchCursor(in_table=in_table,
                                       field_names=field_names)
        area = 0.0
        for row in cursor:
            if row[0] == ws_full_name:
                area += row[1]
        cursor.reset()
        ic_area[feature] = sq_ft_to_acres(area)
    ic_area_by_ws[watershed] = ic_area

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'IC_Area_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed']
    ic_features_list = sorted(ic_features)
    header_list = [i + " (acres)" for i in ic_features_list if i is not None]
    header += header_list
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        out_list = [ic_area_by_ws[watershed][i] for i in ic_features_list]
        out_list = [ws_full_name] + out_list
        writer.writerow(out_list)