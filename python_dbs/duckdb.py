import sqlite3
from typing import Any
import pandas as pd
import duckdb
import time


class DuckdbProcessor:
    def __init__(self):
        self.client = None
        self.init_connection()

    def init_connection(self):
        if self.client is not None:
            self.client.close()
        self.client = duckdb.connect()
    def reset_db(self):
        print("Ciao mamma")
        
        
    
    def run_query(self, query):
        if self.client is None:
            self.init_connection()
        
        return self.client.sql(query).df()


