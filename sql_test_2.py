class db_class:
    def __init__(self, conn, table_name):
        self.conn = conn
        self.table_name = (table_name)

    def create_table(self):
        try: self.conn.cursor().execute(f"CREATE TABLE {self.table_name} (userName TEXT, time FLOAT, PRIMARY KEY (userName))")
        except: print("create_table error")

    def add_rec(self, username, time):
        try:
            self.conn.cursor().execute(f"""INSERT INTO {self.table_name} VALUES (?, ?)""", (username,time))
            self.conn.commit()
        except: print("add_rec error")

    def get_rec(self, username):
        username = "\""+username+"\""
        for i in self.conn.cursor().execute(f"""SELECT * FROM {self.table_name} WHERE userName = {username}"""):
            row = i
        try: return True, [row[0], float(row[1])]
        except: return False, ""


import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="ytkxp2KMmXZU75mufMCP")
cursor = conn.cursor()

table_name = "test_db_1"

username, time = "Oliver", 15.4

try:
    cursor.execute(f"CREATE TABLE {table_name} (userName TEXT, time FLOAT, PRIMARY KEY (userName))")
    print("table created")
except:
    print("create_table error")

try:
    cursor.execute(f"""INSERT INTO {table_name} VALUES (?, ?)""", (username, time))
    conn.commit()
    print("record added")
except:
    print("add_rec error")


for i in cursor.execute(f"""SELECT * FROM {table_name} WHERE userName = {username}"""):
    row = i
try:
    print([row[0], float(row[1])])
except:
    print("get_rec error")

