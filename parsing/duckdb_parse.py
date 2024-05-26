# this file converts tests to unified format

import os
import json
import re
import numpy as np

def get_blocks(test_string):
    blocks = []
    current_block = ""
    for line in test_string.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith(('statement', 'query')):
            # Start a new block if the current one is not empty
            if current_block:
                blocks.append(current_block)
                
            current_block = line
        else:
            if current_block:
                current_block += "\n"+line
    if current_block:
        blocks.append(current_block)
    
    return blocks

TYPE3s = []
def parse_duckdb_test_cases(test_string, test_name):
    # If test file has lines starting with these keywords, we skip it
    EXCLUDE_WORDS = ["read_csv","read_csv_auto", "data/csv/", ".csv", "parquet_scan", "__TEST_DIR__", "load", "set", "concurrentloop", "unzip", "pg_attribute", "nosort key", "loop", "foreach"]
    # If test file has lines starting with these keywords, we remove them
    SKIP_WORDS = ["require", "sleep", "mode"]
    
    TYPE3_VALS = ['v2', 'con1', 'grouping_sets_collation_result', 'secret_to_string', 'r6', 'con5', 's1', 'distinct_ints', 'pg_indexes', 'count_distinct_varchar', 'show_db', 'parquet_scan_result', 'distinct_hugeints', 'result1', 'all_types', 'pg_view', 'pg_index', 'res6', 'webpagecsv', 'nosort', 'bug687_nulls', 'v1', 'default_value', 'q1', 'res4', 'pg_dbase', 'map_hashes', 'structres2', 'empty', 'result_etc_2', 'pgmyschema', 'correct', 'label-240', 'grouping_sets_collation', 'unpivot', 'list', 'sumresult', 'con2', 'result_utc_1', 'con3', 'union_groups_collation_result', 'count_distinct_int', 'nodistinctrewrite2', 'res', 'select_after_update', 'result_1', 'view_info', 'distinct_small', 'r3', 'con4', 'r2', 'r1', 'pg_depend', 'q01', 'result', 'pg_enum', 'alltypes', 'decimal_scan', 'distinctrewrite3', 'updater', 'emptyset', 'describe', 'left_inequality', 'distinctrewrite4', 'count_varchar', 'sortvarchararray', 'value', 'res1', 'scrambled', 'pg_attribute', 'q0', 'userdata1.parquet', 'pg_tspace', 'result_america_null', 'result_utc_2', 'swapped', 'table_info', 'result_etc_3', 'con6', 'right_equality', 'res10', 'lineitemcsv', 'left_equality', 'result_utc_null', 'label-empty', 'unchanged', 'empty_result', 'transform', 'date_scan', 'mapres2', 'expected_blocks', 'ts_scan', 'res7', 'ncvoters_res', 'res0', 'sortnestedvarchararray', 'label-225', 'inner_equality', 'distinctrewrite1', 'r5', 'distinct_bigints', 'distinctrewrite2', 'sortintarray', 'key', 'explicitly_set', 'pg_constraint', 'res8', 'pg_seq', 'clevel', 'r4', 'rowsort', 'result3', 'sort', 'res5', 'result_2', 'nostats', 'pivot', 'result_america_1', 'count_int_grouped', 'inner_inequality', 'mapres1', 'result_america_3', 'expected', 'result_etc_1', 'result_utc_3', 'right_inequality', 'summarize', 'alltypes_dictionary', 'result_etc_null', 'res9', 'duckdb_col', 'structres1', 'q06', 'sortnestedintarray', 'q2', 'result2', 'res3', 'dblist', 'qlateral', 'res2', 'count_int_list', 'count_int', 'pgnamespace', 'nodistinctrewrite1']
    
    
    
    test = {
        "name": test_name,
        "tests": []
    }

    
    lines = test_string.split("\n")
    
    #  Remove comment lines
    lines = [l for l in lines if not l.startswith('#')]
    #  Remove lines starting with SKIP_WORDS
    lines = [l for l in lines if not any(l.startswith(c) for c in SKIP_WORDS)]
    
    #  If any line contains EXCLUDE_WORDS, skip the test
    if any(any([c in l for c in EXCLUDE_WORDS]) for l in lines):
        return []
    #  If any line contains TYPE3_VALS, skip the test
    if any(any([c in l for c in TYPE3_VALS]) for l in lines):
        return []
    
    
    test_string = "\n".join(lines)
    # Go through every block in the test file
    for i, block in enumerate(get_blocks(test_string), start=1):
        test_case = {
            # "type1": "",
            # "type2": None,
            # "type3": None,
            "name" : "",
            "query": "",
            "expected_result": ""
            # "success": None,
            # "expected_results": "",
            # "expected_results_table" : None
        }
        
        
        block_lines = block.split("\n")
        
        print(f"Block {i}:")
        print(block.replace("\n", "\\n\n").replace("\t", "\\t\t"))
        print(block)
        print("\n===")
        
        # Every block starts with 'statement' or 'query'
        # assert block_lines[0].startswith(("statement","query"))
        for l in block_lines[1:]:
            assert not l.startswith(("statement","query"))
        
        match1 = re.match(r"^(statement|query) (\w+) (.*)", block_lines[0])
        match2 = re.match(r"^(statement|query) (\w+)", block_lines[0])
        if match1:
            type1, type2, type3 = match1.groups()
            type3 = type3.strip().split() or None
        elif match2:
            type1, type2 = match2.groups()
            type3 = None  
        
        assert type1 != None
        assert type2 != None
        
        type1 = type1.strip()
        type2 = type2.strip()
        
        
        # Make sure every type has an expected value
        if type1 == "statement":
            assert type2 in ["ok", "error", "maybe"]
        if type1 == "query":
            assert all(c in ['I','R','T'] for c in type2)
        if type3:
            assert all(c in TYPE3_VALS for c in type3)
            # global TYPE3s
            # TYPE3s.extend(type3)
            # TYPE3s = list(set(TYPE3s))
        
        
        # if len(block_lines) == 6:
        #     print("Put a breakpoint here to debug")
        
        # We extract the query from the block (could be multiline). Queries end with a line that is either "----" (when they produce an output) or empty
        query = block_lines[1].strip()
        query_block_idx_start = 1
        query_block_idx_end = 2
        if any(l.strip() in ["----", ""] for l in block_lines):
            query_block_idx_end = next((idx for idx, val in enumerate(block_lines[1:], start=1) if val in ["----", ""]), 2)
        
        query = "\n".join(block_lines[query_block_idx_start:query_block_idx_end]).strip()
        
        assert not any(l.strip() in ["----", ""] for l in query.split("\n"))
        assert not query == ""
        
        
        
        # if type1 == "query":
        #     test_case["success"] = True
        # if type1 == "statement" and type2 == "ok":
        #     test_case["success"] = True
        # if type1 == "statement" and type2 == "error":
        #     test_case["success"] = False
        # if type1 == "statement" and type2 == "maybe":
        #     test_case["success"] = None    
        

        
        # Extracting expected results
        # expected_results = ""
        # expected_results_table = []
        # if "----" in block and block.split("----")[1].strip() != "":
        #     # Expected output is after the "----" line
        #     expected_results = block.split("----")[1]
            
        #     expected_results = "\n".join([i for i in expected_results.split("\n") if i.strip()!=''])
            
        #     if type1 == "query":
        #         expected_results_table = [c for c in [i.split("\t") for i in expected_results.split("\n")] ]
        #         expected_results_table = [[c for c in r if c != ''] for r in expected_results_table]
        #         # Makes sure we dont add any empty strings
        #         assert not any(any(c == '' for c in r) for r in expected_results_table)
                
                
        #         # * When result is a single column, it gets output as a row, so we have to reshape it
        #         print("Expected results table:\n", expected_results_table)
        #         table_shape = np.shape(np.array(expected_results_table))
        #         print("Table shape:", table_shape)
        #         if table_shape[1] == 1 and len(type2) > 1: # Column vector
        #             expected_results_table = np.reshape(np.array(expected_results_table), (-1, len(type2))).tolist()
            
                
        
        # test_case["type1"] = type1
        # test_case["type2"] = type2
        # test_case["type3"] = type3
        test_case["query"] = query
        # test_case["expected_results"] = expected_results
        # test_case["expected_results_table"] = expected_results_table
        
        
        test["tests"].append(test_case)
        
    return test
    
    
