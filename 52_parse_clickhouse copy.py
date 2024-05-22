# this file converts tests to unified format

import os
import json
import chardet
import clickhouse_connect


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
    client = clickhouse_connect.get_client(host='localhost', username='default', password='passwordAST1')

    # go only into 0_stateless
    # the folder contains multiple folder seek all files in nthe .sql file we have the query and in the reference file we have the expected result
    for root, dirs, files in os.walk(test_base_dir + "/0_stateless"):
        for file in files:
            #print("Parsing file", file)
            if file.endswith(".sql"):
                query_file = os.path.join(root, file)
                reference_file = os.path.join(root, file.replace(".sql", ".reference"))
                # Detect the encoding of the file

                with open(query_file, 'r', encoding="utf-8", errors='ignore') as qfile:
                    query = qfile.read()
                    
                # if query contains reinterpretAsString
                if "reinterpretAsString" in query:
                    print("Encountered reinterpretAsString in", query)
                    print("Encoding is", "utf-8")
                    print("File is", query_file)


                # if the reference file does not exist then skip the test
                if not os.path.exists(reference_file):
                    continue

                # if query starts with -- then skip the test
                #if query.startswith("--"):
                #    continue

                # if the query contains more than one ; then skip the test
                #if query.count(";") > 1:
                #    continue

                with open(reference_file, 'r', encoding="utf-8", errors='ignore') as rfile:
                    expected_result = rfile.read()

                expected_result_lines = expected_result.split("\n")
                table = []
                for row in expected_result_lines:
                    # if row is empty then skip it
                    if not row:
                        continue
                    
                    table.append(row.split("\t"))

                    
                # add the test to the all_tests
                all_tests.append({
                    "name": file,
                    "tests": [{
                        "query": query,
                        "expected_result": expected_result,
                        "name": file,
                        "expected_result_table": table
                    }]
                })
                
                count += 1
        
    # write the all_tests to file for each test
    
    test_count = 0
    for test in all_tests:
        #print ("Writing test", test["name"])
        output_filename = test["name"].replace(".sql", "")
        # save file in utf-8
        with open("input/" + database_name + "/" + output_filename + ".json", "w", encoding="utf-8") as f:
            json.dump(test, f, indent=4)
            
        test_count += 1
        
        if test_count > 100:
            break
       
     
parse_clickhouse()
