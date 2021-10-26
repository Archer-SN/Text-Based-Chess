import re


board = [["R", "N", "B", "Q", "K", "B", "N", "R"],
         ["P", "P", "P", "P", "P", "P", "P", "P"],  # White
         ["-", "-", "-", "-", "-", "-", "-", "-"],
         ["-", "-", "-", "-", "-", "-", "-", "-"],
         ["-", "-", "-", "-", "-", "-", "-", "-"],
         ["-", "-", "-", "-", "-", "-", "-", "-"],
         ["P'", "P'", "P'", "P'", "P'", "P'", "P'", "P'"],  # Black
         ["R'", "N'", "B'", "Q'", "K'", "B'", "N'", "R'"]]
COL = ["a", "b", "c", "d", "e", "f", "g", "h"]
current_player = "White"
is_check = False


def new_game(chess_board, current_plr, check):
    chess_board = [["R", "N", "B", "Q", "K", "B", "N", "R"],
                   ["P", "P", "P", "P", "P", "P", "P", "P"],
                   ["-", "-", "-", "-", "-", "-", "-", "-"],
                   ["-", "-", "-", "-", "-", "-", "-", "-"],
                   ["-", "-", "-", "-", "-", "-", "-", "-"],
                   ["-", "-", "-", "-", "-", "-", "-", "-"],
                   ["P'", "P'", "P'", "P'", "P'", "P'", "P'", "P'"],
                   ["R'", "N'", "B'", "Q'", "K'", "B'", "N'", "R'"]]
    current_plr = "White"  # White always starts first
    check = False


