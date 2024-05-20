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




all_tests = load_all_json("sqlite")

print("found", len(all_tests), "tests")

count = 0
total_tests = 0
success_tests = 0
fail_tests = 0
skip_tests = 0

    
for test in all_tests:
    
    
    # check if test.db exists and delete it
    if os.path.exists("test.db"):
        os.remove("test.db")
        
    # delete test2.db and test3.db
    if os.path.exists("test2.db"):
        os.remove("test2.db")
        
    if os.path.exists("test3.db"):
        os.remove("test3.db")
        
    # make connection to sqlite db
    conn = sqlite3.connect("test.db")
    c = conn.cursor()

    print("Running test: ", test["name"], " number ", count, " out of ", len(all_tests))
    count += 1
    
    for testInfo in test["tests"]:
        query = testInfo["query"]
        expected_result = testInfo["expected_result"]
        name = testInfo["name"]
        
        # if query is reset_db then close conn and open new one
        if query == "reset_db":
            print("Resetting db")
            conn.close()

            # check if test.db exists and delete it
            if os.path.exists("test.db"):
                os.remove("test.db")
                
            # delete test2.db and test3.db
            if os.path.exists("test2.db"):
                os.remove("test2.db")
                
            if os.path.exists("test3.db"):
                os.remove("test3.db")
            
            conn = sqlite3.connect("test.db")
            c = conn.cursor()
            continue
        
        #print("Running query", name)
        #print("Query:", query)
        
        try:

            # if query contains atlest 2 ; 
            if query.count(";") > 1:
                c.executescript(query)
                # we assume for now these are larger queries to setup stuff
                success_tests += 1
            else:
                
                # if query contains tointeger then skip
                if "tointeger" in query or "toreal" in query:
                    skip_tests += 1
                    continue
                
                # if BEGIN IMMEDIATE is in query then skip or COMMIT
                if "BEGIN IMMEDIATE" in query or "COMMIT" in query:
                    skip_tests += 1
                    continue
                
                
                c.execute(query)
                result = c.fetchall()
                #print("Result:", result)
                #print("Expected result:", expected_result)
                
                if result == expected_result:
                    #print("Test passed")
                    success_tests += 1
                else:
                    fail_tests += 1
                
            
        except Exception as e:
            print("Failed main test:", test["name"])
            print("Failed test:", name)
            print("Running query:", query)
            
            print("Exception:", e)
            print_err(f"Exception: {e}\n")
            print_err(traceback.format_exc())
            print_err("\n")
            
            exit(1)
            
            fail_tests += 1
            
    total_tests += len(test["tests"])
    
    conn.close()
    
    # check if test.db exists and delete it
    if os.path.exists("test.db"):
        os.remove("test.db")
        
    # delete test2.db and test3.db
    if os.path.exists("test2.db"):
        os.remove("test2.db")
        
    if os.path.exists("test3.db"):
        os.remove("test3.db")
    
print("Total tests:", total_tests, " Success:", success_tests, " Fail:", fail_tests, " Skip:", skip_tests)