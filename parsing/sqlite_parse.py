# this file converts tests to unified format

import os
import json
import re

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
    
    count = 0
    
    with open(log_file, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        current_test = None
        is_query = False
        is_output = False
        
        current_main_test = None
        
        all_tests = []
        
        for line in lines:
            
            # if len(all_tests) > 10:
            #     break
            
            line = line.strip()
            
            # if line starts with ### test/upfrom1.test 45ms (done)
            # then set the main test to the filename
            if line.startswith("### test/"):
                
                
                # if current_main_test is not None then add the current_test to the all_tests
        
                
                current_main_test = line.split()[1].split("/")[-1].split(".")[0]
                #print("Main test: ", current_main_test)
                
            # if line is reset_db
            # then create a new test with query reset_db
            elif line == "reset_db":
                #print("Resetting db command found")
                current_test = {"name": "reset_db", "query": "reset_db", "expected_result": ""}
                is_query = False
                is_output = False
                
                # add the current_test to the all_tests
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
            
            elif not line or line.startswith("#"):
                #if not line:
                    #is_query = False
                    #is_output = False
                continue
            elif line.startswith("----START"):              
                test_name = line.split()[1]
                #print("Test name: ", test_name)
               
                current_test = {"name": test_name, "query": "", "expected_result": ""}
            elif line.startswith("----END"):
                is_query = False
                is_output = False
                
                # add the current_test to the all_tests
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
            # create prefix with count that has 5 digits atleast
            prefix = str(count).zfill(5)
            
            # remove from test any tests with similar name
            #test["tests"] = [dict(t) for t in {tuple(d.items()) for d in test["tests"]}] # todo investigate why some duplicates are there tho
            
            # if any tests contain tointeger or toreal then skip them
            if any("tointeger" in t["query"] or "toreal" in t["query"] for t in test["tests"]):
                print("Skipping test with tointeger or toreal")
                continue
            
            # if any query contains COLLATE then skip them
            if any("COLLATE" in t["query"] for t in test["tests"]):
                print("Skipping test with COLLATE")
                continue
            
            
            cleaned_tests = {
                "name": test["name"],
                "tests": []
            }
            
            has_prior_reset_db = False
            has_only_reset_db = True
            has_any_dollar = False # used for checking if any query contains $ sign -> used for variables
            reset_count = 0
            for t in test["tests"]:
                
                if reset_count > 50:
                    print("Skipping remaining test queries with more than 50 reset_db")
                    continue
                
                if t["query"] == "reset_db":  

                    if has_prior_reset_db:
                        continue
                    
                    has_prior_reset_db = True
                    
                    cleaned_tests["tests"].append({
                        "name": t["name"],
                        "query": t["query"],
                    })
                    
                    reset_count += 1
                    
                    continue
                    
                has_only_reset_db = False
                has_prior_reset_db = False
                
                query = t["query"]
                # split query by ; but now then its inside a string
                statements = re.split(r';(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)', query)

                for statement in statements:
                    
                    # if statement is empty or only whitespace then skip
                    if not statement.strip():
                        continue
                    
                    cleaned_tests["tests"].append({
                        "name": t["name"],
                        "query": statement.strip() + ";",
                    })
                    
                    if "$" in statement:
                        has_any_dollar = True
                        
            if has_any_dollar:
                print("Skipping test with $ sign")
                continue
                    
            if has_only_reset_db:
                print("Skipping test with only reset_db")
                continue
            
            # save the cleaned tests to disk
            with open("input/sqlite/" + prefix + "_" + test["name"] + ".json", "w") as f:
                f.write(json.dumps(cleaned_tests, indent=4))    
            
            count += 1   
            
            # if count > 10:
            #     break
       
     
#parse_duckdb()
parse_sqlite()
