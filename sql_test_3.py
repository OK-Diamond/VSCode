import pyodbc
import pandas as pd

# Trusted Connection to Named Instance
try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=test_db;Trusted_Connection=yes;')
    cursor=conn.cursor()
except:
    print("c")
    

table_name = "test_db"
username, time = "Oliver", 15.4

query = f"CREATE TABLE {table_name} (userName TEXT, time FLOAT, PRIMARY KEY (userName))"
query2 = f"""INSERT INTO {table_name} VALUES (?, ?)""", (username, time)

try:
    pd.read_sql(query, conn)
    print("table created")
except:
    print("a")

try:
    pd.read_sql(query2, conn)
    print("record_added")
except:
    print("b")
'''
cursor.execute("SELECT @@VERSION as version")
while 1:
    row = cursor.fetchone()
    if not row:
        break
    print(row.version)
cursor.close()
conn.close()

'''