import ast
from ast import literal_eval as make_tuple
from python_dbs.postgres import PostgresProcessor


expected = "(1, 2)"
expected = make_tuple(expected)

print(expected)

postgres = PostgresProcessor()

# postgres.reset_db()

# Create data and mock databases
print(postgres.run_query("SELECT datname FROM pg_database"))
# postgres.commit()
print(postgres.run_query("SELECT usename FROM pg_catalog.pg_user WHERE usename != 'root'"))


postgres.reset_db()
print(postgres.run_query("SELECT datname FROM pg_database"))
print(postgres.run_query("SELECT usename FROM pg_catalog.pg_user WHERE usename != 'root'"))


# print(postgres.run_query("CREATE DATABASE test_db"))
# print(postgres.run_query("CREATE TABLE test_table (id INT, name TEXT)"))
# print(postgres.run_query("INSERT INTO test_table (id, name) VALUES (1, 'test')"))
# postgres.commit()
# print(postgres.run_query("CREATE DATABASE test_db2"))
# # Run query and print output
# print(postgres.run_query("SELECT * FROM test_table"))
# print(postgres.run_query("SELECT datname FROM pg_database;"))
