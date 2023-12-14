import sys
sys.path.append("../A-Level-Chess-Algorithm")
from enginepy import Engine
import icecream as ic

def test_default():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    print(bitBoard.board_formatted)
    engine = Engine(bitBoard)
    engine.max_num_searched = int(input("Enter max searched moves: "))
    move_evaluation = engine.min_max_dict(current_colour="WHITE")
    ic(move_evaluation)