import pygame as pg
from random import randint
from time import time as get_time
from math import floor

class gameboard_class:
    def __init__(self, size) -> None:
        self.board = [[0 for i in range(size[0])] for j in range(size[1])]
        '''Tile types: 0 = Empty, 1 = Player-controlled falling  block, 2 = Placed block, 3 = Falling block (not player controlled)'''
        display_size = pg.display.get_window_size()
        self.draw_info = {"rect_size": [(display_size[0]*0.7)/size[0],(display_size[1]*0.9)/size[1]], "y_offset": round(display_size[1]*0.05)}

    def get_board(self) -> None:
        '''Return the board'''
        return self.board
    
    def print_board(self) -> None:
        '''Print the board'''
        print("\n\n\n")
        for i in self.board:
            for j in i: print(j, end="")
            print()
    
    def check_for_block_finish(self, blocktype:int) -> bool:
        block_finish = False
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == blocktype and (i == len(self.board)-1 or self.board[i+1][j] == 2):
                    block_finish = True
        

        if block_finish: # If a match has been found and the blocks are moving downwards.
            self.convert_board_tiles(1, 2) # 'Solidify' all of the player-controlled blocks.
        print("check_for_block_finish with blocktype", blocktype, ":", block_finish)
        return block_finish

    def check_for_row_complete(self) -> int:
        for i in range(len(self.board)):
            count = 0
            for j in range(len(self.board[i])):
                if self.board[i][j] == 2:
                    count += 1
            if count == len(self.board[i]):
                #print("check_for_row_complete", i)
                return i
        return -1
    
    def remove_complete_rows(self) -> None:
        '''Removes complete rows and moves rows above downwards.'''
        row_to_remove = self.check_for_row_complete() # Check if a row is complete and needs to be removed.
        while row_to_remove != -1:
            for i in range(len(self.board[row_to_remove])):
                self.board[row_to_remove][i] = 0
            for i in range(row_to_remove-1, 0, -1):
                for j in range(len(self.board[i])):
                    if self.board[i][j] == 2:
                        self.board[i][j] = 3
            self.move_blocks(3, "down", True)
            self.convert_board_tiles(3, 2)
            row_to_remove = self.check_for_row_complete()
    
    def move_blocks_down(self, blocktype, reiterate=False):
        block_stopped = False
        block_found = False # This prevents a recursion error on an empty board.
        new_board = self.board
        for i in range(len(new_board)-2, -1, -1):
            for j in range(len(new_board[i])-1, -1, -1):
                if new_board[i][j] == blocktype:
                    block_found = True
                    if new_board[i+1][j] != 2:
                        new_board[i][j] = 0
                        new_board[i+1][j] = blocktype
                    else:
                        block_stopped = True

        if block_stopped == False:
            self.board = new_board
            if reiterate and block_found == True:
                if not self.check_for_block_finish(blocktype):
                    self.move_blocks_down(blocktype, reiterate)

    def move_blocks_across(self, blocktype, direction, structure_size, lr_offset):
        block_stopped = False
        new_board = self.board
        max_right_movement = len(self.board)+1 - structure_size

        print("lr_offset", lr_offset)
        if direction == "right" and lr_offset+1 < max_right_movement:
            lr_offset += 1
            for i in range(len(new_board)-1, -1, -1):
                for j in range(len(new_board[i])-2, -1, -1):
                    if new_board[i][j] == blocktype:
                        if new_board[i][j+1] != 2:
                            new_board[i][j] = 0
                            new_board[i][j+1] = blocktype
                        else:
                            block_stopped = True
        if direction == "left" and lr_offset > 0:
            lr_offset -= 1
            for i in range(len(new_board)):
                for j in range(1, len(new_board[i])):
                    if new_board[i][j] == blocktype:
                        if new_board[i][j-1] != 2:
                            new_board[i][j] = 0
                            new_board[i][j-1] = blocktype
                        else:
                            block_stopped = True
        if block_stopped == False:
            self.board = new_board
        return lr_offset

    def convert_board_tiles(self, blocktype_1, blocktype_2):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == blocktype_1:
                    self.board[i][j] = blocktype_2

    def draw(self, display:pg.Surface) -> None:
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 0: rgb = [50,50,50]
                elif self.board[i][j] == 1: rgb = [100,100,150]
                elif self.board[i][j] == 2: rgb = [110,110,110]
                else: rgb = [255,50,50]
                rect = pg.Rect(
                    self.draw_info["rect_size"][0]*j, 
                    self.draw_info["rect_size"][1]*i+self.draw_info["y_offset"], 
                    self.draw_info["rect_size"][0], 
                    self.draw_info["rect_size"][1])
                pg.draw.rect(display, rgb, rect)

