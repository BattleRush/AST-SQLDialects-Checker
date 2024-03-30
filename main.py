import mysql.connector 
import psycopg2
import datetime
import os

if not os.path.exists("input"):
    os.makedirs("input")
    
if not os.path.exists("output"):
    os.makedirs("output")

list_of_dbms = ["mysql", "mariadb", "postgresql", "sqlite"]

# check that for each dbms, there exists a folder in the input folder
for dbms in list_of_dbms:
    if not os.path.exists(f"input/{dbms}"):
        os.makedirs(f"input/{dbms}")

run_date_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


ethz_ids = ["kpiskor", "ethz_2"]

# ask for ethz id as number [0] name ...
print("Please select your ETHZ ID:")
for i, ethz_id in enumerate(ethz_ids):
    print(f"[{i}] {ethz_id}")
    
selected_ethz_id = int(input("Enter the number of your ETHZ ID: "))

print(f"Selected ETHZ ID: {ethz_ids[selected_ethz_id]}")

# create folder if not exists in output
if not os.path.exists(f"output/{ethz_ids[selected_ethz_id]}"):
    os.makedirs(f"output/{ethz_ids[selected_ethz_id]}")
    
current_output_folder = f"output/{ethz_ids[selected_ethz_id]}/{run_date_time}"
os.makedirs(current_output_folder)


# create test.txt file in the output folder
with open(f"{current_output_folder}/test.txt", "w") as f:
    f.write("Hello World!")



print("CONNECT TO MYSQL")

# connect to mysql on port localhost 11003
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="S3cret",
    port="11003",
)

cursor = mydb.cursor()
# list all available databases
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()
for database in databases:
    print(database)

print(mydb) 

print("")
print("CONNECT TO MARIADB")

# connect to mariadb on port localhost 11001
mydb = mysql.connector.connect(
    host="localhost",
    user=""
    password="S3cret",
    port="11001"
)

cursor = mydb.cursor()
# list all available databases
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()
for database in databases:
    print(database)
    
print(mydb)

print("")
print("CONNECT TO POSTGRESQL")

# connect to postgresql on port localhost 11002
mydb = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="S3cret",
    port="11002"
)

cursor = mydb.cursor()
# list all available databases
cursor.execute("SELECT datname FROM pg_database")
databases = cursor.fetchall()
for database in databases:
    print(database)
    
print(mydb)
    