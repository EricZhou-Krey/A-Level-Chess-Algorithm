import sys
sys.path.append("../A-Level-Chess-Algorithm")
from bitboard import BitBoard

def test_bitboard_dict():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    expected_dict = {(bitBoard.piece.ROOK, bitBoard.colour.BLACK): 9295429630892703744,
                     (bitBoard.piece.ROOK, bitBoard.colour.WHITE): 129,
                     (bitBoard.piece.BISHOP, bitBoard.colour.BLACK): 2594073385365405696,
                     (bitBoard.piece.BISHOP, bitBoard.colour.WHITE): 36,
                     (bitBoard.piece.KNIGHT, bitBoard.colour.BLACK): 4755801206503243776,
                     (bitBoard.piece.KNIGHT, bitBoard.colour.WHITE): 66,
                     (bitBoard.piece.QUEEN, bitBoard.colour.BLACK): 576460752303423488,
                     (bitBoard.piece.QUEEN, bitBoard.colour.WHITE): 8,
                     (bitBoard.piece.KING, bitBoard.colour.BLACK): 1152921504606846976,
                     (bitBoard.piece.KING, bitBoard.colour.WHITE): 16,
                     (bitBoard.piece.PAWN, bitBoard.colour.BLACK): 71776119061217280,
                     (bitBoard.piece.PAWN, bitBoard.colour.WHITE): 65280
                     }
    assert bitBoard.bitboard_dict == expected_dict

def test_move_dict():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    expected_dict = ({56: [], 63: [], 0: [], 7: [], 58: [], 61: [], 2: [], 5: [], 57: [40, 42], 62: [45, 47], 1: [16, 18], 6: [21, 23], 59: [], 3: [], 60: [], 4: [], 48: [32, 40], 49: [33, 41], 50: [34, 42], 51: [35, 43], 52: [36, 44], 53: [37, 45], 54: [38, 46], 55: [39, 47], 8: [16, 24], 9: [17, 25], 10: [18, 26], 11: [19, 27], 12: [20, 28], 13: [21, 29], 14: [22, 30], 15: [23, 31]} , \
        {(bitBoard.piece.ROOK, bitBoard.colour.BLACK): [56, 63], 
         (bitBoard.piece.ROOK, bitBoard.colour.WHITE): [0, 7], 
         (bitBoard.piece.BISHOP, bitBoard.colour.BLACK): [58, 61], 
         (bitBoard.piece.BISHOP, bitBoard.colour.WHITE): [2, 5], 
         (bitBoard.piece.KNIGHT, bitBoard.colour.BLACK): [57, 62], 
         (bitBoard.piece.KNIGHT, bitBoard.colour.WHITE): [1, 6], 
         (bitBoard.piece.QUEEN, bitBoard.colour.BLACK): [59], 
         (bitBoard.piece.QUEEN, bitBoard.colour.WHITE): [3], 
         (bitBoard.piece.KING, bitBoard.colour.BLACK): [60], 
         (bitBoard.piece.KING, bitBoard.colour.WHITE): [4], 
         (bitBoard.piece.PAWN, bitBoard.colour.BLACK): [48, 49, 50, 51, 52, 53, 54, 55], 
         (bitBoard.piece.PAWN, bitBoard.colour.WHITE): [8, 9, 10, 11, 12, 13, 14, 15]})
    assert bitBoard.move_dict == expected_dict

