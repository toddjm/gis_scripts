import arcpy
import collections
import csv
import os

# Specify directory paths to the project components.
gdb_name = 'Watershed_GIS_Analysis.gdb'
project_dir = 'Watershed_Master_Plan_GIS_Analysis'
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
tables_dir = 'Tables'
task_dir = 'Single_Member_District_Polygons'


# Set working directory to the project geodatabase.
working_dir = os.path.join(root_dir, project_dir, gdb_name, task_dir)
arcpy.env.workspace = working_dir
arcpy.env.overwriteOutput = True

# Tables to be read in for this script.
district_table = os.path.join(root_dir, project_dir, gdb_name,
                               'Basemap\Single_Member_Districts')

# Populate a list of watershed names from the feature class.
field_names = ['DISTRICT_NAME']
district_names = []
# Set the cursor to search the feature class.
cursor = arcpy.da.SearchCursor(in_table=district_table,
                               field_names=field_names)
# Iterate over rows, append watershed name list with values.
for row in cursor:
    district_names.append(row[0])
# Collapse list of watershed names to contain unique values.
district_names = collections.OrderedDict.fromkeys(district_names).keys()

# Iterate over each watershed, write to file.
for district in district_names:
    search_str = 'DISTRICT_NAME = ' + "'" + district + "'"
    # Insert underscores in place of spaces to output file names.
    out_file = district.replace(" ", "_")
    arcpy.Select_analysis(district_table, out_file, search_str)