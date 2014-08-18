# 
# Function to concatenate values.
# This python function is usable from Python and JavaScript.
# The translation is done by running 'make translations' in the top dir.
# 

def compute_my_cell_compute(data_col, line):
    column = columns[data_col]
    s = ""
    for dc in column.average_columns:
        s += line[dc].value
    line[data_col] = line[data_col].set_value(s)
