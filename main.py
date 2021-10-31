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
checker = [(-1, -1)]
kings = {"White": ["K", "", "'", 1],
         "Black": ["K'", "'", "", -1]}
has_moved = {(0, 0): False, (0, 4): False, (0, 7): False,
             (7, 0): False, (7, 4): False, (7, 7): False}


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


def on_same_side(piece1, piece2):
    if len(piece1) == len(piece2) and piece1 != "-" and piece2 != "-":
        return True
    return False


def get_king_pos(turn):
    king = kings[turn][0]
    king_position = None
    for y, row in enumerate(board):
        if king in row:
            king_position = (y, row.index(king))
            break
    return king_position


def promote_pawn(pawn_y, pawn_x, end_y, ally):
    pawn_piece = board[pawn_y][pawn_x]
    if (len(pawn_piece) == 1 and end_y != 7) or (len(pawn_piece) == 2 and end_y != 0) or pawn_piece not in ["P", "P'"]:
        return
    possible_promotion = ("Q", "N", "R", "B")
    while True:
        promoted_piece = str(input("Promote Pawn to Q N R B: ")).upper()
        if promoted_piece in possible_promotion:
            break
    board[pawn_y][pawn_x] = promoted_piece + ally


def check_pawn(start_y, start_x, end_y, end_x, is_test):
    if len(board[start_y][start_x]) == 1:
        side = 1
        default_pos = 1  # The position that the pawn must be in if it wants to move by 2 blocks.
        ally = ""
    else:
        side = -1
        default_pos = 6
        ally = "'"

    if start_y + side == end_y:
        if ((start_x - 1 == end_x or start_x + 1 == end_x) and board[end_y][end_x] != "-") or (start_x == end_x and board[end_y][end_x] == "-"):
            return True
        if not is_test:
            promote_pawn(start_y, start_x, end_y, ally)
        return True
    elif start_y + side*2 == end_y and start_y == default_pos and end_x == start_x and board[end_y][end_x] == "-" and board[start_y+side][start_x] == "-":
        return True
    return False


def check_rook(start_y, start_x, end_y, end_x):
    if start_y == end_y and start_x != end_x:  # Horizontal Line
        direction = 1
        if start_x > end_x:
            direction = -1  # Set the direction to -1 so we can loop backward if the start_pos is more than end_pos.
        horizontal_line = ["W" for row in range(start_x + direction, end_x, direction) if
                           board[start_y][row] != "-"]
        if len(horizontal_line) == 0:  # If there is no piece between the start piece and end piece.
            return True
    elif start_y != end_y and start_x == end_x:  # Vertical Line
        direction = 1
        if start_y > end_y:
            direction = -1  # Set the direction to -1 so we can loop backward if the start_pos is more than end_pos.
        vertical_line = ["W" for row in range(start_y + direction, end_y, direction) if
                         board[row][start_x] != "-"]
        if len(vertical_line) == 0:  # If there is no piece between the start piece and end piece.
            return True
    return False


def check_knight(y, x, end_pos):
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
                    if end_pos == (y, x):
                        if len(illegal_moves) == 1 and board[end_pos[0]][end_pos[1]] != "-":  # If there is one piece and that one piece is the end_piece.
                            return True
                        elif len(illegal_moves) == 0 and board[end_pos[0]][end_pos[1]] == "-":  # If there is no piece between the start piece and end piece.
                            return True
                except IndexError:
                    break
    return False


def check_queen(start_pos, end_pos):
    # Queen is basically bishop and rook combined so we can reuse bishop and rook's functions.
    if check_bishop(start_pos, end_pos):
        return True
    elif check_rook(start_pos[0], start_pos[1], end_pos[0], end_pos[1]):
        return True
    return False


