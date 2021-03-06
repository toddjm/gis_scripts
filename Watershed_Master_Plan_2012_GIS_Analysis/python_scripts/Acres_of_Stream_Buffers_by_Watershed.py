"""
Writes a csv file with total area of creek buffer for each
64-, 320-, and 640-acre drainage area by each critical
water quality zone (CWQZ, TWQZ) per watershed.

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
root_dir = 'G:\WPDR_Common\Planning\Minehardt'
tables_dir = 'Tables'
task_dir = 'Regulations'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# The creek buffer feature class is unioned with the
# watersheds feature class. The output feature class is edited
# and entries with FID identifiers that are non-positive (i.e. = -1) have
# been removed.
buffer_table = os.path.join(task_dir, 'Creek_Buffers_Watersheds_Union')

# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset. Alternatively, specify
# watershed names as a list (and not one derived from feature
# class names in the Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Create dict to be keyed on watershed name, values containing another dict
# keyed by DA thresholds with values equal to sum of buffer area for each
# DA (in miles). For CWQZ only.
buffer_area_by_DA_CWQZ = {}
drainage_thresholds = [64, 320, 640]
field_names = ['WATERSHED_FULL_NAME',
               'DRAINAGE_AREA_ORDINANCE',
               'Shape_Area',
               'CRITICAL_WATER_QUALITY_ZONE']
cursor = arcpy.da.SearchCursor(in_table=buffer_table,
                               field_names=field_names)
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    area_sum = {}
    for drainage_area in drainage_thresholds:
        area = 0.0
        for row in cursor:
            # Only sum the areas for a given watershed and DA.
            if (row[0] == ws_full_name and
                row[1] == drainage_area and
                row[3] == 'CWQZ'):
                area += row[2]
            area_sum[drainage_area] = sq_ft_to_acres(area)
        cursor.reset()
    buffer_area_by_DA_CWQZ[watershed] = area_sum

# Create dict to be keyed on watershed name, values containing another dict
# keyed by DA thresholds with values equal to sum of buffer area for each
# DA (in miles). For WQTZ only.
buffer_area_by_DA_WQTZ = {}
drainage_thresholds = [64, 320, 640]
cursor = arcpy.da.SearchCursor(in_table=buffer_table,
                               field_names=field_names)
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    area_sum = {}
    for drainage_area in drainage_thresholds:
        area = 0.0
        for row in cursor:
            # Only sum the areas for a given watershed and DA.
            if (row[0] == ws_full_name and
                row[1] == drainage_area and
                row[3] == 'WQTZ'):
                area += row[2]
            area_sum[drainage_area] = sq_ft_to_acres(area)
        cursor.reset()
    buffer_area_by_DA_WQTZ[watershed] = area_sum

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Acres_of_Creek_Buffer_by_Watershed.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              '64-acre buffer (CWQZ, acres)',
              '320-acre drainage (CWQZ, acres)',
              '640-acre drainage (CWQZ, acres)',
              '64-acre buffer (WQTZ, acres)',
              '320-acre drainage (WQTZ, acres)',
              '640-acre drainage (WQTZ, acres)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        cw_64 = buffer_area_by_DA_CWQZ[watershed][64]
        cw_320 = buffer_area_by_DA_CWQZ[watershed][320]
        cw_640 = buffer_area_by_DA_CWQZ[watershed][640]
        tw_64 = buffer_area_by_DA_WQTZ[watershed][64]
        tw_320 = buffer_area_by_DA_WQTZ[watershed][320]
        tw_640 = buffer_area_by_DA_WQTZ[watershed][640]
        writer.writerow([ws_full_name,
                         cw_64,
                         cw_320,
                         cw_640,
                         tw_64,
                         tw_320,
                         tw_640])