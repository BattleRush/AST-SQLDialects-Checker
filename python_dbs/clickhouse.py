import sqlite3
from typing import Any
import pandas as pd
import clickhouse_connect
import time
import os

class ClickhouseProcessor:
    def __init__(self):
        #    This method is called when you create a new object of the class
        #    Here, you can initialize the object's attributes using the parameters
        self.client = clickhouse_connect.get_client(host='localhost', username='default', password='passwordAST1')

    def reset_db(self):
        # disconect, delete file and reconnect
        # TODO propper delete
        print("Resetting Clickhouse")
        self.client.close()
        
        command = "clickhouse-client --query 'DROP DATABASE IF EXISTS test_db' --password=passwordAST1"
        os.system(command)
        
        time.sleep(1)
        self.client = clickhouse_connect.get_client(host='localhost', username='default', password='passwordAST1')

    def run_query(self, query):

        # if query contains multiple queries split them and run them one by one and concatenate the results
        if query.count(";") > 1:
            queries = query.split(";")
            result = []
            for q in queries:
                if q:
                    result.append(self.client.query_df(q))
                return pd.concat(result)
        else:
            return self.client.query_df(query)

