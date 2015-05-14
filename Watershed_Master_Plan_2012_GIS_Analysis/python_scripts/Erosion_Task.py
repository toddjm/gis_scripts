import arcpy
import collections
import csv

# Specify directories.
root_dir = 'G:\WPDR_Common\Planning\Minehardt\Projects'
project_dir = '\Watershed_Master_Plan_GIS_Analysis'
gdb_name = '\Watershed_GIS_Analysis_ND.gdb'

# Set working directory.
working_dir = root_dir + project_dir + gdb_name
arcpy.env.workspace = working_dir

watershed_names = []
feature_class = '\Erosion\Geomorphic_Reaches'
field_name = 'WATERSHED'
cursor = arcpy.SearchCursor(feature_class)
for row in cursor:
    watershed_names.append(row.getValue(field_name))
watershed_names = collections.OrderedDict.fromkeys(watershed_names).keys()
print watershed_names

watershed_dict = {}
cnt = 0
for i in watershed_names:
    watershed_dict[cnt] = i
    cnt += 1
