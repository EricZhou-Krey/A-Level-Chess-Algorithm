import bitboard, math
from icecream import ic
class Engine:
    def __init__(self, __bitboard_object, PAWN_MATERIAL_WEIGHT=10, BISHOP_MATERIAL_WEIGHT=30, KNIGHT_MATERIAL_WEIGHT=30, ROOK_WIEGHT=50, QUEEN_MATERIAL_WEIGHT=100,
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
                KING_POSITIONAL_WEIGHT = [ 
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
            "KING" : KING_POSITIONAL_WEIGHT
        }
        self.__bitboard_object = __bitboard_object
        self.max_time = math.inf
        self.__current_time = 0
        self.max_depth = math.inf
        self.longest_current_move = 0
        self.__current_best_eval = None
    @property
    def material_advantage(self):
        d_material = 0
        w_material = 0
        for key in self.__bitboard_object.bitboard_dict.keys():
            for index, bit in enumerate(str(format(self.__bitboard_object.bitboard_dict[key], "064b"))[::-1]):
                if int(bit) == 1:
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
        for key in self.__bitboard_object.bitboard_dict.keys():
            for board_index, bit in enumerate(str(format(self.__bitboard_object.bitboard_dict[key], "064b"))[::-1]):
                if int(bit) == 1:
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
        move_board = self.__bitboard_object.move_board
        for bit in str(move_board[0])[::-1]:
            if int(bit) == 1:
                w_strategical += 1
        for bit in str(move_board[1])[::-1]:
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

    def min_max_dict(self,
                      current_depth=0,
                      current_colour="WHITE", current_moves=None, current_key_index=None, current_origin_list=None,
                      move_evaluation={}):
        
        def simulate_next_move(current_depth, current_colour, move_evaluation, __bitboard_object, __current_best_eval):
            search_move = current_min_max(move_evaluation, current_colour)[1]
            __bitboard_object.apply_move(search_move)
            if current_colour == "WHITE":
                new_colour = "BLACK"
            else:
                new_colour = "WHITE"
            new_moves, new_key_index, new_origin_list = get_moves_key_origin(__bitboard_object, new_colour)
            move_evaluation[search_move] = {}
            move_evaluation[search_move] = self.min_max_dict(
                        current_depth + 1,
                        new_colour, new_moves, new_key_index, new_origin_list,
                        move_evaluation[search_move])
            __current_best_eval = current_min_max(move_evaluation, current_colour)[0]
            __bitboard_object.revert_move()
            return move_evaluation, __current_best_eval
        
        def get_moves_key_origin(__bitboard_object, colour):
            if colour == "WHITE":
                move_colour_index = 0
            else:
                move_colour_index = 1
            moves, key  = __bitboard_object.split_move_dict[move_colour_index]
            origin_list = list(moves.keys())
            return moves, key, origin_list
        
        def current_min_max(move_evaluation, current_colour):
            if current_colour == "WHITE":
                min_max = -math.inf
                next_colour = "BLACK"
            else:
                min_max = math.inf
                next_colour = "WHITE"
            for move in move_evaluation.keys():
                if type(move_evaluation[move]) is float:
                    evaluation = move_evaluation[move]
                else:
                    evaluation = current_min_max(move_evaluation[move], next_colour)[0]
                if current_colour == "WHITE":
                    if evaluation >= min_max:
                        min_max = evaluation
                        min_max_move = move
                else:
                    if evaluation <= min_max:
                        min_max = evaluation
                        min_max_move = move
            return min_max, min_max_move
        
        def is_current_best(move_evaluation, current_colour, current_depth, __current_best_eval):
            if len(move_evaluation) == 0:
                return False, __current_best_eval
            if current_depth % 2 == 1:
                if current_colour == "WHITE":
                    original_colour = "BLACK"
                else:
                    original_colour = "WHITE"
            else:
                original_colour = current_colour
            min_max = current_min_max(move_evaluation, current_colour)[0]
            if original_colour == current_colour:
                if original_colour == "WHITE" and min_max >= __current_best_eval:
                    __current_best_eval = min_max
                    return True, __current_best_eval
                elif original_colour == "BLACK" and min_max <= __current_best_eval:
                    __current_best_eval = min_max
                    return True, __current_best_eval
            else:
                return True, __current_best_eval
            return False, __current_best_eval
        
        if self.__current_time == 0:
            current_moves, current_key_index, current_origin_list = get_moves_key_origin(self.__bitboard_object, current_colour)
            if current_colour == "WHITE":
                self.__current_best_eval = -math.inf
            else:
                self.__current_best_eval = math.inf
        
        if len(current_origin_list) == {}:
            if not(self.__bitboard_object.king_safe(False)) and current_colour == "WHITE":
                return -math.inf
            elif not(self.__bitboard_object.king_safe()) and current_colour == "BLACK":
                return math.inf
            else:
                return 0.0
        
        if self.longest_current_move < current_depth:
            self.longest_current_move = current_depth
            
        for applied_origin in current_origin_list:
            for applied_to in current_moves[applied_origin]:
                self.__current_time += 1
                looping = True
                for name_key in current_key_index:
                    for list_index in range(len(current_key_index[name_key])):
                        if current_key_index[name_key][list_index] == applied_origin:
                            applied_piece_key = name_key
                            looping = False
                            break
                    if not(looping):
                        break
                if type(applied_to) is int:
                    applied_move = (applied_piece_key, applied_origin, applied_to)
                else:
                    applied_to, promote_key = applied_to
                    applied_move = (applied_piece_key, applied_origin, applied_to, promote_key)
                    
                self.__bitboard_object.apply_move(applied_move)
                w_evaluation, d_evaluation = self.total_advantage
                sum_eval = float(w_evaluation - d_evaluation)
                move_evaluation[applied_move] = sum_eval
                
                self.__bitboard_object.revert_move()
                
        while True:
            best, self.__current_best_eval = is_current_best(move_evaluation, current_colour, current_depth, self.__current_best_eval)
            if self.max_time < self.__current_time or current_depth > self.max_depth:
                return move_evaluation
            elif best:
                move_evaluation, self.__current_best_eval = simulate_next_move(current_depth, current_colour, move_evaluation, self.__bitboard_object, self.__current_best_eval)
            else:
                return move_evaluation
    
    def best_moves(self, move_evaluation:dict, current_colour="WHITE", max_length=999, arrays=3, min_length=2): #needs effeciency
        
        def current_min_max(move_evaluation, current_colour):
            if current_colour == "WHITE":
                min_max = -math.inf
                next_colour = "BLACK"
            else:
                min_max = math.inf
                next_colour = "WHITE"
            for move in move_evaluation.keys():
                if type(move_evaluation[move]) is float:
                    evaluation = move_evaluation[move]
                else:
                    evaluation = current_min_max(move_evaluation[move], next_colour)[0]
                if current_colour == "WHITE":
                    if evaluation >= min_max:
                        min_max = evaluation
                        min_max_move = move
                else:
                    if evaluation <= min_max:
                        min_max = evaluation
                        min_max_move = move
            return min_max, min_max_move
        
        def remove_searched(move_evaluation, result, pointer=0):
            if pointer + 1 == len(result):
                del move_evaluation[result[pointer]]
                if len(move_evaluation) == 0:
                    return None
            else:
                move_evaluation[result[pointer]] = remove_searched(move_evaluation[result[pointer]], result, pointer+1)
                if move_evaluation[result[pointer]] == None:
                    del move_evaluation[result[pointer]]
            return move_evaluation
        
        best_moves = []
        while len(best_moves) < arrays:
            result = []
            temp_move_eval = move_evaluation
            eval, move = current_min_max(temp_move_eval, current_colour)
            for depth in range(max_length):
                result.append(move)
                if type(temp_move_eval[move]) is dict:
                    temp_move_eval = temp_move_eval[move]
                    if current_colour == "WHITE":
                        current_colour = "BLACK"
                    else:
                        current_colour = "WHITE"
                else:
                    break
                move = current_min_max(temp_move_eval, current_colour)[1]
            if min_length <= len(result):
                best_moves.append((eval, result))
            move_evaluation = remove_searched(move_evaluation, result)
        return best_moves

if __name__ == "__main__":
    board = "...rrbk.p..q.pp..p....np..p..N.....pNPP..P.P......P...QP....RRK."
    bitBoard = bitboard.BitBoard(board)
    bitBoard.output_board_formatted
    engine = Engine(bitBoard)
    engine.max_time = int(input("Enter max time: "))
    #engine.max_depth = int(input("Enter max depth: "))
    move_evaluation = engine.min_max_dict(current_colour="BLACK")
    ic(move_evaluation, engine.best_moves(move_evaluation, "BLACK", arrays=1, min_length=engine.longest_current_move))