from typing import Optional, Tuple
from chess_game_support import *


def initial_state() -> Board:
    """
    Returns the board for a new game.

    Parameters:

    Returns:
        (Board): the initial board state
    """
    return "rnbqkbnr", "pppppppp", "........", "........", "........", "........", "PPPPPPPP", "RNBQKBNR"


def print_board(board: Board) -> None:
    """
    Displays the board

    Parameters:
        board (Board): the current board
    """
    row_num = BOARD_SIZE
    for row in board:
        print(row + f'  {row_num}')
        row_num -= 1
    print('\nabcdefgh')


def square_to_position(square: str) -> Position:
    """
    Converts chess notation to its (row, col): Position equivalent.

    Parameters:
        square (str): the square on the chess board

    Returns:
        (Position): a tuple (row, col) which represents the location on
        the board
    """
    if valid_position_format(square):
        y = ord(square[0].lower()) - ord('a')
        x = BOARD_SIZE - int(square[1])
        return x, y


def process_move(user_input: str) -> Move:
    """
    Converts the user input to a Move based on (row, col): Position. Assume
    the user_input is valid.

    Parameters:
        user_input (str): 'position1 position2': The positions (as letterNumber)
        to move from and to respectively

    Returns:
        (Move): a tuple (from, to)
    """
    from_position = square_to_position(user_input[0:2])
    to_position = square_to_position(user_input[-2:])
    return from_position, to_position


def change_position(board: Board, position: Position, character: str) -> Board:
    """
    Returns a copy of board with the character at position changed to character.

    Parameters:
        board (Board): the current board
        position (Position): position that needs changing
        character (str): the piece

    Returns:
        (Board): the new board
    """
    new_board = []
    for row_num in range(BOARD_SIZE):
        if row_num == position[0]:
            row = board[row_num][:position[1]] + character + board[row_num][position[1] + 1:]
            new_board.append(row)
        else:
            new_board.append(board[row_num])
    return tuple(new_board)


def clear_position(board: Board, position: Position) -> Board:
    """
    Clear the piece at position (i.e. replace with an empty square) and
    return the resulting board.

    Parameters:
        board (Board): the current board
        position (Position): position that needs clearing

    Returns:
        (Board): a new board
    """
    return change_position(board, position, '.')


def update_board(board: Board, move: Move) -> Board:
    """
    Assume the move is valid and return an updated version of the board with
    the move made.

    Parameters:
        board (Board): the current board
        move (Move): position that needs clearing

    Returns:
        (Board): a new board
    """
    row, col = move[0]
    piece = board[row][col]  # get what the piece is going to move
    return change_position(clear_position(board, move[0]), move[1], piece)


def is_current_players_piece(piece: str, whites_turn: bool) -> bool:
    """
    Returns true only when piece is belongs to the player whose turn it is.

    Parameters:
        piece (str): the piece user want to move
        whites_turn (bool): True if it's white's turn. False otherwise.

    Returns:
        (bool): True if it's current player's piece
    """
    return piece in WHITE_PIECES if whites_turn else piece in BLACK_PIECES


def is_move_valid(move: Move, board: Board, whites_turn: bool) -> bool:
    """
    Returns true only when the move is valid on the current board state for
    the player whose turn it is.

    Parameters:
        move (Move): (from_position, to_position)
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.

    Returns:
        (bool): True iff it's a valid move.
    """
    if not (out_of_bounds(move[0]) and out_of_bounds(move[1])) \
            and move[0] != move[1] \
            and is_current_players_piece(piece_at_position(move[0], board), whites_turn) \
            and (piece_at_position(move[1], board) == EMPTY
                 or not is_current_players_piece(piece_at_position(move[1], board), whites_turn)) \
            and move[1] in get_possible_moves(move[0], board) \
            and not is_in_check(update_board(board, move), whites_turn):
        return True

    return False


def can_move(board: Board, whites_turn: bool) -> bool:
    """
    Returns true only when the player can make a valid move which does not put them in check.

    Parameters:
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.

    Returns:
        (bool): True iff the player can make a valid move.
    """
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            position = (row, col)
            if is_current_players_piece(piece_at_position(position, board), whites_turn):
                moves = get_possible_moves(position, board)
                for move in moves:
                    if is_move_valid((position, move), board, whites_turn):
                        return True
    return False


def is_stalemate(board: Board, whites_turn: bool) -> bool:
    """
    Returns true only when a stalemate has been reached.

    Parameters:
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.

    Returns:
        (bool): True iff a stalemate has been reached.
    """
    if not is_in_check(board, whites_turn) and not can_move(board, whites_turn):
        return True
    return False


