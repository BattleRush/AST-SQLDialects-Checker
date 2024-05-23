import sqlite3
from typing import Any
import pandas as pd
import clickhouse_connect
import time
import os

class ClickhouseProcessor:
    def __init__(self):
        # Connect to client and aslo enable multiquery
        self.client = clickhouse_connect.get_client(host='localhost', username='default')


    def reset_db(self):
        # TODO proper delete
        print("Resetting Clickhouse")
        self.client.close()
        
        command = "clickhouse-client --query 'DROP DATABASE IF EXISTS test_db' --password=passwordAST1"
        os.system(command)
        
        time.sleep(1)
        self.client = clickhouse_connect.get_client(host='localhost', username='default', password='passwordAST1')

    def run_query(self, query):
        return self.client.query_df(query, settings={"max_execution_time": 5})

