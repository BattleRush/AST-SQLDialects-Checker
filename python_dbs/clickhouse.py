import sqlite3
from typing import Any
import pandas as pd
import clickhouse_connect
import time
import os

class ClickhouseProcessor:
    def __init__(self):
        self.client = None
        self.init_connection()

    def init_connection(self):
        if self.client is not None:
            self.client.close()
            self.client = None

        print("[-] Initializing Clickhouse")
        self.client = clickhouse_connect.get_client(host='localhost', username='default', port=8123)

    def reset_db(self):
        # TODO proper delete
        print("[-] Resetting Clickhouse")
        self.client.close()
        
        command = "clickhouse-client --query 'DROP DATABASE IF EXISTS default'"
        os.system(command)
        
        command = "clickhouse-client --query 'CREATE DATABASE default'"
        os.system(command)
        
        time.sleep(0.1)
        self.client = clickhouse_connect.get_client(host='localhost', username='default', port=8123)

    def run_query(self, query):
        return self.client.query_df(query, settings={"max_execution_time": 5})

