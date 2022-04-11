import pyodbc
#conn_str = ("Driver={SQL Server Native Client 11.0}; Server=127.0.0.1,3306; Database=DB01; Trusted_Connection=yes;")
conn_str = ("Driver={ODBC Driver 17 for SQL Server}; Server=UKXXX00123,45600; Database=test_db; UID=root; PWD=ytkxp2KMmXZU75mufMCP;")

conn = pyodbc.connect(conn_str)

table_name = "test_db"
username, time = "Oliver", 15.4

try:
    conn.cursor().execute(f"CREATE TABLE {table_name} (userName TEXT, time FLOAT, PRIMARY KEY (userName))")
    print("table created")
except:
    print("create_table error")

try:
    conn.cursor().execute(f"""INSERT INTO {table_name} VALUES (?, ?)""", (username, time))
    conn.commit()
    print("record added")
except:
    print("add_rec error")


for i in conn.cursor().execute(f"""SELECT * FROM {table_name} WHERE userName = {username}"""):
    row = i
try:
    print([row[0], float(row[1])])
except:
    print("get_rec error")

