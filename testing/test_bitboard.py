import sys
sys.path.append("../A-Level-Chess-Algorithm")
from bitboard import BitBoard

def test_bitboard_dict():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert str(bitBoard.bitboard_dict) == "{'rook': 129, 'knight': 66, 'bishop': 36, 'queen': 8, 'king': 16, 'pawn': 65280, 'Rook': 9295429630892703744, 'Pawn': 71776119061217280, 'Bishop': 2594073385365405696, 'Knight': 4755801206503243776, 'Queen': 576460752303423488, 'King': 1152921504606846976}"

def test_move_dict():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert str(bitBoard.move_dict) == "({0: [], 7: [], 1: [16, 18], 6: [21, 23], 2: [], 5: [], 3: [], 4: [], 8: [16, 24], 9: [17, 25], 10: [18, 26], 11: [19, 27], 12: [20, 28], 13: [21, 29], 14: [22, 30], 15: [23, 31], 56: [], 63: [], 48: [32, 40], 49: [33, 41], 50: [34, 42], 51: [35, 43], 52: [36, 44], 53: [37, 45], 54: [38, 46], 55: [39, 47], 58: [], 61: [], 57: [40, 42], 62: [45, 47], 59: [], 60: []}, {'rook': [0, 7], 'knight': [1, 6], 'bishop': [2, 5], 'queen': [3], 'king': [4], 'pawn': [8, 9, 10, 11, 12, 13, 14, 15], 'Rook': [56, 63], 'Pawn': [48, 49, 50, 51, 52, 53, 54, 55], 'Bishop': [58, 61], 'Knight': [57, 62], 'Queen': [59], 'King': [60]})"

def test_legal_move_dict():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert str(bitBoard.legal_move_dict) == "({1: [16, 18], 6: [21, 23], 8: [16, 24], 9: [17, 25], 10: [18, 26], 11: [19, 27], 12: [20, 28], 13: [21, 29], 14: [22, 30], 15: [23, 31], 48: [32, 40], 49: [33, 41], 50: [34, 42], 51: [35, 43], 52: [36, 44], 53: [37, 45], 54: [38, 46], 55: [39, 47], 57: [40, 42], 62: [45, 47]}, {'rook': [], 'knight': [1, 6], 'bishop': [], 'queen': [], 'king': [], 'pawn': [8, 9, 10, 11, 12, 13, 14, 15], 'Rook': [], 'Pawn': [48, 49, 50, 51, 52, 53, 54, 55], 'Bishop': [], 'Knight': [57, 62], 'Queen': [], 'King': []})"
    board = "....k.....Q.................................................K..."
    bitBoard = BitBoard(board)
    assert str(bitBoard.legal_move_dict) == "({4: [5, 6], 10: [1, 2, 3, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19, 24, 26, 28, 34, 37, 42, 46, 50, 55, 58], 60: [51, 52, 53, 58, 59, 61, 62]}, {'rook': [], 'knight': [], 'bishop': [], 'queen': [], 'king': [4], 'pawn': [], 'Rook': [], 'Pawn': [], 'Bishop': [], 'Knight': [], 'Queen': [10], 'King': [60]})"
    
def test_pawn():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move("pawn") == 4294901760
    assert bitBoard._get_move("Pawn") == 281470681743360
    
def test_knight():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move("knight") == 10819584
    assert bitBoard._get_move("Knight") == 6936818859638784
    
def test_bishop():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move("bishop") == 142121081854464
    assert bitBoard._get_move("Bishop") == 25501128917581824
    
def test_rook():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move("rook") == 9331882296111890943
    assert bitBoard._get_move("Rook") == 18411139144890810753
    
def test_queen():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move("queen") == 578721933553179895
    assert bitBoard._get_move("Queen") == 17806153522019305480
    
def test_king():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move("king") == 14444
    assert bitBoard._get_move("King") == 7797982754792013824
    
def test_edit_board():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    bitBoard._edit_board(("knight", 1, 16))
    assert bitBoard.board_formatted == 'R N B Q K B N R 0\nP P P P P P P P 1\n. . . . . . . . 2\n. . . . . . . . 3\n. . . . . . . . 4\nn . . . . . . . 5\np p p p p p p p 6\nr . b q k b n r 7\nA B C D E F G H\n'
    bitBoard._edit_board(("knight", 16, 1))
    assert bitBoard.board_formatted == 'R N B Q K B N R 0\nP P P P P P P P 1\n. . . . . . . . 2\n. . . . . . . . 3\n. . . . . . . . 4\n. . . . . . . . 5\np p p p p p p p 6\nr n b q k b n r 7\nA B C D E F G H\n'
    
