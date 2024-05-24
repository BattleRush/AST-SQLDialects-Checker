import sqlite3
from typing import Any
import pandas as pd
import clickhouse_connect
import time
import os
import subprocess

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
        print("[-] Resetting Clickhouse")
        if self.client is not None:
            self.client.close()
            self.client = None
        
        abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docker/")

        shell_command = f"""#!/bin/bash
# Define variables
cd {abspath}
docker compose down clickhouse
docker compose up -d clickhouse
"""
        subprocess.run(shell_command, shell=True, check=True)
        
        
    def run_query(self, query):
        if self.client is None:
            self.init_connection()
        
        return self.client.query_df(query, settings={"max_execution_time": 5})

