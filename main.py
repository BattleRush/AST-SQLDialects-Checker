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
    
        
# def delete_all_tables(connector):



for file in duck_db_files:
    CURRENT_TEST_FILE = file
    if file.endswith(".json"):
        with open(f"input/duckdb/{file}", "r") as f:
            file_index = duck_db_files.index(file)
            print_debug("##################################")
            print_debug(f"Processing file {file_index} out of {len(duck_db_files)} named {file}")
            # at start of each file, reset database
            # duckdb_connector.execute("DROP TABLE IF EXISTS tbl")
            # duckdb_connector.execute("DROP TABLE IF EXISTS test")
            # duckdb_connector.execute("DROP TABLE IF EXISTS test2")
            # duckdb_connector.execute("DROP TABLE IF EXISTS a")
            # duckdb_connector.execute("DROP TABLE IF EXISTS b")
            # duckdb_connector.execute("DROP TABLE IF EXISTS integers")
            
            # create a new connection
            duckdb_connector.commit()
            duckdb_connector.close()
            duckdb_connector = duckdb.connect()
            
            # delete index named i_index on integers table
            duckdb_connector.execute("DROP INDEX IF EXISTS i_index")
            
            data = json.load(f)
            for query in data:
                print_debug("------------------------------")
                current_query = query["query"]
                
                type1 = query["type"]
                type2 = query["type2"]                
                print_debug(f"[-] Executing query: {current_query} it should succeed: {query['success']} of type {type} and {type2}")
                try:
           
                    result = duckdb_connector.execute(current_query)
                    
                    if type1 == "statement" and type2 == "ok":
                        success_count += 1
                        print("[+] Test passed.")
                        continue
                    
                    # check if the result maches the expected result
                    # if not, write the result to the output folder
                    
                    expected_result = query["expected_result"]
                    result_string = result.fetchall()
                    
                    # split expected result by \n and then by \t and remove empty lines
                    expected_result = expected_result.split("\n")
                    expected_result = [line.split("\t") for line in expected_result if line]
                    
                    
                    # print("Expected: ", expected_result)
                    # print("Got: ", result_string)
                    
                    #check if expected result is 1 or 2D
                    if len(expected_result) == 0:
                        # print("Shape of expected result: ", len(expected_result))
                        # print("Shape of result string: ", len(result_string))
                        
                        if len(result_string) != len(expected_result):
                            failure_count += 1
                            shape_mismatch_count += 1
                            print_err(f"[-] Test failed SHAPE MISMATCH. Expected empty result but got {result_string} for query {current_query} in file {file}")
                        # if length is 0 check if got has also 0 length then set as passed
                        if len(expected_result) == 0:
                            success_count += 1
                            print("[+] Test passed.")
                            continue
                        else:
                            failure_count += 1
                            print_err(f"[-] Test failed. Expected empty result but got {result_string} for query {current_query} in file {file}")
                    else:
                        # print("Shape of expected result: ", len(expected_result), len(expected_result[0]))
                        # print("Shape of result string: ", len(result_string), len(result_string[0]))
                        
                        # if shape is mismatched, then fail the test
                        if len(expected_result) != len(result_string) or len(expected_result[0]) != len(result_string[0]):
                            failure_count += 1
                            shape_mismatch_count += 1
                            print_err(f"[-] Test failed SHAPE MISMATCH. Expected shape {len(expected_result)}x{len(expected_result[0])} but got {len(result_string)}x{len(result_string[0])} for query {current_query} in file {file}")
                    
                    failed = False
                    # go row by row and check if the values are the same
                    for i in range(len(expected_result)):
                        if failed:
                            break
                        for j in range(len(expected_result[i])):
                            expected_value = str(expected_result[i][j])
                            result_value = str(result_string[i][j])
                            
                            # if result value is None, then set it to empty string
                            result_value = result_value.replace("None", "NULL")
                            result_value = result_value.replace("True", "true")
                            result_value = result_value.replace("False", "false")
                            
                            # Conversion issues (eg 1.000000 but got 1)
                            # Detect if expected value is some kind of number
                            if expected_value.count('.') <= 1 and expected_value.replace(".", "").isnumeric() and expected_value != result_value:
                                try:
                                    print_err(f"[~] COMMENCING CASTING of result value {result_value} to expected {expected_value}")
                                    goal_cast = duckdb_connector.execute(f"SELECT TYPEOF({expected_value})").fetchall()[0][0]
                                    
                                    # Take care of decimal rounding errors
                                    # if goal_cast.startswith("DECIMAL") and result_value.count('.') <= 1 and result_value.replace(".", "").isnumeric():
                                    print_err(f"\t[-] Expected value ({expected_value}) is a {goal_cast}.")
                                    # Cast
                                    result_value = duckdb_connector.execute(f"SELECT CAST({result_value} AS {goal_cast})").fetchall()[0][0]
                                    result_value = str(result_value).strip()
                                    print_err(f"\t[-] Value got casted")
                                except Exception as e:
                                    print_err(f"[x] Casting err expected_value='{expected_value}' result_value='{result_value}' goal_cast={goal_cast}\n{traceback.format_exc()}")
                                    failed = True
                                    if expected_value != result_value:
                                        print_err(f"[x] MEGA ERROR: Test failed. Expected: {expected_value} but got {result_value} at row {i} column {j} for query {current_query} in file {file}")
                                        
                                        print_err(f"Expected\n {query['expected_result']}\nResult:\n{result_string}")
                                # finally:
                                    

                                    
                        
                            # if expected_value != result_value:
                                
                                
                            
                            
                            if expected_value != result_value:
                                failure_count += 1
                                print_err(f"[-] Test failed. Expected: {expected_value} but got {result_value} at row {i} column {j} for query {current_query} in file {file}")
                                break
                            
                except Exception as e:
                    print("HANDLING EXCEPTION of file ", file)
                    if type1 == "statement" and type2 == "ok":
                        print_err(f"[-] Test failed stmt. Expected statement to pass but got error for query {current_query} in file {file}:\n{traceback.format_exc()}")
                        
                        failure_count += 1
                        if "read_csv" in current_query:
                            print_debug("Skipping the test because it contains read_csv")
                            continue
                        #raise e
                        continue
                    if type1 == "statement" and type2 == "error":
                        success_count += 1
                        print_debug("[+] Test passed.")
                        continue
                    
                    print(current_query)
                    # if query contains read_csv, then skip the test and mark it as failed
                    if "read_csv" in current_query:
                        print_err(f"[-] Test failed read_csv. Expected statement to pass but got error: {e} for query {current_query} in file {file}")
                        failure_count += 1
                    else:
                        #raise e
                        print_err(f"UNKNOWN Expected statement to pass but got error for query {current_query} in file {file}:\n{traceback.format_exc()}")
                        
                        failure_count += 1
                        unknown_count += 1
                # finally:    
                #     duckdb_connector.close()
                #     duckdb_connector = duckdb.connect()


print("Success count: ", success_count)
print("Failure count: ", failure_count)
print("Unknown count: ", unknown_count)
print("Shape mismatch count: ", shape_mismatch_count)
print("Total tests: ", success_count + failure_count)

# print("[-] Connecting to sqlite ...", end="")
# if not os.path.exists("./dbdata/sqlite"):
#     os.makedirs("./dbdata/sqlite")
# sqlite_connector = sqlite3.connect("./dbdata/sqlite/sqlite.db")
# print(" done.")



