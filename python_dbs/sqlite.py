import sqlite3
import pandas as pd
import os
import time

class SQLiteProcessor:
    def __init__(self):
        #  This method is called when you create a new object of the class
        #  Here, you can initialize the object's attributes using the parameters
        self.client = None
        self.init_connection()

    
    def init_connection(self):
        if self.client is not None:
            self.client.close()
            self.client = None
        
        #print("[-] Initializing SQLite")
        self.client = sqlite3.connect('sqlite_processor.db')
        
    def reset_db(self):
        # disconect, delete file and reconnect
        print("[-] Resetting SQLite")
        self.client.close()
        time.sleep(0.1)
        if os.path.exists('sqlite_processor.db'):
            os.remove('sqlite_processor.db')
        
        if os.path.exists('sqlite_processor.db-shm'):
            os.remove('sqlite_processor.db-shm')
        
        if os.path.exists('sqlite_processor.db-wal'):
            os.remove('sqlite_processor.db-wal')
        
        if os.path.exists('sqlite_processor.db-journal'):
            os.remove('sqlite_processor.db-journal')
            
        self.init_connection()




    def run_query(self, query):
        if self.client is None:
            self.init_connection()
        
        cursor = self.client.cursor()
        cursor.execute(query)

        # Fetch all results
        results = cursor.fetchall()

        # Close the cursor
        cursor.close()

        # Check if any results were returned
        if results:
            # Convert the results to a DataFrame
            return pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
            #print(df)
        else:
            # return nothing
            return None

# # Create an object of the class
# my_object = MyClass("value1", "value2")

# # Access the initialized attributes
# print(my_object.attribute1)  # Output: value1
# print(my_object.attribute2)  # Output: value2


# cnx = sqlite3.connect('file.db')

# df = pd.read_sql_query("SELECT * FROM table_name", cnx)