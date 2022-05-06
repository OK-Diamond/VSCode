import pygame as pg
from random import randint, shuffle
from math import floor

class window_class:
    def __init__(self, width, height):
        self.display = pg.display.set_mode((width, height))
        self.height = height
        self.width = width

class board_class:
    def __init__(self, x, y):
        self.x_len, self.y_len = x, y
        self.board_list = [[0 for x in range(self.x_len)] for y in range(self.y_len)]
        ''' board key: 
                -- = blank
                ct = colour type
                colour can be blue, green, red, yellow
                type can be normal or detonator
        '''
        
    def display(self): # Used for bugfixing
        for i in self.board_list:
            for j in i:
                print(j, end="")
            print()
    def draw(self):
        pass
        




def pg_assemble_display(pg_font, ms_board, revealed_board, window):
    rect_size = [(window.width)/ms_board.x_len, (window.height)/ms_board.y_len]
    colour_bank = {"b":[0, 0, 200], "g":[0, 200, 0], "r":[250, 25, 25], "y":[200, 200, 0], "-":[150,150,150]}
    for i in range(len(ms_board.board_list)):
        for j in range(len(ms_board.board_list[i])):
            tile = ms_board.board_list[i][j]
            rect = pg.Rect(j*rect_size[0], i*rect_size[1], rect_size[0], rect_size[1])
            
            pg.draw.rect(window.display, colour_bank(str.lower(tile)), rect, 0) # Tile
            pg.draw.rect(window.display, [0,0,0], rect, 1) # Black border
            window.display.blit(pg_font["font"].render(str(tile), 1, [0,0,0]), (int((j+0.5)*rect_size[0]-len(str(tile))*pg_font["font_size"]/6), int((i+0.5)*rect_size[1] - 0.5*pg_font["font_size"]))) # Tile Value
    pg.display.flip() # Updates the window


def initialise(tile_size, grid_dimensions, bomb_percent):
    bomb_count = floor(grid_dimensions[0]*grid_dimensions[1]*bomb_percent/100)
    
    pg.init() # Initalises PyGame
    pg.display.set_caption("   Minesweeper")
    pg_font = {"font_size":int(tile_size/1.3), "font_type":"monospace"}
    pg_font["font"] = pg.font.SysFont(pg_font["font_type"], pg_font["font_size"])
    
    window = window_class(grid_dimensions[0]*tile_size, grid_dimensions[1]*tile_size)
    window.display.fill((255, 255, 255))
    
    ms_board = minesweeper_board_class(grid_dimensions[0], grid_dimensions[1])
    ms_board.populate(bomb_count)
    ms_board.display()
    
    revealed_board = board_class(grid_dimensions[0], grid_dimensions[1])
    ms_board, revealed_board = search_for_start_square(ms_board, revealed_board, bomb_count)


    print("Controls:\nLeft-click: Reveal tile\nRight-click on an unrevealed tile: Place a flag\nMiddle-click a revealed tile: Reveal all unflagged adjacent tiles")
    return pg_font, ms_board, revealed_board, window, bomb_count

def search_for_start_square(ms_board, revealed_board, bomb_count):
    start_square_found, start_search_count = False, 0
    while not start_square_found:
        i = randint(2, len(ms_board.board_list)-3)
        j = randint(2, len(ms_board.board_list[i])-3)
        #print("[i,j]",[i,j])
        if ms_board.board_list[i][j] == 0:
            revealed_board.board_list[i][j] = 1
            revealed_board.board_list = reveal_nearby([i, j], ms_board.board_list, revealed_board.board_list)
            start_square_found = True
        #start_search_count += 1
        #print("start_search_count", start_search_count)
        #if start_search_count > 100: # If the search takes too long, generate a new board and start again
        #    ms_board.populate(bomb_count)
        #    start_search_count = 0
    return ms_board, revealed_board

    