def convert_to_index(move):
    move = move.lower()
    if len(move) != 4 or not re.search(r"[a-h][1-8][a-h][1-8]", move):
        print("Invalid move!")
        return None
    start_point, end_point = move[:len(move) // 2], move[len(move) // 2:]  # Letters are Columns. Numbers are rows.
    start_index, end_index = (int(start_point[1]) - 1, COL.index(start_point[0])), (int(end_point[1]) - 1,
                                                                                    COL.index(end_point[0]))
    return start_index, end_index


def out_of_range(pos):
    if (pos[0] >= 8 or pos[0] < 0) or (pos[1] >= 8 or pos[1] < 0):
        return True
    return False


def get_king_pos(turn):
    kings = {"White": "K",
             "Black": "K'"}
    king = kings[turn]
    king_position = ""
    for y, row in enumerate(board):
        if king in row:
            king_position = (y, row.index(king))
            break
    return king_position


def check_if_check(turn, king_pos=None):
    kings = {"White": ["K", "", "'", 1],
             "Black": ["K'", "'", "", -1]}
    king = kings[turn][0]
    ally = kings[turn][1]
    enemy = kings[turn][2]
    enemy_dir = kings[turn][3]
    ally_pieces = ["P"+ally, "R"+ally, "N"+ally, "B"+ally, "Q"+ally]
    if not king_pos:
        king_pos = get_king_pos(turn)
    # Checking for Horizontal, Vertical and Diagonal enemies.
    for y_dir in range(-1, 2, 1):
        for x_dir in range(-1, 2, 1):
            y, x = king_pos[0], king_pos[1]
            pieces_to_avoid = []
            if y_dir == 0 or x_dir == 0:  # Horizontal or Vertical
                pieces_to_avoid = ["Q"+enemy, "R"+enemy]
            elif y_dir != 0 and x_dir != 0:  # Diagonal
                pieces_to_avoid = ["Q"+enemy, "B"+enemy]
            while -1 < y + y_dir < 8 and -1 < x + x_dir < 8 and (y_dir != 0 and x_dir != 0):
                y += y_dir
                x += x_dir
                try:
                    piece = board[y][x]
                    if piece in ally_pieces:  # Ally pieces can block the enemy piece from checking
                        break
                    elif piece == "P" + enemy and king_pos[0] + enemy_dir == y:
                        x_dif = king_pos[1] - x
                        if x_dif == 1 or x_dif == -1:
                            return True
                    elif piece not in pieces_to_avoid and piece != "-" and piece != king:  # Enemy pieces can also block the enemy piece
                        break
                    elif piece in pieces_to_avoid:
                        return True
                except IndexError:
                    break
    y, x = king_pos[0], king_pos[1]
    possible_knight = ((y - 2, x - 1), (y - 2, x + 1),
                       (y - 1, x - 2), (y - 1, x + 2),
                       (y + 1, x - 2), (y + 1, x + 2),
                       (y + 2, x - 1), (y + 2, x + 1))
    for curr_move in possible_knight:
        try:
            if board[curr_move[0]][curr_move[1]] == "N" + enemy and curr_move[0] > -1 and curr_move[1] > -1:
                return True
        except IndexError:
            continue
    return False


def check_mate(turn):
    king_pos = get_king_pos(turn)
    y, x = king_pos[0], king_pos[1]
    possible_moves = [(y, x + 1), (y, x - 1),
                      (y + 1, x), (y - 1, x),
                      (y + 1, x + 1), (y - 1, x - 1),
                      (y + 1, x - 1), (y - 1, x + 1)]
    for move in possible_moves:
        if not check_if_check(turn, move):
            return False
    return True


def promote_pawn(pawn_pos):
    possible_promotion = ("Q", "N", "R", "B")
    promoted_piece = None
    while True:
        promoted_piece = str(input("Promote Pawn to Q N R B: "))
        if promoted_piece in possible_promotion:
            break
    board[pawn_pos[0]][pawn_pos[1]] = promoted_piece


def check_pawn(start_pos, end_pos, turn):
    sides = {"White": 1,
             "Black": -1}
    default_pos = {"White": 1,
                   "Black": 6}
    side = sides[turn]

    if start_pos[0] + side == end_pos[0]:
        if (start_pos[1] - 1 == end_pos[1] or start_pos[1] + 1 == end_pos[1]) and board[end_pos[0]][end_pos[1]] != "-":
            return True
        elif start_pos[1] == end_pos[1] and board[end_pos[0]][end_pos[1]] == "-":
            return True
    elif start_pos[0] + side*2 == end_pos[0] and start_pos[0] == default_pos[turn]:
        return True
    return False


def check_rook(start_pos, end_pos):
    if start_pos[0] == end_pos[0] and start_pos[1] != end_pos[1]:  # Horizontal Line
        direction = 1
        if start_pos[1] > end_pos[1]:
            direction = -1  # Set the direction to -1 so we can loop backward if the start_pos is more than end_pos.
        horizontal_line = ["W" for row in range(start_pos[1] + direction, end_pos[1], direction) if
                           board[start_pos[0]][row] != "-"]
        if len(horizontal_line) == 0:
            return True
    elif start_pos[0] != end_pos[0] and start_pos[1] == end_pos[1]:  # Vertical Line
        direction = 1
        if start_pos[0] > end_pos[0]:
            direction = -1  # Set the direction to -1 so we can loop backward if the start_pos is more than end_pos.
        vertical_line = ["W" for row in range(start_pos[0] + direction, end_pos[0], direction) if
                         board[row][start_pos[1]] != "-"]
        if len(vertical_line) == 0:
            return True
    return False


def check_knight(start_pos, end_pos):
    y, x = start_pos[0], start_pos[1]
    possible_moves = ((y-2, x-1), (y-2, x+1),
                      (y-1, x-2), (y-1, x+2),
                      (y+1, x-2), (y+1, x+2),
                      (y+2, x-1), (y+2, x+1))
    if end_pos in possible_moves:
        return True
    return False


def check_bishop(start_pos, end_pos):
    for i in range(-1, 2, 2):
        for m in range(-1, 2, 2):
            illegal_moves = []
            y, x = start_pos[0], start_pos[1]
            while -1 < y < 8 and -1 < x < 8:
                y += i
                x += m
                try:
                    if board[y][x] != "-":
                        illegal_moves.append("W")
                    if end_pos == (y, x):  # There are to valid cases.
                        if len(illegal_moves) == 1 and board[end_pos[0]][end_pos[1]] != "-":  # Only valid when the end_pos is not "-"
                            return True
                        elif len(illegal_moves) == 0 and board[end_pos[0]][end_pos[1]] == "-":  # Only valid when the end_pos is "-"
                            return True
                except IndexError:
                    break
    return False


def check_queen(start_pos, end_pos):
    # Queen is basically bishop and rook combined so we can reuse bishop and rook's functions.
    if check_bishop(start_pos, end_pos):
        return True
    elif check_rook(start_pos, end_pos):
        return True
    return False


def check_king(start_pos, end_pos, turn):
    y, x = start_pos[0], start_pos[1]
    possible_moves = [(y, x+1), (y, x-1),
                      (y+1, x), (y-1, x),
                      (y+1, x+1), (y-1, x-1),
                      (y+1, x-1), (y-1, x+1)]
    if end_pos in possible_moves and not check_if_check(turn, end_pos):
        return True
    return False


def check_move(start_pos, end_pos, turn):
    if out_of_range(start_pos) and out_of_range(end_pos):
        return False
    elif start_pos == end_pos:  # You can't move to the same position
        return False
    elif board[end_pos[0]][end_pos[1]][0] == "K":
        return False

    piece = board[start_pos[0]][start_pos[1]]
    moves_checker = {"P": check_pawn(start_pos, end_pos, turn),
                     "R": check_rook(start_pos, end_pos),
                     "N": check_knight(start_pos, end_pos),
                     "B": check_bishop(start_pos, end_pos),
                     "Q": check_queen(start_pos, end_pos),
                     "K": check_king(start_pos, end_pos, turn),
                     "-": False
                     }
    return moves_checker[piece[0]]


def make_move(move, turn):
    if not convert_to_index(move):
        return False
    start_pos, end_pos = convert_to_index(move)
    s_piece = board[start_pos[0]][start_pos[1]]
    if (len(s_piece) == 1 and turn == "Black") or (len(s_piece) == 2 and turn == "White"):  # You can't move the enemy's piece. That's illegal
        print("Trying to move the enemy piece!")
        return False
    # If the move is valid, we will eat the ending piece and replace it with the starting piece
    if check_move(start_pos, end_pos, turn):
        board[end_pos[0]][end_pos[1]] = board[start_pos[0]][start_pos[1]]
        board[start_pos[0]][start_pos[1]] = "-"
        return True
    else:
        print("Invalid move!")
        print()
        return False


def redo_move(start_pos, end_pos, s_piece, e_piece):
    board[start_pos[0]][start_pos[1]] = s_piece
    board[end_pos[0]][end_pos[1]] = e_piece


def next_turn(player):
    if player == "White":
        return "Black"
    return "White"


def render():
    row_number = 1
    print()
    print("   " + "  ".join(COL))
    print("   " + "-" * 15)
    for row in board:
        formatted_row = [" " + row[i] if i > 0 and (len(row[i]) == 1 or len(row[i]) == 2) and len(row[i-1]) == 1 else row[i] for i in range(len(row))]
        print(str(row_number) + "  " + " ".join(formatted_row))
        row_number += 1


while True:
    render()
    while True:
        input_move = str(input("Input a move: "))
        if not convert_to_index(input_move):
            continue
        start_move, end_move = convert_to_index(input_move)
        start_piece = board[start_move[0]][start_move[1]]
        end_piece = board[end_move[0]][end_move[1]]

        if make_move(input_move, current_player):
            if check_if_check(current_player):
                redo_move(start_move, end_move, start_piece, end_piece)
                print("You can't put your king in danger!")
                continue
            break
    if check_if_check(next_turn(current_player)):
        print("Check!")
    current_player = next_turn(current_player)
