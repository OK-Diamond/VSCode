class db_class:
    '''Takes conn and table_name as parameters on initialisation
    'conn' is the sql database connection'''
    def __init__(self, conn="", table_name=""):
        self.conn = conn
        #self.cursor = conn.cursor()
        self.table_name = table_name

    def create_table(self, *columns:str):
        '''Creates a table using the table name specified on initialisation. Columns should be given in SQL format, for example:
        "userName TEXT", "time FLOAT", "PRIMARY KEY (userName)"'''
        sql_inp = f"CREATE TABLE {self.table_name} ("
        for i in columns: sql_inp += i+", "
        sql_inp = sql_inp[:-2]+")"
        try: self.cursor.execute(sql_inp)
        except: pass

    def add_rec(self, *args) -> None:
        '''Adds a record to the database specified with table_name. Each arg is a column of the table.'''
        sql_inp = f"INSERT INTO {self.table_name} VALUES ("
        for i in args: sql_inp += f"%s, " 
        sql_inp = sql_inp[:-2]+")"
        #print("sql_inp", sql_inp, args)
        try:
            self.cursor.execute(sql_inp, (args))
            self.conn.commit()
        except: pass

    def update_rec(self, set_name, set_val, key_name, key_val) -> None:
        '''Update a record. 'set' is the record to be updated and 'key' is the primary key'''
        if type(key_val) is str: key_val = "\""+key_val+"\""
        try:
            self.cursor.execute(f"""UPDATE {self.table_name} SET {set_name} = {set_val} WHERE {key_name} = {key_val}""")
            self.conn.commit()
        except: pass

    def get_rec(self, fetchone=True, columns="*", **conditions) -> list:
        '''get_rec(self, fetchone=True, column="*", **conditions)

        If fetchall is False, fetchone will be used instead
        Conditions are applied in the following ways (in listed order):
            where : appends " WHERE "+str(conditions["where"])
            order: appends " ORDER BY "+str(conditions["order"])
            limit: appends " LIMIT "+str(conditions["limit"])'''
        
        sql = f"SELECT {columns} FROM {self.table_name}"
        try: sql += " WHERE "+str(conditions["where"])
        except: pass
        try: sql += " ORDER BY "+str(conditions["order"])
        except: pass
        try: sql += " LIMIT "+str(conditions["limit"])
        except: pass
        self.cursor.execute(sql)
        if fetchone: return self.cursor.fetchone()
        else: return self.cursor.fetchall()

    def get_position(self, column_name, key_name, key_val) -> int:
        if type(key_val) is str:
            key_val = "\""+key_val+"\""
        self.cursor.execute(f"""SELECT COUNT(*) FROM {self.table_name} WHERE {column_name} < (SELECT {column_name} FROM {self.table_name} WHERE {key_name} = {key_val}) ORDER BY {column_name}""")
        return self.cursor.fetchone()+1
db = db_class()
print()
db.add_rec("1", 2, "3", "4")

