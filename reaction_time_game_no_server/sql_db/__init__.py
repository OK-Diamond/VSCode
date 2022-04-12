
class db_class:
    def __init__(self, conn):
        self.conn = conn

    def create_table(self, table_name):
        try: self.conn.cursor().execute(f"CREATE TABLE {table_name} (userName TEXT, time FLOAT, PRIMARY KEY (userName))")
        except: pass

    def add_rec(self, username, time, table_name):
        try:
            self.conn.cursor().execute(f"""INSERT INTO {table_name} VALUES (?, ?)""", (username,time))
            self.conn.commit()
        except: pass

    def get_rec(self, table_name, username):
        username = "\""+username+"\""
        for i in self.conn.cursor().execute(f"""SELECT * FROM {table_name} WHERE userName = {username}"""):
            row = i
        try: return True, [row[0], float(row[1])]
        except: return False, ""

    def update_rec(self, table_name, set_name, set_val, key_name, key_val):
        key_val = "\""+key_val+"\""
        try:
            self.conn.cursor().execute(f"""UPDATE {table_name} SET {set_name} = {set_val} WHERE {key_name} = {key_val}""")
            self.conn.commit()
        except: pass

    def get_leaderboard(self, table_name):
        leadboard_bank, curr_pos = [], 1
        for row in self.conn.cursor().execute(f"SELECT * FROM {table_name} ORDER BY time LIMIT 10"):
            leadboard_bank.append(str(curr_pos)+" - "+str(row[0])+" with a time of "+str(row[1])+" secs ")
            curr_pos += 1
        return leadboard_bank

    def get_position(self, table_name, column_name, key_name, key_val):
        key_val = "\""+key_val+"\""
        for i in self.conn.cursor().execute(f"""SELECT COUNT(*) FROM {table_name} WHERE {column_name} < (SELECT {column_name} FROM {table_name} WHERE {key_name} = {key_val}) ORDER BY {column_name}"""):
            return(i[0]+1)
