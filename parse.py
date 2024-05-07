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
    
    # delete the input/sqlite folder
    if os.path.exists("input/sqlite"):
        os.system("rm -rf input/sqlite")
        
    # create the input/sqlite folder
    os.makedirs("input/sqlite")
    
    with open(log_file, 'r') as file:
        lines = file.readlines()
        current_test = None
        is_query = False
        is_output = False
        
        current_main_test = None
        
        all_tests = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                if not line:
                    is_query = False
                    is_output = False
                continue
            elif line.startswith("----START"):              
                test_name = line.split()[1]
                #print("Test name: ", test_name)
                
                # split by - and before this is the main test
                current_main_test = test_name.split("-")[0]
            
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
                
                current_test = {"name": line.split()[1], "query": "", "expected_result": ""}
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
            print("Test: ", test)
            with open("input/sqlite/" + test["name"] + ".json", "w") as f:
                f.write(json.dumps(test, indent=4))                 
                        
def parse_postgresql():
    # check if input/postgresql exists 
    if not os.path.exists("input/postgresql"):
        os.makedirs("input/postgresql")
        
    # go into databases/postgresql/test folder and get every .test file
    
    files = os.listdir("databases/postgresql/test")
    
    # todo
    
    
    
def parse_duckdb_test_cases(test_string):
    tests = []
    current_test = None
    
    is_query = False
    is_output = False

    lines = test_string.split("\n")
    line_index = -1
    for line in lines:
        #print("Line: ", line_index, " has the length of ", len(line))
        line_index += 1
        
        # if line contains read_csv then skip the test
        if "read_csv" in line:
            return []
        
        if "data/csv/" in line:
            return [] # skip for now
        
        if ".csv" in line:
            return []
        
        if "parquet_scan" in line:
            return []
        
        if "__TEST_DIR__" in line:
            return []
        
        #line = line.strip()
        if not line or line.startswith("#"):
            if not line: # sometimes output has commends wtf databases/duckdb/test/sql/copy/csv/csv_null_padding.test
                #print(len(line), " at line ", line_index)
                is_query = False
                is_output = False # ensure no output stats with #
            continue
        elif line.startswith("require"):
            # no idea what to do with it for example require excel
            continue
        elif line.startswith("load"):
            # this test requires a load from file skip this test
            # TODO log this in the future
            return []
        elif line.startswith("set"):
            # TODO what to do with this databases/duckdb/test/sql/copy/parquet/parquet_glob_s3.test
            return []
        elif line.startswith("sleep"): # sleep 1 second
            continue
        elif line.startswith("concurrentloop"): #concurrentloop i 1 100
            return []
        elif line.startswith("unzip"): # unzip data/storage/test.db.gz __TEST_DIR__/test.db
            return []
        elif line.endswith("pg_attribute"):
            return [] # skip these tests as they return nothing
        elif line.endswith("nosort key"):
            return []
        elif line.startswith("loop") or line.startswith("foreach"):
            # TODO handle loops
            #loop i 1 11

# statement ok
# UPDATE integers SET i=${i}+1 WHERE i=${i};

# query I
# SELECT COUNT(*) FROM (SELECT * FROM integers WHERE i > 0 EXCEPT SELECT ${i} + 1) t1;
# ----
# 0

# endloop

            return []
        # if line is mode skip just continue and TODO handle better
        if line.startswith("mode"):
            continue
        
        # todo what the number after QUERY means like query I, query II
        elif line.startswith("query") or line.startswith("statement"):
            if current_test:
                tests.append(current_test)
                
            # todo success
            current_test = {"type": line.split()[0], "query": "", "expected_result": "", "success": None}
            current_test["type2"] = line.split()[1] if len(line.split()) > 1 else None
            
            # if statement ok then put success to true
            if current_test["type"] == "statement" and current_test["type2"] == "ok":
                current_test["success"] = True
            else:
                current_test["success"] = False
                
            # if query then put success to true
            if current_test["type"] == "query":
                current_test["success"] = True
            
            is_query = True
            is_output = False
        elif line.startswith("----"):
            is_query = False
            is_output = True
        else:
            if is_query:
                current_test["query"] += line + "\n"
            elif is_output:
                # if line starts with # skip it
                if line.startswith("#"):
                    continue
                current_test["expected_result"] += line + "\n"
            else:
                raise ValueError(f"Unexpected line ({line_index}) Is Query: {is_query} Is Output: {is_output} Line: {line}")

    if current_test:
        tests.append(current_test)

    return tests
    
def parse_duckdb():
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
parse_sqlite()
