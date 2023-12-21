import math, time, json, numpy
from bitboard import BitBoard
from icecream import ic
class Engine:
    def __init__(self, bitboard:BitBoard) -> None:
        """
        Weight masks and values are loaded here to work out the advanatge of any given position
        In addition, the "max_num_searched", "max_depth" and "max_time" public variables can be 
        used to terminate the mini-max search according to certain cretia, being the number of moves
        ahead of the current positon searched (depth) and amount of moves searched (time)
        
        Public Piece Square tables from Rofchade: http://www.talkchess.com/forum3/viewtopic.php?f=2&t=68311&start=19
        """
        
        with open("engine_weight.json", "r") as engine_weight:
            engine_data = engine_weight.read()
        engine_data = json.loads(engine_data)
        self.__PIECE_MATERIAL_WEIGHT = engine_data["PIECE_MATERIAL_WEIGHT"]
        self.__PIECE_POSITIONAL_WEIGHT = engine_data["PIECE_POSITIONAL_WEIGHT"]
        
        self.bitboard = bitboard
        self.display_progress = False
        self.max_num_searched = math.inf
        self.__num_searched = 0
        self.max_depth = math.inf
        self.max_time = math.inf
        self.__start_time = None
        self.__current_highest_depth =  0
        self.__alpha = math.inf #upper bound for black
        self.__beta = -math.inf #lower bound for white
        
    def __material_advantage(self, game_phase:float) -> (float, float):
        """
        Iterates throught the bitboard dictionary and adds the material weight for each 1 (individual piece) in the bit board for each colour
        """
        d_material = 0
        w_material = 0
        for key in self.bitboard.bitboard_dict.keys():
            for bit in str(format(self.bitboard.bitboard_dict[key], "064b"))[::-1]:
                if int(bit) == 1:
                    if key[0].isupper():
                        d_material += (self.__PIECE_MATERIAL_WEIGHT[key.upper()] * game_phase) + (self.__PIECE_MATERIAL_WEIGHT["E"+key.upper()] * (1 - game_phase))
                    else:
                        w_material += (self.__PIECE_MATERIAL_WEIGHT[key.upper()] * game_phase) + (self.__PIECE_MATERIAL_WEIGHT["E"+key.upper()] * (1 - game_phase))
        return w_material, d_material

    def __positional_advantage(self, game_phase:float) -> (float, float):
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
                        d_positional += (self.__PIECE_POSITIONAL_WEIGHT[key.upper()][::-1][board_index] * game_phase) + (self.__PIECE_POSITIONAL_WEIGHT[key.upper()][::-1][board_index] * (1 - game_phase))
                    else:
                        w_positional += (self.__PIECE_POSITIONAL_WEIGHT[key.upper()][board_index] * game_phase) + (self.__PIECE_POSITIONAL_WEIGHT[key.upper()][board_index] * (1 - game_phase))                        
        return w_positional, d_positional
    
    def __strategical_advantage(self, game_phase:float, colour:str) -> (float, float):
        """
        Intended to cover complex patterns like forks where 1 piece attacks 2 different higher value pieces meaning a certain material gain,
        or king safety or etc however
        Temporarily, adds the the available move squares for each colour and counts the number of tiles covered by their pieces
        """
        w_strategical = d_strategical = 0
        if colour == "WHITE":
            colour_index = 0
        return w_strategical, d_strategical
    
    def __total_advantage(self, colour) -> (float, float):
        """
        Totals the advantage for each colour from the previous functions creating an estimate for which colour is winning in a given position,
        and by how much that colour is winning by
        """
        game_phase = 1
        (w_strategical, d_strategical) = self.__strategical_advantage(game_phase, colour)
        (w_positional, d_positional) = self.__positional_advantage(game_phase)
        (w_material, d_material) = self.__material_advantage(game_phase)
        
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

        def within_alpha_beta(colour:str, evaluation:float) -> bool:
            if (colour == "BLACK" and evaluation >= self.__beta) or (colour == "WHITE" and evaluation <= self.__alpha):
                return True
            return False
        
        def update_alpha_beta(colour:str, move_evaluation:dict, search_move:tuple) -> None:
            if type(move_evaluation[search_move]) is dict:
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
            """
            Sorts the evaluation of moves in move evaluations to be "stand pat" being the middle evaluations move
            going from the middle outward, explained why in documentation
            """
            
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
            for eval in evaluation_list:
                if not(type(eval) is float):
                    return move_evaluation.keys()
                
            if type(evaluation_list[0]) is float:
                evaluation_list = merge_sort(evaluation_list)
                evaluation_list = remove_duplicates(evaluation_list)
                
                vector = []
                mid = len(evaluation_list) / 2
                for index in range(math.floor(mid)):
                    vector.append(math.floor(mid)-index)
                    vector.append(math.ceil(mid)+index)
                if mid % 1 == 0:
                    del vector[0]
                vector.append(0)
                
                evaluation_list = numpy.array(evaluation_list)
                vector = numpy.array(vector)
                
                ordered_move_list = []
                for evaluation in evaluation_list[vector]:
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
    
        if None in [current_moves, current_key_index, current_origin_list]:
                current_moves, current_key_index, current_origin_list = get_moves_key_origin(self.bitboard, current_colour)
                
        if current_depth == self.__current_highest_depth:
            if not(type(move_evaluation) is dict):
                move_evaluation = {}
                
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
                    
                    if self.display_progress:
                        result = ""
                        for limit, current, desc in [[self.max_time, time.time() - self.__start_time, "Time to finish"], [self.max_depth, self.__current_highest_depth, "Depth to finish"], [self.max_num_searched, self.__num_searched, "Num search to finish"]]:
                            if limit != math.inf:
                                result += desc + " " + str(current/limit) + " "
                                result += str(current) + "/" + str(limit) + " "
                            print(result)
                                
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
                    
                    w_evaluation, d_evaluation = self.__total_advantage(current_colour)
                    sum_eval = float(w_evaluation - d_evaluation)
                    move_evaluation[applied_move] = sum_eval
                    move_list = []
                    for move_capture in self.bitboard.applied_moves:
                        if type(move_capture) == tuple and len(move_capture) == 3:
                            move_list.append(move_capture)
                        else:
                            move_list.append(move_capture[0])
                            
                    self.bitboard.revert_move()
                    
                    if not(within_alpha_beta(current_colour, sum_eval)):
                        return move_evaluation
                
        """
        Finally, the recursion is defined by first checking: the current depth is not beyond what it has previously checked,
        sorting the moves to optimize alpha beta pruning, simulating every move in said order, then updating recursion parameters
        """
        
        within_maxes = self.max_num_searched > self.__num_searched and self.max_depth > self.__current_highest_depth and (time.time() - self.__start_time) < self.max_time
        while within_maxes and current_depth <= self.__current_highest_depth and type(move_evaluation) == dict:
            if current_depth == 0:
                self.__current_highest_depth += 1
            
            sorted_moves = sort_move_evaluation_keys(move_evaluation)
            for search_move in sorted_moves:
                
                move_evaluation = simulate_next_move(current_depth, current_colour, move_evaluation, search_move)
                
                within_maxes = self.max_num_searched > self.__num_searched and self.max_depth > self.__current_highest_depth and (time.time() - self.__start_time) < self.max_time
                if not(within_maxes):
                    break
                
                if current_depth + 1 == self.__current_highest_depth:
                    update_alpha_beta(current_colour, move_evaluation, search_move)
                    
            if current_depth != 0:
                break
            
        return move_evaluation
    
    def find_ordered_move_eval(self, move_evaluation):
        def insert_index(num:float, num_list:list, low:int=None, mid:int=None, high:int=None) -> int:
            if None in [low, high, mid]:
                low = 0
                high = len(num_list)-1
                if high < low:
                    return 0
                
            if high >= low:
                mid = (low + high) // 2
                if num == num_list[mid]:
                    return mid
                elif num > num_list[mid]:
                    return insert_index(num, num_list, mid+1, mid, high)
                else:
                    return insert_index(num, num_list, low, mid, mid-1)
            elif num > num_list[high] or high < 0:
                return low
            else:
                return high
        
        def find_best(move_evaluation) -> float:
            if len(move_evaluation) < 0:
                return 0
            if list(move_evaluation.keys())[0][0][0].isupper():
                is_white = False
                best = math.inf
            else:
                is_white = True
                best = -math.inf
            for move in move_evaluation.keys():
                if type(move_evaluation[move]) is float:
                    evaluation = move_evaluation[move]
                else:
                    evaluation = find_best(move_evaluation[move])
                if (is_white and best < evaluation) or (not(is_white) and best > evaluation):
                    best = evaluation
            return best
                
        ordered_move_eval = []
        for move in move_evaluation.keys():
            if type(move_evaluation[move]) is float:
                ordered_move_eval.insert(insert_index(move_evaluation[move], [move_eval[1] for move_eval in ordered_move_eval]), (move, move_evaluation[move]))
            else:
                evaluation = find_best(move_evaluation[move])
                ordered_move_eval.insert(insert_index(evaluation, [move_eval[1] for move_eval in ordered_move_eval]), (self.find_ordered_move_eval(move_evaluation[move]), evaluation, move))
        return ordered_move_eval


if __name__ == "__main__":
    board = ".....rk........p.pN..Qp..P.p....P..............P......PK....q..."
    bitBoard = BitBoard(board)
    bitBoard.can_castle = {
            "BLACK" : {"left": True, "right": True},
            "WHITE" : {"left": True, "right": True}
        }
    print(bitBoard.board_formatted)
    engine = Engine(bitBoard)
    engine.display_progress = True
    engine.max_depth = int(input("Enter a max depth: "))
    move_evaluation = engine.min_max_dict(current_colour="BLACK")
    print()