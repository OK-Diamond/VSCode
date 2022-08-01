import pygame as pg
from random import randint, shuffle
from math import floor
from time import sleep
from os import path as os_path
from os import getcwd
import slider_input
#import wx

class window_class:
    def __init__(self, width, height):
        self.display = pg.display.set_mode((width, height))
        self.height = height
        self.width = width
        return

class board_class:
    def __init__(self, x, y):
        self.x_len, self.y_len = x, y
        self.board_list = [[0 for x in range(self.x_len)] for y in range(self.y_len)]
        return
        
    def display(self): # Used for bugfixing
        for i in self.board_list:
            for j in i:
                print(j, end="")
            print()
        return
        

class minesweeper_board_class(board_class):
    def __init__(self, x, y):
        board_class.__init__(self, x, y)
        
    def populate(self, mine_count):
        self.board_list = [[0 for i in range(self.x_len)] for j in range(self.y_len)]
        # Populate mines
        while mine_count > 0:
            i = randint(0, len(self.board_list)-1)
            j = randint(0, len(self.board_list[i])-1)
            if self.board_list[i][j] != "X":
                self.board_list[i][j] = "X"
                mine_count -= 1
        # Fill values of other tiles
        old_board = []
        for i in range(len(self.board_list)):
            old_board.append([])
            for j in self.board_list[i]:
                old_board[i].append(j)
        self.__update_corners(old_board) # Corners
        self.__update_edges(old_board) # Edges
        self.__update_centre(old_board) # Centre
        return
        
    def __update_corners(self, old_board):
        if self.board_list[0][0] != "X": # Top-left
            self.board_list[0][0] = 0
            for tile in [old_board[0][1], old_board[1][0], old_board[1][1]]:
                if tile == "X":
                    self.board_list[0][0] += 1
        if self.board_list[0][-1] != "X": # Top-right
            self.board_list[0][-1] = 0
            for tile in [old_board[0][-2], old_board[1][-1], old_board[1][-2]]:
                if tile == "X":
                    self.board_list[0][-1] += 1
        if self.board_list[-1][0] != "X": # Bottom-left
            self.board_list[-1][0] = 0
            for tile in [old_board[-2][0], old_board[-1][1], old_board[-2][1]]:
                if tile == "X":
                    self.board_list[-1][0] += 1
        if self.board_list[-1][-1] != "X": # Bottom-left
            self.board_list[-1][-1] = 0
            for tile in [old_board[-1][-2], old_board[-2][-1], old_board[-2][-2]]:
                if tile == "X":
                    self.board_list[-1][-1] += 1
        return
    def __update_edges(self, old_board):
        for i in range(1, len(old_board[0])-1): # Top
            if self.board_list[0][i] != "X":
                self.board_list[0][i] = 0
                for tile in [old_board[0][i-1], old_board[0][i+1], old_board[1][i-1], old_board[1][i], old_board[1][i+1]]:
                    if tile == "X":
                        self.board_list[0][i] += 1
        for i in range(1, len(old_board)-1): # Left
            if self.board_list[i][0] != "X":
                self.board_list[i][0] = 0
                for tile in [old_board[i-1][0], old_board[i+1][0], old_board[i-1][1], old_board[i][1], old_board[i+1][1]]:
                    if tile == "X":
                        self.board_list[i][0] += 1
        for i in range(1, len(old_board[-1])-1): # Bottom
            if self.board_list[-1][i] != "X":
                self.board_list[-1][i] = 0
                for tile in [old_board[-1][i-1], old_board[-1][i+1], old_board[-2][i-1], old_board[-2][i], old_board[-2][i+1]]:
                    if tile == "X":
                        self.board_list[-1][i] += 1
        for i in range(1, len(old_board)-1): # Right
            if self.board_list[i][-1] != "X":
                self.board_list[i][-1] = 0
                for tile in [old_board[i-1][-1], old_board[i+1][-1], old_board[i-1][-2], old_board[i][-2], old_board[i+1][-2]]:
                    if tile == "X":
                        self.board_list[i][-1] += 1
        return
    def __update_centre(self, old_board):
        for y in range(1, len(old_board)-1):
            for x in range(1, len(old_board[y])-1):
                if self.board_list[y][x] != "X":
                    self.board_list[y][x] = 0
                    for tile in [old_board[y-1][x-1], old_board[y-1][x], old_board[y-1][x+1], old_board[y][x-1], old_board[y][x+1], old_board[y+1][x-1], old_board[y+1][x], old_board[y+1][x+1]]:
                        if tile == "X":
                            self.board_list[y][x] += 1
        return

def reveal_nearby(pos, ms_board_list, revealed_board_list):
    revealed_board_list[pos[0]][pos[1]] = 1
    for i in range(pos[0]-1, pos[0]+2):
        for j in range(pos[1]-1, pos[1]+2):
            if [i,j] != pos and (i>=0 and i<len(ms_board_list)) and (j>=0 and j<len(ms_board_list[0]) and revealed_board_list[i][j] == 0):
                if ms_board_list[i][j] == 0:
                    revealed_board_list = reveal_nearby([i, j], ms_board_list, revealed_board_list)
                revealed_board_list[i][j] = 1
    return revealed_board_list

