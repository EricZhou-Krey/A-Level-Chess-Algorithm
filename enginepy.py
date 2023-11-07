import bitboard, time, math
from icecream import ic
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
        self.bitboard_object = bitboard_object
        self.extending = True
        self.origin_pointer = 0
        self.move_pointer = 0
        self.current_time = 0
        self.current_best_eval = 0
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
    
    def min_max_dict(self, max_time,
                      current_depth=0, current_evaluation_move=[], ordered_eval=[],
                      current_colour="WHITE", current_moves=0, current_key_index=0, current_origin_list=0,
                      move_evaluation={}, applied_moves=[], evaluation_move={}):
        if self.current_time == 0:
            current_moves, current_key_index, current_origin_list = self.get_moves_key_origin(self.bitboard_object, current_colour)
            if current_colour == "WHITE":
                self.current_best_eval = -math.inf
            else:
                self.current_best_eval = math.inf
        if max_time < self.current_time:
            return move_evaluation, evaluation_move
        applied_origin = current_origin_list[self.origin_pointer]
        self.current_time += 1
        if type(move_evaluation) is float:
            return move_evaluation, evaluation_move
        elif not(self.extending) and not(self.is_current_best(move_evaluation, current_colour, current_depth)):
            return move_evaluation, evaluation_move
        if self.extending:
            looping = True
            for name_key in current_key_index:
                for list_index in range(len(current_key_index[name_key])):
                    if current_key_index[name_key][list_index] == applied_origin:
                        applied_piece_key = name_key
                        looping = False
                        break
                if not(looping):
                    break
            if self.move_pointer < len(current_moves[applied_origin]):
                if type(current_moves[applied_origin][self.move_pointer]) is int:
                    applied_to = current_moves[applied_origin][self.move_pointer]
                    applied_move = (applied_piece_key, applied_origin, applied_to)
                else:
                    applied_to, promote_key = current_moves[applied_origin][self.move_pointer]
                    applied_move = (applied_piece_key, applied_origin, applied_to, promote_key)
                
                captured = self.bitboard_object.apply_move(applied_move)
                w_evaluation, d_evaluation = self.total_advantage
                move_evaluation[applied_move] = w_evaluation - d_evaluation
                
                if w_evaluation - d_evaluation not in evaluation_move.keys():
                    evaluation_move[w_evaluation-d_evaluation] = []
                evaluation_move[w_evaluation-d_evaluation].append(self.moves_to_current(applied_moves, applied_move))
                evaluation_move = self.remove_overlappying_moves(evaluation_move, applied_moves)
                
                self.bitboard_object.revert_move(applied_move, captured)
                
            move_evaluation = self.iterate_min_max(current_moves, current_origin_list, move_evaluation, applied_origin)
        else:
            move_evaluation = self.simulate_next_move(max_time, current_depth, current_colour, move_evaluation, applied_moves)
        
        return self.min_max_dict(
            max_time,
            current_depth, current_evaluation_move, ordered_eval,
            current_colour, current_moves, current_key_index, current_origin_list,
            move_evaluation, applied_moves, evaluation_move)
            
    def iterate_min_max(self, current_moves, current_origin_list, move_evaluation, applied_origin):
        if self.move_pointer + 1 >= len(current_moves[applied_origin]):
            self.move_pointer = 0
            if self.origin_pointer + 1 >= len(current_origin_list):
                self.origin_pointer = 0
                self.extending = False
            else:
                self.origin_pointer += 1
        else:
            self.move_pointer += 1
        return move_evaluation
    
    def simulate_next_move(self, max_time, current_depth, current_colour, move_evaluation, applied_moves):
        search_move = self.current_min_max(move_evaluation, current_colour)[1]
        captured = self.bitboard_object.apply_move(search_move)
        applied_moves.append(search_move)
        if current_colour == "WHITE":
            new_colour = "BLACK"
        else:
            new_colour = "WHITE"
            
        self.extending = True
        new_moves, new_key_index, new_origin_list = self.get_moves_key_origin(self.bitboard_object, new_colour)
        move_evaluation[search_move] = {}
        move_evaluation[search_move] = self.min_max_dict(
                    max_time,
                    current_depth + 1, [], [],
                    new_colour, new_moves, new_key_index, new_origin_list,
                    move_evaluation[search_move], applied_moves)[0]
        if move_evaluation[search_move] == {}:
            if current_colour == "WHITE":
                return math.inf
            else:
                return -math.inf
        self.current_best_eval = self.current_min_max(move_evaluation, current_colour)[0]
        move = applied_moves.pop()
        self.bitboard_object.revert_move(move, captured)
        self.extending = False
        return move_evaluation

    def is_current_best(self, move_evaluation, current_colour, current_depth):
        if not(len(move_evaluation) > 0):
            return True
        if current_depth % 2 == 1:
            if current_colour == "WHITE":
                original_colour = "BLACK"
            else:
                original_colour = "WHITE"
        else:
            original_colour = current_colour
        min_max = self.current_min_max(move_evaluation, current_colour)[0]
        if original_colour == "WHITE" and min_max >= self.current_best_eval:
            self.current_best_eval = min_max
            return True
        elif original_colour == "BLACK" and min_max <= self.current_best_eval:
            self.current_best_eval = min_max
            return True
        else:
            return False
        
    def current_min_max(self, move_evaluation, current_colour):
        if current_colour == "WHITE":
            min_max = -math.inf
            next_colour = "BLACK"
        else:
            min_max = math.inf
            next_colour = "WHITE"
        for move in move_evaluation.keys():
            if type(move_evaluation[move]) is float or type(move_evaluation[move]) is int:
                evaluation = move_evaluation[move]
            elif type(move_evaluation[move]) is dict:
                evaluation = self.current_min_max(move_evaluation[move], next_colour)[0]
            if current_colour == "WHITE":
                if evaluation >= min_max:
                    min_max = evaluation
                    min_max_move = move
            else:
                if evaluation <= min_max:
                    min_max = evaluation
                    min_max_move = move
        return min_max, min_max_move

    def remove_overlappying_moves(self, evaluation_move, applied_moves):
        del_list = []
        for eval in evaluation_move.keys():
            for index, move in enumerate(evaluation_move[eval]):
                apply_move_list = []
                for apply_move in applied_moves:
                    apply_move_list.append(apply_move)
                if move == apply_move_list:
                    del_list.append((eval, index))
        backpush = 0
        deleted_eval = []
        for eval, index in del_list:
            if index-backpush >= 0 and not(eval in deleted_eval):
                del evaluation_move[eval][index-backpush]
                backpush += 1
            if index-backpush < 0 and not(eval in deleted_eval):
                deleted_eval.append(eval)
                del evaluation_move[eval]
        return evaluation_move
    
    def moves_to_current(self, applied_moves, applied_move=0):
        moves_to_current = []
        for move in applied_moves:
            moves_to_current.append(move)
        if applied_move != 0:
            moves_to_current.append(applied_move)
        return moves_to_current
    
    def order_eval_list(self, evaluation_move):
        eval_list = list(evaluation_move.keys())
        return self.merge_sort(eval_list)
    
    def merge_sort(self, list):
        if len(list) > 1:
            mid = len(list) // 2
            left = list[:mid]
            right = list[mid:]
            
            self.merge_sort(left)
            self.merge_sort(right)
            
            list = self.compare(list, left, right)
            
        return list
    
    def compare(self, list, left, right, left_pointer=0, right_pointer=0, list_pointer=0):
        if left_pointer  >= len(left) or right_pointer >= len(right):
            if left_pointer < len(left):
                list[list_pointer] = left[left_pointer]
                list = self.compare(list, left, right, left_pointer+1, right_pointer, list_pointer+1)
            elif right_pointer < len(right):
                list[list_pointer] = right[right_pointer]
                list = self.compare(list, left, right, left_pointer, right_pointer+1, list_pointer+1)
            else:
                return list
        else:
            if left[left_pointer] < right[right_pointer]:
                list[list_pointer] = left[left_pointer]
                list = self.compare(list, left, right, left_pointer+1, right_pointer, list_pointer+1)
            else:
                list[list_pointer] = right[right_pointer]
                list = self.compare(list, left, right, left_pointer, right_pointer+1, list_pointer+1)
        return list
    
    def get_moves_key_origin(self, position, colour):
        if colour == "WHITE":
            move_colour_index = 0
        else:
            move_colour_index = 1
        moves, key  = position.split_move_dict[move_colour_index]
        origin_list = list(moves.keys())
        return moves, key, origin_list
    
if __name__ == "__main__":
    board = ".............k.....r...p...R.P......P.P.P..p...P.P...P........K."
    ic(len(board))
    bitBoard = bitboard.IBitBoard(board)
    bitBoard.output_board_formatted()
    engine = Engine(bitBoard)
    max_time = int(input("Enter max time: "))
    move_evaluation, evaluation_move = engine.min_max_dict(max_time, current_colour="WHITE")
    ic(move_evaluation)
    ic(engine.current_min_max(move_evaluation, "WHITE"))
    #progress of bitboard first
    