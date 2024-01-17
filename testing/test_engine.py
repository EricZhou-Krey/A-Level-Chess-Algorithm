import sys
sys.path.append("../A-Level-Chess-Algorithm")
from enginepy import Engine
from bitboard import BitBoard

def test_evalaution():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    engine = Engine(bitBoard)
    engine.max_time = 1
    move_evaluation = engine.min_max_dict()
    assert True
        