def test_legal_move_dict():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    expected_dict = ({57: [40, 42], 62: [45, 47], 1: [16, 18], 6: [21, 23], 48: [32, 40], 49: [33, 41], 50: [34, 42], 51: [35, 43], 52: [36, 44], 53: [37, 45], 54: [38, 46], 55: [39, 47], 8: [16, 24], 9: [17, 25], 10: [18, 26], 11: [19, 27], 12: [20, 28], 13: [21, 29], 14: [22, 30], 15: [23, 31]},
                     {(bitBoard.piece.ROOK, bitBoard.colour.BLACK): [], 
                      (bitBoard.piece.ROOK, bitBoard.colour.WHITE): [], 
                      (bitBoard.piece.BISHOP, bitBoard.colour.BLACK): [], 
                      (bitBoard.piece.BISHOP, bitBoard.colour.WHITE): [], 
                      (bitBoard.piece.KNIGHT, bitBoard.colour.BLACK): [57, 62], 
                      (bitBoard.piece.KNIGHT, bitBoard.colour.WHITE): [1, 6], 
                      (bitBoard.piece.QUEEN, bitBoard.colour.BLACK): [], 
                      (bitBoard.piece.QUEEN, bitBoard.colour.WHITE): [],
                      (bitBoard.piece.KING, bitBoard.colour.BLACK): [], 
                      (bitBoard.piece.KING, bitBoard.colour.WHITE): [], 
                      (bitBoard.piece.PAWN, bitBoard.colour.BLACK): [48, 49, 50, 51, 52, 53, 54, 55], 
                      (bitBoard.piece.PAWN, bitBoard.colour.WHITE): [8, 9, 10, 11, 12, 13, 14, 15]})
    assert bitBoard.legal_move_dict == expected_dict
    board = "....k.....Q.................................................K..."
    bitBoard = BitBoard(board)
    expected_dict = ({10: [1, 2, 3, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19, 24, 26, 28, 34, 37, 42, 46, 50, 55, 58], 60: [51, 52, 53, 58, 59, 61, 62], 4: [5, 6]}, 
                     {(bitBoard.piece.ROOK, bitBoard.colour.BLACK): [], 
                      (bitBoard.piece.ROOK, bitBoard.colour.WHITE): [], 
                      (bitBoard.piece.BISHOP, bitBoard.colour.BLACK): [], 
                      (bitBoard.piece.BISHOP, bitBoard.colour.WHITE): [], 
                      (bitBoard.piece.KNIGHT, bitBoard.colour.BLACK): [], 
                      (bitBoard.piece.KNIGHT, bitBoard.colour.WHITE): [], 
                      (bitBoard.piece.QUEEN, bitBoard.colour.BLACK): [10],
                      (bitBoard.piece.QUEEN, bitBoard.colour.WHITE): [], 
                      (bitBoard.piece.KING, bitBoard.colour.BLACK): [60], 
                      (bitBoard.piece.KING, bitBoard.colour.WHITE): [4], 
                      (bitBoard.piece.PAWN, bitBoard.colour.BLACK): [], 
                      (bitBoard.piece.PAWN, bitBoard.colour.WHITE): []})
    assert bitBoard.legal_move_dict == expected_dict
    
def test_pawn():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move((bitBoard.piece.PAWN, bitBoard.colour.WHITE)) == 4294901760
    assert bitBoard._get_move((bitBoard.piece.PAWN, bitBoard.colour.BLACK)) == 281470681743360
    
def test_knight():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move((bitBoard.piece.KNIGHT, bitBoard.colour.WHITE)) == 10819584
    assert bitBoard._get_move((bitBoard.piece.KNIGHT, bitBoard.colour.BLACK)) == 6936818859638784
    
def test_bishop():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move((bitBoard.piece.BISHOP, bitBoard.colour.WHITE)) == 142121081854464
    assert bitBoard._get_move((bitBoard.piece.BISHOP, bitBoard.colour.BLACK)) == 25501128917581824
    
def test_rook():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move((bitBoard.piece.ROOK, bitBoard.colour.WHITE)) == 9331882296111890943
    assert bitBoard._get_move((bitBoard.piece.ROOK, bitBoard.colour.BLACK)) == 18411139144890810753
    
def test_queen():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move((bitBoard.piece.QUEEN, bitBoard.colour.WHITE)) == 578721933553179895
    assert bitBoard._get_move((bitBoard.piece.QUEEN, bitBoard.colour.BLACK)) == 17806153522019305480
    
def test_king():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    assert bitBoard._get_move((bitBoard.piece.KING, bitBoard.colour.WHITE)) == 14444
    assert bitBoard._get_move((bitBoard.piece.KING, bitBoard.colour.BLACK)) == 7797982754792013824
    
def test_edit_board():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    bitBoard.edit_board(((bitBoard.piece.KNIGHT, bitBoard.colour.WHITE), 1, 16))
    assert bitBoard.board_formatted == 'R N B Q K B N R 0\nP P P P P P P P 1\n. . . . . . . . 2\n. . . . . . . . 3\n. . . . . . . . 4\nn . . . . . . . 5\np p p p p p p p 6\nr . b q k b n r 7\nA B C D E F G H\n'
    bitBoard.edit_board(((bitBoard.piece.KNIGHT, bitBoard.colour.WHITE), 16, 1))
    assert bitBoard.board_formatted == 'R N B Q K B N R 0\nP P P P P P P P 1\n. . . . . . . . 2\n. . . . . . . . 3\n. . . . . . . . 4\n. . . . . . . . 5\np p p p p p p p 6\nr n b q k b n r 7\nA B C D E F G H\n'
    
