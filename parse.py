from parsing.clickhouse_parse import parse_clickhouse
from parsing.postgresql_parse import parse_postgres
from parsing.sqlite_parse import parse_sqlite
from parsing.duckdb_parse import parse_duckdb


parse_clickhouse()
parse_postgres()
parse_sqlite()
parse_duckdb()

print("Parsing done")