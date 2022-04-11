import pygame as pg
from math import sqrt, log
from random import randint
from os import system, name
from time import time as get_time
import sql_commands
from sqlite3 import connect as sql_conn

class window_class:
    def __init__(self, width, height):
        self.display, self.height, self.width = pg.display.set_mode((width, height)), height, width

class target_class:
    def __init__(self, pos, radius):
        self.pos, self.radius = pos, radius
    def draw(self, window, dist_to_mouse):
        dist_relative_to_screen = dist_to_mouse/(sqrt(window.width**2 + window.height**2))
        gradient = 0.5
        
        #r = max(min(int((gradient*255-dist_to_mouse)/gradient), 254), 0)
        r = max(min(int(-log(dist_relative_to_screen*gradient)/7*255)+50, 255), 0)
        g = 50
        #b = min(int(dist_to_mouse/gradient), 254)
        b = 255-r
        #print("rgb",[r,g,b])
        pg.draw.circle(window.display, [r,g,b], (self.pos[0],self.pos[1]), self.radius, 0)

class mouse_class:
    def __init__(self, radius):
        self.radius, self.pos = radius, pg.mouse.get_pos()
    def update_pos(self):
        self.pos = pg.mouse.get_pos()
    def draw(self, window):
        self.update_pos()
        pg.draw.circle(window.display, (130,150,25), (self.pos[0],self.pos[1]), self.radius, 0)

class input_box_class:
    def __init__(self, x_pos, y_pos, width, height, font, text=""):
        self.rect, self.colour = pg.Rect(x_pos, y_pos, width, height), pg.Color("lightskyblue3")
        self.font, self.text = font, text
        self.txt_surface = self.font.render(self.text, True, self.colour)
        self.active = False
    def handle_event(self, event):
        text_to_return = ""
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos): self.active = not self.active # Toggle whether the text box is active or not
            else: self.active = False
            self.colour = pg.Color("dodgerblue2") if self.active else pg.Color("lightskyblue3") # Change the current colour of the input box
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_RETURN: text_to_return, self.text = str(self.text), ""
            elif event.key == pg.K_BACKSPACE: self.text = self.text[:-1]
            elif len(self.text) < 15: self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, self.colour) # Re-render the text
        return text_to_return
    def update(self): # Resize the box if the text is too long
        self.rect.w = max(200, self.txt_surface.get_width()+10)
    def draw(self, window):
        window.display.blit(self.font.render("Enter your username:", True, pg.Color(200,220,200)), (self.rect.x, self.rect.y-50)) # Blit the prompt text
        window.display.blit(self.txt_surface, (self.rect.x+5, self.rect.y+2)) # Blit the input box
        pg.draw.rect(window.display, self.colour, self.rect, 2) # Blit the rect

def update_game_display(window, mouse, target_bank):
    window.display.fill((30, 30, 30))
    for i in range(len(target_bank)-1,-1,-1):
        target = target_bank[i]
        dist_to_mouse = int(sqrt(((target.pos[0]-mouse.pos[0])**2) + ((target.pos[1]-mouse.pos[1])**2)))
        if dist_to_mouse < target.radius+mouse.radius: target_bank.pop(i)
        else: target.draw(window, dist_to_mouse)
    mouse.draw(window)
    pg.display.flip() # Updates the window

def display_paragraph(window, text_display_bank):
    window.display.fill((30, 30, 30))
    font_size = 25
    font = pg.font.SysFont("monospace", font_size)
    colour = pg.Color(200, 220, 200)
    x_pos = 20
    y_pos = 20
    for line_pos in range(len(text_display_bank)):
        window.display.blit(font.render(text_display_bank[line_pos], True, colour), (x_pos, font_size*line_pos+y_pos))
    pg.display.flip()

def main_game(window):
    mouse = mouse_class(10)
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
        mouse.update_pos()
        update_game_display(window, mouse, target_bank)
        if len(target_bank) == 0:
            game_time = round(get_time()-start_time, 3)
            running_game = False
    return game_time


def main_input(window):
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
        input_box.update()
        window.display.fill((30, 30, 30))
        input_box.draw(window)
        pg.display.flip()




def main_db(window, game_time, username):
    db, table_name = sql_commands.db_class(sql_conn("leaderboard.db")), "tblLeaderboard"
    text_display_bank = ["You won in "+str(game_time)+" seconds"]
    db.create_table(table_name)
    rec_exists, user_data = db.get_rec(table_name, username)
    if rec_exists:
        if game_time < user_data[1]:
            time_change = str(round(user_data[1]-game_time, 3))
            text_display_bank += ["", "Well Done! You beat your previous fastest", "time by "+time_change+" seconds."]
            db.update_rec(table_name, "time", game_time, "userName", username)
        else: text_display_bank += ["", "Your fastest time", "is "+str(user_data[1])+" seconds. Keep trying!"]
    else: db.add_rec(username, game_time, table_name)
    text_display_bank += ["","Leaderboard:"]+db.get_leaderboard(table_name)+["","Your leaderboard position: "+str(db.get_position(table_name,"time","userName",username))] + ["Press Q to quit"]
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