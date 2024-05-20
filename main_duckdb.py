import mysql.connector 
import mariadb
import psycopg2
import datetime
import os
import sys
import sqlite3
import duckdb
import json
import pandas as pd
import traceback
import numpy as np
# if not os.path.exists("input"):
#     os.makedirs("input")
    
# if not os.path.exists("output"):
#     os.makedirs("output")


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

DUCKDB_TESTS_PATH = os.path.dirname(os.path.abspath(__file__)) + "/databases/duckdb/test/sql/"
CURRENT_TEST_FILE = None
CURRENT_EXPECTED_VALUE = None
CURRENT_RESULT = None

def print_err(content, **kwargs):
    print(content, file=sys.stderr, **kwargs)
    with open(f"{current_output_folder}/{CURRENT_TEST_FILE}.err.log", "a") as f:
        f.write(content)

def print_debug(content, **kwargs):
    print(content, **kwargs)
    with open(f"{current_output_folder}/{CURRENT_TEST_FILE}.debug.log", "a") as f:
        f.write(content)

def print_all(content, **kwargs):
    print_err(content, **kwargs)
    print_debug(content, **kwargs)


def is_numeric_value(value):
    return value.count('.') <= 1 and value.replace(".", "").isnumeric()

# print("[-] Connecting to mysql ...", end="")
# mysql_connector = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="mysql",
#     port="11001",
#     database="mysql"
# )
# print(" done.")


# print("[-] Connecting to mariadb ... ", end="")
# mariadb_connector = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="mariadb",
#     port=11002,
#     database="mariadb"
# )
# print(" done.")


# print("[-] Connecting to postgresql ...", end="")
# postgres_connector = psycopg2.connect(
#     host="localhost",
#     user="postgres",
#     password="postgres",
#     port="11003"
# )
# print(" done.")

# run this before pip install duckdb --upgrade
print("[-] Connecting to duckdb ...", end="")
duckdb_connector = duckdb.connect()
# go trough input/duckdb and get all the .json files
duck_db_files = os.listdir("input/duckdb")
success_count = 0
failure_count = 0
shape_mismatch_count = 0
unknown_count = 0



def clear_db(connector):
    

    if type(connector) is duckdb.DuckDBPyConnection:  
        # Retrieve database name
        db_name = connector.execute("SELECT current_database();").fetchone()[0]
        print(db_name)    
          
        # Delete all views
        tables = connector.execute(f"SELECT table_name FROM information_schema.tables WHERE table_catalog='{db_name}' and table_type='VIEW';").fetchall()
        if len(tables) > 0:
            print("[-] Clearing views ...")
            for row in tables:
                print(f"\t[-] DROP VIEW IF EXISTS \"{row[0]}\" CASCADE;")
                connector.execute(f"DROP VIEW IF EXISTS \"{row[0]}\" CASCADE;")
    
        #  Delete all tables
        tables = connector.execute("SELECT table_name FROM information_schema.tables WHERE table_catalog='{db_name}' and table_type in ('BASE TABLE', 'LOCAL TEMPORARY');").fetchall()
        if len(tables) > 0:
            print("[-] Clearing tables ...")
            for row in tables:
                print(f"\t[-] DROP TABLE IF EXISTS \"{row[0]}\" CASCADE;")
                connector.execute(f"DROP TABLE IF EXISTS \"{row[0]}\" CASCADE;")
        
        # Delete all schemas
        excluded_schemas = ','.join([f"'{s}'" for s in ["information_schema", "main", "pg_catalog"]])
        tables = connector.execute(f"SELECT schema_name, schema_owner FROM information_schema.schemata WHERE catalog_name='{db_name}' AND schema_name NOT IN ({excluded_schemas})").fetchall()
        if len(tables) > 0:
            print("[-] Clearing tables ...")
            for row in tables:
                print(f"\t[-] DROP SCHEMA IF EXISTS \"{row[0]}\" CASCADE;")
                print(row)
                connector.execute(f"DROP SCHEMA IF EXISTS \"{row[0]}\" CASCADE;")
                
        connector.commit()
    
       

