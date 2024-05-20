
import datetime
import os
import sys
import sqlite3
import json
import pandas as pd
import traceback
import clickhouse_connect
import ast
import numpy as np


from common import load_json, get_files, load_all_json

# if not os.path.exists("input"):
#     os.makedirs("input")
    
# if not os.path.exists("output"):
#     os.makedirs("output")

CURRENT_TEST_FILE = None

list_of_dbms = ["mysql", "mariadb", "postgresql", "sqlite"]

# check that for each dbms, there exists a folder in the input folder
# for dbms in list_of_dbms:
#     if not os.path.exists(f"input/{dbms}"):
#         os.makedirs(f"input/{dbms}")

run_date_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


ethz_ids = ["kpiskor", "acerfeda"]

# ask for ethz id as number [0] name ...

#if previous_selection.txt exists, then read the selected ethz id from there
if os.path.exists("previous_selection.txt"):
    with open("previous_selection.txt", "r") as f:
        selected_ethz_id = int(f.read())
        print(f"Selected ETHZ ID: {ethz_ids[selected_ethz_id]}")
else:
    print("Please select your ETHZ ID:")
    for i, ethz_id in enumerate(ethz_ids):
        print(f"[{i}] {ethz_id}")
    
    selected_ethz_id = int(input("Enter the number of your ETHZ ID: "))

# write to disk
with open("previous_selection.txt", "w") as f:
    f.write(str(selected_ethz_id))

print(f"Selected ETHZ ID: {ethz_ids[selected_ethz_id]}")

# create folder if not exists in output
if not os.path.exists(f"output/{ethz_ids[selected_ethz_id]}"):
    os.makedirs(f"output/{ethz_ids[selected_ethz_id]}")
    
current_output_folder = f"output/{ethz_ids[selected_ethz_id]}/{run_date_time}"
os.makedirs(current_output_folder)


# # create test.txt file in the output folder
# with open(f"{current_output_folder}/test.txt", "w") as f:
#     f.write("Hello World!")


def print_err(content, **kwargs):
    print(content, file=sys.stderr, **kwargs)
    with open(f"{current_output_folder}/{CURRENT_TEST_FILE}.err.log", "a") as f:
        f.write(content)
def print_debug(content, **kwargs):
    print(content, **kwargs)
    with open(f"{current_output_folder}/{CURRENT_TEST_FILE}.debug.log", "a") as f:
        f.write(content)




all_tests = load_all_json("clickhouse")

print("found", len(all_tests), "tests")

count = 0
total_tests = 0
success_tests = 0
fail_tests = 0
skip_tests = 0


client = clickhouse_connect.get_client(host='localhost', username='default', password='passwordAST1')


# run select 1 to check if the connection is working
print("Running select 1")
result = client.query("SELECT 1")
print("Result:", result)

