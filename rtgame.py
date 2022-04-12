import pygame as pg
from math import sqrt, log
from random import randint
from time import time as get_time
import mysql.connector

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
    
    '''def delete_table(self):
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")'''




'''
Features to add:
    Give the player's name a different colour in the leaderboard to make it stand out from everyone else
    Make the leaderboard screen resize to fit the window size.
    Add selectable difficulties, each with their own leaderboards.
'''

class window_class:
    def __init__(self, width:int, height:int) -> None:
        '''Hold information on the PyGame window.'''
        self.display, self.height, self.width = pg.display.set_mode((width, height)), height, width

class target_class:
    def __init__(self, pos, radius) -> None:
        '''Stores targets, which are circles that appear in the PyGame window that dissapear when the cursor touches them.'''
        self.pos, self.radius = pos, radius
    def draw(self, window, dist_to_cursor:float) -> None:
        '''Draws the target to the PyGame window. The window still needs to be flipped (using pg.display.flip()) for this to appear.'''
        dist_relative_to_screen = dist_to_cursor/(sqrt(window.width**2 + window.height**2))
        gradient = 0.5 # You can adust this to change the distance at which the target becomes more red
        r = max(min(int(-log(dist_relative_to_screen*gradient)/7*255)+50, 255), 0)
        g = 50
        b = 255-r
        pg.draw.circle(window.display, [r,g,b], (self.pos[0],self.pos[1]), self.radius, 0)

class cursor_class:
    def __init__(self, radius) -> None:
        '''Holds information on the cursor.'''
        self.radius, self.pos = radius, pg.mouse.get_pos()
    def __update_pos(self) -> None:
        '''Updates self.pos to be equal to the coordinates of the cursor.'''
        self.pos = pg.mouse.get_pos()
    def draw(self, window) -> None:
        '''Draws a circle around the cursor.'''
        self.__update_pos()
        pg.draw.circle(window.display, (130,150,25), (self.pos[0],self.pos[1]), self.radius, 0)

class input_box_class:
    def __init__(self, x_pos, y_pos, width, height, font, text=""):
        '''Class for a text input box.'''
        self.rect, self.colour = pg.Rect(x_pos, y_pos, width, height), pg.Color("dodgerblue2")
        self.font, self.text = font, text
        self.txt_surface = self.font.render(self.text, True, self.colour)
        self.active = True
    def handle_event(self, event) -> str:
        '''Checks to see if the user has selected/deselected the input box, and manages typing into the box.
        'event' should be a PyGame event (ie. from pg.event.get()).'''
        text_typed = ""
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos): self.active = not self.active # Toggle whether the text box is active or not
            else: self.active = False
            self.colour = pg.Color("dodgerblue2") if self.active else pg.Color("lightskyblue3") # Change the current colour of the input box
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_RETURN: text_typed, self.text = str(self.text), ""
            elif event.key == pg.K_BACKSPACE: self.text = self.text[:-1]
            elif len(self.text) < 15: self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, self.colour) # Re-render the text
        return text_typed
    def __update_width(self) -> None:
        '''Resizes the box if the text is too long.'''
        self.rect.w = max(200, self.txt_surface.get_width()+10)
    def draw(self, window) -> None:
        '''Draws the text imput box and the 'Enter your username' prompt to the PyGame window. The window still needs to be flipped (using pg.display.flip()) for this to appear.'''
        self.__update_width()
        window.display.blit(self.font.render("Enter your username:", True, pg.Color(200,220,200)), (self.rect.x, self.rect.y-50)) # Blit the prompt text
        window.display.blit(self.txt_surface, (self.rect.x+5, self.rect.y+2)) # Blit the input box
        pg.draw.rect(window.display, self.colour, self.rect, 2) # Blit the rect

def update_game_display(window, cursor: cursor_class, target_bank: list) -> None:
    '''Updates all aspects of the window during the reaction game, including the mouse and targets. Also slips the window.'''
    window.display.fill((30, 30, 30))
    for i in range(len(target_bank)-1,-1,-1):
        target = target_bank[i]
        dist_to_cursor = int(sqrt(((target.pos[0]-cursor.pos[0])**2) + ((target.pos[1]-cursor.pos[1])**2)))
        if dist_to_cursor < target.radius+cursor.radius: target_bank.pop(i)
        else: target.draw(window, dist_to_cursor)
    cursor.draw(window)
    pg.display.flip() # Updates the window

