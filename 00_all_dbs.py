
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

# reset all dbs
for db in list_of_dbms:
    print("Resetting", db)
    if db == "clickhouse":
        clickhouse_processor.reset_db()
    elif db == "sqlite":
        sqlite_processor.reset_db()
    else:
        raise Exception(f"Unknown db name: {db}")

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
        print(test_file["name"])
        has_been_reset = False
        
        for query_test in test_file["tests"]:
            #print(query_test)
            name = query_test["name"]
            print(" Query Name:", name)
            query = query_test["query"]
            
            # if query reset_db skip for now
            if query.lower().strip() == "reset_db":
                continue
        
            #print("=================================")
            #print(f"Processing {query_test}")
            
            #print("Query:", query)
            
            # split query by ; and run each query
            #print("Splitting query")
            queries = query.split(";")
            
            for q in queries:
                
                
                # if q = reset_db then reset the db
                if q.strip().lower() == "reset_db":
                    if has_been_reset:
                        continue # skip if the db has already been reset
                    
                    has_been_reset = True
                    if current_db == "clickhouse":
                        clickhouse_processor.reset_db()
                    elif current_db == "sqlite":
                        sqlite_processor.reset_db()
                    else:
                        raise Exception(f"Unknown db name: {current_db}")
                    continue
                
                has_been_reset = False
                
                # current_query_report = {
                #     "source_db": current_db,
                #     "target_db": "",
                #     "test_name": name,
                #     "query": q,
                #     "success_reference": False,
                #     "success_test": False,
                #     "result_match": False,
                #     "exception_reference": "",
                #     "exception_test": ""
                # }
                
                #print("Query [Part]:", q)
                try:
                    for target_db in list_of_dbms:
                        #print("Running query on", target_db)
                        
                        if current_db == target_db:
                            continue # skip for now the same DBs
                        
                        current_query_report = {
                            "source_db": current_db,
                            "target_db": target_db,
                            "test_name": name,
                            "query": q,
                            "success_reference": False,
                            "success_test": False,
                            "result_match": False,
                            "exception_reference": "",
                            "exception_test": ""
                        }
                        
                        # Reference Test
                        try:
                            result_reference = run_query(current_db, q)
                            #print("Result reference:", result_reference)
                            current_query_report["success_reference"] = True
                            
                        except Exception as e:
                            current_query_report["success_reference"] = False
                            current_query_report["exception_reference"] = str(e)
                            #print(f"Exception: {e}")
                            
                        # Target Test
                        try:
                            result_received = run_query(target_db, q)
                            #print("Result received:", result_received)
                            current_query_report["success_test"] = True
                        except Exception as e:
                            current_query_report["success_test"] = False
                            current_query_report["exception_test"] = str(e)
                            #print(f"Exception: {e}")
                            
                        if current_query_report["success_reference"] and current_query_report["success_test"]:
                            is_same = compare_dataframes(result_reference, result_received)
                            
                            if is_same:
                                #print("Results are the same")
                                current_query_report["result_match"] = True
                            else:
                                #print("Results are different")
                                current_query_report["result_match"] = False
                            
                        if target_db == current_db:
                            continue # for now skin as sometimes query are DELETE IF EXISTS; then CREATE, but if we do DELETE, DELETE, CREATE, CREATE then the results will not match as the last query will crash    
                        
                        # if target_db is the same as the source_db and results dont match or one has error but the other does not
                        if target_db == current_db and (current_query_report["result_match"] == False or (current_query_report["success_reference"] != current_query_report["success_test"])):
                            print("Error: Results do not match")
                            print("Name:", current_query_report["test_name"])
                            print("Reference:", current_query_report["success_reference"])
                            print("Test:", current_query_report["success_test"])
                            print("Match:", current_query_report["result_match"])
                            exit(1)
                        
                        progress_report.append(current_query_report)                  
                 
                except Exception as e:
                    print(f"Exception: {e}")
                    exit(1)
                    exception_count += 1
                    
                
                total_count += 1
                
            
            #print("=================================")
        
    print(f"Total: {total_count}, Success: {success_count}, Failed: {failed_count}, Exception: {exception_count}")

print("All tests passed")

# save the progress report to a file
with open("progress_report.json", "w") as f:
    json.dump(progress_report, f, indent=4)
    
# also output the result as csv table
import pandas as pd
df = pd.DataFrame(progress_report)
df.to_csv("progress_report.csv", index=False)


# can you generate a html file with the output
# if both tests are successful but the results dont match then make the table line in light yellow, if they do match then make it in light green
# if one of the tests failed then make the line light red

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

html += "<table>"

# make test name column max 150px wide
# make the query column max 300px wide


html += "<tr>"
html += "<th>Source DB</th>"
html += "<th>Target DB</th>"
html += "<th>Test Name</th>"
html += "<th style='max-width: 300px;'>Query</th>"
html += "<th>Success Reference</th>"
html += "<th>Success Test</th>"
html += "<th>Result Match</th>"

# for the 2 exception columns make them 50px wide but only write Exception if there is an exception with a tooltip of the exception
html += "<th style='max-width: 50px;'>Exception Reference</th>"
html += "<th style='max-width: 50px;'>Exception Test</th>"

html += "</tr>"

for row in progress_report:
    
    row_color = ""
    if row["success_reference"] and row["success_test"] and not row["result_match"]:
        row_color = "background-color: #FFFFE0;"
    elif row["success_reference"] and row["success_test"] and row["result_match"]:
        row_color = "background-color: #90EE90;"
    elif not row["success_reference"] or not row["success_test"]:
        row_color = "background-color: #FFA07A;"
        
    
    html += "<tr style='" + row_color + "'>"
    html += f"<td>{row['source_db']}</td>"
    html += f"<td>{row['target_db']}</td>"
    # ensure sting is broken if too long
    html += f"<td>{row['test_name']}</td>"
    html += f"<td style='max-width: 300px;'>{row['query']}</td>"
    html += f"<td>{row['success_reference']}</td>"
    html += f"<td>{row['success_test']}</td>"
    html += f"<td>{row['result_match']}</td>"
    
    if row["exception_reference"]:
        html += f"<td style='max-width: 300px;'>{row['exception_reference']}</td>"
    else:
        html += "<td></td>"
        
    if row["exception_test"]:
        html += f"<td style='max-width: 300px;'>{row['exception_test']}</td>"
    else:
        html += "<td></td>"
    html += "</tr>"
    
html += "</table>"
html += "</body>"
html += "</html>"

with open("progress_report.html", "w") as f:
    f.write(html)