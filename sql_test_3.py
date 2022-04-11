import pyodbc
import pandas as pd

# Trusted Connection to Named Instance
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=test_db;Trusted_Connection=yes;')
cursor=conn.cursor()


pd.read_sql(query, conn)

cursor.execute("SELECT @@VERSION as version")
while 1:
    row = cursor.fetchone()
    if not row:
        break
    print(row.version)
cursor.close()
conn.close()

