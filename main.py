import mysql.connector 
import mariadb
import psycopg2
import datetime
import os
import sqlite3
import duckdb
import json
import pandas as pd

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

for file in duck_db_files:
    if file.endswith(".json"):
        with open(f"input/duckdb/{file}", "r") as f:
            file_index = duck_db_files.index(file)
            print("##################################3")
            print("Processing file ", file_index, " out of ", len(duck_db_files), " named ", file)
            # at start of each file, reset database
            # duckdb_connector.execute("DROP TABLE IF EXISTS tbl")
            # duckdb_connector.execute("DROP TABLE IF EXISTS test")
            # duckdb_connector.execute("DROP TABLE IF EXISTS test2")
            # duckdb_connector.execute("DROP TABLE IF EXISTS a")
            # duckdb_connector.execute("DROP TABLE IF EXISTS b")
            # duckdb_connector.execute("DROP TABLE IF EXISTS integers")
            
            # create a new connection
            duckdb_connector = duckdb.connect()
            
            # delete index named i_index on integers table
            duckdb_connector.execute("DROP INDEX IF EXISTS i_index")
            
            data = json.load(f)
            for query in data:
                print("------------------------------")
                current_query = query["query"]
                
                type = query["type"]
                type2 = query["type2"]                
                print(f"[-] Executing query: {current_query} it should succed: {query['success']} of type {type} and {type2}")
                try:
           
                    result = duckdb_connector.execute(current_query)
                    
                    if type == "statement" and type2 == "ok":
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
                    
                    
                    print("Expected: ", expected_result)
                    print("Got: ", result_string)
                    
                    #check if expected result is 1 or 2D
                    if len(expected_result) == 0:
                        print("Shape of expected result: ", len(expected_result))
                        print("Shape of result string: ", len(result_string))
                        
                        if len(result_string) != len(expected_result):
                            failure_count += 1
                            shape_mismatch_count += 1
                            print(f"[-] Test failed SHAPE MISMATCH. Expected empty result but got {result_string} for query {current_query} in file {file}")
                            with open(f"{current_output_folder}/{file}.log", "a") as f:
                                f.write(f"Expected empty result but got {result_string} for query {current_query} in file {file}\n")
                            continue
                        
                        # if length is 0 check if got has also 0 length then set as passed
                        if len(expected_result) == 0:
                            success_count += 1
                            print("[+] Test passed.")
                            continue
                        else:
                            failure_count += 1
                            print(f"[-] Test failed. Expected empty result but got {result_string} for query {current_query} in file {file}")
                            with open(f"{current_output_folder}/{file}.log", "a") as f:
                                f.write(f"Expected empty result but got {result_string} for query {current_query} in file {file}\n")
                            continue
                        
                    else:
                        print("Shape of expected result: ", len(expected_result), len(expected_result[0]))
                        print("Shape of result string: ", len(result_string), len(result_string[0]))
                        
                        # if shape is mismatched, then fail the test
                        if len(expected_result) != len(result_string) or len(expected_result[0]) != len(result_string[0]):
                            failure_count += 1
                            shape_mismatch_count += 1
                            print(f"[-] Test failed SHAPE MISMATCH. Expected shape {len(expected_result)}x{len(expected_result[0])} but got {len(result_string)}x{len(result_string[0])} for query {current_query} in file {file}")
                            with open(f"{current_output_folder}/{file}.log", "a") as f:
                                f.write(f"Expected shape {len(expected_result)}x{len(expected_result[0])} but got {len(result_string)}x{len(result_string[0])} for query {current_query} in file {file}\n")
                            continue
                    
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
                            
                            if expected_value != result_value:
                                failure_count += 1
                                print(f"[-] Test failed. Expected: {expected_value} but got {result_value} at row {i} column {j} for query {current_query} in file {file}")
                                failed = True
                                
                                # write log file
                                with open(f"{current_output_folder}/{file}.log", "a") as f:
                                    f.write(f"Expected: {expected_value} but got {result_value} at row {i} column {j} for query {current_query} in file {file} \n")

                                break
                            
                except Exception as e:
                    print("HANDLING EXCEPTION of file ", file)
                    if type == "statement" and type2 == "ok":
                        print(f"[-] Test failed stmt. Expected statement to pass but got error: {e} for query {current_query} in file {file}")
                        failure_count += 1
                        with open(f"{current_output_folder}/{file}.log", "a") as f:
                            f.write(f"statement ok Expected statement to pass but got error: {e} for query {current_query} in file {file} \n")
                        if "read_csv" in current_query:
                            print("Skipping the test because it contains read_csv")
                            continue
                        #raise e
                        continue
                    if type == "statement" and type2 == "error":
                        success_count += 1
                        print("[+] Test passed.")
                        continue
                    
                    print(current_query)
                    # if query contains read_csv, then skip the test and mark it as failed
                    if "read_csv" in current_query:
                        print(f"[-] Test failed ERR. Expected statement to pass but got error: {e} for query {current_query} in file {file}")
                        failure_count += 1
                        with open(f"{current_output_folder}/{file}.log", "a") as f:
                            f.write(f"non read csv Expected statement to pass but got error: {e} for query {current_query} in file {file} \n")
                        continue
                    else:
                        #raise e
                        with open(f"{current_output_folder}/{file}.log", "a") as f:
                            f.write(f"UNKNOWN Expected statement to pass but got error: {e} for query {current_query} in file {file} \n")
                        failure_count += 1
                        unknown_count += 1

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



