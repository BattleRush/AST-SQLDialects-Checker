import json
import os
import re

def extract_sql_queries(file_path):
    with open(file_path, 'r', encoding="utf-8", errors='ignore') as file:
        content = file.read()

    # Split content by semicolons ensure the ; is not inside quotes
    statements = re.split(r';(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)', content)
    
    # Remove leading/trailing whitespace from each statement
    statements = [statement.strip() for statement in statements if statement.strip()]
    
    # go trough statements and remove any line that starts with \echo
    cleaned_statements = []
    
    for statement in statements:
        lines = statement.split("\n")
        cleaned_lines = []
        for line in lines:
            if "\\echo" not in line:
                cleaned_lines.append(line)
                
            # if we encounter a \copy <table> <file> get the file
            if "\\copy" in line:
                # for now we skip these
                return []               
                
            
        cleaned_statement = "\n".join(cleaned_lines)
        
        if "$" in cleaned_statement:
            return []
        
        cleaned_statement = cleaned_statement.strip()
        
        # if statement doesnt end with ; then add it
        if not cleaned_statement.endswith(";"):
            cleaned_statement += ";"
        
        cleaned_statements.append(cleaned_statement)
        
    

    print("Returning", len(statements), "statements")
    return statements


def clean_input_folder(database):
    if os.path.exists(f"input/{database}"):
        if os.name == "posix":  # Linux
            os.system(f"rm -rf input/{database}")
        elif os.name == "nt":  # Windows
            os.system(f"rmdir /s /q input\\{database}")
            
    os.makedirs(f"input/{database}")


def parse_postgres():
    main_path = "databases/postgresql/"
        
    clean_input_folder("postgresql")

    # get all .sql files inside main_path recursively

    all_sql_files = []
    for root, dirs, files in os.walk(main_path):
        for file in files:
            if file.endswith(".sql"):
                all_sql_files.append(os.path.join(root, file))
                
    print("First 4 files:", all_sql_files[:4])


    all_tests = []

    # parse each file and extract the sql queries
    for sql_file in all_sql_files:
        test_name = sql_file.split("/")[-1]
        test = {
            "name": test_name,
            "tests": []
        }
        #print("Parsing file", sql_file)
        sql_queries = extract_sql_queries(sql_file)
        
        if len(sql_queries) == 0:
            print("No queries found in", sql_file)
            continue
        
        print("Found", len(sql_queries), "queries")
        print(sql_queries[:2])
        
        tests = []
        for query in sql_queries:
            tests.append({
                "query": query,
                "name": test_name
            })
            
        test["tests"] = tests
        
        all_tests.append(test)
        #print(sql_queries[:2])
        
    #print("First 4 tests:", all_tests[:4])

    count = 0
    # save the parsed tests to disk
    for i, test in enumerate(all_tests):
        test_name = test["name"]
        # temove .sql extension
        test_name = test_name[:-4]
        
        count += 1
        
        prefix = str(count).zfill(5)
        #print("Saving test", test_name)
        with open(f"input/postgresql/{prefix}_{test_name}.json", "w") as f:
            json.dump(test, f, indent=4)


    print("Parsing postgresql tests done")

