import pygame as pg
from math import sqrt, log
from random import randint
from time import time as get_time
import mysql.connector

'''
Features to add:
    Give the player's name a different colour in the leaderboard to make it stand out from everyone else
    Make the leaderboard screen resize to fit the window size.
    Add selectable difficulties, each with their own leaderboards.
'''


class db_class:
    def __init__(self, conn, table_name:str) -> None:
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
        try: self.cursor.execute(sql_inp)
        except: pass
    def add_rec(self, *args) -> None:
        '''Adds a record to the database specified with table_name. Each arg is a column of the table.'''
        sql_inp = f"INSERT INTO {self.table_name} VALUES ("
        for i in args: sql_inp += f"%s, " 
        sql_inp = sql_inp[:-2]+")"
        try:
            self.cursor.execute(sql_inp, (args))
            self.conn.commit()
        except: pass
    def update_rec(self, set_name, set_val, where="") -> None:
        '''Update a record. 'set' is the record to be updated and 'key' is the primary key'''
        sql_inp = f"""UPDATE {self.table_name} SET {set_name} = {set_val}"""
        if where != "":
            sql_inp += f""" WHERE {where}"""
        try:
            self.cursor.execute(sql_inp)
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
        try:
            self.cursor.execute(sql_inp)
            return self.cursor.fetchall()
        except: return ""
    def delete_table(self): self.cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")

class window_class:
    def __init__(self, width:int, height:int) -> None:
        '''Hold information on the PyGame window.'''
        self.display, self.height, self.width = pg.display.set_mode((width, height)), height, width

###
class button_class:
    def __init__(self, pos, font, text="", stored_value="", box_rgb=[250, 250, 250], text_rgb=[0, 0, 0]) -> None:
        '''Class for a text input box.'''
        self.font, self.text, self.stored_value = font, text, stored_value
        self.txt_surface = self.font.render(self.text, True, pg.Color(text_rgb))
        size = [max(200, self.txt_surface.get_width()+10), self.txt_surface.get_height()+10]
        self.rect = pg.Rect(pos[0], pos[1], size[0], size[1])
        self.box_rgb, self.text_rgb = box_rgb, text_rgb
        self.border_rgb = [5,5,5] if self.box_rgb[0]+self.box_rgb[1]+self.box_rgb[2] > 255*3/2 else [250,250,250]
        self.pressed = False
    def __update_width(self) -> None:
        '''Resizes the box if the text is too long.'''
        self.rect.w = max(200, self.txt_surface.get_width()+10)
    def draw(self, window) -> None:
        '''Draws the text imput box and the 'Enter your username' prompt to the PyGame window. The window still needs to be flipped (using pg.display.flip()) for this to appear.'''
        self.__update_width()
        if self.pressed: # invert colours if the button is held down (tracked with self.pressed)
            curr_box_rgb = [255-self.box_rgb[0], 255-self.box_rgb[1], 255-self.box_rgb[2]]
            curr_text_rgb = [255-self.text_rgb[0], 255-self.text_rgb[1], 255-self.text_rgb[2]]
            curr_border_rgb = [255-self.border_rgb[0], 255-self.border_rgb[1], 255-self.border_rgb[2]]
        else:
            curr_box_rgb = self.box_rgb
            curr_text_rgb = self.text_rgb
            curr_border_rgb = self.border_rgb
        pg.draw.rect(window, pg.Color(curr_box_rgb), self.rect) # Draw the rect
        pg.draw.rect(window, pg.Color(curr_border_rgb), self.rect, 2) # Draw the rect border
        window.blit(self.font.render(self.text, True, pg.Color(curr_text_rgb)), (self.rect.x+5, self.rect.y+2)) # Draw the text
        

    def handle_event(self, event) -> tuple[bool, str]:
        '''Returns a bool indicating whether the button has been clicked, followed by either self.stored_value (if button was clicked) or "" (if it wasn't)'''
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.pressed = False
            if self.rect.collidepoint(event.pos):
                return True, self.stored_value
        return False, ""


class target_class:
    def __init__(self, pos, radius) -> None:
        '''Stores targets, which are circles that appear in the PyGame window that dissapear when the cursor touches them.'''
        self.pos, self.radius = pos, radius
    def draw(self, window, dist_to_cursor:float) -> None:
        '''Draws the target to the PyGame window. The window still needs to be flipped (using pg.display.flip()) for this to appear.'''
        dist_relative_to_screen = dist_to_cursor/(sqrt(pg.display.get_window_size()[0]**2 + pg.display.get_window_size()[1]**2))
        gradient = 1 # You can adust this to change the distance at which the target becomes more red
        r = max(min(int(-log(dist_relative_to_screen*gradient)/7*255)+50, 255), 0)
        g, b = 50, 255-r
        pg.draw.circle(window, [r,g,b], (self.pos[0],self.pos[1]), self.radius, 0)

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
        pg.draw.circle(window, (130,150,25), (self.pos[0],self.pos[1]), self.radius, 0)

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
        window.blit(self.font.render("Enter your username:", True, pg.Color(200,220,200)), (self.rect.x, self.rect.y-50)) # Blit the prompt text
        window.blit(self.txt_surface, (self.rect.x+5, self.rect.y+2)) # Blit the input box
        pg.draw.rect(window, self.colour, self.rect, 2) # Blit the rect

###
def update_menu_display(window, font, button_list):
    window.fill((30, 30, 30))
    window.blit(font.render("Select difficulty:", True, pg.Color(200, 220, 200)), (20,20)) # Blit the prompt text
    for button in button_list:
        button.draw(window)
    pg.display.flip()

