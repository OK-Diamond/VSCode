#import pygame
from os import system, name
from random import randint # Used for the clear() function.
import sql_code # A library that I made for interfacing with sqlite3. It doesn't do much in the way of heavy lifting, but it's better than starting from scratch.

def clear() -> None:
    '''Clears the console'''
    system('cls' if name in ('nt', 'dos') else 'clear')

class board_class:
    def __init__(self, encoded_board="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0") -> None:
        '''Inialises the game board. 'encoded_board' parameter loads a string-encoded board and defaults to the starting board.'''
        self.board = []
        boardstring, self.player_to_move, self.castle_options, self.en_passant, self.halfmove_clock = encoded_board.split(" ")
        self.halfmove_clock = int(self.halfmove_clock)
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
        '''Translates the board into a single string, storing all neccessary information'''
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
        encoded_board += " "+self.player_to_move+" "+self.castle_options+" "+self.en_passant+" "+str(self.halfmove_clock)
        return encoded_board
    
    def display_board(self) -> None:
        '''Outputs the board to the console in a user-friendly format'''
        print("+—————————————————+")
        for y in range(8):
            print("| ", end="")
            for x in range(8):
                print(self.board[y][x], "", end="")
            print("|")
        print("+—————————————————+")
        return

    def get_possible_moves(self) -> list:
        '''Returns a list of all possible boardstates after the current one. I had prevously stored the moves themselves (e.g. e3 to f2) but I found that that would have made it difficult to interfact with the database foring boardstates; after all, you can achieve the exact same boardstate via different moves.'''
        boardlist = []
        #print("len(self.board)", len(self.board))
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if (self.player_to_move == "w" and self.board[i][j] in ["P", "B", "N", "R", "Q", "K"]) or (self.player_to_move == "b" and self.board[i][j] in ["p", "b", "n", "r", "q", "k"]):
                    possible_boards = self._move_test([i, j])
                    if len(possible_boards) > 0:
                        for k in possible_boards:
                            boardlist.append(k)
        return boardlist

    def _move_test(self, pos: list) -> list:
        '''Private function called by 'get_possible_moves' to find all possible moves from a certain piece.'''
        boardlist = []
        piece_type, old_en_passant = self.board[pos[0]][pos[1]], self.en_passant
        template = board_class(self.encode_to_str())
        template.halfmove_clock += 1
        template.en_passant = "-"
        template.player_to_move = "b" if self.player_to_move == "w" else "w"
        
        opponent_piece_bank = ["P", "B", "N", "R", "Q", "K"] if piece_type == str.lower(piece_type) else ["p", "b", "n", "r", "q", "k"]
        # Pawn
        if piece_type in ["P", "p"]:
            template.halfmove_clock = 0
            if piece_type == "P": direction = -1 # White
            else: direction = 1 # Black
            for diagonal in [-1, 1]: # Check for opposing pieces on diagonals and en passant
                target = [pos[0]+direction, pos[1]+diagonal]
                en_passant = True if (len(old_en_passant) > 1 and target == [int(old_en_passant[0]), int(old_en_passant[1])]) else False
                if target[0] in range(8) and target[1] in range(8):
                    #print([target[0], target[1]])
                    if self.board[target[0]][target[1]] in opponent_piece_bank or en_passant:
                        if (direction == 1 and target[0] == 7) or (direction == -1 and target[0] == 0): # Pawn promotion on capture
                            promotion_options = ["Q", "N"] if piece_type == "P" else ["q", "n"]
                            for promotion in promotion_options:
                                temp_board = board_class(template.encode_to_str())
                                temp_board.board[pos[0]][pos[1]], temp_board.board[target[0]][target[1]] = " ", promotion
                                boardlist.append(temp_board.encode_to_str())
                        else:
                            temp_board = board_class(template.encode_to_str())
                            temp_board.board[pos[0]][pos[1]], temp_board.board[target[0]][target[1]] = " ", piece_type
                            if en_passant:
                                temp_board.board[pos[0]][target[1]] = " "
                            boardlist.append(temp_board.encode_to_str())
                        del temp_board
            if pos[0]+direction in range(8) and self.board[pos[0]+direction][pos[1]] == " ": # Check for moving by 1
                if (direction == 1 and pos[0]+direction == 7) or (direction == -1 and pos[0]+direction == 0): # Pawn promotion when advancing normally
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
                            temp_board.halfmove_clock = 0
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
                                temp_board.halfmove_clock = 0
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
                                temp_board.halfmove_clock = 0
                                piece_found = True
                            boardlist.append(temp_board.encode_to_str())
                            del temp_board
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
                                temp_board.halfmove_clock = 0
                            boardlist.append(temp_board.encode_to_str())
                            del temp_board
        return boardlist

