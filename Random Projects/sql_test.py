import mysql.connector
conn = mysql.connector.connect(host="127.0.0.1", user="root", password="ytkxp2KMmXZU75mufMCP", database="leaderboard_db")
print("conn", conn)


cursor = conn.cursor()

table_name = "leaderboard"
username, time = "Leo", 100.4

try:
    cursor.execute(f"CREATE TABLE {table_name} (userName VARCHAR(15), time FLOAT, PRIMARY KEY (userName))")
    print("table created")
except:
    print("create_table error")

try:
    cursor.execute(f"INSERT INTO {table_name} VALUES (%s, %s)", (username, time))
    conn.commit()
    print("record added")
except:
    print("add_rec error")


username = "\""+username+"\""
cursor.execute(f"SELECT * FROM {table_name}") # WHERE userName = {username}")

result = cursor.fetchall()

for i in result:
  print(i)


print("done")

