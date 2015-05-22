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
task_dir = 'Creek_Flooding'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Tables to be read in for this script.
building_table = os.path.join(task_dir, 'Building_Footprints_2013')
floodplain_table = os.path.join(task_dir, 'Floodplain_100_Year')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Extract planimetrics per watershed.
building_cnt_by_ws = {}
building_layer = 'Building_Layer'
floodplain_layer = 'Floodplain_Layer'
arcpy.Delete_management(building_layer)
arcpy.Delete_management(floodplain_layer)
arcpy.MakeFeatureLayer_management(building_table, building_layer)
arcpy.MakeFeatureLayer_management(floodplain_table, floodplain_layer)
for watershed in watershed_names:
    ws_polygon = os.path.join('Watershed_Polygons', watershed)
    arcpy.SelectLayerByLocation_management(building_layer,
                                           'have_their_center_in',
                                           ws_polygon)
    arcpy.SelectLayerByLocation_management(building_layer,
                                           'intersect',
                                           floodplain_layer,
                                           selection_type='subset_selection')
    cnt = int(arcpy.GetCount_management('building_layer').getOutput(0))
    building_cnt_by_ws[watershed] = cnt

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Number_of_Structures_100_Year_Flood_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Structures in 100-year floodplain (count)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        cnt = building_cnt_by_ws[watershed]
        writer.writerow([ws_full_name,
                         cnt])