def pg_assemble_display(ms_board, revealed_board, display_info, window):
    rect_size = display_info["rect_size"]
    for i in range(len(ms_board.board_list)):
        for j in range(len(ms_board.board_list[i])):
            tile = ms_board.board_list[i][j]
            rect = pg.Rect(j*rect_size[0], i*rect_size[1], rect_size[0], rect_size[1])
            if revealed_board.board_list[i][j] == 0:
                pg.draw.rect(window.display, [100, 100, 100], rect, 0) # Tile
                pg.draw.rect(window.display, [0, 0, 0], rect, 1) # Black border
            elif revealed_board.board_list[i][j] == 1:
                pg.draw.rect(window.display, ([200, 0, 0] if tile == "X" else [200, 200, 200]), rect, 0) # Tile
                pg.draw.rect(window.display, [0, 0, 0], rect, 1) # Black border
                if tile == "X":
                    window.display.blit(display_info["bomb_image"], (j*rect_size[0]+1, i*rect_size[1]+1))
                else:
                    rgb = [min(tile*5%255, 150), min(tile*25%255, 150), min(tile*50%255, 150)]
                    window.display.blit(display_info["font"].render(str(tile), 1, rgb), (int((j+0.5)*rect_size[0]-len(str(tile))*display_info["font_size"]/6), int((i+0.5)*rect_size[1] - 0.5*display_info["font_size"]))) # Tile Value
            elif revealed_board.board_list[i][j] == 2:
                pg.draw.rect(window.display, [100, 100, 100], rect, 0) # Tile
                pg.draw.rect(window.display, [0, 0, 0], rect, 1) # Black border
                window.display.blit(display_info["flag_image"], (j*rect_size[0]+1, i*rect_size[1]+1))
    pg.display.flip() # Updates the window
    return


def initialise(tile_size, grid_dimensions, bomb_percent, window):
    bomb_count = floor(grid_dimensions[0]*grid_dimensions[1]*bomb_percent/100)
    
    pg.display.set_caption("   Minesweeper")
    
    ms_board = minesweeper_board_class(grid_dimensions[0], grid_dimensions[1])
    ms_board.populate(bomb_count)
    revealed_board = board_class(grid_dimensions[0], grid_dimensions[1])
    ms_board, revealed_board = search_for_start_square(ms_board, revealed_board, bomb_count)

    file_location = os_path.realpath(os_path.join(getcwd(), os_path.dirname(__file__))) # Obtains the path of the program.
    display_info = {}
    display_info["rect_size"] = [(window.width)/ms_board.x_len, (window.height)/ms_board.y_len]
    display_info["flag_image"] = pg.transform.scale(pg.image.load(os_path.join(file_location, "flag.png")).convert_alpha(), (display_info["rect_size"][0]-2, display_info["rect_size"][1]-2))
    display_info["bomb_image"] = pg.transform.scale(pg.image.load(os_path.join(file_location, "bomb.png")).convert_alpha(), (display_info["rect_size"][0]-2, display_info["rect_size"][1]-2))

    display_info["font_size"] = int(tile_size/1.3)
    display_info["font_type"] = "monospace"
    display_info["font"] = pg.font.SysFont(display_info["font_type"], display_info["font_size"])

    print("Controls:\nLeft-click: Reveal tile\nRight-click on an unrevealed tile: Place a flag\nMiddle-click a revealed tile: Reveal all unflagged adjacent tiles")
    
    return ms_board, revealed_board, display_info, bomb_count

def search_for_start_square(ms_board: minesweeper_board_class, revealed_board, bomb_count):
    start_square_found, start_search_count = False, 0
    while not start_square_found:
        i = randint(2, len(ms_board.board_list)-3)
        j = randint(2, len(ms_board.board_list[i])-3)
        if ms_board.board_list[i][j] == 0:
            revealed_board.board_list[i][j] = 1
            revealed_board.board_list = reveal_nearby([i, j], ms_board.board_list, revealed_board.board_list)
            start_square_found = True
        start_search_count += 1
        if start_search_count > 100: # If the search takes too long, generate a new board and start again
            ms_board.populate(bomb_count)
            start_search_count = 0
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

def reveal_sequence(ms_board, revealed_board, display_info, window):
    for i in range(len(ms_board.board_list)):
        for j in range(len(ms_board.board_list[i])):
            revealed_board.board_list[i][j] = 1
        pg_assemble_display(ms_board, revealed_board, display_info, window)
        sleep(0.2)
    return

def main():
    info_object = pg.display.Info() # Obtains the screen size
    #difficulty = slider_input.main([1, 10])

    print("info_object", info_object)
    quit()

    print("info_object.current_w, info_object.current_h", info_object.current_w, info_object.current_h)
    
    
    grid_dimensions = [5+difficulty,5+difficulty]
    print("grid_dimensions", grid_dimensions)
    tile_size = min(60, int((0.8*info_object.current_h)/grid_dimensions[1]))
    print("tile_size", tile_size)
    window = window_class(grid_dimensions[0]*tile_size, grid_dimensions[1]*tile_size)
    window.display.fill((255, 255, 255))
    bomb_percent = 20 #int(15+difficulty*1.5)
    ms_board, revealed_board, display_info, bomb_count = initialise(tile_size, grid_dimensions, bomb_percent, window)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                running = False
                pg.quit()
                quit()
            if event.type == pg.MOUSEBUTTONUP:
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
                    for i in range(target_pos[0]-1, target_pos[0]+2):
                        for j in range(target_pos[1]-1, target_pos[1]+2):
                            if [i,j] != target_pos:
                                try:
                                    flag_count += (1 if revealed_board.board_list[i][j] == 2 else 0)
                                except:
                                    pass
                    if ms_board.board_list[target_pos[0]][target_pos[1]] == flag_count:
                        revealed_board.board_list = reveal_nearby(target_pos, ms_board.board_list, revealed_board.board_list)
        game_end = check_for_game_end(ms_board.board_list, revealed_board.board_list, bomb_count)
        if game_end == "won" or game_end == "lost":
            running = False
        pg_assemble_display(ms_board, revealed_board, display_info, window)
    reveal_sequence(ms_board, revealed_board, display_info, window)
    sleep(2)
    return
        
if __name__ == "__main__":
    pg.init() # Initalises PyGame
    main()
