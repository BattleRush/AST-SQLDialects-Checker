import sqlite3
from typing import Any
import pandas as pd
import psycopg2, psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE

import time
import subprocess
from subprocess import PIPE
import numpy as np
import os

class PostgresProcessor:
    
    def __init__(self):
        self.client = None
        #self.init_connection()

    def reset_db(self):
        print("[-] Resetting Postgres")
        if self.client is not None:
            self.client.close()
            self.client = None
        return
        
        abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docker/")

        shell_command = f"""#!/bin/bash
# Define variables
cd {abspath}
docker compose down -t 0 postgres
docker compose up -d postgres
"""
        subprocess.run(shell_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=PIPE)
        
        

    def init_connection(self):
        if self.client is not None:
            self.client.close()
            self.client = None

        print("[-] Initializing Postgres")
        # Connect to the PostgreSQL server
        self.client = psycopg2.connect(host="localhost", user="root", password="root", port=11003)
        self.client.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Check if the user 'test' exists and create it if not
        with self.client.cursor() as cursor:
            cursor.execute("SELECT usename FROM pg_user")
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname='test'")
            if cursor.fetchall() == []:
                print("\t[-] Creating user 'test' ... ", end="")
                cursor.execute("CREATE USER test WITH PASSWORD 'test'")
                print("Done")
                
        # Close the current connection and create a new one to the default database
        self.client.close()

        # Connect to the PostgreSQL server with autocommit to create the database
        temp_client = psycopg2.connect(host="localhost", user="root", password="root", port=11003)
        temp_client.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with temp_client.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='test_db'")
            if cursor.fetchall() == []:
                print("\t[-] Creating database 'test_db' ... ", end="")
                cursor.execute("CREATE DATABASE test_db")
                print("Done")

        temp_client.close()
        
        self.client = psycopg2.connect(host="localhost", user='root', password='root', dbname='test_db', port=11003)
        self.client.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
    def run_query(self, query):
        if self.client is None:
            self.init_connection()
            
    
        with self.client.cursor() as cursor:
            cursor.execute(query)
            
            try:
                results = cursor.fetchall()
                
                # return df
                if results:
                    return pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
                else:
                    return None
            except Exception as e:
                #cursor.execute("ROLLBACK")
                #self.client.commit()
                
                # if exception with no results to fetch then return None
                if "no results to fetch" in str(e):
                    return None
                
                # rollback the last failed transaction
                print("Rolling back transaction in Postgres")
                self.client.rollback()
                
                raise e                
        
    def commit(self):
        self.client.commit()
    def client(self):
        return self.client
