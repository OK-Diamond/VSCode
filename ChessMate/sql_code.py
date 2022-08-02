from sqlite3 import Connection, Error, connect  # Used to store SQL files

def connect(database_name:str) -> Connection:
    '''Returns the database connection, which needs to be passed into most other functions from this file.'''
    return connect(f"""{database_name}.db""")

def quit(connection: Connection):
    '''Commits any unsaved changes and closes the connection to the database.'''
    connection.commit()
    connection.close()

class table():
    def __init__(self, connection: Connection, table_name: str) -> None:
        '''Initalises a table'''
        self.table_name = table_name
        self.conn = connection
        return

    def list_rec(self, key: str, keyfield: str|int) -> None:
        '''Lists the first rec where 'key' = 'keyfield'.'''
        if type(keyfield) == str:
            keyfield = f"\"{keyfield}\""
        self.conn.cursor().execute(f"""SELECT Board FROM {self.table_name} WHERE {key} = {keyfield}""")
        row = self.conn.cursor().fetchone()
        try:
            print(row)
        except Error as e:
            print("Record not found:", e)
        return

    def list_column(self, column: str) -> None:
        '''Prints every item in the specified column'''
        for row in self.conn.cursor().execute(f"""SELECT {column} FROM {self.table_name}"""):
            for item in row:
                if type(item) is not int and len(item) > 0:
                    print("item", item, "item[0]", item[0])
        return

    def delete_table(self) -> None:
        '''Drops the entire table. This cannot be undone, so be careful when using this.'''
        self.conn.cursor().execute(f"""DROP TABLE IF EXISTS {self.table_name} """)
        return
		
    def get_table_name(self) -> str:
        '''Returns the name of the table'''
        return self.table_name
