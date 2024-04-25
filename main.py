import mysql.connector 
import mariadb
import psycopg2
import datetime
import os
import sqlite3

# if not os.path.exists("input"):
#     os.makedirs("input")
    
# if not os.path.exists("output"):
#     os.makedirs("output")

list_of_dbms = ["mysql", "mariadb", "postgresql", "sqlite"]

# check that for each dbms, there exists a folder in the input folder
# for dbms in list_of_dbms:
#     if not os.path.exists(f"input/{dbms}"):
#         os.makedirs(f"input/{dbms}")

run_date_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


ethz_ids = ["kpiskor", "acerfeda"]

# ask for ethz id as number [0] name ...
# print("Please select your ETHZ ID:")
# for i, ethz_id in enumerate(ethz_ids):
#     print(f"[{i}] {ethz_id}")
    
# selected_ethz_id = int(input("Enter the number of your ETHZ ID: "))
selected_ethz_id = 1

print(f"Selected ETHZ ID: {ethz_ids[selected_ethz_id]}")

# create folder if not exists in output
if not os.path.exists(f"output/{ethz_ids[selected_ethz_id]}"):
    os.makedirs(f"output/{ethz_ids[selected_ethz_id]}")
    
current_output_folder = f"output/{ethz_ids[selected_ethz_id]}/{run_date_time}"
# TODO ENABLE THIS LINE WHEN WE GOT OUTPUT DATA TO COLLECT
#os.makedirs(current_output_folder)


# # create test.txt file in the output folder
# with open(f"{current_output_folder}/test.txt", "w") as f:
#     f.write("Hello World!")



print("[-] Connecting to mysql ...", end="")
mysql_connector = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    port="11001",
    database="mysql"
)
print(" done.")


print("[-] Connecting to mariadb ... ", end="")
mariadb_connector = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mariadb",
    port=11002,
    database="mariadb"
)
print(" done.")


print("[-] Connecting to postgresql ...", end="")
postgres_connector = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="postgres",
    port="11003"
)
print(" done.")

print("[-] Connecting to sqlite ...", end="")
if not os.path.exists("./dbdata/sqlite"):
    os.makedirs("./dbdata/sqlite")
sqlite_connector = sqlite3.connect("./dbdata/sqlite/sqlite.db")
print(" done.")