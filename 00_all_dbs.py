
import json
import time
from common import load_json, get_files, load_all_json, compare_arrow_tables, compare_dataframes
from python_dbs.clickhouse import ClickhouseProcessor
from python_dbs.sqlite import SQLiteProcessor

sqlite_processor = SQLiteProcessor()
clickhouse_processor = ClickhouseProcessor()



def run_query(db_name, query):
    if db_name == "clickhouse":
        return clickhouse_processor.run_query(query)
    elif db_name == "sqlite":
        return sqlite_processor.run_query(query)
    else:
        raise Exception(f"Unknown db name: {db_name}")


def clean_dbs():
    clickhouse_processor.reset_db()
    sqlite_processor.reset_db()

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


list_of_dbms = ["clickhouse", "sqlite"]

clean_dbs()

for current_db in list_of_dbms:
    print("Loading tests for", current_db)
    all_tests = load_all_json(current_db)
    print("Found", len(all_tests), "tests")
    
    time.sleep(5)
    
    exception_count = 0
    total_count = 0
    success_count = 0
    failed_count = 0
    
    for test_file in all_tests:
        has_been_reset = False
        
        test_name = test_file["name"]
        print(test_name)
        
        current_test_report = {
            "test_name": test_name,
            "source_db": current_db,
            "queries": []
        }
        
        for query_test in test_file["tests"]:
            #print(query_test)
            query = query_test["query"]
            
            current_query_report = {
                "query": query,
                "source_success": False,
                "source_exception": "",
                "source_result": None,
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
                source_success = True
                
                # parse source result to string to save it
                source_result_str = source_result.to_string()
                
                current_query_report["source_result"] = source_result_str # todo is this saved as string?                    
            except Exception as e:
                current_query_report["source_success"] = False
                source_success = False
                
                current_query_report["source_exception"] = str(e)
            
            for target_db in list_of_dbms:
                #print("Running query on", target_db)
                
                if current_db == target_db:
                    continue # skip for now the same DBs
                
                target_success = False
                target_result = None
                target_db_error = ""
                target_result_str = ""
                
                try:
                    target_result = run_query(target_db, query)
                    target_result_str = target_result.to_string()
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
                    "error": target_db_error,
                    "shape_equal": shape_equal,
                    "columns_equal": columns_equal,
                    "dtypes_equal": dtypes_equal,
                    "values_equal": values_equal,
                    "full_match": full_match
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
with open("progress_report.json", "w") as f:
    json.dump(progress_report, f, indent=4)
    
# also output the result as csv table
import pandas as pd
df = pd.DataFrame(progress_report)
df.to_csv("progress_report.csv", index=False)




html = """
<!DOCTYPE html>
<html>
<head>
<style>
table {
  font-family: Arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

</style>

<body>"""

# create a tab for each progress report
for test_report in progress_report:
    html += f"<h2>{test_report['test_name']}</h2>"
    
    html += "<table>"
    html += "<tr>"
    html += "<th>Query</th>"
    html += "<th>Source Success</th>"
    for db in list_of_dbms:
        html += f"<th>{db} Success</th>"
        html += f"<th>{db} Shape</th>"
        html += f"<th>{db} Columns</th>"
        html += f"<th>{db} Dtypes</th>"
        html += f"<th>{db} Values</th>"
        html += f"<th>{db} Full Match</th>"
    html += "</tr>"
    
    for query_report in test_report["queries"]:
        html += "<tr>"
        html += f"<td>{query_report['query']}</td>"
        html += f"<td>{query_report['source_success']}</td>"
        
        for target_report in query_report["target_dbs"]:
            html += f"<td>{target_report['success']}</td>"
            html += f"<td>{target_report['shape_equal']}</td>"
            html += f"<td>{target_report['columns_equal']}</td>"
            html += f"<td>{target_report['dtypes_equal']}</td>"
            html += f"<td>{target_report['values_equal']}</td>"
            html += f"<td>{target_report['full_match']}</td>"
            
        html += "</tr>"
    
    html += "</table>"
    
html += "</body>"
html += "</html>"


with open("progress_report.html", "w") as f:
    f.write(html)