def test_apply_move():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    expected_dict = {(bitBoard.piece.ROOK, bitBoard.colour.BLACK): 9295429630892703744, 
                     (bitBoard.piece.ROOK, bitBoard.colour.WHITE): 129, 
                     (bitBoard.piece.BISHOP, bitBoard.colour.BLACK): 2594073385365405696, 
                     (bitBoard.piece.BISHOP, bitBoard.colour.WHITE): 36, 
                     (bitBoard.piece.KNIGHT, bitBoard.colour.BLACK): 4755801206503243776, 
                     (bitBoard.piece.KNIGHT, bitBoard.colour.WHITE): 66, 
                     (bitBoard.piece.QUEEN, bitBoard.colour.BLACK): 576460752303423488, 
                     (bitBoard.piece.QUEEN, bitBoard.colour.WHITE): 8, 
                     (bitBoard.piece.KING, bitBoard.colour.BLACK): 1152921504606846976, 
                     (bitBoard.piece.KING, bitBoard.colour.WHITE): 16, 
                     (bitBoard.piece.PAWN, bitBoard.colour.BLACK): 71776119061217280, 
                     (bitBoard.piece.PAWN, bitBoard.colour.WHITE): 16842240}
    bitBoard.apply_move(((bitBoard.piece.PAWN, bitBoard.colour.WHITE), 8, 24))
    assert bitBoard.applied_moves == [((bitBoard.piece.PAWN, bitBoard.colour.WHITE), 8, 24)]
    assert bitBoard.bitboard_dict == expected_dict
    
    expected_dict = {(bitBoard.piece.ROOK, bitBoard.colour.BLACK): 9295429630892703744, 
                     (bitBoard.piece.ROOK, bitBoard.colour.WHITE): 129, 
                     (bitBoard.piece.BISHOP, bitBoard.colour.BLACK): 2594073385365405696, 
                     (bitBoard.piece.BISHOP, bitBoard.colour.WHITE): 36, 
                     (bitBoard.piece.KNIGHT, bitBoard.colour.BLACK): 4755801206503243776, 
                     (bitBoard.piece.KNIGHT, bitBoard.colour.WHITE): 66, 
                     (bitBoard.piece.QUEEN, bitBoard.colour.BLACK): 576460752303423488, 
                     (bitBoard.piece.QUEEN, bitBoard.colour.WHITE): 8, 
                     (bitBoard.piece.KING, bitBoard.colour.BLACK): 1152921504606846976, 
                     (bitBoard.piece.KING, bitBoard.colour.WHITE): 16, 
                     (bitBoard.piece.PAWN, bitBoard.colour.BLACK): 71776119061282817, 
                     (bitBoard.piece.PAWN, bitBoard.colour.WHITE): 16842240}
    bitBoard.apply_move(((bitBoard.piece.PAWN, bitBoard.colour.BLACK), 0, 16))
    assert bitBoard.applied_moves == [((bitBoard.piece.PAWN, bitBoard.colour.WHITE), 8, 24), ((bitBoard.piece.PAWN, bitBoard.colour.BLACK), 0, 16)]
    assert bitBoard.bitboard_dict == expected_dict
    
