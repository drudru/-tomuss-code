# Regression tests for the function.
# They are executed in Python and Javascript when running
# 'make' in PYTHON_JS directory.

def my_cell_compute_regtest():
    columns_set([Column(), Column(), Column({"average_columns": [0, 1]})])
    line = [Cell('x', "z"), Cell('y', "", "", "C"), CE("xy")]
    check_result(line, 2, compute_my_cell_compute)
        
    print('my_cell_compute regtest are fine')

my_cell_compute_regtest()

