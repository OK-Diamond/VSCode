class db_class:
    def __init__(self, conn, table_name:str):
        '''Takes conn and table_name as parameters on initialisation
        'conn' is the sql database connection'''
        self.conn = conn
        self.cursor = conn.cursor()
        self.table_name = table_name

    def create_table(self, *columns:str) -> None:
        '''Creates a table using the table name specified on initialisation. Columns should be given in SQL format, for example:
        "userName TEXT", "time FLOAT", "PRIMARY KEY (userName)"'''
        sql_inp = f"CREATE TABLE {self.table_name} ("
        for i in columns: sql_inp += i+", "
        sql_inp = sql_inp[:-2]+")"
        try: 
            self.cursor.execute(sql_inp)
        except: print("create_table error")

    def add_rec(self, *args) -> None:
        '''Adds a record to the database specified with table_name. Each arg is a column of the table.'''
        sql_inp = f"INSERT INTO {self.table_name} VALUES ("
        for i in args: sql_inp += f"%s, " 
        sql_inp = sql_inp[:-2]+")"
        #print("sql_inp", sql_inp, args)
        try:
            self.cursor.execute(sql_inp, (args))
            self.conn.commit()
        except: print("add_rec error")

    def update_rec(self, set_name, set_val, key_name, key_val) -> None:
        '''Update a record. 'set' is the record to be updated and 'key' is the primary key'''
        if type(key_val) is str: key_val = "\""+key_val+"\""
        try:
            self.cursor.execute(f"""UPDATE {self.table_name} SET {set_name} = {set_val} WHERE {key_name} = {key_val}""")
            self.conn.commit()
        except: pass

    def get_rec(self, columns="*", **conditions) -> list:
        '''Conditions are applied in the following ways (in listed order):
            where : appends " WHERE "+str(conditions["where"])
            order: appends " ORDER BY "+str(conditions["order"])
            limit: appends " LIMIT "+str(conditions["limit"])'''
        sql_inp = f"SELECT {columns} FROM {self.table_name}"
        try: sql_inp += " WHERE "+str(conditions["where"])
        except: pass
        try: sql_inp += " ORDER BY "+str(conditions["order"])
        except: pass
        try: sql_inp += " LIMIT "+str(conditions["limit"])
        except: pass
        #print("sql_inp", sql_inp)
        try:
            self.cursor.execute(sql_inp)
            return self.cursor.fetchall()
        except:
            print("get_rec error")
            return ""
    
    #def delete_table(self): self.cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")