def update_game_display(window, cursor: cursor_class, target_bank: list) -> None:
    '''Updates all aspects of the window during the reaction game, including the mouse and targets. Also slips the window.'''
    window.fill((30, 30, 30))
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
    window.fill((30, 30, 30))
    font_size, colour = 25, pg.Color(200, 220, 200)
    font = pg.font.SysFont("monospace", font_size)
    x_pos, y_pos = 20, 20
    for line_pos in range(len(text_display_bank)):
        window.blit(font.render(text_display_bank[line_pos], True, colour), (x_pos, font_size*line_pos+y_pos))
    pg.display.flip()

###
def main_menu(window) -> tuple[list, int]:
    '''The main loop for the main menu. Returns the window size for the game and the number of targets as a integer'''
    font_size = 25
    font = pg.font.SysFont("monospace", font_size)
    button_list = []
    for i in range(3):
        button_list.append(button_class([20, 60+(font_size+45)*i], font, ["Easy", "Medium", "Hard"][i], i+1))
    running_menu = True
    while running_menu:
        for event in pg.event.get():
            for button in button_list:
                button_click, difficulty_level = button.handle_event(event)
                if button_click:
                    return difficulty_level
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                running_menu = False
                pg.quit()
                break
        update_menu_display(window, font, button_list)

def main_game(window, target_count:int) -> float:
    '''The main loop for the reaction time game. Returns the game_time, which is the amount of time that the game took as a float (rounded to 3 decimal places).'''
    cursor = cursor_class(10)
    target_bank = []
    for i in range(target_count):
        pos_x = randint(int(pg.display.get_window_size()[0]*0.1),int(pg.display.get_window_size()[0]*0.9))
        pos_y = randint(int(pg.display.get_window_size()[1]*0.1),int(pg.display.get_window_size()[1]*0.9))
        target_bank.append(target_class([pos_x, pos_y], 8))
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
        window.fill((30, 30, 30))
        input_box.draw(window)
        pg.display.flip()

def tuple_to_list(x):
    temp, x = list(x), []
    for i in temp[0]: x.append(i)
    return x

def main_db(window, game_time, username:str, difficulty_level:int) -> None:
    game_time = int(game_time*1000)
    difficulty = ["Easy", "Medium", "Hard"][difficulty_level-1]
    '''The code managing updating the MySQL servers, then displaying the leaderboard.'''
    conn = mysql.connector.connect(host="192.168.1.127", user="root", password="ytkxp2KMmXZU75mufMCP", database="leaderboard_db")
    db = db_class(conn, "tbl_leaderboard")
    db.delete_table()
    text_display_bank = [f"You won in {game_time/1000} seconds"]
    db.create_table("userName VARCHAR(15)", "difficulty INT(3)", "time INT(255)", "PRIMARY KEY (userName, difficulty)")
    user_data = db.get_rec(where=f"""userName = \"{username}\" AND difficulty = {difficulty_level}""")
    if user_data == "" or user_data == []:
        db.add_rec(username, difficulty_level, game_time)
        user_data = [username, difficulty_level, game_time]
        text_display_bank += [f"Record added for {username} on {difficulty.lower()} difficuly."]
    else:
        user_data = tuple_to_list(user_data)
        #print("user_data", user_data, type(user_data))
        if game_time < user_data[2]:
            time_change = str(round(user_data[2]-game_time, 3))
            text_display_bank += ["", "Well Done! You beat your previous fastest", f"time by {time_change/1000} seconds."]
            db.update_rec("time", game_time, f"""userName = \"{username}\" AND difficulty = {difficulty_level}""")
            #print("user_data, game_time", user_data, game_time)
            user_data[2] = game_time
        else: text_display_bank += ["", f"Your fastest time at {difficulty.lower()} difficulty", f"is {user_data[2]/1000} seconds. Keep trying!"]

    text_display_bank += ["", "Leaderboard:"]
    #print("database:", db.get_rec(order="time"))
    leaderboard_bank = db.get_rec("*", where=f"difficulty = {difficulty_level}", order="time", limit=10)
    for position in range(len(leaderboard_bank)):
        text_display_bank += [f"{position+1} - {leaderboard_bank[position][0]} with a time of {leaderboard_bank[position][2]/1000} seconds"]
    #print("user_data", user_data)
    #print("user_pos list", db.get_rec("*", where=f"time <= {user_data[2]} AND difficulty = {difficulty_level}", order="time"))
    #print("user_pos list", db.get_rec("COUNT(*)", where=f"time <= {user_data[2]} AND difficulty = {difficulty_level}", order="time")[0][0])
    user_pos = db.get_rec("COUNT(*)", where=f"time <= {user_data[2]} AND difficulty = {difficulty_level}", order="time")[0][0]
    text_display_bank += ["", f"Your leaderboard position: {user_pos+1}"]
    text_display_bank += ["(note: may be slightly inaccurate since SQL", " can't compare floats very well)"]
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
    #pg.display.get_window_size()
    pg.init()
    window = pg.display.set_mode([800,600])
    difficulty_level = main_menu(window)
    window, target_count = pg.display.set_mode([difficulty_level*50+700, difficulty_level*50+500]), 5+difficulty_level*2
    game_time = main_game(window, target_count)
    window = pg.display.set_mode([800,600])
    username = main_input(window)
    main_db(window, game_time, username, difficulty_level)
    pg.quit()