def test_apply_move():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    bitBoard.apply_move(("pawn", 8, 24))
    assert bitBoard.applied_moves == [("pawn", 8, 24)]
    assert str(bitBoard.bitboard_dict) == "{'rook': 129, 'knight': 66, 'bishop': 36, 'queen': 8, 'king': 16, 'pawn': 16842240, 'Rook': 9295429630892703744, 'Pawn': 71776119061217280, 'Bishop': 2594073385365405696, 'Knight': 4755801206503243776, 'Queen': 576460752303423488, 'King': 1152921504606846976}"
    bitBoard.apply_move(("rook", 0, 16))
    assert bitBoard.applied_moves == [('pawn', 8, 24), ('rook', 0, 16)]
    assert str(bitBoard.bitboard_dict) == "{'rook': 65664, 'knight': 66, 'bishop': 36, 'queen': 8, 'king': 16, 'pawn': 16842240, 'Rook': 9295429630892703744, 'Pawn': 71776119061217280, 'Bishop': 2594073385365405696, 'Knight': 4755801206503243776, 'Queen': 576460752303423488, 'King': 1152921504606846976}"
    
def test_revert_move():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    bitBoard.apply_move(("pawn", 8, 24))
    bitBoard.apply_move(("rook", 0, 16))
    bitBoard.revert_move()
    assert bitBoard.applied_moves == [("pawn", 8, 24)]
    assert str(bitBoard.bitboard_dict) == "{'rook': 129, 'knight': 66, 'bishop': 36, 'queen': 8, 'king': 16, 'pawn': 16842240, 'Rook': 9295429630892703744, 'Pawn': 71776119061217280, 'Bishop': 2594073385365405696, 'Knight': 4755801206503243776, 'Queen': 576460752303423488, 'King': 1152921504606846976}"
    bitBoard.revert_move()
    assert bitBoard.applied_moves == []
    assert str(bitBoard.bitboard_dict) == "{'rook': 129, 'knight': 66, 'bishop': 36, 'queen': 8, 'king': 16, 'pawn': 65280, 'Rook': 9295429630892703744, 'Pawn': 71776119061217280, 'Bishop': 2594073385365405696, 'Knight': 4755801206503243776, 'Queen': 576460752303423488, 'King': 1152921504606846976}"
    
def test_castle():
    board = "r...k..r................................................R...K..R"
    bitBoard = BitBoard(board)
    bitBoard.apply_move(("king", 4, 3))
    assert str(bitBoard._BitBoard__can_castle) == "{'BLACK': {'left': True, 'right': True}, 'WHITE': {'left': (False, True), 'right': (False, True)}}"
    bitBoard.revert_move()
    bitBoard.apply_move(("king", 4, 2))
    assert bitBoard.board_formatted == 'R . . . K . . R 0\n. . . . . . . . 1\n. . . . . . . . 2\n. . . . . . . . 3\n. . . . . . . . 4\n. . . . . . . . 5\n. . . . . . . . 6\n. . k r . . . r 7\nA B C D E F G H\n'
    
def test_en_passant():
    board = "....k............................p..............P...........K..."
    bitBoard = BitBoard(board)
    bitBoard.apply_move(("Pawn", 48, 32))
    bitBoard.apply_move(("pawn", 33, 40))
    assert bitBoard.board_formatted == '. . . . K . . . 0\n. . . . . . . . 1\np . . . . . . . 2\n. . . . . . . . 3\n. . . . . . . . 4\n. . . . . . . . 5\n. . . . . . . . 6\n. . . . k . . . 7\nA B C D E F G H\n'
    bitBoard.revert_move()
    assert bitBoard.board_formatted == '. . . . K . . . 0\n. . . . . . . . 1\n. . . . . . . . 2\nP p . . . . . . 3\n. . . . . . . . 4\n. . . . . . . . 5\n. . . . . . . . 6\n. . . . k . . . 7\nA B C D E F G H\n'

def test_king_safety():
    board = "....k......Q................................................K..."
    bitBoard = BitBoard(board)
    assert bitBoard.king_safe(True) == False
    assert bitBoard.king_safe(False) == True
