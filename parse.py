# this file converts tests to unified format

import os
import json

 
def parse_postgresql():
    # check if input/postgresql exists 
    if not os.path.exists("input/postgresql"):
        os.makedirs("input/postgresql")
        
    # go into databases/postgresql/test folder and get every .test file
    
    files = os.listdir("databases/postgresql/test")
    
    # todo
    
    
    # check if input/duckdb exists 
    if not os.path.exists("input/duckdb"):
        os.makedirs("input/duckdb")
        
    # go into databases/duckdb/test folder and get every .test file recursively
    all_tests = []
    
    for root, dirs, files in os.walk("databases/duckdb/test/sql"):
        for file in files:
            if file.endswith(".test"):
                all_tests.append(os.path.join(root, file))
                
    print("Total tests found:", len(all_tests))
    
    #print first test
    #print("First test:", all_tests[0])
    
    success = 0
    fail = 0
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252']  # Add other encodings as needed

    for test in all_tests:
        print("Parsing test ", all_tests.index(test) + 1, " out of ", len(all_tests), ": ", test)
    
        with open(test, 'r', encoding='iso-8859-1') as file:
            test_string = file.read()
        parsed_tests = parse_duckdb_test_cases(test_string)
        
        # if parsed_tests is empty, fail increment
        if not parsed_tests:
            fail += 1
        else:
            success += 1
        
        # save json formatted in input/duckdb folder
        # output file is without databases/duckdb/test/sql and remaining / replace with -
        #print("Output filename:", test)
        output_filename = test.replace("databases/duckdb/test/sql/", "").replace("/", "-")
        #print("Output filename:", output_filename)
        # if file exists, remove it
        if os.path.exists("input/duckdb/" + output_filename + ".json"):
            os.remove("input/duckdb/" + output_filename + ".json")
        
        with open("input/duckdb/" + output_filename + ".json", "w") as f:
            # convert object to json
            tests_json = json.dumps(parsed_tests, indent=4)
            
            f.write(tests_json)
        
    print ("Success:", success, " Fail:", fail)
    #print(parsed_tests)

#parse_duckdb()
#parse_sqlite()
