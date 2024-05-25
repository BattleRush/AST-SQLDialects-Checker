
import json
import time
from common import load_json, get_files, load_all_json, compare_arrow_tables, compare_dataframes
#from python_dbs.clickhouse import ClickhouseProcessor
from python_dbs.sqlite import SQLiteProcessor
from python_dbs.postgres import PostgresProcessor
from python_dbs.clickhouse import ClickhouseProcessor
from python_dbs.duckdb import DuckdbProcessor
from python_dbs.clickhouse_postgresql import ClickhousePostgreProcessor
from collections import defaultdict
import subprocess
from subprocess import PIPE
import os


sqlite_processor = SQLiteProcessor()
postgres_processor = PostgresProcessor()
clickhouse_processor = ClickhouseProcessor()
clickhouse_postgresql_processor = None #ClickhousePostgreProcessor()
duckdb_processor = DuckdbProcessor()



def run_query(db_name, query):
    if db_name == "clickhouse":
        return clickhouse_processor.run_query(query)
    elif db_name == "sqlite":
        return sqlite_processor.run_query(query)
    elif db_name == "postgresql":
        return postgres_processor.run_query(query)
    elif db_name == "duckdb":
        return duckdb_processor.run_query(query)
    elif db_name == "clickhouse_postgresql":
        return clickhouse_postgresql_processor.run_query(query)
    else:
        raise Exception(f"Unknown db name: {db_name}")


def clean_dbs():
    #clickhouse_processor.reset_db()
    sqlite_processor.reset_db()
    postgres_processor.reset_db()
    duckdb_processor.reset_db()
    clickhouse_processor.reset_db()
    abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./docker/")

    shell_command = f"""
cd docker
docker compose down -t 0 -v
docker compose up -d
"""

    os.system(shell_command)
    #subprocess.run(shell_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=PIPE)

    time.sleep(2)


# create a table of the progress report
# we will have the following columns:
# source_db, target_db, test_name, query, success_reference, success_test, result_match
# source db is the db from which the query iriginated
# target db is the db to which the query was run
# test_name is the name of the test
# query is the query that was run
# success_reference if the query ran successfully on the reference db from which the query originated
# success_test if the query ran successfully on the target db
# result_match if the result of the query on the reference db and the target db match

progress_report = []


list_of_dbms = ["postgresql", "sqlite", "clickhouse", "duckdb"]

clean_dbs()

skip = 0
take = 1000

for current_db in list_of_dbms:
    print("Loading tests for", current_db)
    all_tests = load_all_json(current_db, True)
    print("Found", len(all_tests), "tests")
    
    time.sleep(1)
    
    exception_count = 0
    total_count = 0
    success_count = 0
    failed_count = 0
    
    index = 0
    
    for test_file in all_tests:

        has_been_reset = False
        
        test_name = test_file["name"]
        index += 1
        
        if index < skip or index > skip + take:
            continue
        
        clean_dbs()
        print(f"Running test {test_name} number {index} out of {len(all_tests)} from current_db {current_db}")
        
        current_test_report = {
            "test_name": test_name,
            "source_db": current_db,
            "queries": []
        }
        
        for query_test in test_file["tests"]:
            query = query_test["query"]
            
            current_query_report = {
                "query": query,
                "source_success": False,
                "source_exception": "",
                "source_result": None,
                "source_shape": None,
                "source_result_html": "",
                "target_dbs": []
            }
            
            # if query reset_db skip for now
            if query.lower().strip() == "reset_db":
                if has_been_reset:
                    continue
                
                clean_dbs()
                has_been_reset = True
                continue
        
            has_been_reset = False
            
    
            
            source_success = False
            source_result = None
            # Source Test
            try:
                source_result = run_query(current_db, query)
                
                current_query_report["source_success"] = True
                current_query_report["source_shape"] = source_result.shape if source_result is not None else None
                source_success = True
                
                # parse source result to string to save it
                if source_result is not None:
                    source_result_str = source_result.to_string()
                    current_query_report["source_result_html"] = source_result.to_html()
                else:
                    source_result_str = ""
                
                current_query_report["source_result"] = source_result_str # todo is this saved as string?                    
            except Exception as e:
                current_query_report["source_success"] = False
                source_success = False
            
                current_query_report["source_exception"] = str(e)
            
            for target_db in list_of_dbms:
                #print("Running query on", target_db)
                
                if current_db == target_db:
                    continue # skip for now the same DBs
                
                # it clickhouse is the source db check if the query contains create table
                # and replace with create temporary table
                # this is a workaround for many tests from other dbs failing in clickhouse
                if current_db == "clickhouse":
                    if "CREATE TABLE" in query:
                        query = query.replace("CREATE TABLE", "CREATE TEMPORARY TABLE")
                
                target_success = False
                target_result = None
                target_db_error = ""
                target_result_str = ""
                target_shape = None
                target_result_html = ""
                
                try:
                    target_result = run_query(target_db, query)
                    if target_result is not None:
                        target_result_str = target_result.to_string()
                        target_result_html = target_result.to_html()                        
                    else:
                        target_result_str = ""
                    target_shape = target_result.shape if target_result is not None else None
                    target_success = True
                except Exception as e:
                    target_success = False
                    target_result = None
                    target_db_error = str(e)
            
                
                shape_equal, columns_equal, dtypes_equal, values_equal = compare_dataframes(source_result, target_result)
                
                full_match = shape_equal and columns_equal and dtypes_equal and values_equal
                
                            
                current_target_report = {
                    "db": target_db,
                    "success": target_success,
                    "result": target_result_str,
                    "result_html": target_result_html,
                    "error": target_db_error,
                    "shape_equal": shape_equal,
                    "columns_equal": columns_equal,
                    "dtypes_equal": dtypes_equal,
                    "values_equal": values_equal,
                    "full_match": full_match,
                    "shape": target_shape
                }
                
                current_query_report["target_dbs"].append(current_target_report)
                    
                # if target_db == current_db:
                #     continue # for now skin as sometimes query are DELETE IF EXISTS; then CREATE, but if we do DELETE, DELETE, CREATE, CREATE then the results will not match as the last query will crash    
                
                # # if target_db is the same as the source_db and results dont match or one has error but the other does not
                # if target_db == current_db and (current_query_report["result_match"] == False or (current_query_report["success_reference"] != current_query_report["success_test"])):
                #     print("Error: Results do not match")
                #     print("Name:", current_query_report["test_name"])
                #     print("Reference:", current_query_report["success_reference"])
                #     print("Test:", current_query_report["success_test"])
                #     print("Match:", current_query_report["result_match"])
                #     exit(1)
                
            current_test_report["queries"].append(current_query_report)
            
        
        progress_report.append(current_test_report)              
            
print("All tests passed")

# save the progress report to a file
with open(f"output/progress_report_{skip}_{skip + take}.json", "w") as f:
    json.dump(progress_report, f, indent=4)
    
# also output the result as csv table
# import pandas as pd
# df = pd.DataFrame(progress_report)
# df.to_csv("progress_report.csv", index=False)

exit(1) # we dont generate anymore the html report here for this run generate_html.py