def castling(start_y, start_x, end_y, end_x, turn, is_test):
    side = None
    if end_x < start_x:
        side = 1
    elif end_x > start_x:
        side = -1
    pieces_between = ["" for i in range(end_x+side, start_x, side) if board[start_y][i] != "-"]
    if len(pieces_between) > 0:
        return False
    start_pos = (start_y, start_x)
    end_pos = (end_y, end_x)
    king_piece = board[start_y][start_x]
    rook_piece = board[end_y][end_x]
    if not has_moved[start_pos] and not has_moved[end_pos] and not check_if_check(turn, (end_y, end_x+side)):
        if is_test:  # If it is just a check then we will return True right away because it would be more messy if we have to change it back
            return True
        board[start_y][start_x] = "-"
        board[end_y][end_x] = "-"
        board[end_y][end_x+side] = king_piece
        board[start_y][start_x+side*-1] = rook_piece
        return True
    return False


def check_king(y, x, end_y, end_x, turn, is_test):
    possible_moves = [(y, x+1), (y, x-1),
                      (y+1, x), (y-1, x),
                      (y+1, x+1), (y-1, x-1),
                      (y+1, x-1), (y-1, x+1)]
    end_pos = (end_y, end_x)
    if end_pos in possible_moves:
        return True
    if board[y][x][0] == "K" and board[end_y][end_x][0] == "R" and not check_if_check(turn):
        return castling(y, x, end_y, end_x, turn, is_test)
    return False


def check_move(start_pos, end_pos, turn, is_test=False):
    start_y, start_x = start_pos[0], start_pos[1]
    end_y, end_x = end_pos[0], end_pos[1]
    start_piece = board[start_y][start_x]
    end_piece = board[end_y][end_x]
    if out_of_range(start_pos) and out_of_range(end_pos):
        return False
    elif start_pos == end_pos:  # You can't move to the same position
        return False
    elif end_piece[0] == "K":
        return False
    elif start_piece == "-":
        return False
    elif (turn == "White" and len(start_piece) == 2) or (turn == "Black" and len(start_piece) == 1):
        return False
    elif on_same_side(start_piece, end_piece) and start_piece[0] != "K" and end_piece[0] != "R":  # Trying to eat ally piece. King and Rook are an exception because we can use them for castling.
        return False
    moves_checker = {"P": check_pawn(start_y, start_x, end_y, end_x, is_test),
                     "R": check_rook(start_y, start_x, end_y, end_x),
                     "N": check_knight(start_y, start_x, end_pos),
                     "B": check_bishop(start_pos, end_pos),
                     "Q": check_queen(start_pos, end_pos),
                     "K": check_king(start_y, start_x, end_y, end_x, turn, is_test),
                     }
    return moves_checker[start_piece[0]]


def redo_move(start_pos, end_pos, s_piece, e_piece):
    board[start_pos[0]][start_pos[1]] = s_piece
    board[end_pos[0]][end_pos[1]] = e_piece


def make_move(move, turn):
    if not convert_to_index(move):
        return False
    start_pos, end_pos = convert_to_index(move)
    st_piece = board[start_pos[0]][start_pos[1]]
    ed_piece = board[end_pos[0]][end_pos[1]]
    # If the move is valid, we will eat the ending piece and replace it with the starting piece
    if check_move(start_pos, end_pos, turn):
        board[end_pos[0]][end_pos[1]] = board[start_pos[0]][start_pos[1]]
        board[start_pos[0]][start_pos[1]] = "-"
        if check_if_check(current_player):
            redo_move(start_pos, end_pos, st_piece, ed_piece)
            print("You can't put your king in danger!")
            return False
        if start_pos in has_moved:
            has_moved[start_pos] = True
        if end_pos in has_moved:
            has_moved[end_pos] = True
        return True
    else:
        print("Invalid move!")
        print()
        return False


def check_by_knight(king_pos, enemy):
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