def are_results_equal(expected, actual):
    for i in range(len(expected)):
        for j in range(len(expected[i])):
            expected_value = str(expected[i][j])
            result_value = str(actual[i][j])
            
            # if result value is None, then set it to empty string
            result_value = result_value.replace("None", "NULL")
            result_value = result_value.replace("True", "true")
            result_value = result_value.replace("False", "false")
            
            # Conversion issues (eg 1.000000 but got 1)
            # Detect if expected value is some kind of number
            if  is_numeric_value(expected_value) and is_numeric_value(result_value) and expected_value != result_value:
                try:
                    print_all(f"[~] COMMENCING CASTING of result value {result_value} to expected {expected_value}")
                    goal_cast = duckdb_connector.execute(f"SELECT TYPEOF({expected_value})").fetchall()[0][0]
                    
                    # Take care of decimal rounding errors
                    # if goal_cast.startswith("DECIMAL") and result_value.count('.') <= 1 and result_value.replace(".", "").isnumeric():
                    print_all(f"\t[-] Expected value ({expected_value}) is a {goal_cast}.")
                    # Cast
                    newresult = duckdb_connector.execute(f"SELECT CAST({result_value} AS {goal_cast})").fetchall()[0][0]
                    newresult = str(newresult).strip()
                    result_value = newresult
                    print_all(f"\t[-] Value got casted to {newresult}.")
                except Exception as e:
                    # failed = True
                    print_err(f"[X] CASTING ERROR: Manual casting failed. Expected: {expected_value} but got {result_value} at row {i} column {j} for query {query_current}")
                    print_err(f"Expected\n {query['query_exp_result']}\nResult:\n{actual}")
                    assert False
                
                # if expected_value != result_value:
                #     print_err(f"[X] POST-casting Test failed. Expected: {expected_value} but got {result_value} at ({i},{j}) for query '{query_current}'")
                #     return False
                
                
            if expected_value != result_value:
                print_err(f"[X] Query failed. Expected: {expected_value} but got {result_value} at ({i},{j}) for query '{query_current}'")
                return False
    
    return True


def are_results_same_shape(expected, actual):
    array1 = np.array(expected)
    array2 = np.array(actual)
    return array1.shape == array2.shape

def is_empty_result(result):
    return len(result) == 0



total_failure_count = 0
total_success_count = 0
total_unknown_count = 0
total_count = 0

is_test_skipped = False
is_test_failing = False
is_unknown_error = False


