import math, time
from bitboard import BitBoard
from icecream import ic
class Engine:
    def __init__(self, bitboard:BitBoard, PAWN_MATERIAL_WEIGHT:float=10, BISHOP_MATERIAL_WEIGHT:float=30, KNIGHT_MATERIAL_WEIGHT:float=30, ROOK_WIEGHT:float=50, QUEEN_MATERIAL_WEIGHT:float=100, KING_MATERIAL_WEIGHT:float=0,
                #POSITIONAL_WEIGHT - indexed from 0-63, a1 to h8
                WPAWN_POSITIONAL_WEIGHT : list = [
                     0,0,0,0,0,0,0,0,
                     1,1,1,1,1,1,1,1,
                     2,2,2,2,2,2,2,2,
                     3,3,3,3,3,3,3,3,
                     4,4,4,4,4,4,4,4,
                     5,5,5,5,5,5,5,5,
                     6,6,6,6,6,6,6,6,
                     7,7,7,7,7,7,7,7
                ],
                DPAWN_POSITIONAL_WEIGHT : list = [
                     7,7,7,7,7,7,7,7,
                     6,6,6,6,6,6,6,6,
                     5,5,5,5,5,5,5,5,
                     4,4,4,4,4,4,4,4,
                     3,3,3,3,3,3,3,3,
                     2,2,2,2,2,2,2,2,
                     1,1,1,1,1,1,1,1,
                     0,0,0,0,0,0,0,0
                ],
                BISHOP_POSITIONAL_WEIGHT : list = [
                     0,1,2,3,3,2,1,0,
                     1,2,3,4,4,3,2,1,
                     2,3,4,5,5,4,3,2,
                     3,4,5,6,6,5,4,3,
                     3,4,5,6,6,5,4,3,
                     2,3,4,5,5,4,3,2,
                     1,2,3,4,4,3,2,1,
                     0,1,2,3,3,2,1,0
                ],
                KNIGHT_POSITIONAL_WEIGHT : list = [
                     0,1,2,2,2,2,1,0,
                     1,2,4,4,4,4,2,1,
                     2,4,6,6,6,6,4,2,
                     2,4,6,6,6,6,4,2,
                     2,4,6,6,6,6,4,2,
                     2,4,6,6,6,6,4,2,
                     1,2,4,4,4,4,2,1,
                     0,1,2,2,2,2,1,0
                ],
                ROOK_POSITIONAL_WEIGHT : list = [
                     0,0,0,0,0,0,0,0,
                     0,1,1,1,1,1,1,0,
                     0,1,2,2,2,2,1,0,
                     0,1,2,3,3,2,1,0,
                     0,1,2,3,3,2,1,0,
                     0,1,2,2,2,2,1,0,
                     0,1,1,1,1,1,1,0,
                     0,0,0,0,0,0,0,0
                ],
                QUEEN_POSITIONAL_WEIGHT : list = [
                     0,1,2,3,3,2,1,0,
                     1,3,4,5,5,4,3,1,
                     2,4,6,7,7,6,4,2,
                     3,5,7,9,9,7,5,3,
                     3,5,7,9,9,7,5,3,
                     2,4,6,7,7,6,4,2,
                     1,3,4,5,5,4,3,1,
                     0,1,2,3,3,2,1,0
                ],
                KING_POSITIONAL_WEIGHT : list = [ 
                     0,0,0,0,0,0,0,0,
                     0,1,1,1,1,1,1,0,
                     0,1,2,2,2,2,1,0,
                     0,1,2,3,3,2,1,0,
                     0,1,2,3,3,2,1,0,
                     0,1,2,2,2,2,1,0,
                     0,1,1,1,1,1,1,0,
                     0,0,0,0,0,0,0,0
                ]) -> None:
        """
        Weight masks and values are assigned here to work out the advanatge of any given position
        In addition, the "max_num_searched", "max_depth" and "max_time" public variables can be 
        used to terminate the mini-max search according to certain cretia, being the number of moves
        ahead of the current positon searched (depth) and amount of moves searched (time)
        """
        self.__PIECE_MATERIAL_WEIGHT = {
            "PAWN" : PAWN_MATERIAL_WEIGHT,
            "BISHOP" : BISHOP_MATERIAL_WEIGHT,
            "KNIGHT" : KNIGHT_MATERIAL_WEIGHT,
            "ROOK" : ROOK_WIEGHT,
            "QUEEN" : QUEEN_MATERIAL_WEIGHT,
            "KING" : KING_MATERIAL_WEIGHT
        }
        self.__POSITION_WEIGHT = {
            "WPAWN" : WPAWN_POSITIONAL_WEIGHT,
            "DPAWN" : DPAWN_POSITIONAL_WEIGHT,
            "BISHOP" : BISHOP_POSITIONAL_WEIGHT,
            "KNIGHT" : KNIGHT_POSITIONAL_WEIGHT,
            "ROOK" : ROOK_POSITIONAL_WEIGHT,
            "QUEEN" : QUEEN_POSITIONAL_WEIGHT,
            "KING" : KING_POSITIONAL_WEIGHT
        }
        with open("")
        self.bitboard = bitboard
        self.max_num_searched = math.inf
        self.__num_searched = 0
        self.max_depth = math.inf
        self.max_time = math.inf
        self.__start_time = None
        self.__current_highest_depth =  1
        self.__alpha = math.inf #upper bound for black
        self.__beta = -math.inf #lower bound for white
        self.__ordered_eval_move = []
    @property
    def ordered_eval_move(self) -> list:
        return self.__ordered_eval_move
    @property
    def material_advantage(self) -> (float, float):
        """
        Iterates throught the bitboard dictionary and adds the material weight for each 1 (individual piece) in the bit board for each colour
        """
        d_material = 0
        w_material = 0
        for key in self.bitboard.bitboard_dict.keys():
            for bit in str(format(self.bitboard.bitboard_dict[key], "064b"))[::-1]:
                if int(bit) == 1:
                    if key[0].isupper():
                        d_material += self.__PIECE_MATERIAL_WEIGHT[key.upper()]
                    else:
                        w_material += self.__PIECE_MATERIAL_WEIGHT[key.upper()]
                        
        return w_material, d_material
    @property
    def positional_advantage(self) -> (float, float):
        """
        Iterates throught the bitboard dictionary and adds the positional weight for each 1 (individual piece) in the bit board for each colour,
        according to the index location of the bit (piece location)
        """
        w_positional = 0
        d_positional = 0
        for key in self.bitboard.bitboard_dict.keys():
            for board_index, bit in enumerate(str(format(self.bitboard.bitboard_dict[key], "064b"))[::-1]):
                if int(bit) == 1:
                    if key[0].isupper():
                        if key == "Pawn":
                            d_positional += self.__POSITION_WEIGHT["DPAWN"][board_index]
                        else:
                            d_positional += self.__POSITION_WEIGHT[key.upper()][board_index]
                    else:
                        if key == "pawn":
                            w_positional += self.__POSITION_WEIGHT["WPAWN"][board_index]
                        else:
                            w_positional += self.__POSITION_WEIGHT[key.upper()][board_index]
        return w_positional, d_positional
    @property
    def strategical_advantage(self) -> (float, float):
        """
        Intended to cover complex patterns like forks where 1 piece attacks 2 different higher value pieces meaning a certain material gain,
        or king safety or etc however
        Temporarily, adds the the available move squares for each colour and counts the number of tiles covered by their pieces
        """
        w_strategical = 0
        d_strategical = 0
        move_board = self.bitboard.move_board
        for bit in str(move_board[0])[::-1]:
            if int(bit) == 1:
                w_strategical += 1
        for bit in str(move_board[1])[::-1]:
            if int(bit) == 1:
                d_strategical += 1
        return w_strategical, d_strategical
    @property
    def total_advantage(self) -> (float, float):
        """
        Totals the advantage for each colour from the previous functions creating an estimate for which colour is winning in a given position,
        and by how much that colour is winning by
        """
        (w_strategical, d_strategical) = self.strategical_advantage
        (w_positional, d_positional) = self.positional_advantage
        (w_material, d_material) = self.material_advantage
        w_advantage = w_strategical + w_positional + w_material
        d_advantage = d_strategical + d_positional + d_material
        return w_advantage, d_advantage

    def min_max_dict(self,
                      current_depth:int=0,
                      current_colour:str="WHITE", current_moves=None, current_key_index=None, current_origin_list=None,
                      move_evaluation:dict={}):
        def simulate_next_move(current_depth, current_colour, move_evaluation, search_move) -> dict:
            """
            Extends the move tree by finding the current best move on the current position,
            then simulating that best move, and recuring the mini max algorithm on the new position
            
            After the branch that is being searched becomes worse than the current best tree,
            move evaluation is updated, current best eval is updated, the simulated move is reverted
            and move evaluation is returned
            """
            
            self.bitboard.apply_move(search_move)
            if current_colour == "WHITE":
                new_colour = "BLACK"
            else:
                new_colour = "WHITE"
            move_evaluation[search_move] = {}
            move_evaluation[search_move] = self.min_max_dict(
                        current_depth + 1,
                        new_colour, None, None, None,
                        move_evaluation[search_move])
            self.bitboard.revert_move()
            return move_evaluation
        
        def get_moves_key_origin(bitboard:BitBoard, colour:str) -> (dict, dict, list):
            """
            Extracts the avaiable moves, key index and origin list from the bitboard object passed into the function
            """
            if colour == "WHITE":
                move_colour_index = 0
            else:
                move_colour_index = 1
            moves, key  = bitboard.split_move_dict[move_colour_index]
            origin_list = list(moves.keys())
            return moves, key, origin_list
                    
        def insert_to_ordered_eval_move(evaluation:float, move_list:list, low=None, high=None) -> None:
            if None in [low, high]:
                low = 0
                high = len(self.__ordered_eval_move)-1
                if high < 0:
                    self.__ordered_eval_move.insert(low, (move_list, evaluation))
                    return
                
            if high >= low:
                mid = (low + high) // 2
                ordered_evaluation = self.__ordered_eval_move[mid][1]
                if ordered_evaluation == evaluation:
                    self.__ordered_eval_move.insert(mid, (move_list, sum_eval))
                elif ordered_evaluation > evaluation:
                    insert_to_ordered_eval_move(evaluation, move_list, low, mid-1)
                else:
                    insert_to_ordered_eval_move(evaluation, move_list, mid+1, high)
            elif evaluation > self.__ordered_eval_move[high][1] or high < 0:
                self.__ordered_eval_move.insert(low, (move_list, evaluation))
            else:
                self.__ordered_eval_move.insert(high, (move_list, evaluation))

        def within_alpha_beta(colour:str, evaluation:float) -> bool:
            if (colour == "BLACK" and evaluation >= self.__beta) or (colour == "WHITE" and evaluation <= self.__alpha):
                return True
            return False
        
        def update_alpha_beta(colour:str, move_evaluation:dict, search_move:tuple) -> None:
            if colour == "BLACK":
                best_move_eval = -math.inf
                for eval in move_evaluation[search_move].values():
                    best_move_eval = max(best_move_eval, eval)
                self.__alpha = min(self.__alpha, best_move_eval)
            else:
                best_move_eval = math.inf
                for eval in move_evaluation[search_move].values():
                    best_move_eval = min(best_move_eval, eval)
                self.__beta = max(self.__beta, best_move_eval)
        
        def sort_move_evaluation_keys(move_evaluation:dict) -> list:
            def merge_sort(num_list:float):
                def compare(num_list:list, left:list, right:list, left_pointer:int=0, right_pointer:int=0, list_pointer:int=0):
                    if left_pointer >= len(left) or right_pointer >= len(right):
                        if left_pointer < len(left):
                            num_list[list_pointer] = left[left_pointer]
                            num_list = compare(num_list, left, right, left_pointer+1, right_pointer, list_pointer+1)
                        elif right_pointer< len(right):
                            num_list[list_pointer] = right[right_pointer]
                            num_list = compare(num_list, left, right, left_pointer, right_pointer+1, list_pointer+1)
                        else:
                            return num_list
                    else:
                        if left[left_pointer] < right[right_pointer]:
                            num_list[list_pointer] = left[left_pointer]
                            num_list = compare(num_list, left, right, left_pointer+1, right_pointer, list_pointer+1)
                        else:
                            num_list[list_pointer] = right[right_pointer]
                            num_list = compare(num_list, left, right, left_pointer, right_pointer+1, list_pointer+1)
                    return num_list
                
                if len(num_list) > 1:
                    mid = len(num_list) // 2
                    left = num_list[:mid]
                    right = num_list[mid:]
                    
                    merge_sort(left)
                    merge_sort(right)
                    
                    num_list = compare(num_list, left, right)
                    
                return num_list
            
            def remove_duplicates(evaluation_list:list):
                previous = None
                remove_list = []
                for evaluation in evaluation_list:
                    if previous == evaluation:
                        remove_list.append(evaluation)
                    previous = evaluation
                for remove_eval in remove_list:
                    evaluation_list.remove(remove_eval)
                return evaluation_list
            
            evaluation_list = [eval for eval in move_evaluation.values()]
            if type(evaluation_list[0]) is float:
                evaluation_list = merge_sort(evaluation_list)
                evaluation_list = remove_duplicates(evaluation_list)
                
                ordered_move_list = []
                #incorrect ordering
                for evaluation in evaluation_list:
                    for move in [key for key, value in move_evaluation.items() if value == evaluation]:
                        ordered_move_list.append(move)
                        
                return ordered_move_list
            
            return move_evaluation.keys()
        
        """
        Main loop for the chess engine, being the mini-max algorithm explained in the documentation and analysis:
        
        Firstly, if the recursive algorithm has no current_moves, current_key_index or current_origin_list used to iterate
        bewteen moves of the current position they are calulated - usually occurs at the start of the algorithm, and when a
        new move is simulated
        
        Then checkmate and stalemate positions are checked, where: if currently there are no legal moves to be made by the active player
        then if the current king is in danger, then positive or negative infinity for black or white as the oppoent has
        achieved checkmate, if the king is still safe but no moves are avaiable then 0 is return as this is stalemate
        """
        
        if self.__start_time == None:
            self.__start_time = time.time()
            
        if current_depth + 1 >= self.__current_highest_depth:
            if None in [current_moves, current_key_index, current_origin_list]:
                current_moves, current_key_index, current_origin_list = get_moves_key_origin(self.bitboard, current_colour)
            
            if len(current_origin_list) == 0:
                if not(self.bitboard.king_safe(False)) and current_colour == "WHITE":
                    return -math.inf
                elif not(self.bitboard.king_safe()) and current_colour == "BLACK":
                    return math.inf
                else:
                    return 0.0 
            """
            Current avaiable moves are iterated through and simulated by: applying the move, appending the evaluation of the new position
            into the move_evaluation dicitonary with move and evaluation as the value, key pair and reverting the move afterward
            """
                
            for applied_origin in current_origin_list:
                for applied_to in current_moves[applied_origin]:
                    self.__num_searched += 1
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
                        
                    self.bitboard.apply_move(applied_move)
                    w_evaluation, d_evaluation = self.total_advantage
                    sum_eval = float(w_evaluation - d_evaluation)
                    move_evaluation[applied_move] = sum_eval
                    move_list = []
                    for move_capture in self.bitboard.applied_moves:
                        if type(move_capture) == tuple and len(move_capture) == 3:
                            move_list.append(move_capture)
                        else:
                            move_list.append(move_capture[0])
                    insert_to_ordered_eval_move(sum_eval, move_list)
                    self.bitboard.revert_move()
                    
                    if not(within_alpha_beta(current_colour, sum_eval)):
                        return move_evaluation
                
        """
        Finally, while the current tree is the best possible tree, the algorithm recursively searchs through different branches appending the evaluation
        on the move evaluation dictionary until a base case is reached either the current time (amount of searched moves) exceeds that of the max time set
        by the user, the current max depth exceeds the max depth set by the user or the current time spent exceeds the max time set by the user
        """
        
        while current_depth < self.__current_highest_depth:
            sorted_moves = sort_move_evaluation_keys(move_evaluation)
            for search_move in sorted_moves:
                if self.bitboard.applied_moves in self.__ordered_eval_move:
                    self.__ordered_eval_move.remove(self.bitboard.applied_moves)
                
                move_evaluation = simulate_next_move(current_depth, current_colour, move_evaluation, search_move)
                
                within_maxes = self.max_num_searched > self.__num_searched and self.max_depth > self.__current_highest_depth and (time.time() - self.__start_time) < self.max_time
                if not(within_maxes):
                    break
                
                if current_depth + 2 >= self.__current_highest_depth:
                    update_alpha_beta(current_colour, move_evaluation, search_move)
            
            if current_depth == 0:
                self.__alpha = math.inf
                self.__beta = -math.inf
                self.__current_highest_depth += 1
                
            if not(within_maxes):
                break
                
        return move_evaluation

if __name__ == "__main__":
    while True:
        pass