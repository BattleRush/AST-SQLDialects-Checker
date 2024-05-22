
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
from ast import literal_eval as make_tuple

from common import load_json, get_files, load_all_json

def check_if_same(received, expected):

    print("received type", type(received), " expected type", type(expected))

    # if received is a tuple convert to list
    if type(received) == tuple:
        received = list(received)
        print("received is tuple, converting to list", received)
        #exit(1)

    # if received is byte but expected is str parse received to str
    if type(received) == bytes and type(expected) == str:
        received = received.decode('latin1')
        print("received is bytes, converting to str", received)
        #exit(1)

    if type(received) != type(expected):
        print_err(f"Received {received} does not match {expected}")
        print_err(f"Type {type(received)} does not match {type(expected)}")
        return False
    
    # check if type is int
    if type(received) == int:
        if received != expected:
            print_err(f"Expected {expected} but got {received} (int)")
            return False
        return True
    
    if type(received) == float:
        if received != expected:
            print_err(f"Expected {expected} but got {received} (float)")
            return False
        return True
    
    if type(received) == str:
        if received != expected:
            print_err(f"Expected {expected} but got {received} (str)")
            return False
        return True
    
    if type(received) == list:
        if len(received) != len(expected):
            print_err(f"Expected {expected} but got {received} (list)")
            return False
        
        for i, item in enumerate(received):
            if not check_if_same(item, expected[i]):
                return False
        return True
    
    if type(received) == bool:
        if received != expected:
            print_err(f"Expected {expected} but got {received} (bool)")
            return False
        return True
    
    if type(received) == datetime.datetime:
        if received != expected:
            print_err(f"Expected {expected} but got {received} (datetime.datetime)")
            return False
        return True

    if type(received) == datetime.date:
        if received != expected:
            print_err(f"Expected {expected} but got {received} (datetime.date)")
            return False
        return True

    if type(received) == datetime.time:
        if received != expected:
            print_err(f"Expected {expected} but got {received} (datetime.time)")
            return False
        return True
    
    if type(received) == bytes:
        if received != expected:
            print_err(f"Expected {expected} but got {received} (bytes)")
            return False
        return True
    
    if type(received) == tuple:
        print("comparing tuple")
        if received != expected:
            print_err(f"Expected {expected} but got {received} (tuple)")
            return False
        return True
    
    print(f"Type {type(received)} not handled")
    exit(1)
        
def parse_value(received, expected):
    parsed_received = None
    parsed_expected = None

    print("parse_value: ", received, "Type:", type(received))
    
    if type(received) == int:
        parsed_received = received
        parsed_expected = int(expected)
    elif type(received) == float:
        parsed_received = received
        parsed_expected = float(expected)
        if np.isnan(parsed_received) and np.isnan(parsed_expected):
            parsed_received = 0
            parsed_expected = 0
    elif type(received) == str:
        parsed_received = received
        parsed_expected = str(expected)
    elif type(received) == list:
        
        parsed_received = []
        parsed_expected = []
        
        print("going down the list")
        print("passing expected", expected, " of type", type(expected))
        # parse the expected to a list

        if type(expected) != list:
            expected = expected.replace('NULL', 'None')  # replace 'NULL' with 'None' such that python understands it

            expected = ast.literal_eval(expected)
       

        print("expected_list", expected)
            
        for i, item in enumerate(received):
            print("------")
            print("item", item, "Type:", type(item))
            print("expected[i]", expected[i], "Type:", type(expected[i]))
            print("type of item", type(item), "type of expected[i]", type(expected[i]))
            parsed_received.append(item)

            received_value, expected_value = parse_value(item, expected[i])
            print("parse_value->received_value", received_value, "Type:", type(received_value))
            print("parse_value->expected_value", expected_value, "Type:", type(expected_value))
            parsed_expected.append(expected_value)

            
        # go trough received and convert to string

        if len(received) > 0:
            print("received 0", received[0], "Type:", type(received[0]))
            if type(received[0]) == bytes:
                received_value = []
                print("received is list of bytes")
                for item in received:
                    # convert byte value to string
                    received_value.append(item.decode('latin1'))
            elif type(received[0]) == type(None):
                print("received is list of None")
                received_value = []
                for item in received:
                    received_value.append("\\N")
            else:
                print_err(f"Type {type(received[0])} not handled")
                received_value = received

    elif type(received) == bool:
        parsed_received = received
        parsed_expected = bool(expected)
    elif type(received) == datetime.datetime:
        parsed_received = received
        # parse datetime to format 1970-01-01 00:00:00
        parsed_expected = expected
        #parsed_expected = datetime.datetime(expected)
        print("parsed_expecteddatetime.datetime: ", parsed_expected)
    elif type(received) == datetime.date:
        parsed_received = received
        #parsed_expected = datetime.date(expected)
        parsed_expected = expected
    elif type(received) == datetime.time:
        parsed_received = received
        #parsed_expected = datetime.time(expected)
        parsed_expected = expected
    # bytes
    elif type(received) == bytes:

        parsed_received = str(received)        
        # remove b' and ' from the string
        parsed_received = parsed_received[2:-1]
        
        parsed_expected = expected
        
        
    # tuple
    elif type(received) == tuple:
        print("received is tuple")
        parsed_received = received
        # replace ", " with ","
        #expected = str(expected).replace(", ", ",")
        #print("Expected", expected)
        # parse (1, 2) to a tuple
        #parsed_expected = make_tuple(expected)

        # convert tuple to array
        parsed_received = list(received)
        print("parsed_received", parsed_received)
        # parse string to tuple first and then to list
        #print("expected", expected, " of type", type(expected))
        #expected_tuple = make_tuple(expected)
        print("expected_tuple", expected)
        parsed_expected = list(expected)

        print("parsed_expected list", parsed_expected)
        # process now as list
        parsed_received, parsed_expected = parse_value(parsed_received, parsed_expected)
        
        print("parsed_received", parsed_received)
        print("parsed_expected", parsed_expected)
    elif type(received) == type(None):
        parsed_received = "\\N"
        parsed_expected = expected
    else:
        print_err(f"Type {type(received)} not handled 22")
        exit(1) 
        
    return parsed_received, parsed_expected



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
skip_tests_syntax_err = 0

