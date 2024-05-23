import sqlite3
from typing import Any
import pandas as pd
import psycopg2, psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE

import time
import subprocess
import numpy as np


class PostgresProcessor:
    
    def __init__(self):
        self.client = None
        self.init_connection()

    def reset_db(self):
        print("[-] Resetting Postgres")
        self.client.close()
        self.client = None
        
        with psycopg2.connect(host="localhost", user="root", password="root", port=11003) as client:
            client.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with client.cursor() as cursor:
                cursor.execute("SELECT usename FROM pg_catalog.pg_user WHERE usename != 'root'")
                for user in cursor.fetchall():
                    print(f"\t[-] Dropping user: {user[0]} ... ", end="")
                    cursor.execute(f"SELECT datname FROM pg_database JOIN pg_roles ON pg_database.datdba = pg_roles.rolname WHERE rolname = '{user[0]}'")
                    for db in cursor.fetchall():
                        print(f"\t\t[-] Dropping database: {db[0]} ... ", end="")
                        cursor.execute(f"DROP DATABASE {db[0]}")
                        print("Done")
                    cursor.execute(f"DROP USER {user[0]}")
                client.commit()
                cursor.close()
        
        #  Run a command
        
            with client.cursor() as cursor:
                print("Done")
                cursor.execute("SELECT * FROM pg_catalog.pg_user WHERE usename != 'root'")
                print(cursor.fetchall())
                cursor.execute("SELECT * FROM pg_database")
                print(cursor.fetchall())
        time.sleep(1)
        # self.init_connection()

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
        
        self.client = psycopg2.connect(host="localhost", user='test', password='test', dbname='test_db', port=11003)
            
    def run_query(self, query):
        print("Running query: ", query)
        if self.client is None:
            self.init_connection()
            
        try:
            print("Running transactional query: ", query)
            with self.client.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print("Error: ", e)
            return None
        
    def commit(self):
        self.client.commit()
    def client(self):
        return self.client