for file in duck_db_files:
    CURRENT_TEST_FILE = file
    
    total_failure_count += is_test_failing
    total_success_count += not is_test_failing
    total_count += not is_test_skipped
    total_unknown_count += is_unknown_error
    
    is_test_failing = False
    is_test_skipped = False
    is_unknown_error = False
    
    if file.endswith(".json"):
        with open(f"input/duckdb/{file}", "r") as f:
            file_index = duck_db_files.index(file)
            print_debug("\n\n##################################")
            print_debug(f"Processing file {file_index} / {len(duck_db_files)} named {file}")
            
            # create a new connection
            duckdb_connector.commit()
            duckdb_connector.close()
            duckdb_connector = duckdb.connect()
            
            duckdb_connector.execute("DROP INDEX IF EXISTS i_index")
            
            data = json.load(f)
            
            
            # Skip files that contain read_csv
            if "read_csv" in "".join([query["query"] for query in data]):
                print_debug(f"Skipping file {file} as it contains instruction 'read_csv'")
                is_test_skipped = True
                continue
            
            
            
            #  Go through every query in the test case
            for query in data:
                print_debug("------------------------------\n")
                
                query_current       = query["query"]
                query_exp_result    = query["expected_result"]
                query_current_type1 = query["type"]
                query_current_type2 = query["type2"]
                query_current_hastosucceed = query['success']
                
                
                
                
                
                try:  
                    print_debug(f"[-] Executing query: '{query_current.strip()}'\n" + \
                                f"Expected to succeed: {query_current_hastosucceed}\n" + \
                                f"Type: {query_current_type1}\n" + \
                                f"Result type: {query_current_type2}\n")

                    result = duckdb_connector.execute(query_current)
                    result_string = result.fetchall()
                    
                    print_debug(f"Expected result: ({type(query_exp_result)}) \n{query_exp_result}\n" + \
                                f"Result: ({type(result_string)})\n{result_string}\n")
                    
                # Handle error when running a query
                except Exception as e:   
                    #  Query was expected to pass
                    if query_current_type1 == "statement" and query_current_type2 == "ok":
                        print_err(f"[-] Unexpected error. Expected statement to pass but got error for query {query_current} in file {file}:\n{traceback.format_exc()}")
                        is_test_failing = True
                        break
                    
                    # Query was expected to fail
                    if query_current_type1 == "statement" and not query_current_hastosucceed and query_current_type2 == "error":
                        print_debug("[+] Test passed. (received error as expected)")
                        is_test_failing = False
                        continue
                    
                    # We dont know what the fuck is going on
                    print_err(f"UNKNOWN Expected statement to pass but got error for query {query_current} in file {file}:\n{traceback.format_exc()}")
                    is_test_failing = True
                    is_unknown_error = True
                    break
               
               
                # QUERY SUCCESSFUL
                
                # Query is expected to just pass
                if query_current_type1 == "statement" and query_current_type2 == "ok":
                    print_debug("[+] Test passed. (query ok as expected)")
                    is_test_failing = False
                    continue
                
                
                
                # check if the result maches the expected result
                # if not, write the result to the output folder
                
                
                
                CURRENT_EXPECTED_VALUE = query_exp_result
                CURRENT_RESULT = result_string
                
                # split expected result by \n and then by \t and remove empty lines
                query_exp_result = query_exp_result.split("\n")
                query_exp_result = [line.split("\t") for line in query_exp_result if line]
                
                
                
                if not are_results_same_shape(query_exp_result, result_string):
                    print_err(f"[-] Test failed SHAPE MISMATCH. Expected shape {len(query_exp_result)}x{len(query_exp_result[0])} but got {len(result_string)}x{len(result_string[0])} for query {query_current}")  
                    is_test_failing = True
                    break
                
                
                if is_empty_result(result_string):
                    print_debug("[+] Query passed. (empty result as expected)")
                    continue
                
                                
                # go row by row and check if the values are the same
                if not are_results_equal(query_exp_result, result_string):
                    print_err(f"[-] Query failed. Result does not match expected result for query")
                    is_test_failing = True
                    break
                else:
                    print_debug("[+] Test passed. (result matches expected result)")
                    is_test_failing = False
                    continue




base_sucess_count = 11828
base_failure_count = 6957
base_unknown_count = 380
base_shape_mismatch_count = 357
base_total_tests = base_sucess_count + base_failure_count
base_pass_rate = base_sucess_count / base_total_tests



print("\nSuccess count: ", success_count, f"( {'+' if (success_count - base_sucess_count) >= 0 else ''}{success_count - base_sucess_count})")
print("Failure count: ", failure_count, f"( {'+' if (failure_count - base_failure_count) >= 0 else ''}{failure_count - base_failure_count})")
print("Unknown count: ", unknown_count, f"( {'+' if (unknown_count - base_unknown_count) >= 0 else ''}{unknown_count - base_unknown_count})")
print("Shape mismatch count: ", shape_mismatch_count, f"( {'+' if (shape_mismatch_count - base_shape_mismatch_count) >= 0 else ''}{shape_mismatch_count - base_shape_mismatch_count})")
print("Pass rate: ", success_count / (success_count + failure_count), f"( {'+' if (success_count / (success_count + failure_count) - base_pass_rate) >= 0 else ''}{success_count / (success_count + failure_count) - base_pass_rate})")
print("Total tests: ", success_count + failure_count, f"( {'+' if (success_count + failure_count - base_total_tests) >= 0 else ''}{success_count + failure_count - base_total_tests})")
