import sys, json
sys.path.append("../A-Level-Chess-Algorithm")
from enginepy import Engine
from bitboard import BitBoard

def test_evalaution():
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    engine = Engine(BitBoard(board))
    engine.max_time = 1
    engine.min_max_dict()
    assert True
    
def test_order_move_eval():
    def format_every_pair(d_list, function_key):
        d_list = function_key(d_list)
        for key, val in d_list.items():
            if type(val) is list:
                d_list[key] = format_every_pair(d_list[key], function_key)
        return d_list
    
    with open("test_evaluation.json", "r") as t_eval_file:
        move_evaluation_list = t_eval_file.read()
    move_evaluation_list = json.loads(move_evaluation_list)
    
    list_dictionary = lambda d_list: {tuple(dictionary["key"]) : dictionary["value"] for dictionary in d_list}
    move_evaluation = format_every_pair(move_evaluation_list, list_dictionary)
    Engine.find_ordered_move_eval(move_evaluation)
    assert True

def test_material_advantage():
    board = "................................................................"
    engine = Engine(BitBoard(board))
    assert engine._Engine__material_advantage(1) == (0,0)
    assert engine._Engine__material_advantage(0) == (0,0)
    pieces = ["pawn", "rook", "bishop", "knight", "queen"]
    expected_values = engine._Engine__PIECE_MATERIAL_WEIGHT
    for piece in pieces:
        engine.bitboard._edit_board((piece, 0, 0))
        engine.bitboard._edit_board((piece[0].upper()+piece[1:], 63, 63))
        assert engine._Engine__material_advantage(1) == (expected_values[piece.upper()], expected_values[piece.upper()])
        assert engine._Engine__material_advantage(0) == (expected_values["E"+piece.upper()], expected_values["E"+piece.upper()])

def test_positional_advantage():
    board = "................................................................"
    engine = Engine(BitBoard(board))
    assert engine._Engine__positional_advantage(0) == (0,0)
    assert engine._Engine__positional_advantage(1) == (0,0)
    expected_values = engine._Engine__PIECE_POSITIONAL_WEIGHT
    pieces = ["pawn", "rook", "bishop", "knight", "queen"]
    for piece in pieces:
        for index in range(63):
            engine.bitboard._edit_board((piece, index, index))
            assert engine._Engine__positional_advantage(1) == (expected_values[piece.upper()][index], 0)
            assert engine._Engine__positional_advantage(0) == (expected_values["E"+piece.upper()][index], 0)
            engine.bitboard._edit_board((None, index, index))
            engine.bitboard._edit_board((piece[0].upper()+piece[1:], index, index))
            assert engine._Engine__positional_advantage(1) == (0, expected_values[piece.upper()][::-1][index])
            assert engine._Engine__positional_advantage(0) == (0, expected_values["E"+piece.upper()][::-1][index])
            engine.bitboard._edit_board((None, index, index))
            
def test_strategical_advantage_null():
    board = "................................................................"
    engine = Engine(BitBoard(board))
    assert engine._Engine__strategical_advantage(0) == ([0,0,0,0], [0,0,0,0])
    assert engine._Engine__strategical_advantage(1) == ([0,0,0,0], [0,0,0,0])
    
def test_strategical_advantage_king_mobility():
    board = "...................k.......................K...................."
    engine = Engine(BitBoard(board))
    expected_values = engine._Engine__STRATEGICAL_WEIGHT
    e_strat_advantage = engine._Engine__strategical_advantage(0)
    strat_advantage = engine._Engine__strategical_advantage(1)
    assert [e_strat_advantage[0][0], e_strat_advantage[1][0]] == [0, 0]
    assert [strat_advantage[0][0], strat_advantage[1][0]] == [10*expected_values["KING_MOBILITY_NEGATIVE"], 10*expected_values["KING_MOBILITY_NEGATIVE"]]

def test_strategial_advantage_mobility():
    board = "........P..............................................p........"
    engine = Engine(BitBoard(board))
    expected_values = engine._Engine__STRATEGICAL_WEIGHT
    e_strat_advantage = engine._Engine__strategical_advantage(0)
    strat_advantage = engine._Engine__strategical_advantage(1)
    assert [e_strat_advantage[0][1], e_strat_advantage[1][1]] == [expected_values["EMOBILITY"][0], expected_values["EMOBILITY"][0]]
    assert [strat_advantage[0][1], strat_advantage[1][1]] == [expected_values["MOBILITY"][0], expected_values["MOBILITY"][0]]
    
def test_strategical_advantage_connected_pawns():
    board = "........PP............................................pp........"
    engine = Engine(BitBoard(board))
    expected_values = engine._Engine__STRATEGICAL_WEIGHT
    e_strat_advantage = engine._Engine__strategical_advantage(0)
    strat_advantage = engine._Engine__strategical_advantage(1)
    assert [e_strat_advantage[0][2], e_strat_advantage[1][2]] == [2*expected_values["CONNECTED_PAWNS"], 2*expected_values["CONNECTED_PAWNS"]]
    assert [strat_advantage[0][2], strat_advantage[1][2]] == [2*expected_values["CONNECTED_PAWNS"], 2*expected_values["CONNECTED_PAWNS"]]
    
def test_strategical_advantage_static_exchange():
    board = "..............................qQ................................"
    engine = Engine(BitBoard(board))
    expected_value = engine._Engine__PIECE_MATERIAL_WEIGHT["QUEEN"]
    e_strat_advantage = engine._Engine__strategical_advantage(0)
    strat_advantage = engine._Engine__strategical_advantage(1)
    assert [e_strat_advantage[0][3], e_strat_advantage[1][3]] == [expected_value, expected_value]
    assert [strat_advantage[0][3], strat_advantage[1][3]] == [expected_value, expected_value]

if __name__ == "__main__":
    pass