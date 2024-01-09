import sys
sys.path.append("../A-Level-Chess-Algorithm")
from enginepy import Engine
from bitboard import BitBoard

def test_evalaution():
    try:
        board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
        bitBoard = BitBoard(board)
        engine = Engine(bitBoard)
        engine.max_num_searched = 10000
        move_evaluation = engine.min_max_dict()
        assert True
    except:
        assert False
        