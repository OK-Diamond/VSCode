from sqlite3 import Connection, Error  # Used to store SQL files
from sqlite3 import connect as conn

def connect(database_name:str) -> Connection:
    '''Returns the database connection, which needs to be passed into most other functions from this file.'''
    return conn(database_name)

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

    def list_rec(self, conditions: str = "") -> list:
        '''Lists all recs where the condition is true.'''
        rec_bank = []
        if len(conditions) == 0:
            for row in self.conn.cursor().execute(f"""SELECT * FROM {self.table_name}"""):
                rec_bank.append(row)
        else:
            for row in self.conn.cursor().execute(f"""SELECT * FROM {self.table_name} WHERE {conditions}"""):
                rec_bank.append(row)
        return rec_bank

    def update_rec(self, key:str, value, conditions: str = ""):
        try:
            if len(conditions) == 0:
                self.conn.cursor().execute(f"""UPDATE {self.table_name} SET {key} = {value}""")
            else:
                self.conn.cursor().execute(f"""UPDATE {self.table_name} SET {key} = {value} WHERE {conditions}""")
            self.conn.commit()
            print(f"Record updated: {key}")
        except Error as e:
            print(f"update_rec failed: {e}")

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
