import json
import os
import pyarrow as pa
import pyarrow.compute as pc
import pandas as pd

def compare_dataframes(df1, df2):
    
    if df1 is None and df2 is None:
        return True, True, True, True

    if df1 is None or df2 is None:
        return False, False, False, False
    
    shape_equal = df1.shape == df2.shape
    columns_equal = list(df1.columns) == list(df2.columns)
    dtypes_equal = df1.dtypes.equals(df2.dtypes)
    values_equal = df1.equals(df2)
    
    return shape_equal, columns_equal, dtypes_equal, values_equal
    # # Check shape
    # if df1.shape != df2.shape:
    #     return f"Shape mismatch: {df1.shape} vs {df2.shape}"
    
    # # Check column names
    # if list(df1.columns) != list(df2.columns):
    #     return f"Column names mismatch: {list(df1.columns)} vs {list(df2.columns)}"
    
    # # Check data types
    # if not df1.dtypes.equals(df2.dtypes):
    #     type_mismatches = df1.dtypes.compare(df2.dtypes)
    #     return f"Data type mismatch:\n{type_mismatches}"
    
    # # Check values
    # if not df1.equals(df2):
    #     value_mismatches = (df1 != df2).stack()
    #     return f"Value mismatches:\n{value_mismatches[value_mismatches]}"
    
    #return "DataFrames are equal"
def compare_arrow_tables(table1, table2):
    # Check schema (including shape)
    if table1.schema != table2.schema:
        return f"Schema mismatch: {table1.schema} vs {table2.schema}"
    
    # Check values
    for column_name in table1.column_names:
        array1 = table1[column_name]
        array2 = table2[column_name]
        if not array1.equals(array2):
            differences = pc.equal(array1, array2)
            mismatches = pc.is_null(differences).combine_chunks().to_pylist()
            mismatch_indices = [i for i, match in enumerate(mismatches) if not match]
            return f"Value mismatches in column '{column_name}': {mismatch_indices}"
    
    return "Arrow Tables are equal"

def load_json(file):
    with open(file, "r", encoding="utf-8", errors='ignore') as f:
        return json.load(f)
    
    
def get_files(database):
    all_tests = []
    # in folder input/database/ get all json files
    for root, dirs, files in os.walk(f"input/{database}"):
        for file in files:
            if file.endswith(".json"):
                all_tests.append(os.path.join(root, file))
                
    # sort the files
    all_tests.sort()
    
    # print first 4 files
    print("First 4 files:", all_tests[:4])
                
    return all_tests

def load_all_json(database):
    all_tests = get_files(database)
    parsed_tests = []
    for test in all_tests:
        parsed_tests.append(load_json(test))
    return parsed_tests


def clean_input_folder(database):
    if os.path.exists(f"input/{database}"):
        if os.name == "posix":  # Linux
            os.system(f"rm -rf input/{database}")
        elif os.name == "nt":  # Windows
            os.system(f"rmdir /s /q input\\{database}")
            
    os.makedirs(f"input/{database}")