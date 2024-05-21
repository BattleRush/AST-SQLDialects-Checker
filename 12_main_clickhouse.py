
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
execption_tests = 0

client = clickhouse_connect.get_client(host='localhost', username='default', password='passwordAST1')


# run select 1 to check if the connection is working
print("Running select 1")
result = client.query("SELECT 1")
print("Result:", result)

for test in all_tests:
    for test_case in test["tests"]:
        query = test_case["query"]

        #To add new test, create a `.sql` or `.sh` file in `queries/0_stateless` directory, check it manually and then generate `.reference` file in the following way: `clickhouse-client --multiquery < 00000_test.sql > 00000_test.reference` or `./00000_test.sh > ./00000_test.reference`.

        # write the current query to a temp file
        with open("temp.sql", "w") as f:
            f.write(query)

        # run the query
        print("Running test: ", test["name"], " number ", count, " out of ", len(all_tests))

        try:
            command = f"clickhouse-client --user default --password passwordAST1 --multiquery < temp.sql > temp.reference"
            # get response from running the command with 10 second timeout
            result = os.system(command)
            
            print("Result:", result)

            if(result != 0):
                print("Syntax error in the query")
                skip_tests_syntax_err += 1
                continue

            # read the reference file
            with open("temp.reference", "r") as f:
                received_result = f.read()

            expected_result = test_case["expected_result"]

            # compare the results
            if received_result == expected_result:
                print("Test Passed")
                success_tests += 1
            else:

                print ("-----------------")
                print(received_result)
                print ("-----------------")
            
                print("Test Failed")
                fail_tests += 1
                #exit(1)
        except Exception as e:
            print ("-----------------")
            print(str(e))
            print ("-----------------")
            # if db exeption then skip the test
            if "DB::Exception" in str(e):
                print("Skipping test due to DB::Exception")
                skip_tests += 1
                count += 1
                continue

            print("Test Failed exception")
            print(e)
            execption_tests += 1
            

        count += 1
    
    
print("Total tests:", total_tests, " Success:", success_tests, " Fail:", fail_tests, " Skip:", skip_tests, " Skip Syntax Error:", skip_tests_syntax_err, " Exception Tests:", execption_tests)