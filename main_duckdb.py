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



run_date_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

ethz_ids = ["kpiskor", "acerfeda"]



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




DUCKDB_TESTS_PATH = os.path.dirname(os.path.abspath(__file__)) + "/databases/duckdb/test/sql/"

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
    
       
def is_floatingpoint_value(value):
    return value.count('.') == 1 and value.replace(".", "").isnumeric()
def is_integer_value(value):
    return value.isnumeric()


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
            if expected_value != result_value and \
                 ((is_integer_value(expected_value) and is_integer_value(result_value)) or \
                 ((is_floatingpoint_value(expected_value) and is_floatingpoint_value(result_value)))): 
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
                    assert False
                
                # if expected_value != result_value:
                #     print_err(f"[X] POST-casting Test failed. Expected: {expected_value} but got {result_value} at ({i},{j}) for query '{query_current}'")
                #     return False
                
                
            if expected_value != result_value:
                print_err(f"[X] Error. Values do not match. Expected: {expected_value} but got {result_value} at ({i},{j}) for query '{query_current}'")
                return False
    
    return True


def are_results_same_shape(expected, actual):
    shape_expected = (len(expected),max([len(r) for r in expected])) if len(expected) > 0 else (0,0) 
    shape_actual   = (len(actual),max([len(r) for r in actual])) if len(actual) > 0 else (0,0)
    
    return shape_expected == shape_actual, shape_expected, shape_actual

def is_empty_result(result):
    return len(result) == 0


DUCKDB_TESTS_PATH = os.path.dirname(os.path.abspath(__file__)) + "/databases/duckdb/test/sql/"
def get_duckdb_testpath(file):
    return os.path.join(DUCKDB_TESTS_PATH + file)



total_failure_count = 0
total_success_count = 0
total_unknown_count = 0
total_count = 0

is_test_skipped = False
is_test_failing = False
is_unknown_error = False


for file in duck_db_files:
    CURRENT_TEST_FILE = file
    
    total_failure_count += not is_test_skipped and is_test_failing
    total_success_count += not is_test_skipped and not is_test_failing
    total_count += not is_test_skipped
    total_unknown_count += is_unknown_error
    
    is_test_failing = False
    is_test_skipped = False
    is_unknown_error = False
    
    if file.endswith(".json"):
        with open(f"input/duckdb/{file}", "r") as f:
            file_index = duck_db_files.index(file)
            print_all("\n\n##################################")
            print_all("##################################\n")
            
            print_all(f"Processing file {file_index} / {len(duck_db_files)}\n{get_duckdb_testpath(file)}")
            
            # create a new connection
            duckdb_connector.commit()
            duckdb_connector.close()
            duckdb_connector = duckdb.connect()
            
            duckdb_connector.execute("DROP INDEX IF EXISTS i_index")
            
            data = json.load(f)
            
            
            #  Go through every query in the test case
            for query in data:
                print_all("------------------------------\n")
                
                query_current       = query["query"]
                query_exp_result    = query["expected_results_table"]
                query_exp_result_string    = query["expected_results"]
                query_current_type1 = query["type1"]
                query_current_type2 = query["type2"]
                query_current_type3 = query["type3"]
                query_current_hastosucceed = query['success']
                
                
                # if query_current == "PRAGMA enable_verification":
                #     print("Ciao")
                
                try:  
                    print_all(f"[-] Executing query: '{query_current.strip()}'\n" + \
                                f"Expected to succeed: {query_current_hastosucceed}\n" + \
                                f"Type: {query_current_type1}\n" + \
                                f"Result type: {query_current_type2}\n")

                    current_result = duckdb_connector.execute(query_current).fetchall()
                    
                    # In the tables returned by duckdb connector each row is a tuple, so we convert it to a list of lists
                    current_result = [list(r) for r in current_result]
                                    
                    print_all(f"Expected result: ({type(query_exp_result_string)}) \n{query_exp_result_string}\n" + \
                              f"Expected result: ({type(query_exp_result)}) \n{query_exp_result}\n" + \
                                f"Result:          ({type(current_result)})   \n{current_result}\n")
                    
                # Handle error when running a query
                except Exception as e:   
                    #  Query was expected to pass
                    if query_current_hastosucceed == True:
                        print_err(f"[-] Error. Expected statement to pass but got error for query {query_current} in file {file}:\n{traceback.format_exc()}")
                        is_test_failing = True
                        break
                    
                    # Query was expected to fail
                    if query_current_type1 == "statement" and query_current_hastosucceed == False:
                        print_debug("[+] Test passed. (received error as expected)")
                        is_test_failing = False
                        continue
                    
                    # 
                    if query_current_type1 == "statement" and query_current_hastosucceed == None:
                        print_debug("[+] Test passed. (received error as expected)")
                        is_test_failing = False
                        continue
                    
                    # We dont know what the fuck is going on
                    print_err(f"UNKNOWN Error: Expected statement to pass but got error for query {query_current} in file {file}:\n{traceback.format_exc()}")
                    is_test_failing = True
                    is_unknown_error = True
                    break
               
               
                # QUERY SUCCESSFUL
                if query_current_type1 == "statement" and query_current_hastosucceed == False:
                        print_err(f"[-] Error. Expected to receive an error but query passed.")
                        is_test_failing = True
                        break
                
                # If query is expected to just pass
                if query_current_type1 == "statement" and query_current_hastosucceed == True:
                    print_debug("[+] Test passed. (query ok as expected)")
                    is_test_failing = False
                    continue
                
                
                # Make sure shape matches
                shape_match, shape_exp, shape_actual = are_results_same_shape(query_exp_result, current_result)
                if not shape_match:
                    print_err(f"[-] Error. Test failed SHAPE MISMATCH. Expected shape {shape_exp} but got {shape_actual} for query {query_current}")  
                    is_test_failing = True
                    break
                
                # If query is expected to return empty result
                if is_empty_result(current_result):
                    print_debug("[+] Query passed. (empty result as expected)")
                    continue
                
                                
                # Check if results are equal
                if not are_results_equal(query_exp_result, current_result):
                    print_err(f"[-] Query failed. Result does not match expected result for query")
                    is_test_failing = True
                    break
                else:
                    print_debug("[+] Test passed. (result matches expected result)")
                    is_test_failing = False
                    continue




base_success_count = 595
base_failure_count = 255
base_unknown_count = 21
base_total_tests = base_success_count + base_failure_count
base_pass_rate = base_success_count / base_total_tests



print("\nSuccess count: ", total_success_count, f"( {'+' if (total_success_count - base_success_count) >= 0 else ''}{total_success_count - base_success_count})")
print("Failure count: ", total_failure_count, f"( {'+' if (total_failure_count - base_failure_count) >= 0 else ''}{total_failure_count - base_failure_count})")
print("Unknown count: ", total_unknown_count, f"( {'+' if (total_unknown_count - base_unknown_count) >= 0 else ''}{total_unknown_count - base_unknown_count})")
print("Pass rate: ", total_success_count / (total_count), f"( {'+' if (total_success_count / (total_count) - base_pass_rate) >= 0 else ''}{total_success_count / (total_count) - base_pass_rate})")
print("Total tests: ", total_count, f"( {'+' if (total_count - base_total_tests) >= 0 else ''}{total_count - base_total_tests})")
