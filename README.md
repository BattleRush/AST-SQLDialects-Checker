# Understanding the Difference Between SQL Dialects using DBMS Test Suites Report
*Authors: Albert Cerfeda, Karlo Piskor*

## PostgreSQL Summary
![PostgreSQL](./tex/img/postgres_summary.png)

## SQLite Summary
![SQLITE](./tex/img/sqlite_summary.png)

## Detailed view of a single test case query
![Detailed](./tex/img/details.png)

This project leverages the existing test suites for popular DBMSs such as Sqlite, Clickhouse, PostgreSQL, DuckDB and cross-evaluation for assessing the differences and intricacies of SQL dialects.
### Reproduction package
- 00 - Make sure to clone all submodules, namely the Sqlite, Clickhouse, PostgreSQL and DuckDB codebases. After doing so, replace the `tester.tcl` file inside of the SQLite submodule with out modified one. Our verison intercepts SQL queries and outputs them to a log file for us to retrieve later on [See [SQLITE.md](./SQLITE.md)].

- 01 - Run the `01_parse.py` Python script to parse the tests contained in the submodules into the `input/` folder.
- 02 (Optional) - Select specific tests from the `input/` folder to cross evaluate, by copying them to the `input_clean/` folder. After doing so run the `02_verify.py` Python script to verify that you copied the files correctly. We already provide a selection of test cases in the `input_clean/` folder.
- 03 - Run the tester against the aggregated test cases from all DBMSs. You can do so by running the `03_main.py` Python script. The evaluation might take a while, as it frequently stops and restarts Docker containers between each run. After the execution is completed, an HTML report is stored inside the `output/` folder.
- 04 - To generate the HTML report, run the `04_generate_html.py` Python script. The script will generate a report based on the output of the previous step and store it in the `output/` folder.
- The file `00_repull.py` is a helper script that can be used to repull the test cases content into the `input_clean/` folder. This is useful when a parser has been updated and the test cases need to be updated or to verify that no test case from a wrong database ended in the wrong database folder in the `input_clean/` folder.

The file `report_html_and_json.tar.gz` contains the HTML report and the JSON file with the raw data of the report and can be extracted to the `output/` folder.