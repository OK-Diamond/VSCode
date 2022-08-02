import pygame
import os

def clear() -> None: os.system('cls' if os.name in ('nt', 'dos') else 'clear') # Clears the console

class board_class:
    def __init__(self, encoded_board="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") -> None:
        '''Inialises the game board. 'encoded_board' parameter loads a string-encoded board and defaults to the starting board.'''
        self.board = []
        boardstring, self.player_to_move, self.castle_options, self.en_passant, self.halfmove_clock, self.fullmove_count = encoded_board.split(" ")
        self.halfmove_clock, self.fullmove_count = int(self.halfmove_clock), int(self.fullmove_count)
        for i in boardstring.split("/"):
            self.board.append([])
            for j in i:
                try:
                    j = int(j)
                    for k in range(j):
                        self.board[-1].append(" ")
                except:
                    self.board[-1].append(j)
        return

    def encode_to_str(self) -> str:
        encoded_board = ""
        blank_count = 0
        for i in self.board:
            for j in i:
                if j == " ":
                    blank_count += 1
                else:
                    if blank_count > 0:
                        encoded_board += str(blank_count)
                        blank_count = 0
                    encoded_board += j
            if blank_count > 0:
                encoded_board += str(blank_count)
                blank_count = 0
            encoded_board += "/"
        encoded_board = encoded_board[0:-1]
        encoded_board += " "+self.player_to_move+" "+self.castle_options+" "+self.en_passant+" "+str(self.halfmove_clock)+" "+str(self.fullmove_count)
        return encoded_board
    
    def display_board(self) -> None:
        print("+—————————————————+")
        for y in range(8):
            print("| ", end="")
            for x in range(8):
                print(self.board[y][x], "", end="")
            print("|")
        print("+—————————————————+")
        return

    def get_possible_moves(self) -> list:
        boardlist = []
        #print("len(self.board)", len(self.board))
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if (self.player_to_move == "w" and self.board[i][j] in ["P", "B", "N", "R", "Q", "K"]) or (self.player_to_move == "b" and self.board[i][j] in ["p", "b", "n", "r", "q", "k"]):
                    possible_boards = self.move_test([i, j])
                    if len(possible_boards) > 0:
                        for k in possible_boards:
                            boardlist.append(k)
        return boardlist

    def move_test(self, pos: list) -> list:
        boardlist = []
        piece_type, old_en_passant = self.board[pos[0]][pos[1]], self.en_passant
        template = board_class(self.encode_to_str())
        template.en_passant = "-"
        if self.player_to_move == "w":
            template.fullmove_count += 1
            template.player_to_move = "b"
        else:
            template.player_to_move = "w"
        opponent_piece_bank = ["P", "B", "N", "R", "Q", "K"] if piece_type == str.lower(piece_type) else ["p", "b", "n", "r", "q", "k"]
        # Pawn
        if piece_type in ["P", "p"]:
            template.fullmove_count = 0
            if piece_type == "P": direction = -1 # White
            else: direction = 1 # Black
            for diagonal in [-1, 1]: # Check for opposing pieces on diagonals and en passant
                target = [pos[0]+direction, pos[1]+diagonal]
                en_passant = True if (len(old_en_passant) > 1 and target == [int(old_en_passant[0]), int(old_en_passant[1])]) else False
                if (target[0] >= 0 and target[1] <= 1) and (target[1] >= 0 and target[1] <= 7):
                    if self.board[target[0]][target[1]] in opponent_piece_bank or en_passant:
                        temp_board = board_class(template.encode_to_str())
                        temp_board.board[pos[0]][pos[1]], temp_board.board[target[0]][target[1]] = " ", piece_type
                        if en_passant:
                            temp_board.board[pos[0]][target[1]] = " "
                        boardlist.append(temp_board.encode_to_str())
                        del temp_board
            if pos[0]+direction in range(8) and self.board[pos[0]+direction][pos[1]] == " ": # Check for moving by 1
                
                if (direction == 1 and pos[0]+direction == 7) or (direction == -1 and pos[0]+direction == 0):
                    promotion_options = ["Q", "N"] if piece_type == "P" else ["q", "n"]
                    for promotion in promotion_options:
                        temp_board = board_class(template.encode_to_str())
                        temp_board.board[pos[0]][pos[1]], temp_board.board[pos[0]+direction][pos[1]] = " ", promotion
                        boardlist.append(temp_board.encode_to_str())
                else:
                    temp_board = board_class(template.encode_to_str())
                    temp_board.board[pos[0]][pos[1]], temp_board.board[pos[0]+direction][pos[1]] = " ", piece_type
                    boardlist.append(temp_board.encode_to_str())
                    if (piece_type == "P" and pos[0] == 6) or (piece_type == "p" and pos[0] == 1) and temp_board.board[pos[0]+(direction*2)][pos[1]] == " ": # Check for moving by 2
                        temp_board.board[pos[0]+direction][pos[1]], temp_board.board[pos[0]+(direction*2)][pos[1]] = " ", piece_type
                        temp_board.en_passant = str(pos[0]+direction)+str(pos[1])
                        boardlist.append(temp_board.encode_to_str())
                del temp_board
        # Knight
        if piece_type in ["N", "n"]:
            for y,x in [(-2,1), (-1,2), (1,2), (2,1), (2,-1), (1,-2), (-1,-2), (-2,-1)]:
                if pos[0]+y in range(8) and pos[1]+x in range(8):
                    if self.board[pos[0]+y][pos[1]+x] == " " or self.board[pos[0]+y][pos[1]+x] in opponent_piece_bank:
                        temp_board = board_class(template.encode_to_str())
                        temp_board.board[pos[0]][pos[1]], temp_board.board[pos[0]+y][pos[1]+x] = " ", piece_type
                        if self.board[pos[0]+y][pos[1]+x] in opponent_piece_bank:
                            temp_board.fullmove_count = 0
                        boardlist.append(temp_board.encode_to_str())
                        del temp_board
        # Bishop and Diagonal Queen
        if piece_type in ["B", "b", "Q", "q"]:
            for y,x in [(-1,-1), (-1,1), (1,1), (1,-1)]:
                piece_found = False
                for target in range(1,8): # Check for possible moves in increasing x and decreasing y (north-east)
                    if not piece_found and pos[0]+(target*y) in range(8) and pos[1]+(target*x) in range(8):
                        if self.board[pos[0]+(target*y)][pos[1]+(target*x)] == " " or self.board[pos[0]+(target*y)][pos[1]+(target*x)] in opponent_piece_bank:
                            temp_board = board_class(template.encode_to_str())
                            temp_board.board[pos[0]][pos[1]], temp_board.board[pos[0]+(target*y)][pos[1]+(target*x)] = " ", piece_type
                            if self.board[pos[0]+(target*y)][pos[1]+(target*x)] in opponent_piece_bank:
                                temp_board.fullmove_count = 0
                                piece_found = True
                            boardlist.append(temp_board.encode_to_str())
                            del temp_board
                        else:
                            piece_found = True
        # Rook and Vertical & Horizontal Queen
        if piece_type in ["R", "r", "Q", "q"]:
            for y,x in [(-1,0), (0,1), (1,0), (0,-1)]:
                piece_found = False
                for target in range(1,8): # Check for possible moves in increasing x and decreasing y (north-east)
                    if not piece_found and pos[0]+(target*y) in range(8) and pos[1]+(target*x) in range(8):
                        if self.board[pos[0]+(target*y)][pos[1]+(target*x)] == " " or self.board[pos[0]+(target*y)][pos[1]+(target*x)] in opponent_piece_bank:
                            temp_board = board_class(template.encode_to_str())
                            temp_board.board[pos[0]][pos[1]], temp_board.board[pos[0]+(target*y)][pos[1]+(target*x)] = " ", piece_type
                            if self.board[pos[0]+(target*y)][pos[1]+(target*x)] in opponent_piece_bank:
                                temp_board.fullmove_count = 0
                            boardlist.append(temp_board.encode_to_str())
                            del temp_board
                            if self.board[pos[0]+(target*y)][pos[1]+(target*y)] in opponent_piece_bank:
                                piece_found = True
                        else:
                            piece_found = True
        # King
        if piece_type in ["K", "k"]:
            for y in range(-1, 2):
                for x in range(-1, 2):
                    if (y != 0 or x != 0) and pos[0]+y in range(8) and pos[1]+x in range(8):
                        if self.board[pos[0]+y][pos[1]+x] == " " or self.board[pos[0]+y][pos[1]+x] in opponent_piece_bank:
                            temp_board = board_class(template.encode_to_str())
                            temp_board.board[pos[0]][pos[1]], temp_board.board[pos[0]+y][pos[1]+x] = " ", piece_type
                            if self.board[pos[0]+y][pos[1]+x] in opponent_piece_bank:
                                temp_board.fullmove_count = 0
                            boardlist.append(temp_board.encode_to_str())
                            del temp_board
        return boardlist
        
        

