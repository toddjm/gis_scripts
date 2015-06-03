"""
Write a csv file with CEF information per watershed.

"""
import arcpy
import csv
import os

def sq_ft_to_acres(x):
    """
    Return acres given square feet.
    """
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
outcrop_table = os.path.join(task_dir, 'Rock_Outcrop_Watershed_Intersect')
springs_table = os.path.join(task_dir, 'Springs')
wetland_table = os.path.join(task_dir, 'Wetland_Watershed_Union')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Compute number of springs per watershed.
# Make a layer for the springs for select by location operation.
springs_layer = 'Springs_Layer'
arcpy.Delete_management(springs_layer)
arcpy.MakeFeatureLayer_management(springs_table, springs_layer)
# For each watershed, get count of springs with their centers in that
# watershed.
springs_count = {}
for watershed in watershed_names:
    ws_polygon = os.path.join('Watershed_Polygons', watershed)
    arcpy.SelectLayerByLocation_management(springs_layer,
                                           'have_their_center_in',
                                           ws_polygon)
    cnt = arcpy.GetCount_management(springs_layer)
    springs_count[watershed] = cnt

# Compute number of wetland features per watershed. Note: Dataset has
# been unioned with Use Ratio Policy turned on for the 'SHAPE_Area' field.
# For each watershed, get count of wetlands completely within that
# watershed. Also compute area of wetland (acres) per watershed.
wetland_count = {}
wetland_area = {}
field_names = ['WATERSHED_FULL_NAME', 'SHAPE_Area']
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    cursor = arcpy.da.SearchCursor(in_table=wetland_table,
                                   field_names=field_names)
    area_total = 0.0
    cnt = 0
    for row in cursor:
        if row[0] == ws_full_name:
            area_total += row[1]
            cnt += 1
    wetland_area[watershed] = sq_ft_to_acres(area_total)
    wetland_count[watershed] = cnt
    cursor.reset()

# Compute number of linear feet of rock outcrop per watershed.
# Note: Dataset has been intersected with Use Ratio Policy turned on
# for the 'SHAPE_Length' field. For each watershed, calculate the total
# length (feet) of rock outcrop completely within that watershed.
outcrop_total = {}
field_names = ['WATERSHED_FULL_NAME', 'SHAPE_Length']
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    cursor = arcpy.da.SearchCursor(in_table=outcrop_table,
                                   field_names=field_names)
    len_total = 0.0
    for row in cursor:
        if row[0] == ws_full_name:
            len_total += row[1]
    outcrop_total[watershed] = len_total
    cursor.reset()

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'CEF_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Springs (count)',
              'Wetlands (count)',
              'Wetlands (acres)',
              'Rock Outcrop (feet)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        sp_cnt = springs_count[watershed]
        wl_cnt = wetland_count[watershed]
        wl_area = wetland_area[watershed]
        ro_len = outcrop_total[watershed]
        writer.writerow([ws_full_name,
                         sp_cnt,
                         wl_cnt,
                         wl_area,
                         ro_len])