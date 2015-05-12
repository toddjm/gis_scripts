import arcpy
import collections
import csv
import os

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Watershed_Polygons'


# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name, task_dir)
arcpy.env.workspace = working_dir
arcpy.env.overwriteOutput = True

# Tables to be read in for this script. Note that special
# charaters (apostrophes and periods) have been removed from
# the Watersheds_2012 table.
watershed_table = os.path.join(root_dir, project_dir, gdb_name,
                               'Basemap\Watersheds_2012')

# Populate a list of watershed names from the feature class.
field_names = ['WATERSHED_FULL_NAME']
watershed_names = []
# Set the cursor to search the feature class.
cursor = arcpy.da.SearchCursor(in_table=watershed_table,
                               field_names=field_names)
# Iterate over rows, append watershed name list with values.
for row in cursor:
    watershed_names.append(row[0])
# Collapse list of watershed names to contain unique values.
watershed_names = collections.OrderedDict.fromkeys(watershed_names).keys()

# Iterate over each watershed, write to file.
for wn in watershed_names:
    search_str = 'WATERSHED_FULL_NAME = ' + "'" + wn + "'"
    # Insert underscores in place of spaces to output file names.
    out_file = wn.replace(" ", "_")
    arcpy.Select_analysis(watershed_table, out_file, search_str)