def test_revert_move():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    bitBoard.apply_move(((bitBoard.piece.PAWN, bitBoard.colour.WHITE), 8, 24))
    bitBoard.apply_move(((bitBoard.piece.ROOK, bitBoard.colour.WHITE), 0, 16))
    bitBoard.revert_move()
    expected_dict = {(bitBoard.piece.ROOK, bitBoard.colour.BLACK): 9295429630892703744, 
                     (bitBoard.piece.ROOK, bitBoard.colour.WHITE): 129, 
                     (bitBoard.piece.BISHOP, bitBoard.colour.BLACK): 2594073385365405696, 
                     (bitBoard.piece.BISHOP, bitBoard.colour.WHITE): 36, 
                     (bitBoard.piece.KNIGHT, bitBoard.colour.BLACK): 4755801206503243776, 
                     (bitBoard.piece.KNIGHT, bitBoard.colour.WHITE): 66, 
                     (bitBoard.piece.QUEEN, bitBoard.colour.BLACK): 576460752303423488, 
                     (bitBoard.piece.QUEEN, bitBoard.colour.WHITE): 8, 
                     (bitBoard.piece.KING, bitBoard.colour.BLACK): 1152921504606846976, 
                     (bitBoard.piece.KING, bitBoard.colour.WHITE): 16, 
                     (bitBoard.piece.PAWN, bitBoard.colour.BLACK): 71776119061217280, 
                     (bitBoard.piece.PAWN, bitBoard.colour.WHITE): 16842240}
    
    assert bitBoard.applied_moves == [((bitBoard.piece.PAWN, bitBoard.colour.WHITE), 8, 24)]
    assert bitBoard.bitboard_dict == expected_dict
    
    expected_dict = {(bitBoard.piece.ROOK, bitBoard.colour.BLACK): 9295429630892703744, 
                     (bitBoard.piece.ROOK, bitBoard.colour.WHITE): 129, 
                     (bitBoard.piece.BISHOP, bitBoard.colour.BLACK): 2594073385365405696, 
                     (bitBoard.piece.BISHOP, bitBoard.colour.WHITE): 36, 
                     (bitBoard.piece.KNIGHT, bitBoard.colour.BLACK): 4755801206503243776, 
                     (bitBoard.piece.KNIGHT, bitBoard.colour.WHITE): 66, 
                     (bitBoard.piece.QUEEN, bitBoard.colour.BLACK): 576460752303423488, 
                     (bitBoard.piece.QUEEN, bitBoard.colour.WHITE): 8, 
                     (bitBoard.piece.KING, bitBoard.colour.BLACK): 1152921504606846976, 
                     (bitBoard.piece.KING, bitBoard.colour.WHITE): 16, 
                     (bitBoard.piece.PAWN, bitBoard.colour.BLACK): 71776119061217280, 
                     (bitBoard.piece.PAWN, bitBoard.colour.WHITE): 65280}
    bitBoard.revert_move()
    assert bitBoard.applied_moves == []
    assert bitBoard.bitboard_dict == expected_dict
    
def test_castle():
    board = "r...k..r................................................R...K..R"
    bitBoard = BitBoard(board)
    expected_can_castle = {bitBoard.colour.BLACK: 
        {bitBoard.direction.LEFT: True, bitBoard.direction.RIGHT: True}, 
        bitBoard.colour.WHITE: 
            {bitBoard.direction.LEFT: (False, True), bitBoard.direction.RIGHT: (False, True)}}
    bitBoard.apply_move(((bitBoard.piece.KING, bitBoard.colour.WHITE), 4, 3))
    assert bitBoard.can_castle == expected_can_castle
    bitBoard.revert_move()
    bitBoard.apply_move(((bitBoard.piece.KING, bitBoard.colour.WHITE), 4, 2))
    assert bitBoard.board_formatted == 'R . . . K . . R 0\n. . . . . . . . 1\n. . . . . . . . 2\n. . . . . . . . 3\n. . . . . . . . 4\n. . . . . . . . 5\n. . . . . . . . 6\n. . k r . . . r 7\nA B C D E F G H\n'
    
def test_en_passant():
    board = "....k............................p..............P...........K..."
    bitBoard = BitBoard(board)
    bitBoard.apply_move(((bitBoard.piece.PAWN, bitBoard.colour.BLACK), 48, 32))
    bitBoard.apply_move(((bitBoard.piece.PAWN, bitBoard.colour.WHITE), 33, 40))
    assert bitBoard.board_formatted == '. . . . K . . . 0\n. . . . . . . . 1\np . . . . . . . 2\n. . . . . . . . 3\n. . . . . . . . 4\n. . . . . . . . 5\n. . . . . . . . 6\n. . . . k . . . 7\nA B C D E F G H\n'
    bitBoard.revert_move()
    assert bitBoard.board_formatted == '. . . . K . . . 0\n. . . . . . . . 1\n. . . . . . . . 2\nP p . . . . . . 3\n. . . . . . . . 4\n. . . . . . . . 5\n. . . . . . . . 6\n. . . . k . . . 7\nA B C D E F G H\n'

def test_king_safety():
    board = "....k......Q................................................K..."
    bitBoard = BitBoard(board)
    assert bitBoard.king_safe(bitBoard.colour.WHITE) == False
    assert bitBoard.king_safe(bitBoard.colour.BLACK) == True

if __name__ == "__main__":
    pass