import json
import os
import re

def extract_sql_queries(file_path):
    with open(file_path, 'r', encoding="utf-8", errors='ignore') as file:
        content = file.read()

    # Split content by semicolons
    statements = content.split(';')
    
    # Remove leading/trailing whitespace from each statement
    statements = [statement.strip() for statement in statements if statement.strip()]

    print("Returning", len(statements), "statements")
    return statements


def clean_input_folder(database):
    if os.path.exists(f"input/{database}"):
        if os.name == "posix":  # Linux
            os.system(f"rm -rf input/{database}")
        elif os.name == "nt":  # Windows
            os.system(f"rmdir /s /q input\\{database}")
            
    os.makedirs(f"input/{database}")

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
        "queries": []
    }
    #print("Parsing file", sql_file)
    sql_queries = extract_sql_queries(sql_file)
    print("Found", len(sql_queries), "queries")
    print(sql_queries[:2])
    test["queries"] = sql_queries
    
    all_tests.append(test)
    #print(sql_queries[:2])
    
#print("First 4 tests:", all_tests[:4])

# save the parsed tests to disk
for i, test in enumerate(all_tests):
    test_name = test["name"]
    # temove .sql extension
    test_name = test_name[:-4]
    
    #print("Saving test", test_name)
    with open(f"input/postgresql/test_{test_name}.json", "w") as f:
        json.dump(test, f, indent=4)
        
    if i > 100:
        break


print("Parsing postgresql tests done")