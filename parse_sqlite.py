# this file converts tests to unified format

import os
import json

def parse_sqlite():
    
    log_file = "databases/sqlite/testrunner.log"
    

    # in the log file the tests are structured like this
    # ----START func7-200
    # >>>>
    # SELECT round(ln(5),2), log(100.0), log(100), log(2,'256');
    # <<<<
    # ;;;;
    # 1.61 2.0 2.0 8.0
    # ::::
    # ----END
    
    # open the file and extract the sql query, expected result and the name of the test which is after START
    
    # delete the input/sqlite folder only on linux
    if os.name == "posix":  # Linux
        if os.path.exists("input/sqlite"):
            os.system("rm -rf input/sqlite")
        os.makedirs("input/sqlite")
    elif os.name == "nt":  # Windows
        if os.path.exists("input/sqlite"):
            os.system("rmdir /s /q input\\sqlite")
        os.makedirs("input\\sqlite")

    print("Parsing sqlite tests")
    
    with open(log_file, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        current_test = None
        is_query = False
        is_output = False
        
        current_main_test = None
        
        all_tests = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                #if not line:
                    #is_query = False
                    #is_output = False
                continue
            elif line.startswith("----START"):              
                test_name = line.split()[1]
                #print("Test name: ", test_name)
                
            
                if current_test is not None:
                    # check if all_test contains the current_main_test as name
                    found = False
                    for test in all_tests:
                        if test["name"] == current_main_test:
                            found = True
                            break
                        
                    # check if all_tests contains the current_test as name if yes then add the test to the tests
                    if not found:
                        all_tests.append({"name": current_main_test, "tests": [current_test]})
                    else:
                        for test in all_tests:
                            if test["name"] == current_main_test:
                                test["tests"].append(current_test)
                                break

                # split by - and before this is the main test
                current_main_test = test_name.split("-")[0]

                #print("Test: ", test_name)
               
                current_test = {"name": test_name, "query": "", "expected_result": ""}
            elif line.startswith("----END"):
                is_query = False
                is_output = False
            elif line.startswith(">>>>"):

                is_query = True
            elif line.startswith("<<<<"):
                is_query = False
            elif line.startswith(";;;;"):
                is_output = True
            elif line.startswith("::::"):
                is_output = False
            else:
                if is_query:
                
                    current_test["query"] += line + "\n"
                elif is_output:
                    current_test["expected_result"] += line + "\n"
                else:
                    
                    #raise ValueError(f"Unexpected line: {line}")
                    pass # skip the line

        # save remaining test
        if current_test is not None:
            # check if all_test contains the current_main_test as name
            found = False
            for test in all_tests:
                if test["name"] == current_main_test:
                    found = True
                    break

            if not found:
                all_tests.append({"name": current_main_test, "tests": [current_test]})
            else:
                for test in all_tests:
                    if test["name"] == current_main_test:
                        test["tests"].append(current_test)
                        break
        
        # save all tests in a json file
        for test in all_tests:
            #print("Test: ", test)
            with open("input/sqlite/" + test["name"] + ".json", "w") as f:
                f.write(json.dumps(test, indent=4))                 
     
#parse_duckdb()
parse_sqlite()