for test in all_tests:
    for test_case in test["tests"]:
        total_tests += 1
        print("Running test", test_case["name"])
        query = test_case["query"]
        expected_result = test_case["expected_result"]

        try:            

            # if query contains FORMAT then skip
            if "FORMAT " in query:
                print("Encountered FORMAT in", query)
                print("Skipping test")
                skip_tests += 1
                continue
            
            # remove comments from the query also consider comments inside the query
            query = ' '.join(query.splitlines())
            query = query.split("--")[0] # todo handle -- inside the query
            
            # convert query to string
            query = str(query)

            # remove semicolon from the end of the query
            if query.endswith(";\n") or query.endswith("; "):
                query = query[:-2]

            result = client.query(query)

            result_set = result.result_set

            expected_table = test_case["expected_result_table"]

            #if expected table has no length then check if the result is empty
            if len(expected_table) == 0:
                print("Result rows", result.result_rows)
                if len(result.result_rows) == 0:
                    success_tests += 1
                    continue

                first_value = result_set[0][0]
                if str(first_value) != '':
                    print_err(f"Expected empty result but got '{first_value}'")
                    exit(1)
                else:
                    success_tests += 1
                    continue

            for i, row in enumerate(result_set):
                for j, cell in enumerate(row):
                    # get type of cell 
                    print("Cell", i, j, "Type:", type(cell))

                    # parse to type(cell)
                    parsed_cell_expected = None
                    cell_value = None



                    if type(cell) == int:
                        parsed_cell_expected = int(expected_table[i][j])
                        cell_value = cell
                    elif type(cell) == float:
                        parsed_cell_expected = float(expected_table[i][j])
                        cell_value = cell
                        if np.isnan(parsed_cell_expected) and np.isnan(cell_value):
                            parsed_cell_expected = 0
                            cell_value = 0
                    elif type(cell) == str:
                        parsed_cell_expected = expected_table[i][j]
                        cell_value = cell
                    elif type(cell) == list:
                        if(len(cell) > 0):
                            print("Cell 0", cell[0], "Type:", type(cell[0]))
                            
                        parsed_cell_expected = ast.literal_eval(expected_table[i][j])
                        print(parsed_cell_expected)
                        # go trough cell and convert to string

                        if len(cell) > 0:
                            print("Cell 0", cell[0], "Type:", type(cell[0]))
                            if type(cell[0]) == bytes:
                                cell_value = []
                                print("Cell is list of bytes")
                                for item in cell:
                                    # convert byte value to string
                                    cell_value.append(item.decode('latin1'))
                            elif type(cell[0]) == type(None):
                                print("Cell is list of None")
                                cell_value = []
                                for item in cell:
                                    cell_value.append("\\N")
                            else:
                                print_err(f"Type {type(cell[0])} not handled")
                                cell_value = cell
                        else:
                            print_err("Empty list")
                            cell_value = cell

                    elif type(cell) == bool:
                        parsed_cell_expected = bool(expected_table[i][j])
                        cell_value = cell
                    elif type(cell) == datetime.datetime:
                        parsed_cell_expected = datetime.datetime(expected_table[i][j])
                        cell_value = cell
                    elif type(cell) == datetime.date:
                        parsed_cell_expected = datetime.date(expected_table[i][j])
                        cell_value = cell
                    elif type(cell) == datetime.time:
                        parsed_cell_expected = datetime.time(expected_table[i][j])
                        cell_value = cell
                    # bytes
                    elif type(cell) == bytes:
                        parsed_cell_expected = expected_table[i][j] # handle it as string
                        cell_value = str(cell)
                        # remove b' and ' from the string
                        cell_value = cell_value[2:-1]
                    # tuple
                    elif type(cell) == tuple:
                        parsed_cell_expected = ast.literal_eval(expected_table[i][j])
                        cell_value = cell
                    elif type(cell) == type(None):
                        parsed_cell_expected = expected_table[i][j]
                        cell_value = "\\N"
                    else:
                        print_err(f"Type {type(cell)} not handled")
                        exit(1)   

                    # if the cell type is list then compare the length of the list and values of the list
                    if type(cell) == list:
                        if len(cell_value) != len(parsed_cell_expected):
                            print_err(f"Cell type {type(cell)} is expected LIST LEN")
                            print_err(f"Cell {i}, {j} does not match. Expected: '{expected_table[i][j]}' Got: '{cell_value}'")
                            print_err(f"Query: {query}")
                            #print_err(f"Expected Result: {expected_result}")
                            #print_err(f"Result: {result}")
                            #raise Exception("Result does not match")
                            exit(1)
                        for k, item in enumerate(cell_value):
                            if item != parsed_cell_expected[k]:
                                print_err(f"Cell type {type(cell)} is expected LIST ITEM VAL")
                                print_err(f"Cell {i}, {j} does not match. Expected: '{expected_table[i][j]}' Got: '{cell_value}'")
                                print_err(f"Query: {query}")
                                #print_err(f"Expected Result: {expected_result}")
                                #print_err(f"Result: {result}")
                                #raise Exception("Result does not match")
                                exit(1)
                        success_tests += 1
                        continue
                            

                    if cell_value != parsed_cell_expected:
                        print_err(f"Cell type {type(cell)} is expected")
                        print_err(f"Cell {i}, {j} does not match. Expected: '{expected_table[i][j]}' Got: '{cell_value}'")
                        print_err(f"Query: {query}")
                        #print_err(f"Expected Result: {expected_result}")
                        #print_err(f"Result: {result}")
                        #raise Exception("Result does not match")
                        exit(1)

            success_tests += 1

        except Exception as e:
            print("Test failed")
            fail_tests += 1
            print_err(f"Error in test {test_case['name']}\n{traceback.format_exc()}")
            print_err(f"Query: {query}")
            print_err(f"Expected Result: {expected_result}")
            print_err(f"Error: {e}")
            exit(1)
    
    
    
print("Total tests:", total_tests, " Success:", success_tests, " Fail:", fail_tests, " Skip:", skip_tests)