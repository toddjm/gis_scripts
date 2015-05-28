import arcpy
import collections
import csv
import os

# Arguments:
#    0: input workspace
#    1: input feature class
#    2: field name to sum shape area (e.g. 'WATERSHED_FULL_NAME')
#    3: output table

# Function to convert sq. ft. to acres.
def sq_ft_to_acres(x):
    return x / 43560.0

# Set working directory to the project geodatabase.
working_dir = arcpy.GetParameterAsText(0)
arcpy.env.workspace = working_dir

# Specify input feature class.
in_fc = arcpy.GetParameterAsText(1)

# Specify field name to sum areas.
in_fn = arcpy.GetParameterAsText(2)

# Specify output table name.
out_table = arcpy.GetParameterAsText(3)

# Populate a list from input field name, remove multiple values.
fn_values = []
# Set the cursor to search the feature class.
cursor = arcpy.da.SearchCursor(in_table=in_fc,
                               field_names=in_fn)
# Iterate over rows, append project stages list with values.
for row in cursor:
    fn_values.append(row[0])
# Collapse list to contain unique values.
fn_values = collections.OrderedDict.fromkeys(fn_values).keys()

# Create a dict keyed by fn_value, values are shape acres (total).
total_area = {}
# Search fields containing fn_value and Shape_Area.
cursor = arcpy.da.SearchCursor(in_table=in_fc,
                               field_names=[in_fn, 'Shape_Area'])
# Iterate over each fn_value.
for fn in fn_values:
    for row in cursor:
        if row[0] == fn:
            total_area[fn] = sq_ft_to_acres(row[1])
    cursor.reset()

# Writing tables.
with open(out_table, 'wb') as f:
    writer = csv.writer(f)
    header = ['Name',
              'Area (acres)']
    writer.writerow(header)
    for fn in fn_values:
        area = total_area[fn]
        writer.writerow([fn,
                         area])