def parse_duckdb():
    all_test_files = []
    
    # check if input/duckdb exists 
    if not os.path.exists("input/duckdb"):
        os.makedirs("input/duckdb")
    for root, dirs, files in os.walk("input/duckdb"):
        for file in files:
            os.remove(os.path.join(root, file))
       
        
    for root, dirs, files in os.walk("databases/duckdb/test/sql"):
        for file in files:
            if file.endswith(".test"):
                all_test_files.append(os.path.join(root, file))
                
    print("Total tests found:", len(all_test_files))
    
    #print first test
    #print("First test:", all_test_files[0])
    
    success = 0
    skipped = 0

    count = 0
    for test in all_test_files:
        print("Parsing test ", all_test_files.index(test) + 1, " out of ", len(all_test_files), ": ", test)
        
        # * errors='replace' will replace any unknown characters with a replacement character
        # *     There are some tests that use invalid characters (see ./databases/duckdb/test/sql/insert/test_insert_invalid.test)
        with open(test, 'r', encoding='utf-8', errors='replace') as file:
            test_string = file.read()
            
        test_name = test.split("/")[-1]
        print("Test name:", test_name)
        parsed_tests = parse_duckdb_test_cases(test_string, test_name)
        
        # if parsed_tests is empty, skipped increment
        if not parsed_tests:
            skipped += 1
        else:
            success += 1
        
        # save json formatted in input/duckdb folder
        # output file is without databases/duckdb/test/sql and remaining / replace with -
        #print("Output filename:", test)
        output_filename = test.replace("databases/duckdb/test/sql/", "").replace("/", "-")
        #print("Output filename:", output_filename)
        # if file exists, remove it
        
        if parsed_tests:
            # with open("input/duckdb/" + output_filename + ".json", "w") as f:
            #     f.write(json.dumps(parsed_tests, indent=4))
            count += 1
            prefix = str(count).zfill(5)
            #print("Saving test", test_name)
            with open(f"input/duckdb/{prefix}_{output_filename}.json", "w") as f:
                json.dump(parsed_tests, f, indent=4)
        
    print ("Success:", success, " Skipped:", skipped)
    #print(parsed_tests)

parse_duckdb()