def check_game_over(board: Board, whites_turn: bool) -> bool:
    """
    Returns true only when the game is over (either due to checkmate or
    stalemate). Also prints information about the result if the game is over, or
    if the player is in check.

    Parameters:
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.

    Returns:
        (bool): True iff the game is over.
    """
    if is_in_check(board, whites_turn):
        if can_move(board, whites_turn):
            if whites_turn:
                print('\nWhite is in check')
            else:
                print('\nBlack is in check')
            return False
        else:
            print('\nCheckmate')
            return True
    elif is_stalemate(board, whites_turn):
        print('\nStalemate')
        return True
    return False


def attempt_promotion(board: Board, whites_turn: bool) -> Board:
    """
    Checks whether there is a pawn on the board that needs to be promoted.
    Updates the board if necessary.

    Parameters:
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.

    Returns:
        (Board): a new board if promoted. The old one otherwise.
    """
    if whites_turn:
        row = 0
        pawn = WHITE_PAWN
    else:
        row = 7
        pawn = BLACK_PAWN
    ask_1 = 'What piece would you like (q, n, r, b)? '
    ask_2 = 'Not a valid piece. ' + ask_1
    for col in range(BOARD_SIZE):
        if piece_at_position((row, col), board) == pawn:
            promotion = input(ask_1)
            while True:
                # check if it is legal piece
                if promotion in ('q', 'n', 'r', 'b'):
                    break
                promotion = input(ask_2)

            if whites_turn:
                promotion = promotion.upper()
            return change_position(board, (row, col), promotion)
    return board


def is_valid_castle_attempt(move: Move, board: Board, whites_turn: bool,
                            castling_info: Tuple[bool, bool, bool]) -> bool:
    """
    Returns true only when the given move is a valid attempt at castling for
    the current board state.

    Parameters:
        move (Move): (from_position, to_position)
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.
        castling_info (tuple):  a tuple of booleans which are True if the
                                player’s left rook, king, and right rook have
                                moved this game, respectively.

    Returns:
        (bool): True iff the given move is a valid attempt at castling.
    """
    legal_castle_move = (
        ((7, 4), (7, 6)),
        ((7, 4), (7, 2)),
        ((0, 4), (0, 6)),
        ((0, 4), (0, 2))
    )
    from_position, to_position = move
    king = WHITE_KING if whites_turn else BLACK_KING
    rook = WHITE_ROOK if whites_turn else BLACK_ROOK

    if piece_at_position(from_position, board) == king \
            and move in legal_castle_move \
            and not castling_info[1]:
        if from_position[1] < to_position[1]:
            # moved to right
            rook_position = (from_position[0], 7)
            direction = 1
            squares = 4
            rook_moved = castling_info[2]
            no_pieces_between = piece_at_position((from_position[0], from_position[1] + 1), board) is EMPTY \
                                and piece_at_position((from_position[0], from_position[1] + 2), board) is EMPTY
        else:
            # moved to left
            rook_position = (from_position[0], 0)
            direction = -1
            squares = 5
            rook_moved = castling_info[0]
            no_pieces_between = piece_at_position((from_position[0], from_position[1] - 1), board) is EMPTY \
                                and piece_at_position((from_position[0], from_position[1] - 2), board) is EMPTY \
                                and piece_at_position((from_position[0], from_position[1] - 3), board) is EMPTY
        if piece_at_position(rook_position, board) == rook \
                and not rook_moved \
                and no_pieces_between:
            for i in range(squares):  # not in check all the way
                move_to_square = (from_position, (from_position[0], from_position[1] + i * direction))
                if is_in_check(update_board(board, move_to_square), whites_turn):
                    return False
            return True
    return False


def perform_castling(move: Move, board: Board) -> Board:
    """
    Given a valid castling move, returns the resulting board state.

    Parameters:
        move (Move): a valid castling move.
        board (Board): the current board.

    Returns:
        (Board): a new board after castling.
    """
    kings_row, kings_end_col = move[1]
    if kings_end_col == 6:
        rooks_move = ((kings_row, 7), (kings_row, 5))
    else:
        rooks_move = ((kings_row, 0), (kings_row, 3))

    return update_board(update_board(board, move), rooks_move)


