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
    
    def mini_max_dict(self, position, max_time, max_depth,
                      current_time=0, current_depth=0, current_max_depth=0,
                      origin_pointer=0, move_pointer=0, apply_move_pointer=0, evaluation_pointer=0,
                      current_colour = "WHITE", current_moves=0, current_key_index=0, current_origin_list=0,
                      move_evaluation={}, applied_moves=[], evaluation_move={}):
        if max_time < current_time or max_depth < current_max_depth:
            return move_evaluation, evaluation_move
        if current_time == 0:
            current_moves, current_key_index, current_origin_list = self.get_moves_key_origin(position, current_colour)
        applied_origin = current_origin_list[origin_pointer]
        current_time += 1 # time
        if current_depth == current_max_depth:
            looping = True
            for name_key in current_key_index:
                for list_index in range(len(current_key_index[name_key])):
                    if current_key_index[name_key][list_index] == applied_origin:
                        applied_piece_key = name_key
                        looping = False
                        break
                if not(looping):
                    break
            if move_pointer < len(current_moves[applied_origin]):
                applied_to = current_moves[applied_origin][move_pointer]
                applied_move = (applied_piece_key, applied_origin, applied_to)
                
                captured = position.apply_move(applied_move)
                w_evaluation, d_evaluation = self.total_advantage
                move_evaluation[applied_move] = w_evaluation - d_evaluation
                
                evaluation_move = self.remove_overlappying_moves(evaluation_move, applied_moves)
                if w_evaluation - d_evaluation not in evaluation_move.keys():
                    evaluation_move[w_evaluation-d_evaluation] = []
                evaluation_move[w_evaluation-d_evaluation].append(self.moves_to_current(applied_moves, applied_move))
                
                position.revert_move(applied_move, captured)
                
        move_evaluation, current_max_depth, origin_pointer, move_pointer = self.iterate_mini_max(
            position, max_time, max_depth,
            current_time, current_depth, current_max_depth,
            origin_pointer, move_pointer, apply_move_pointer, evaluation_pointer,
            current_colour, current_moves, current_key_index, current_origin_list,
            move_evaluation, applied_moves, applied_origin, evaluation_move)
        
        #debugging, slows progam
        #ic(current_depth, current_max_depth, current_colour, move_evaluation, applied_moves, current_moves, current_origin_list, move_pointer, origin_pointer)
        
        return self.mini_max_dict(
            position, max_time, max_depth,
            current_time, current_depth, current_max_depth,
            origin_pointer, move_pointer, apply_move_pointer, evaluation_pointer,
            current_colour, current_moves, current_key_index, current_origin_list,
            move_evaluation, applied_moves, evaluation_move)
            
    def iterate_mini_max(
        self, position, max_time, max_depth,
        current_time, current_depth, current_max_depth,
        origin_pointer, move_pointer, apply_move_pointer, evaluation_pointer,
        current_colour, current_moves, current_key_index, current_origin_list,
        move_evaluation, applied_moves, applied_origin, evaluation_move):
        if move_pointer >= len(current_moves[applied_origin]):
            move_pointer = 0
            if origin_pointer >= len(current_origin_list):
                origin_pointer = 0
                move_evaluation, current_max_depth = self.simulate_next_move(
                position, max_time, max_depth,
                current_time, current_depth, current_max_depth,
                origin_pointer, move_pointer, apply_move_pointer, evaluation_pointer,
                current_colour, current_moves, current_key_index, current_origin_list,
                move_evaluation, applied_moves, evaluation_move)
            else:
                origin_pointer += 1
        else:
            move_pointer += 1
        return move_evaluation, current_max_depth, origin_pointer, move_pointer
    
    def simulate_next_move(
        self, position, max_time, max_depth,
        current_time, current_depth, current_max_depth,
        origin_pointer, move_pointer, apply_move_pointer, evaluation_pointer,
        current_colour, current_moves, current_key_index, current_origin_list,
        move_evaluation, applied_moves, evaluation_move):
        """
        ordered_eval = self.order_eval_list(evaluation_move)
        search_move = evaluation_move[ordered_eval[len(ordered_eval)-evaluation_pointer]][apply_move_pointer]
        captured = position.apply_move(search_move)
        applied_moves.append((search_move, captured))
        if current_colour == "WHITE":
            new_colour = "BLACK"
        else:
            new_colour = "WHITE"
        new_moves, new_key_index, new_origin_list = self.get_moves_key_origin(position, new_colour, current_moves, current_key_index, current_origin_list)
        move_evaluation[move] = {}
        move_evaluation[move] = self.mini_max_dict(
                    position, max_time, max_depth,
                    current_time, current_depth + 1, current_max_depth,
                    origin_pointer, move_pointer, apply_move_pointer,
                    new_colour, new_moves, new_key_index, new_origin_list,
                    move_evaluation[move], applied_moves)
        move, captured = applied_moves.pop()
        position.revert_move(move, captured)
        
        if apply_move_pointer >= len(evaluation_move[ordered_eval[len(ordered_eval)-evaluation_pointer]]):
            
        
        return move_evaluation
        """
        if current_max_depth + 1 < max_depth:
            for move in move_evaluation.keys():
                captured = position.apply_move(move)
                applied_moves.append((move, captured))
                if current_colour == "WHITE":
                    new_colour = "BLACK"
                else:
                    new_colour = "WHITE"
                new_moves, new_key_index, new_origin_list = self.get_moves_key_origin(position, new_colour)
                move_evaluation[move] = {}
                move_evaluation[move] = self.mini_max_dict(
                    position, max_time, max_depth,
                    current_time, current_depth + 1, current_max_depth,
                    origin_pointer, move_pointer, apply_move_pointer, evaluation_pointer,
                    new_colour, new_moves, new_key_index, new_origin_list,
                    move_evaluation[move], applied_moves)[0]
                move, captured = applied_moves.pop()
                position.revert_move(move, captured)
        current_max_depth += 1
        return move_evaluation, current_max_depth
        
    
    def remove_overlappying_moves(self, evaluation_move, applied_moves):
        del_list = []
        for eval in evaluation_move.keys():
            for index, move in enumerate(evaluation_move[eval]):
                apply_move_list = []
                for apply_move, captured in applied_moves:
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
    
    def moves_to_current(self, applied_moves, applied_move):
        moves_to_current = []
        for move, captured in applied_moves:
            moves_to_current.append(move)
        moves_to_current.append(applied_move)
        return moves_to_current
    
    def order_eval_list(self, evaluation_move): #wip
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
    
    #current need to a save a dictionary with moves linked to the evaluation and using a merge sort at the end to find every move from best to worst
if __name__ == "__main__":
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = bitboard.BitBoard(board)
    engine = Engine(bitBoard)
    max_depth = int(input("Enter a depth, only low depth work fully: "))
    move_evaluation, evaluation_move = engine.mini_max_dict(bitBoard, 5000, max_depth)
    ic(evaluation_move)