class structure_manager_class:
    def __init__(self, board_width):
        self.structure_bank = [
            [ # 0 Rotations
                [[0,0,0], [1,1,0], [0,1,1]], 
                [[0,0,0], [0,1,1], [1,1,0]], 
                [[0,0,0,0], [0,0,0,0], [0,0,0,0], [1,1,1,1]], 
                [[1,1], [1,1]], 
                [[0,0,0],[0,0,1],[1,1,1]], 
                [[0,0,0],[1,0,0],[1,1,1]], 
                [[1,1,1], [0,1,0], [0,0,0]]
            ], 
            [ # 1 Rotation
                [[0,1,0], [1,1,0], [1,0,0]], 
                [[1,0,0], [1,1,0], [0,1,0]], 
                [[1,0,0,0], [1,0,0,0], [1,0,0,0], [1,0,0,0]], 
                [[1,1], [1,1]], 
                [[1,1,1], [0,0,1], [0,0,0]], 
                [[1,1,1,],[1,0,0],[0,0,0]], 
                [[1,1,1,],[0,1,0],[0,0,0]]
            ], 
            [ # 2 Rotations
                [[0,0,0], [1,1,0], [0,1,1]], 
                [[0,0,0], [0,1,1], [1,1,0]], 
                [[0,0,0,0], [0,0,0,0], [0,0,0,0], [1,1,1,1]], 
                [[1,1], [1,1]], 
                [[0,0,0], [1,1,1], [1,0,0]], 
                [[0,0,0], [1,1,1], [0,0,1]], 
                [[0,0,0], [1,1,1], [0,1,0]]
            ],
            [ # 3 Rotations
                [[0,1,0], [1,1,0], [1,0,0]], 
                [[1,0,0], [1,1,0], [0,1,0]], 
                [[1,0,0,0], [1,0,0,0], [1,0,0,0], [1,0,0,0]], 
                [[1,1], [1,1]], 
                [[1,0,0], [1,1,1], [0,0,0]], 
                [[0,0,1], [1,1,1], [0,0,0]], 
                [[0,1,0], [1,1,1], [0,0,0]]
            ]
        ]
        self.current_structure, self.next_structure = 0, 3
        self.current_layer = 0
        self.rotation, self.lr_offset = 0, 0
        self.lr_offset_default = floor(board_width/2)
    def load_next_structure(self):
        self.current_structure = self.next_structure
        self.next_structure = randint(0, len(self.structure_bank[0])-1)
        self.current_layer, self.rotation = 0, 0
        self.lr_offset = self.lr_offset_default
    def calc_next_layer(self, board):
        if self.current_layer >= self.get_structure_size()-1:
                return [0 for i in board[0]]
        layer = self.structure_bank[self.rotation][self.current_structure][self.current_layer]
        self.current_layer += 1
        print("self.current_layer", self.current_layer, self.get_structure_size())
        left_space = [0 for i in range(self.lr_offset)]
        right_space = [0 for i in range(len(board[0])-len(layer)-len(left_space))]
        #print("left_space, layer, right_space", left_space, layer, right_space)
        to_return = []
        for i in left_space:
            to_return.append(i)
        for i in layer:
            to_return.append(i)
        for i in right_space:
            to_return.append(i)
        #print("to_return", to_return)
        return to_return
    def get_next_layer(self, board):
        layer = self.calc_next_layer(board)
        print("layer", layer)
        for i in range(len(layer)):
            if layer[i] == 1:
                if board[0][i] != 0:
                    return board, True
                else:
                    board[0][i] = layer[i]
        return board, False
    def get_structure_size(self):
        return len(self.structure_bank[self.rotation][self.current_structure][self.current_layer])
    

def update_pg_display(display, board) -> None:
    display.fill([30, 30, 30])
    board.draw(display)
    pg.display.update()

def main() -> None:
    # -- Initialisation --
    pg.init()
    display = pg.display.set_mode([600, 400])
    gameboard = gameboard_class([8,8]) # Initialise the board.
    pg.display.set_caption("Tetris")
    active_tile, game_running = False, True
    old_time = get_time()
    structure_manager = structure_manager_class(len(gameboard.get_board()))
    structure_manager.load_next_structure()

    # -- Game --
    while game_running:
        update_pg_display(display, gameboard)
        active_tile = False
        for i in gameboard.board:
            for j in i:
                if j == 1:
                    active_tile = True

        if not active_tile:
            structure_manager.load_next_structure()
            gameboard.board, game_over = structure_manager.get_next_layer(gameboard.board)
            if game_over:
                print("Game over")
                game_running = False
                pg.quit()
                break
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    print("Game over")
                    game_running = False
                    pg.quit()
                    break
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a or event.key == pg.K_LEFT:
                        structure_manager.lr_offset = structure_manager.lr_offset = gameboard.move_blocks_across(1, "left", structure_manager.get_structure_size(), structure_manager.lr_offset) # Move the structure left.
                    elif event.key == pg.K_d or event.key == pg.K_RIGHT:
                        structure_manager.lr_offset = structure_manager.lr_offset = gameboard.move_blocks_across(1, "right", structure_manager.get_structure_size(), structure_manager.lr_offset) # Move the structure right.
                    elif event.key == pg.K_w or event.key == pg.K_UP:
                        gameboard.move_blocks_down(1, True) # Quick-drop the structure.
                        gameboard.remove_complete_rows() # Remove all completed rows.
            if get_time()-old_time > 0.8:
                old_time = get_time()
                if gameboard.check_for_block_finish(1): # Check if the 1s have finished moving and a new block needs to be generated.
                    gameboard.remove_complete_rows() # Remove all completed rows.
                else:
                    gameboard.move_blocks_down(1) # Move all of the 1s down by 1.
                    gameboard.board, game_over = structure_manager.get_next_layer(gameboard.board) # Load the next layer of the current structure.dd
                    if game_over:
                        print("Game over")
                        game_running = False
                        pg.quit()
                        break
                    

main()