def is_valid_en_passant(
        move: Move, board: Board, whites_turn: bool,
        en_passant_position: Optional[Position]) -> bool:
    """
    Returns true only when the supplied move constitutes a valid en passant move.

    Parameters:
        move (Move): (from_position, to_position)
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.
        en_passant_position (Optional[Position]):
            the position skipped by the opponent’s pawn, or None if a
            pawn did not move forward two positions on the last move.

    Returns:
        (bool): True iff the supplied move constitutes a valid en passant move.
    """
    from_position, to_position = move
    if whites_turn:
        direction = -1
        self_pawn = WHITE_PAWN
        other_pawn = BLACK_PAWN
        should_start_at_row = 3
    else:
        direction = 1
        self_pawn = BLACK_PAWN
        other_pawn = WHITE_PAWN
        should_start_at_row = 4

    if en_passant_position is not None \
            and en_passant_position == move[1] \
            and to_position[0] == from_position[0] + direction \
            and from_position[0] == should_start_at_row \
            and piece_at_position(from_position, board) == self_pawn \
            and piece_at_position((from_position[0], to_position[1]), board) == other_pawn:
        return True
    return False


def perform_en_passant(move: Move, board: Board, whites_turn: bool) -> Board:
    """
    Given a valid en passant move, returns the resulting board state.

    Parameters:
        move (Move): (from_position, to_position)
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.

    Returns:
        (Board): a new board after en passant
    """
    other_pawn_position = (move[0][0], move[1][1])
    return update_board(clear_position(board, other_pawn_position), move)


def update_castling_info(
        move: Move, whites_turn: bool, castling_info: Tuple[bool, bool, bool]
) -> Tuple[bool, bool, bool]:
    """
    Returns the updated castling information for the player whose turn it is,
    after performing the given, valid move.

    Parameters:
        move (Move): (from_position, to_position)
        whites_turn (bool): True if it's white's turn. False otherwise.
        castling_info (tuple):  a tuple of booleans which are True if the
                                player’s left rook, king, and right rook have
                                moved this game, respectively.

    Returns:
        (tuple<bool, bool, bool>): new castling_info
    """
    row = 7 if whites_turn else 0
    rook_king_rook_position = ((row, 0), (row, 4), (row, 7))
    castling_info_list = list(castling_info)

    for i, moved in enumerate(castling_info_list):
        if moved:
            continue
        if move[0] == rook_king_rook_position[i]:
            castling_info_list[i] = True

    return tuple(castling_info_list)


def update_en_passant_position(move: Move, board: Board, whites_turn: bool) -> Optional:
    """
    If the current player’s pawn just moved forward two squares, returns the
    position that an opponent pawn could take to perform a valid en passant
    move. If no en passant move should be possible, returns None.

    Parameters:
        move (Move): (from_position, to_position)
        board (Board): the current board.
        whites_turn (bool): True if it's white's turn. False otherwise.
    """
    from_position, to_position = move
    if whites_turn:
        direction = -1
        pawn = WHITE_PAWN
        should_at_row = 4
    else:
        direction = 1
        pawn = BLACK_PAWN
        should_at_row = 3

    if piece_at_position(to_position, board) == pawn \
            and to_position[0] == should_at_row \
            and to_position[0] - from_position[0] == 2 * direction:
        return from_position[0] + direction, from_position[1]
    return None


def main():
    """Entry point to gameplay"""
    board = initial_state()
    whites_turn = True
    en_passant_position = None
    castling_info_white = (False, False, False)
    castling_info_black = (False, False, False)

    while True:
        print_board(board)
        if check_game_over(board, whites_turn):
            break
        if whites_turn:
            castling_info = castling_info_white
            move = input("\nWhite's move: ")
        else:
            castling_info = castling_info_black
            move = input("\nBlack's move: ")

        if move == 'h' or move == 'H':
            print(HELP_MESSAGE)
            continue
        elif move == 'q' or move == 'Q':
            confirmation = input("Are you sure you want to quit? ")
            if confirmation == 'y' or confirmation == 'Y':
                break
            else:
                continue

        # check validity of the move format
        if not valid_move_format(move):
            print('Invalid move\n')
            continue

        # check validity of the move and perform the move if it's valid
        move = process_move(move)
        if is_move_valid(move, board, whites_turn):
            board = update_board(board, move)
        elif is_valid_en_passant(move, board, whites_turn, en_passant_position):
            board = perform_en_passant(move, board, whites_turn)
        elif is_valid_castle_attempt(move, board, whites_turn, castling_info):
            board = perform_castling(move, board)
        else:
            print('Invalid move\n')
            continue

        # after performing move
        board = attempt_promotion(board, whites_turn)

        if whites_turn:
            castling_info_white = update_castling_info(move, whites_turn, castling_info)
        else:
            castling_info_black = update_castling_info(move, whites_turn, castling_info)

        en_passant_position = update_en_passant_position(move, board, whites_turn)

        whites_turn = not whites_turn


if __name__ == "__main__":
    main()
