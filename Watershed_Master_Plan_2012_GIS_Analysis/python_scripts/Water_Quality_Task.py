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
task_dir = 'Water_Quality'

# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name)
arcpy.env.workspace = working_dir

# Populate a list of watershed names from the feature class.
# Watershed names are those matching feature classes in the
# Watershed_Polygons feature dataset.
watershed_names = []
watershed_names = arcpy.ListFeatureClasses(feature_dataset=
                                           'Watershed_Polygons')

# Create dict to be keyed on watershed name with values equal to sum of EII
# reaches in each watershed (in acres).
eii_reaches_area = {}
# Search fields containing watershed name and Shape_Area.
in_table = os.path.join(task_dir, 'Watershed_Integrity_Scores_2012')
field_names = ['WATERSHED_FULL_NAME', 'Shape_Area']
cursor = arcpy.da.SearchCursor(in_table=in_table,
                               field_names=field_names)
# Iterate over each watershed.
for watershed in watershed_names:
    ws_full_name = watershed.replace("_", " ")
    area_sum = 0.0
    for row in cursor:
        # Only sum the area for EII reaches for a given watershed.
        if row[0] == ws_full_name:
            area_sum += row[1]
    eii_reaches_area[watershed] = sq_ft_to_acres(area_sum)
    cursor.reset()

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir, 'Water_Quality.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Area of EII Reaches (acres)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        writer.writerow([ws_full_name,
                         eii_reaches_area[watershed]])