def display_paragraph(window, text_display_bank:list) -> None:
    '''Blits all lines of text in the text_display_bank to the window, then flips the window.
    I intend to add some kind of atuo-text resizing so that it will always fit the screen later.'''
    window.display.fill((30, 30, 30))
    font_size, colour = 25, pg.Color(200, 220, 200)
    font = pg.font.SysFont("monospace", font_size)
    x_pos, y_pos = 20, 20
    for line_pos in range(len(text_display_bank)):
        window.display.blit(font.render(text_display_bank[line_pos], True, colour), (x_pos, font_size*line_pos+y_pos))
    pg.display.flip()

def main_game(window) -> float:
    '''The main loop for the reaction time game. Returns the game_time, which is the amount of time that the game took as a float (rounded to 3 decimal places).'''
    cursor = cursor_class(10)
    target_bank, targets = [], 10
    for i in range(targets):
        target_bank.append(target_class([randint(int(window.width*0.1),int(window.width*0.9)), randint(int(window.height*0.1),int(window.height*0.9))], 8))
    running_game = True
    start_time = get_time()
    while running_game:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                running_game = False
                pg.quit()
                break
        update_game_display(window, cursor, target_bank)
        if len(target_bank) == 0:
            game_time = round(get_time()-start_time, 3)
            running_game = False
    return game_time

def main_input(window) -> str:
    '''The main loop for the input box, where the user's username is collected. Returns the username as a string.'''
    font = pg.font.SysFont("monospace", 32)
    input_box = input_box_class(100, 100, 140, 40, font)
    running_input = True
    while running_input:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running_input = False
                pg.quit()
                break
            username = input_box.handle_event(event)
            if username != "": return username
        window.display.fill((30, 30, 30))
        input_box.draw(window)
        pg.display.flip()

def main_db(window, game_time:float, username:str) -> None:
    '''The code managing updating the MySQL servers, then displaying the leaderboard.'''
    conn = mysql.connector.connect(host="192.168.1.127", user="root", password="ytkxp2KMmXZU75mufMCP", database="leaderboard_db")
    db = db_class(conn, "tbl_leaderboard")
    text_display_bank = ["You won in "+str(game_time)+" seconds"]
    db.create_table("userName VARCHAR(15)", "time FLOAT", "PRIMARY KEY (userName)")
    user_data = db.get_rec(where=f"""userName = \"{username}\"""")
    print("user_data", user_data)
    if user_data != "" and user_data != []:
        user_data = user_data[0]
        if game_time < user_data[1]:
            time_change = str(round(user_data[1]-game_time, 3))
            text_display_bank += ["", "Well Done! You beat your previous fastest", "time by "+time_change+" seconds."]
            db.update_rec("time", game_time, "userName", username)
        else: text_display_bank += ["", "Your fastest time", "is "+str(user_data[1])+" seconds. Keep trying!"]
    else:
        db.add_rec(username, game_time)
        user_data = [username, game_time]
    text_display_bank += ["", "Leaderboard:"]
    leaderboard_bank = db.get_rec("*", order="time", limit=10)
    for position in range(len(leaderboard_bank)):
        text_display_bank += [str(position+1)+" - "+leaderboard_bank[position][0]+" with a time of "+str(leaderboard_bank[position][1])+" seconds"]
    text_display_bank += ["","Your leaderboard position: "+str(db.get_rec("COUNT(*)", where="time <"+str(user_data[1]), order="time")[0][0])]
    text_display_bank += ["Press Q to quit"]
    display_paragraph(window, text_display_bank)
    running_db = True
    while running_db:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                running_db = False
                pg.quit()
                break

if __name__ == '__main__':
    pg.init()
    window = window_class(800, 600)
    game_time = main_game(window)
    username = main_input(window)
    main_db(window, game_time, username)
