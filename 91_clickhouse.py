
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
        name = test_case["name"].replace(".sql", "")
        query = test_case["query"]

        df = client.query_df(query)
        
        # save df as binary array
        binary = df.to_parquet()
        print(binary)
        
        test_case["df"] = binary
        

        
        with open(f"input/clickhouse/{name}.json", "w") as f:
            json.dump(test, f, indent=4)
        
    
    