def process_turn(gameboard:board_class):
    error_msg = ""
    while True:
        clear()
        print(error_msg)
        if gameboard.player_to_move == "w":
            print("White's Turn")
        else:
            print("Black's Turn")
        print("Current Board:")
        gameboard.display_board()
        print("Possible Moves:")
        move_bank = gameboard.get_possible_moves()
        for i in range(len(move_bank)):
            a = board_class(move_bank[i])
            print(f"{i+1}. {move_bank[i]}")
            a.display_board()
        user_inp = input("Please enter the number of the move that you would like to make: ")
        try:
            user_inp = int(user_inp)
            if user_inp in range(1, len(move_bank)+1):
                return move_bank[user_inp-1]
            else:
                error_msg = f"Error: User input must be in the range 1-{len(move_bank)+1}"
        except:
            error_msg = "Error: Input must be an integer"

def check_for_game_over(gameboard:board_class) -> str:
    if gameboard.fullmove_count >= 50:
        return "Draw"
    white_king_found, black_king_found = False, False
    for i in gameboard.board or len(gameboard.get_possible_moves() == 0):
        for j in i:
            if j == "K":
                white_king_found = True
            elif j == "k":
                black_king_found = True
    if not white_king_found:
        return "Black Wins"
    elif not black_king_found:
        return "White Wins"
    

def main():
    gameboard = board_class()
    game_running = True
    while game_running:
        gameboard = board_class(process_turn(gameboard))
        check_for_game_over(gameboard)

if __name__ == "__main__":
    main()
