import bitboard, time, math
from sorting_techniques import pysort
from icecream import ic
class EngineParameters:
    def __init__(self,
                 origin_pointer, move_pointer, apply_move_pointer, evaluation_pointer,
                 current_colour, current_moves, current_key_index, current_origin_list,
                 applied_moves, evaluation_move):
        self.origin_pointer = origin_pointer
        self.move_pointer = move_pointer
        self.apply_move_pointer = apply_move_pointer
        self.evaluation_pointer = evaluation_pointer
        self.current_colour = current_colour
        self.current_moves = current_moves
        self.current_key_index = current_key_index
        self.current_origin_list = current_origin_list
        self.applied_moves = applied_moves
        self.evaluation_move = evaluation_move
                
class Engine:
    def __init__(self, bitboard_object, PAWN_MATERIAL_WEIGHT=1, BISHOP_MATERIAL_WEIGHT=3, KNIGHT_MATERIAL_WEIGHT=3, ROOK_WIEGHT=5, QUEEN_MATERIAL_WEIGHT=10,
                #POSITIONAL_WEIGHT - indexed from 0-63, a1 to h8
                WPAWN_POSITIONAL_WEIGHT = [
                     0,0,0,0,0,0,0,0,
                     1,1,1,1,1,1,1,1,
                     2,2,2,2,2,2,2,2,
                     3,3,3,3,3,3,3,3,
                     4,4,4,4,4,4,4,4,
                     5,5,5,5,5,5,5,5,
                     6,6,6,6,6,6,6,6,
                     7,7,7,7,7,7,7,7
                ],
                DPAWN_POSITIONAL_WEIGHT = [
                     7,7,7,7,7,7,7,7,
                     6,6,6,6,6,6,6,6,
                     5,5,5,5,5,5,5,5,
                     4,4,4,4,4,4,4,4,
                     3,3,3,3,3,3,3,3,
                     2,2,2,2,2,2,2,2,
                     1,1,1,1,1,1,1,1,
                     0,0,0,0,0,0,0,0
                ],
                BISHOP_POSITIONAL_WEIGHT = [
                     0,1,2,3,3,2,1,0,
                     1,2,3,4,4,3,2,1,
                     2,3,4,5,5,4,3,2,
                     3,4,5,6,6,5,4,3,
                     3,4,5,6,6,5,4,3,
                     2,3,4,5,5,4,3,2,
                     1,2,3,4,4,3,2,1,
                     0,1,2,3,3,2,1,0
                ],
                KNIGHT_POSITIONAL_WEIGHT = [
                     0,1,2,2,2,2,1,0,
                     1,2,4,4,4,4,2,1,
                     2,4,6,6,6,6,4,2,
                     2,4,6,6,6,6,4,2,
                     2,4,6,6,6,6,4,2,
                     2,4,6,6,6,6,4,2,
                     1,2,4,4,4,4,2,1,
                     0,1,2,2,2,2,1,0
                ],
                ROOK_POSITIONAL_WEIGHT = [
                     0,0,0,0,0,0,0,0,
                     0,1,1,1,1,1,1,0,
                     0,1,2,2,2,2,1,0,
                     0,1,2,3,3,2,1,0,
                     0,1,2,3,3,2,1,0,
                     0,1,2,2,2,2,1,0,
                     0,1,1,1,1,1,1,0,
                     0,0,0,0,0,0,0,0
                ],
                QUEEN_POSITIONAL_WEIGHT = [
                     0,1,2,3,3,2,1,0,
                     1,3,4,5,5,4,3,1,
                     2,4,6,7,7,6,4,2,
                     3,5,7,9,9,7,5,3,
                     3,5,7,9,9,7,5,3,
                     2,4,6,7,7,6,4,2,
                     1,3,4,5,5,4,3,1,
                     0,1,2,3,3,2,1,0
                ],
                KING_POSITIONAL_WEIGHT = [ #temp will change for later in game
                     0,0,0,0,0,0,0,0,
                     0,1,1,1,1,1,1,0,
                     0,1,2,2,2,2,1,0,
                     0,1,2,3,3,2,1,0,
                     0,1,2,3,3,2,1,0,
                     0,1,2,2,2,2,1,0,
                     0,1,1,1,1,1,1,0,
                     0,0,0,0,0,0,0,0
                ]):
        self.PIECE_MATERIAL_WEIGHT = {
            "PAWN" : PAWN_MATERIAL_WEIGHT,
            "BISHOP" : BISHOP_MATERIAL_WEIGHT,
            "KNIGHT" : KNIGHT_MATERIAL_WEIGHT,
            "ROOK" : ROOK_WIEGHT,
            "QUEEN" : QUEEN_MATERIAL_WEIGHT
        }
        self.POSITIONAL_WEIGHT = {
            "WPAWN" : WPAWN_POSITIONAL_WEIGHT,
            "DPAWN" : DPAWN_POSITIONAL_WEIGHT,
            "BISHOP" : BISHOP_POSITIONAL_WEIGHT,
            "KNIGHT" : KNIGHT_POSITIONAL_WEIGHT,
            "ROOK" : ROOK_POSITIONAL_WEIGHT,
            "QUEEN" : QUEEN_POSITIONAL_WEIGHT,
            "KING" : KNIGHT_POSITIONAL_WEIGHT
        }
        self.bitboard_object = bitboard_object
        self.py_sort = pysort.Sorting()
    @property
    def material_advantage(self):
        d_material = 0
        w_material = 0
        for key in self.bitboard_object.bitboard_dict.keys():
            for board in self.bitboard_object.bitboard_dict[key]:
                match key:
                    case "pawn":
                        w_material += self.PIECE_MATERIAL_WEIGHT["PAWN"]
                    case "bishop":
                        w_material += self.PIECE_MATERIAL_WEIGHT["BISHOP"]
                    case "knight":
                        w_material += self.PIECE_MATERIAL_WEIGHT["KNIGHT"]
                    case "rook":
                        w_material += self.PIECE_MATERIAL_WEIGHT["ROOK"]
                    case "queen":
                        w_material += self.PIECE_MATERIAL_WEIGHT["QUEEN"]
                    case "Pawn":
                        d_material += self.PIECE_MATERIAL_WEIGHT["PAWN"]
                    case "Bishop":
                        d_material += self.PIECE_MATERIAL_WEIGHT["BISHOP"]
                    case "Knight":
                        d_material += self.PIECE_MATERIAL_WEIGHT["KNIGHT"]
                    case "Rook":
                        d_material += self.PIECE_MATERIAL_WEIGHT["ROOK"]
                    case "Queen":
                        d_material += self.PIECE_MATERIAL_WEIGHT["QUEEN"]
        return w_material, d_material
    @property
    def positional_advantage(self):
        w_positional = 0
        d_positional = 0
        for key in self.bitboard_object.bitboard_dict.keys():
            for board in self.bitboard_object.bitboard_dict[key]:
                board_index = int(math.log2(board))
                match key:
                    case "pawn":
                        w_positional += self.POSITIONAL_WEIGHT["WPAWN"][board_index]
                        break
                    case "bishop":
                        w_positional += self.POSITIONAL_WEIGHT["BISHOP"][board_index]
                        break
                    case "knight":
                        w_positional += self.POSITIONAL_WEIGHT["KNIGHT"][board_index]
                        break
                    case "rook":
                        w_positional += self.POSITIONAL_WEIGHT["ROOK"][board_index]
                        break
                    case "queen":
                        w_positional += self.POSITIONAL_WEIGHT["QUEEN"][board_index]
                        break
                    case "king":
                        w_positional += self.POSITIONAL_WEIGHT["KING"][board_index]
                        break
                    case "Pawn":
                        d_positional += self.POSITIONAL_WEIGHT["DPAWN"][board_index]
                        break
                    case "Bishop":
                        d_positional += self.POSITIONAL_WEIGHT["BISHOP"][board_index]
                        break
                    case "Knight":
                        d_positional += self.POSITIONAL_WEIGHT["KNIGHT"][board_index]
                        break
                    case "Rook":
                        d_positional += self.POSITIONAL_WEIGHT["ROOK"][board_index]
                        break
                    case "Queen":
                        d_positional += self.POSITIONAL_WEIGHT["QUEEN"][board_index]
                        break
                    case "King":
                        d_positional += self.POSITIONAL_WEIGHT["KING"][board_index]
                        break
        return w_positional, d_positional
    @property
    def strategical_advantage(self):
        w_strategical = 0
        d_strategical = 0
        move_board = self.bitboard_object.move_board
        for bit in self.bitboard_object.correct_format(move_board[0]):
            if int(bit) == 1:
                w_strategical += 1
        for bit in self.bitboard_object.correct_format(move_board[1]):
            if int(bit) == 1:
                d_strategical += 1
        return w_strategical, d_strategical
    @property
    def total_advantage(self):
        (w_strategical, d_strategical) = self.strategical_advantage
        (w_positional, d_positional) = self.positional_advantage
        (w_material, d_material) = self.material_advantage
        w_advantage = w_strategical + w_positional + w_material
        d_advantage = d_strategical + d_positional + d_material
        return w_advantage, d_advantage
    def start_mini_max_dict(self, position, max_time, max_depth,
                      origin_pointer=0, move_pointer=0, apply_move_pointer=0, evaluation_pointer=0,
                      current_colour = "WHITE", current_moves=0, current_key_index=0, current_origin_list=0,
                      applied_moves=[], evaluation_move={}):
        engine_parameter = EngineParameters(
                 origin_pointer, move_pointer, apply_move_pointer, evaluation_pointer,
                 current_colour, current_moves, current_key_index, current_origin_list,
                 applied_moves, evaluation_move)
        engine_parameter.current_moves, engine_parameter.current_key_index, engine_parameter.current_origin_list = self.get_moves_key_origin(position, engine_parameter.current_colour, engine_parameter.current_moves, engine_parameter.current_key_index, engine_parameter.current_origin_list)
        return self.mini_max_dict(engine_parameter, position, max_time, max_depth)
    
    def mini_max_dict(self, engine_parameter, position, max_time, max_depth, current_time=0, current_depth=0, current_max_depth=0, move_evaluation={}):
        #change this so that the it returns only when the position becomes worse than a previous position
        if (max_time < current_time) or (max_depth < current_max_depth): #self.not_best(engine_parameter.evaluation_move): #engine_parameter.max_depth < engine_parameter.current_max_depth:
            return move_evaluation, engine_parameter.evaluation_move
        applied_origin = engine_parameter.current_origin_list[engine_parameter.origin_pointer]
        engine_parameter.applied_origin = applied_origin
        if current_depth == current_max_depth:
            current_time += 1 # time
            looping = True
            for name_key in engine_parameter.current_key_index:
                for list_index in range(len(engine_parameter.current_key_index[name_key])):
                    if engine_parameter.current_key_index[name_key][list_index] == applied_origin:
                        applied_piece_key = name_key
                        looping = False
                        break
                if not(looping):
                    break
            if engine_parameter.move_pointer < len(engine_parameter.current_moves[applied_origin]):
                applied_to = engine_parameter.current_moves[applied_origin][engine_parameter.move_pointer]
                applied_move = (applied_piece_key, applied_origin, applied_to)
                
                captured = position.apply_move(applied_move)
                w_evaluation, d_evaluation = self.total_advantage
                move_evaluation[applied_move] = w_evaluation - d_evaluation
                if w_evaluation - d_evaluation not in engine_parameter.evaluation_move.keys():
                    engine_parameter.evaluation_move[w_evaluation - d_evaluation] = []
                engine_parameter.evaluation_move[w_evaluation-d_evaluation].append(self.moves_to_current(engine_parameter.applied_moves, applied_move))
                position.revert_move(applied_move, captured)
                
        move_evaluation, current_max_depth = self.iterate_mini_max(engine_parameter, position, max_time, max_depth, current_time, current_depth, current_max_depth, move_evaluation)
        
        #debugging, slows progam
        #ic(engine_parameter.current_depth, engine_parameter.current_max_depth, engine_parameter.current_colour, move_evaluation, engine_parameter.applied_moves, engine_parameter.current_moves, engine_parameter.current_origin_list, engine_parameter.move_pointer, engine_parameter.origin_pointer)
        return self.mini_max_dict(engine_parameter, position, max_time, max_depth, current_time, current_depth, current_max_depth, move_evaluation)
            
    def moves_to_current(self, applied_moves, applied_move):
        moves_to_current = []
        for previous_move_captured in applied_moves:
            previous_move, previous_captured = previous_move_captured
            moves_to_current.append(previous_move)
        moves_to_current.append(applied_move)
        return moves_to_current

    def iterate_mini_max(self, engine_parameter, position, max_time, max_depth, current_time, current_depth, current_max_depth, move_evaluation):
        if engine_parameter.move_pointer + 1 >= len(engine_parameter.current_moves[engine_parameter.applied_origin]):
            engine_parameter.move_pointer = 0
            if engine_parameter.origin_pointer + 1 >= len(engine_parameter.current_origin_list):
                engine_parameter.origin_pointer = 0
                move_evaluation, current_max_depth = self.simulate_next_move(engine_parameter, position, max_time, max_depth, current_time, current_depth, current_max_depth, move_evaluation)
            else:
                engine_parameter.origin_pointer += 1
        else:
            engine_parameter.move_pointer += 1
        return move_evaluation, current_max_depth
    
    def simulate_next_move(self, engine_parameter, position, max_time, max_depth, current_time, current_depth, current_max_depth, move_evaluation):
        """
        ordered_eval = self.order_eval_list(engine_parameter.evaluation_move)
        search_move = engine_parameter.evaluation_move[ordered_eval[engine_parameter.evaluation_pointer]][engine_parameter.apply_move_pointer]
        captured = position.apply_move(search_move)
        engine_parameter.applied_moves.append((search_move, captured))
        if engine_parameter.current_colour == "WHITE":
            new_colour = "BLACK"
        else:
            new_colour = "WHITE"
        new_moves, new_key_index, new_origin_list = self.get_moves_key_origin(position, new_colour, engine_parameter.current_moves, engine_parameter.current_key_index, engine_parameter.current_origin_list)
        move_evaluation[move] = {}
        move_evaluation[move] = self.mini_max_dict(engine_parameter)[0]
        
        engine_parameter.origin_pointer = len(engine_parameter.current_origin_list)-1
        move_pointer = len(engine_parameter.current_moves[applied_origin])-1
        move, captured = engine_parameter.applied_moves.pop()
        position.revert_move(move, captured)
        
        """
        if not(current_max_depth + 1 >= max_depth):
            for move in list(move_evaluation):
                captured = position.apply_move(move)
                engine_parameter.applied_moves.append((move, captured))
                old_colour = engine_parameter.current_colour
                old_moves = engine_parameter.current_moves
                old_key_index = engine_parameter.current_key_index
                old_origin_list = engine_parameter.current_origin_list
                
                if engine_parameter.current_colour == "WHITE":
                    engine_parameter.current_colour = "BLACK"
                else:
                    engine_parameter.current_colour = "WHITE"
                moves, key_index, origin_list = self.get_moves_key_origin(position, engine_parameter.current_colour, engine_parameter.current_moves, engine_parameter.current_key_index, engine_parameter.current_origin_list)
                engine_parameter.current_moves, engine_parameter.current_key_index, engine_parameter.current_origin_list = moves, key_index, origin_list
                
                move_evaluation[move] = self.mini_max_dict(engine_parameter, position, max_time, max_depth, current_time, current_depth+1, current_max_depth, move_evaluation)[0]
                
                revert_move, captured = engine_parameter.applied_moves.pop()
                position.revert_move(revert_move, captured)
                engine_parameter.current_colour = old_colour
                engine_parameter.current_moves = old_moves
                engine_parameter.current_key_index = old_key_index
                engine_parameter.current_origin_list = old_origin_list
                
        engine_parameter.origin_pointer = len(engine_parameter.current_origin_list)-1
        engine_parameter.move_pointer = len(engine_parameter.current_moves[engine_parameter.applied_origin])-1
        current_max_depth += 1
        return move_evaluation, current_max_depth
    def order_eval_list(self, applied_move):
        order_eval = []
        for eval in evaluation_move.keys:
            order_eval.append(eval)
        return self.py_sort.mergeSort(order_eval)

    def get_moves_key_origin(self, position, colour, moves, key, origin_list):
        if colour == "WHITE":
            move_colour_index = 0
        else:
            move_colour_index = 1
        moves, key  = position.split_move_dict[move_colour_index]
        origin_list = list(moves.keys())
        return moves, key, origin_list

    #WIP - efficiency
if __name__ == "__main__":
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = bitboard.BitBoard(board)
    engine = Engine(bitBoard)
    max_depth = int(input("Enter a depth, only low depth work fully: "))
    move_evaluation, evaluation_move = engine.start_mini_max_dict(bitBoard, 50, max_depth)
    ic(move_evaluation, evaluation_move)