def process_turn(gameboard:board_class) -> str:
    '''Manages a player's turn, which involve displaying their move options and handling inputs.'''
    move_bank = gameboard.get_possible_moves()
    # Here, the user input is hijacked by the computer:
    #return move_bank[randint(0, len(move_bank)-1)]
    error_msg = ""
    while True:
        clear()
        if gameboard.player_to_move == "w":
            print("White's Turn")
        else:
            print("Black's Turn")
        print("Current Board:")
        gameboard.display_board()
        print("Possible Moves:")
        for i in range(len(move_bank)):
            a = board_class(move_bank[i])
            print(f"{i+1}. {move_bank[i]}")
            a.display_board()
        print("\n", error_msg)
        user_inp = input("Please enter the number of the move that you would like to make: ")
        try:
            user_inp = int(user_inp)
            if user_inp in range(1, len(move_bank)+1):
                return move_bank[user_inp-1]
            else:
                error_msg = f"Input Error: User input must be in the range 1-{len(move_bank)+1}"
        except:
            error_msg = "Input Error: Input must be an integer"

def check_for_game_over(gameboard:board_class, previous_moves_bank:list) -> tuple[str, str]:
    '''Checks various aspects of the board to see if the game has ended. Returns two strings: The first is the victory type (W, B, D or blank) and the second is some text that can be displayed to the user to explain why the game has ended.'''
    if gameboard.halfmove_clock >= 50:
        return "d", "Draw by the 50-move rule"
    
    white_king_found, black_king_found = False, False
    print(gameboard.board)
    for i in gameboard.board: # or len(gameboard.get_possible_moves() == 0)
        for j in i:
            print(j, j=="k")
            if j == "K":
                white_king_found = True
            if j == "k":
                black_king_found = True
    print("white_king_found, black_king_found", white_king_found, black_king_found)
    if not white_king_found:
        return "b", "Black wins by checkmate"
    elif not black_king_found:
        return "w", "White wins by checkmate"
    threefold_repetition_counter = 0
    for i in previous_moves_bank:
        for j in i:
            if gameboard.encode_to_str().split(" ")[0:-1] == str(j).split(" ")[0:-1]: # The [0:-1] is used to remove the halfmove clock, which is not tracked for a threefold repetition draw.
                threefold_repetition_counter += 1
                #print(i, j)
            if threefold_repetition_counter >= 5: # Requires 5 matches (instead of the expected three) because it counts each other board twice + it counts itself once.
                #print(gameboard.encode_to_str())
                return "d", "Draw by threefold repetition"
    return "", ""

class move_table_class(sql_code.table):
    def __init__(self, connection) -> None:
        '''Initialises the move table'''
        sql_code.table.__init__(self, connection, "move_table")
        try:  # Create table
            self.conn.cursor().execute(f"""CREATE TABLE {self.table_name} (board1 VARCHAR(90) NOT NULL, board2 VARCHAR(90) NOT NULL, weight INTEGER NOT NULL, PRIMARY KEY (board1, board2)) """)
            self.conn.commit()
        except sql_code.Error as e:
            pass #print(e)
        return
    
    def add_rec(self, board1: str, board2: str, weight: int) -> None:
        try:
            self.conn.cursor().execute(f"""INSERT INTO {self.table_name} (board1, board2, weight) VALUES (?,?,?)""", (board1, board2, weight))
            self.conn.commit()
            #print("record added")
        except sql_code.Error as e:
            pass #print(f"add_rec failed: {e}")
        return

def main() -> None:
    sql_connection = sql_code.connect("./ChessMate/chessmate_database.db")
    move_table = move_table_class(sql_connection)
    previous_moves_bank = []
    #gameboard = board_class()
    gameboard = board_class("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0")
    game_running = True
    while game_running:
        board1 = gameboard.encode_to_str()
        gameboard = board_class(process_turn(gameboard))
        board2 = gameboard.encode_to_str()
        previous_moves_bank.append([board1, board2])

        move_table_rec = move_table.list_rec(f"board1 = '{board1}' and board2 = '{board2}'")
        #print(move_table_rec)
        if len(move_table_rec) == 0:
            move_table.add_rec(board1, board2, 50)

        game_state, result = check_for_game_over(gameboard, previous_moves_bank)
        if result != "":
            game_running = False
    #print(previous_moves_bank)
    

    for i in previous_moves_bank:
        if game_state == "w":
            if i[0].split(" ")[1] == "w":
                move_table.update_rec("weight", "weight+4", f"board1 = '{i[0]}' AND board2 = '{i[1]}'")
            elif i[0].split(" ")[1] == "b":
                move_table.update_rec("weight", "weight-5", f"board1 = '{i[0]}' AND board2 = '{i[1]}'")
        elif game_state == "b":
            if i[0].split(" ")[1] == "w":
                move_table.update_rec("weight", "weight-5", f"board1 = '{i[0]}' AND board2 = '{i[1]}'")
            elif i[0].split(" ")[1] == "b":
                move_table.update_rec("weight", "weight+4", f"board1 = '{i[0]}' AND board2 = '{i[1]}'")
        elif game_state == "d":
            move_table.update_rec("weight", "weight-1", f"board1 = '{i[0]}' AND board2 = '{i[1]}'")
    del previous_moves_bank[0:-3]
    for i in previous_moves_bank:
        board_class(i[1]).display_board()
    #gameboard.display_board()
    print(result, " - Total moves:", len(previous_moves_bank))
    sql_code.quit(sql_connection)
    return

if __name__ == "__main__":
    #while True:
    main()




