# this file converts tests to unified format

import os
import json
import chardet
import clickhouse_connect
import pandas as pd


def parse_clickhouse():
    
    database_name = "clickhouse"
   
    # delete the input/sqlite folder only on linux
    if os.name == "posix":  # Linux
        if os.path.exists("input/" + database_name):
            os.system("rm -rf input/" + database_name)
        os.makedirs("input/" + database_name)
    elif os.name == "nt":  # Windows
        if os.path.exists("input/" + database_name):
            os.system("rmdir /s /q input\\" + database_name)
        os.makedirs("input\\" + database_name)

    print("Parsing " + database_name + " tests")
    
    count = 0

    test_base_dir = "databases/" + database_name + "/tests/queries"
    
    all_tests = []
    #client = clickhouse_connect.get_client(host='localhost', username='default', password='passwordAST1')

    # go only into 0_stateless
    # the folder contains multiple folder seek all files in nthe .sql file we have the query and in the reference file we have the expected result
    for root, dirs, files in os.walk(test_base_dir + "/0_stateless"):
        for file in files:
            #print("Parsing file", file)
            if file.endswith(".sql"):
                query_file = os.path.join(root, file)
                # Detect the encoding of the file

                with open(query_file, 'r', encoding="utf-8", errors='ignore') as qfile:
                    query = qfile.read()
                    
                #print(file)
                #print(query)
                    
                
                #query_result = client.execute(query)
                #df = pd.DataFrame(query_result, columns=[x.name for x in query_result])
                #df = client.query_df(query)
                
                #print(df)
                
                #exit

                queries = query.split(";")
                
                # remove empty queries or that are only whitespace or newlines
                queries = [q for q in queries if q.strip()]
                
                tests = []
                for q in queries:
                    tests.append({
                        "query": q + ";",
                        "name": file
                    })
                    
                # add the test to the all_tests
                all_tests.append({
                    "name": file,
                    "tests": tests
                })
                
                count += 1
        
    # write the all_tests to file for each test
    
    test_count = 0
    count = 0
    for test in all_tests:
        #print ("Writing test", test["name"])
        output_filename = test["name"].replace(".sql", "")
        
        # if name contains crash or fail skip
        
        if "crash" in output_filename or "fail" in output_filename or "overflow" in output_filename:
            print("Skipping", output_filename)
            continue
        
        count += 1
        prefix = str(count).zfill(5)
        #print("Saving test", test_name)
        with open(f"input/{database_name}/{prefix}_{output_filename}.json", "w") as f:
            json.dump(test, f, indent=4)

            
        test_count += 1
       
     
parse_clickhouse()