def check_if_check(turn, king_pos=None):
    king = kings[turn][0]
    ally = kings[turn][1]
    enemy = kings[turn][2]
    enemy_dir = kings[turn][3]
    ally_pieces = ["P" + ally, "R" + ally, "N" + ally, "B" + ally, "Q" + ally]
    if not king_pos:
        king_pos = get_king_pos(turn)
    king_y, king_x = king_pos[0], king_pos[1]
    # Checking for Horizontal, Vertical and Diagonal enemies.
    for y_dir in range(-1, 2, 1):
        for x_dir in range(-1, 2, 1):
            if y_dir == 0 and x_dir == 0:
                continue
            y, x = king_pos[0], king_pos[1]
            pieces_to_avoid = []
            if y_dir == 0:  # Horizontal
                pieces_to_avoid = ["Q" + enemy, "R" + enemy]
            elif x_dir == 0:
                pieces_to_avoid = ["Q" + enemy, "R" + enemy]  # Vertical
            elif y_dir != 0 and x_dir != 0:  # Diagonal
                pieces_to_avoid = ["Q" + enemy, "B" + enemy]
            while -1 < y < 8 and -1 < x < 8:
                y += y_dir
                x += x_dir
                if y <= -1 or x <= -1:
                    break
                try:
                    piece = board[y][x]
                    if piece in ally_pieces:  # Ally pieces can block the enemy piece from checking
                        break
                    elif piece == "P" + enemy and king_y + enemy_dir == y and abs(king_x - x) == 1:
                        checker[0] = (y, x)
                        return True
                    elif piece not in pieces_to_avoid and piece != "-" and piece != king:  # Enemy pieces can also block the enemy piece
                        break
                    elif piece in pieces_to_avoid:
                        checker[0] = (y, x)
                        return True
                except IndexError:
                    break
    # If the king is not checked by the above then we will check if it is checked by knight
    return check_by_knight(king_pos, enemy)


def check_if_blockable(turn, king_pos):
    checker_pos = checker[0]
    checker_y, checker_x = checker_pos[0], checker_pos[1]
    king_y, king_x = king_pos[0], king_pos[1]
    y_turn, x_turn = 0, 0
    if checker_y < king_y:
        y_turn = 1
    elif checker_y > king_y:
        y_turn = -1
    if checker_x < king_x:
        x_turn = 1
    elif checker_x > king_x:
        x_turn = -1

    while checker_y != king_y or checker_x != king_x:
        for y, row in enumerate(board):
            for x, element in enumerate(row):
                if check_move((y, x), checker_pos, turn):
                    print(element)
                    return True
        checker_y += y_turn
        checker_x += x_turn


def check_mate(turn):
    king_pos = get_king_pos(turn)
    y, x = king_pos[0], king_pos[1]
    possible_moves = [(y, x + 1), (y, x - 1),
                      (y + 1, x), (y - 1, x),
                      (y + 1, x + 1), (y - 1, x - 1),
                      (y + 1, x - 1), (y - 1, x + 1)]
    for move in possible_moves:
        if out_of_range(move) or board[move[0]][move[1]] != "-":
            continue
        if not check_if_check(turn, move):
            return False
    if check_if_blockable(turn, king_pos):
        return False
    return True


def stale_mate(turn):
    remaining_pieces = 0
    for row in board:
        for piece in row:
            if piece != "-":
                remaining_pieces += 1
    if remaining_pieces == 2:  # These 2 pieces are kings. Which means that it is a stalemate because king alone can't make a checkmate.
        return True

    # This one checks if there is a possible move. If no then stalemate.
    for start_y in range(8):  # The board is always 8x8. That's why I use 8 instead of len(board).
        for start_x in range(8):
            for end_y in range(8):
                for end_x in range(8):
                    if board[start_y][start_x] == "-":  # Skip "-" to save time
                        continue
                    if check_move((start_y, start_x), (end_y, end_x), turn, True):
                        st_piece = board[start_y][start_x]
                        ed_piece = board[end_y][end_x]
                        board[end_y][end_x] = board[start_y][start_x]
                        board[start_y][start_x] = "-"
                        if check_if_check(turn):
                            redo_move((start_y, start_x), (end_y, end_x), st_piece, ed_piece)
                            continue
                        else:
                            redo_move((start_y, start_x), (end_y, end_x), st_piece, ed_piece)
                            return False
    return True


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
    if check_if_check(current_player):
        if check_mate(current_player):
            print("Checkmate!")
            break
        print("Check!")
    elif stale_mate(current_player):
        print("Stalemate!")
        break
    print(current_player + " Turn!")

    while True:
        input_move = str(input("Input a move: "))
        if not convert_to_index(input_move):
            continue
        start_move, end_move = convert_to_index(input_move)

        if make_move(input_move, current_player):
            break
    current_player = next_turn(current_player)
