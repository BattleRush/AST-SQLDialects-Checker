import json
import os

def load_json(file):
    with open(file, "r") as f:
        return json.load(f)
    
    
def get_files(database):
    all_tests = []
    # in folder input/database/ get all json files
    for root, dirs, files in os.walk(f"input/{database}"):
        for file in files:
            if file.endswith(".json"):
                all_tests.append(os.path.join(root, file))
                
    # sort the files
    all_tests.sort()
    
    # print first 4 files
    print("First 4 files:", all_tests[:4])
                
    return all_tests

def load_all_json(database):
    all_tests = get_files(database)
    parsed_tests = []
    for test in all_tests:
        parsed_tests.append(load_json(test))
    return parsed_tests