import ast
from ast import literal_eval as make_tuple
from python_dbs.postgres import PostgresProcessor
from python_dbs.clickhouse import ClickhouseProcessor
from python_dbs.duckdb import DuckdbProcessor
from python_dbs.sqlite import SQLiteProcessor
import json

 
clickhouse = ClickhouseProcessor()
postgres = PostgresProcessor()
duckdb = DuckdbProcessor()
sqlite = SQLiteProcessor()


# Run a test query
query = "SELECT 1, 2"

print("Clickhouse: " + json.dumps(clickhouse.run_query(query).to_dict()))
print("Postgres: " + json.dumps(postgres.run_query(query).to_dict()))
print("Duckdb: " + json.dumps(duckdb.run_query(query).to_dict()))
print("SQLite: " + json.dumps(sqlite.run_query(query).to_dict()))