client = clickhouse_connect.get_client(host='localhost', username='default', password='passwordAST1')


# run select 1 to check if the connection is working
print("Running select 1")
result = client.query("SELECT 1")
print("Result:", result)

for test in all_tests:
    for test_case in test["tests"]:
        print("#############################################")
        total_tests += 1
        print("Running test", test_case["name"])
        query = test_case["query"]
        expected_result = test_case["expected_result"]
        expected_table = test_case["expected_result_table"]

        try:            

            # if query contains FORMAT then skip
            if "FORMAT_" in query or "FORMAT " in query:
                print("Encountered FORMAT in", query)
                print("Skipping test")
                skip_tests += 1
                continue
            
            if "formatReadableDecimalSize" in query:
                print("Encountered formatReadableDecimalSize in", query)
                print("Skipping test")
                skip_tests += 1
                continue
            
            if "reinterpretAsString" in query:
                print("Encountered reinterpretAsString in", query)
                print("Skipping test")
                skip_tests += 1
                continue
            
            # remove comments from the query also consider comments inside the query
            #query = ' '.join(query.splitlines())
            #query = query.split("--")[0] # todo handle -- inside the query
            
            # convert query to string and concat with new line
            query = str(query)
            #query = '\n'.join(query.split())

            # remove semicolon from the end of the query
            if query.endswith(";\n") or query.endswith("; "):
                query = query[:-2]
            
            # if there is ; replace it
            if ";" in query:
                query = query.replace(";", "")

            result = client.query(query)

            #print(result.rows_stream )
            # loop through rows_stream 
            result_table = []
            for row in result.result_rows:
                print(row)
                
                row_list = []
                for cell in row:
                    print("cell", cell)
                    # parse cell to string
                    row_list.append(str(cell))
                result_table.append(row_list)
            print("Result table", result_table)
            print("Expected table", expected_table)

            # check if result_table is same as expected_table
            if len(result_table) != len(expected_table):
                print_err(f"Expected {expected_table} but got {result_table}")
                exit(1)
            
            for i, row in enumerate(result_table):
                # check size for row
                if len(row) != len(expected_table[i]):
                    print_err(f"Expected ROW {expected_table} but got {result_table}")
                    exit(1)

                for j, cell in enumerate(row):
                    # get type of cell 
                    print("Cell", i, j, "Type:", type(cell))
                    expected_value = expected_table[i][j]
                    received_value = cell

                    print("Expected value", expected_value, "Type:", type(expected_value))
                    print("Received value", received_value, "Type:", type(received_value))

                    if expected_value != received_value:
                        print_err(f"Expected '{expected_value}' but got '{received_value}'")
                        exit(1)

                    
            
            """
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
                                parsed_received, parsed_expected = parse_value(cell, expected_table[i][j])
                                
                                print("check_if_same")
                                print("check if same with types", type(parsed_received), type(parsed_expected))
                                if check_if_same(parsed_received, parsed_expected):
                                    print("Test passed")
                                else:
                                    print_err(f"Error in test {test_case['name']}")
                                    print_err(f"Query: {query}")
                                    print_err(f"Expected Result: {expected_result}")
                                    exit(1)
            """
            success_tests += 1

        except Exception as e:
            # is syntax error then skip
            if "SYNTAX_ERROR" in str(e):
                print("Syntax error in query")
                print("Skipping test")
                skip_tests_syntax_err += 1
                continue

            print("Test failed")
            fail_tests += 1
            print_err(f"Error in test {test_case['name']}\n{traceback.format_exc()}")
            print_err(f"Query: {query}")
            print_err(f"Expected Result: {expected_result}")
            print_err(f"Error: {e}")
            exit(1)
    
    
    
print("Total tests:", total_tests, " Success:", success_tests, " Fail:", fail_tests, " Skip:", skip_tests, " Skip Syntax Error:", skip_tests_syntax_err)