def check_for_game_end(ms_board_list, rev_board_list, bomb_count):
    safe_tiles_found = 0
    for i in range(len(ms_board_list)):
        for j in range(len(ms_board_list[i])):
            if rev_board_list[i][j] == 1:
                if ms_board_list[i][j] == "X":
                    print("Game over: You lose!")
                    return "lost"
                else: safe_tiles_found += 1
    if safe_tiles_found == len(ms_board_list)*len(ms_board_list[0]) - bomb_count:
        print("Game Over: You Win!")
        return "won"
    else:
        return ""

def reveal_sequence(pg_font, ms_board, revealed_board, window):
    unrev_location_bank = []
    for i in range(len(ms_board.board_list)):
        for j in range(len(ms_board.board_list[i])):
            if revealed_board.board_list[i][j] != 1:
                unrev_location_bank.append([i,j])
    shuffle(unrev_location_bank)

    while len(unrev_location_bank)>0:
        [i,j] = unrev_location_bank.pop(0)
        revealed_board.board_list[i][j] = 1
        pg_assemble_display(pg_font, ms_board, revealed_board, window)
        pg.display.flip()
        pg.time.delay(2)
        

def main():
    difficulty = int(input("Enter difficulty from 1 (easy) to 10 (very hard)"))
    
    tile_size = 60
    grid_dimensions = [floor(8+difficulty/3),floor(8+difficulty/3)]
    bomb_percent = int(15+difficulty*1.5)
    pg_font, ms_board, revealed_board, window, bomb_count = initialise(tile_size, grid_dimensions, bomb_percent)
    
    ms_board.display()
    running = True
    while running:
        for event in pg.event.get():
            '''if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    revealed_board.board_list = [[0 for i in range(grid_dimensions[0])] for j in range(grid_dimensions[1])]
                    ms_board.populate(bomb_count)
                    ms_board, revealed_board = search_for_start_square(ms_board, revealed_board, bomb_count)'''
            if event.type == pg.MOUSEBUTTONUP:
                #print(event.button)
                click_pos = pg.mouse.get_pos()
                target_pos = [floor(click_pos[1]*ms_board.y_len/window.height), floor(click_pos[0]*ms_board.x_len/window.width)]
                if event.button == 3:
                    if revealed_board.board_list[target_pos[0]][target_pos[1]] == 2:
                        revealed_board.board_list[target_pos[0]][target_pos[1]] = 0
                    elif revealed_board.board_list[target_pos[0]][target_pos[1]] == 0:
                        revealed_board.board_list[target_pos[0]][target_pos[1]] = 2
                elif event.button == 1:
                    revealed_board.board_list[target_pos[0]][target_pos[1]] = 1
                    if ms_board.board_list[target_pos[0]][target_pos[1]] == 0:
                        revealed_board.board_list = reveal_nearby(target_pos, ms_board.board_list, revealed_board.board_list)
                elif event.button == 2 and revealed_board.board_list[target_pos[0]][target_pos[1]] == 1:
                    flag_count = 0
                    #print("target_pos",target_pos)
                    for i in range(target_pos[0]-1, target_pos[0]+2):
                        for j in range(target_pos[1]-1, target_pos[1]+2):
                            if [i,j] != target_pos:
                                try: flag_count += (1 if revealed_board.board_list[i][j] == 2 else 0)
                                except: pass
                    if ms_board.board_list[target_pos[0]][target_pos[1]] == flag_count:
                        revealed_board.board_list = reveal_nearby(target_pos, ms_board.board_list, revealed_board.board_list)
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                break
        game_end = check_for_game_end(ms_board.board_list, revealed_board.board_list, bomb_count)
        if game_end == "won":
            # Make some confetti or something
            running = False
        elif game_end == "lost":
            running = False
        pg_assemble_display(pg_font, ms_board, revealed_board, window)
    reveal_sequence(pg_font, ms_board, revealed_board, window)
        
if __name__ == "__main__":
    main()


