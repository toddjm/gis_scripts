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

# Populate a dict for each watershed, keyed on watershed name
# with acreage of tree canopy coverage as values.
tree_canopy_coverage = {}
field_names = ['Value', 'Count']
for watershed in watershed_names:
    raster_file_name = 'Tree_Canopy_' + watershed
    if arcpy.ListRasters(raster_file_name):
        cursor = arcpy.da.SearchCursor(in_table=raster_file_name,
                                       field_names=field_names)
        for row in cursor:
            if row[0] == 0:
                no_trees = row[1]
            elif row[0] == 1:
                trees = row[1]
        total = trees + no_trees
        ratio = trees / total
        ws_area = watershed_area[watershed]
        tree_canopy_coverage[watershed] = ws_area * ratio
        cursor.reset()

# Writing tables.
out_file = os.path.join(root_dir, project_dir, tables_dir,
                        'Tree_Canopy_Coverage.csv')
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    header = ['Watershed',
              'Total area (acres)',
              'Tree canopy coverage (acres)',
              'Tree canopy coverage (%)']
    writer.writerow(header)
    for watershed in watershed_names:
        ws_full_name = watershed.replace("_", " ")
        ws_area = watershed_area[watershed]
        tcc = tree_canopy_coverage[watershed]
        pct = 100.0 * tcc / ws_area
        writer.writerow([ws_full_name,
                         ws_area,
                         tcc,
                         pct])