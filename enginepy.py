import math
from json import loads as json_loads
from numpy import array as np_array
from time import time
from bitboard import BitBoard
from enum import Enum

class Engine:
    def __init__(self, bitboard:BitBoard) -> None:
        def format_table(weights:list[int]):
            result = []
            for row in range(len(weights)//8):
                result.extend(weights[((row+1)*8)-1:(row*8)-1 if (row*8)-1 > 0 else None:-1])
            return result
        
        """
        Weight masks and values are loaded here to work out the advanatge of any given position
        In addition, the "max_num_searched", "max_depth" and "max_time" public variables can be 
        used to terminate the mini-max search according to certain cretia, being the number of moves
        ahead of the current positon searched (depth) and amount of moves searched (time)
        
        Public Piece Square tables from Rofchade: http://www.talkchess.com/forum3/viewtopic.php?f=2&t=68311&start=19
        """
        
        with open("engine_weight.json", "r") as engine_weight:
            engine_data = engine_weight.read()
        engine_data = json_loads(engine_data)
        
        self.__PIECE_MATERIAL_WEIGHT = engine_data["PIECE_MATERIAL_WEIGHT"]
        self.__PIECE_POSITIONAL_WEIGHT = engine_data["PIECE_POSITIONAL_WEIGHT"]
        self.__PIECE_POSITIONAL_WEIGHT = {key:format_table(value) for key, value in self.__PIECE_POSITIONAL_WEIGHT.items()}
        self.__STRATEGICAL_WEIGHT = engine_data["STRATEGICAL_WEIGHT"]
        self.__STRATEGICAL_WEIGHT = {key:(format_table(value) if key in ["MOBILITY", "EMOBILITY"] else value) for key, value in self.__STRATEGICAL_WEIGHT.items()}
        
        self.move_evaluation = {}
        self.bitboard = bitboard
        self.enum_piece_to_name = {
            BitBoard.piece.PAWN : "PAWN",
            BitBoard.piece.BISHOP : "BISHOP",
            BitBoard.piece.KNIGHT : "KNIGHT",
            BitBoard.piece.ROOK : "ROOK",
            BitBoard.piece.QUEEN : "QUEEN",
            BitBoard.piece.KING : "KING"
        }
        self.display_progress = False
        
        self.max_num_searched = math.inf
        self.max_depth = math.inf
        self.max_time = math.inf
        
        self.__num_searched = 0
        self.__start_time = None
        self.current_highest_depth =  0
        
        self.__alpha = math.inf #upper bound for black
        self.__beta = -math.inf #lower bound for white
        
    def __material_advantage(self, game_phase:float) -> tuple[float, float]:
        """
        Iterates throught the bitboard dictionary and adds the material weight for each 1 (individual piece) in the bit board for each colour
        """
        d_material = 0
        w_material = 0
        for key, bitboard in self.bitboard.bitboard_dict.items():
            key_name, key_colour = key
            for bit in str(format(bitboard, "064b"))[::-1]:
                if int(bit) == 1:
                    if key_colour == BitBoard.colour.BLACK:
                        d_material += (self.__PIECE_MATERIAL_WEIGHT[self.enum_piece_to_name[key_name]] * game_phase) + \
                            (self.__PIECE_MATERIAL_WEIGHT["E"+self.enum_piece_to_name[key_name]] * (1 - game_phase))
                    else:
                        w_material += (self.__PIECE_MATERIAL_WEIGHT[self.enum_piece_to_name[key_name]] * game_phase) + \
                            (self.__PIECE_MATERIAL_WEIGHT["E"+self.enum_piece_to_name[key_name]] * (1 - game_phase))
        return w_material, d_material

    def __positional_advantage(self, game_phase:float) -> tuple[float, float]:
        """
        Iterates throught the bitboard dictionary and adds the positional weight for each 1 (individual piece) in the bit board for each colour,
        according to the index location of the bit (piece location)
        """
        w_positional = 0
        d_positional = 0
        for key, bitboard in self.bitboard.bitboard_dict.items():
            key_name, key_colour = key
            for board_index, bit in enumerate(str(format(bitboard, "064b"))[::-1]):
                if int(bit) == 1:
                    if key_colour == BitBoard.colour.BLACK:
                        d_positional += (self.__PIECE_POSITIONAL_WEIGHT[self.enum_piece_to_name[key_name]][::-1][board_index] * game_phase) \
                            + (self.__PIECE_POSITIONAL_WEIGHT["E"+self.enum_piece_to_name[key_name]][::-1][board_index] * (1 - game_phase))
                    else:
                        w_positional += (self.__PIECE_POSITIONAL_WEIGHT[self.enum_piece_to_name[key_name]][board_index] * game_phase) \
                            + (self.__PIECE_POSITIONAL_WEIGHT["E"+self.enum_piece_to_name[key_name]][board_index] * (1 - game_phase))                        
        return w_positional, d_positional
    
    def __strategical_advantage(self, game_phase:float) -> tuple[float, float]:
        def king_safety_modifier(game_phase:float):
            """
            King Safety - gives advanatge if the king is not in danger
            """
            strategical = [0,0]
            for active_colour_index in range(2):
                active_key_to_king_key = {1:(BitBoard.piece.KING, BitBoard.colour.WHITE), \
                    0:(BitBoard.piece.KING, BitBoard.colour.BLACK)}
                king_key = active_key_to_king_key[active_colour_index]
                
                active_key_to_similar_key = {1:0, 0:1}
                king_bitboard = self.bitboard.bitboard_dict[king_key]
                
                similar = self.bitboard.combined_board[active_key_to_similar_key[active_colour_index]]
                king_mobility = self.bitboard.get_king_bitboard(king_bitboard, similar)
                for bit in str(format(king_mobility, "064b"))[::-1]:
                    if int(bit) == 1:
                        strategical[active_colour_index] += (self.__STRATEGICAL_WEIGHT["KING_MOBILITY_NEGATIVE"] * game_phase)
            return strategical
        
        def mobility_modifier(game_phase:float):
            """
            Mobility and Center Control - where advantage is given for contolling squares
            """
            strategical = [0,0]
            move = self.bitboard.move_board
            for active_colour_index in range(2):
                if active_colour_index:
                    mobility_board, e_mobility_board = self.__STRATEGICAL_WEIGHT["MOBILITY"], self.__STRATEGICAL_WEIGHT["EMOBILITY"]
                else:
                    mobility_board, e_mobility_board = self.__STRATEGICAL_WEIGHT["MOBILITY"][::-1], self.__STRATEGICAL_WEIGHT["EMOBILITY"][::-1]

                for index, bit in enumerate(str(format(move[active_colour_index], "064b"))[::-1]):
                    if int(bit) == 1:
                        strategical[active_colour_index] += (mobility_board[index] * game_phase) + (e_mobility_board[index] * (1 - game_phase))
                        
            return strategical
        
        def pawn_structure_modifier():
            """
            Pawn Structure - where advantage is given if pawns are connected or not connected
            """
            strategical = [0,0]
            for active_colour_index in range(2):
                active_key_to_pawn_key = {1:(BitBoard.piece.PAWN, BitBoard.colour.WHITE), \
                    0:(BitBoard.piece.PAWN, BitBoard.colour.BLACK)}
                
                pawn_key = active_key_to_pawn_key[active_colour_index]
                pawn_bitboard = self.bitboard.bitboard_dict[pawn_key]
                mobility_pawn_bitboard = self.bitboard.get_pawn_mobility(pawn_bitboard)
                for bit in str(format(mobility_pawn_bitboard & pawn_bitboard, "064b"))[::-1]:
                    if int(bit) == 1:
                        strategical[active_colour_index] += self.__STRATEGICAL_WEIGHT["CONNECTED_PAWNS"]
            return strategical
        
        def static_exchange_modifier():
            """
            Static Exchange Evalution - where advantage is given if a piece of lesser value can capture a piece of higher value and calculates
            chains of captures and their advantage for each player
            """
            strategical = [0,0]
            move_dict, key_to_index = self.bitboard.legal_move_dict
            capture_location_to_key = {}
            index_to_key = {}
            
            w_board, d_board = self.bitboard.combined_board
            w_move_board, d_move_board = self.bitboard.move_board
            capture_board = str(format(d_board & w_move_board | w_board & d_move_board, "064b"))[::-1]
            
            for from_ind, to_inds in move_dict.items():
                key = [piece for piece, from_index in key_to_index.items() if from_ind in from_index][0]
                index_to_key[from_ind] = key
                for to_ind in to_inds:
                    if type(to_ind) is tuple: to_ind, _ = to_ind
                    if capture_board[to_ind] == str(0): continue
                    if to_ind in capture_location_to_key.keys():
                        capture_location_to_key[to_ind].append(key)
                    else:
                        capture_location_to_key[to_ind] = [key]

            for c_location, keys in capture_location_to_key.items():
                if c_location in index_to_key.keys():
                    attacking_pieces = [index_to_key[c_location]]+keys
                    d_values = [(self.__PIECE_MATERIAL_WEIGHT[self.enum_piece_to_name[piece_name]] * game_phase) + \
                                (self.__PIECE_MATERIAL_WEIGHT["E"+self.enum_piece_to_name[piece_name]] * (1 - game_phase)) for piece_name, piece_colour in attacking_pieces \
                                    if piece_colour == BitBoard.colour.BLACK]
                    w_values = [(self.__PIECE_MATERIAL_WEIGHT[self.enum_piece_to_name[piece_name]] * game_phase) + \
                                (self.__PIECE_MATERIAL_WEIGHT["E"+self.enum_piece_to_name[piece_name]] * (1 - game_phase)) for piece_name, piece_colour in attacking_pieces \
                                    if piece_colour == BitBoard.colour.WHITE]
                    c_colour = BitBoard.colour.WHITE
                    while d_values and w_values:
                        if c_colour == BitBoard.colour.WHITE:
                            strategical[1] += w_values.pop(w_values.index(min(w_values)))
                            c_colour = BitBoard.colour.BLACK
                        else: 
                            strategical[0] += d_values.pop(d_values.index(min(d_values)))
                            c_colour = BitBoard.colour.WHITE
                        
            return strategical
        
        strategical = []
        strategical.append(king_safety_modifier(game_phase))
        strategical.append(mobility_modifier(game_phase))
        strategical.append(pawn_structure_modifier())
        strategical.append(static_exchange_modifier())
        return [advantage[0] for advantage in strategical], [advantage[1] for advantage in strategical]
    
    @property
    def __total_advantage(self) -> tuple[float, float]:
        """
        Totals the advantage for each colour from the previous functions creating an estimate for which colour is winning in a given position,
        and by how much that colour is winning by
        """
        w_board, d_board = self.bitboard.combined_board
        piece_bitboard = (w_board|d_board) ^ \
            (self.bitboard.bitboard_dict[(BitBoard.piece.PAWN, BitBoard.colour.WHITE)] | \
                self.bitboard.bitboard_dict[(BitBoard.piece.PAWN, BitBoard.colour.BLACK)])
        num_pieces = 0
        for bit in str(format(piece_bitboard, "064b"))[::-1]:
            if int(bit) == 1:
                num_pieces += 1
        game_phase = num_pieces/16
        (w_strategical, d_strategical) = self.__strategical_advantage(game_phase)
        (w_positional, d_positional) = self.__positional_advantage(game_phase)
        (w_material, d_material) = self.__material_advantage(game_phase)
        
        w_advantage = w_positional + w_material + sum(w_strategical)
        d_advantage = d_positional + d_material + sum(d_strategical)
        return w_advantage, d_advantage

    def min_max_dict(self,
                      current_depth:int=0,
                      current_colour=None, current_moves=None, current_key_index=None, current_origin_list=None,
                      move_evaluation:dict={}) -> dict:
        
        def simulate_next_move(current_depth, current_colour, move_evaluation, search_move) -> dict:
            """
            Extends the move tree by finding the current best move on the current position,
            then simulating that best move, and recuring the mini max algorithm on the new position
            
            After the branch that is being searched becomes worse than the current best tree,
            move evaluation is updated, current best eval is updated, the simulated move is reverted
            and move evaluation is returned
            """
            self.bitboard.apply_move(search_move)
            new_colour = BitBoard.colour.BLACK if current_colour == BitBoard.colour.WHITE else BitBoard.colour.WHITE
            move_evaluation[search_move] = self.min_max_dict(
                        current_depth + 1,
                        new_colour, None, None, None,
                        move_evaluation[search_move])
            self.bitboard.revert_move()
        
        def get_moves_key_origin(bitboard:BitBoard, colour:Enum) -> tuple[dict, dict, list]:
            """
            Extracts the avaiable moves, key index and origin list from the bitboard object passed into the function
            """
            moves, key  = bitboard.split_move_dict[colour]
            origin_list = list(moves.keys())
            return moves, key, origin_list
        
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
                
                evaluation_list = np_array(evaluation_list)
                vector = np_array(vector)
                
                ordered_move_list = []
                for evaluation in evaluation_list[vector]:
                    for move in [key for key, value in move_evaluation.items() if value == evaluation]:
                        ordered_move_list.append(move)
                        
                return ordered_move_list
            
            return move_evaluation.keys()
        
        def display_progress() -> None:
            result = ""
            for limit, current, desc in [[self.max_time, round(time() - self.__start_time, 3), "Time to finish"], \
                [self.max_depth, self.current_highest_depth, "Depth to finish"], \
                [self.max_num_searched, self.__num_searched, "Num search to finish"]]:
                if limit != math.inf:
                    result += desc + " " + str(round(current/limit, 3)) + " "
                    result += str(current) + "/" + str(limit) + "\n"
            print(result)
            
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
            self.__start_time = time()
            self.move_evaluation = move_evaluation
            
        if current_colour == None:
            current_colour = BitBoard.colour.WHITE
            
        if None in [current_moves, current_key_index, current_origin_list]:
                current_moves, current_key_index, current_origin_list = get_moves_key_origin(self.bitboard, current_colour)
                
        if current_depth == self.current_highest_depth:
            if not(type(move_evaluation) is dict):
                move_evaluation = {}
                
            if len(current_origin_list) == 0:
                if not(self.bitboard.king_safe(current_colour)) and current_colour == BitBoard.colour.WHITE:
                    return -math.inf
                elif not(self.bitboard.king_safe(current_colour)) and current_colour == BitBoard.colour.BLACK:
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
                    
                    if self.display_progress: display_progress()

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
                        applied_move = (applied_piece_key, applied_origin, applied_to)
                    self.bitboard.apply_move(applied_move)
                    
                    w_evaluation, d_evaluation = self.__total_advantage
                    sum_eval = float(w_evaluation - d_evaluation)
                    move_evaluation[applied_move] = sum_eval
                            
                    self.bitboard.revert_move()
                    
                    within_alpha_beta = lambda colour, evaluation : (colour == BitBoard.colour.BLACK and evaluation >= self.__beta) or \
                        (colour == BitBoard.colour.WHITE and evaluation <= self.__alpha)
                        
                    if not(within_alpha_beta(current_colour, sum_eval)):
                        return move_evaluation
                
        """
        Finally, the recursion is defined by first checking: the current depth is not beyond what it has previously checked,
        sorting the moves to optimize alpha beta pruning, simulating every move in said order, then updating recursion parameters
        """
        
        within_maxes = lambda : self.max_num_searched > self.__num_searched and \
            self.max_depth > self.current_highest_depth and \
            (time() - self.__start_time) < self.max_time
            
        while within_maxes() and current_depth <= self.current_highest_depth and type(move_evaluation) == dict:
            if current_depth == 0:
                self.current_highest_depth += 1
            
            sorted_moves = sort_move_evaluation_keys(move_evaluation)
            for search_move in sorted_moves:
                
                simulate_next_move(current_depth, current_colour, move_evaluation, search_move)
                
                if not(within_maxes()):
                    break
                
                if current_depth + 1 == self.current_highest_depth:
                    update_alpha_beta(current_colour, move_evaluation, search_move)
                    
            if current_depth != 0:
                break
            
        return move_evaluation
    
    @staticmethod
    def find_ordered_move_eval(move_evaluation:dict) -> list:
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
            sample_piece, sample_colour = list(move_evaluation.keys())[0][0]
            best = math.inf if sample_colour == BitBoard.colour.BLACK else -math.inf
            for move in move_evaluation.keys():
                if type(move_evaluation[move]) is float:
                    evaluation = move_evaluation[move]
                else:
                    evaluation = find_best(move_evaluation[move])
                if (sample_colour == BitBoard.colour.WHITE and best < evaluation) or (sample_colour == BitBoard.colour.BLACK and best > evaluation):
                    best = evaluation
            return best
                
        ordered_move_eval = []
        for move in move_evaluation.keys():
            if type(move_evaluation[move]) is float:
                ordered_move_eval.insert(insert_index(move_evaluation[move], [move_eval[1] for move_eval in ordered_move_eval]), (move, move_evaluation[move]))
            else:
                evaluation = find_best(move_evaluation[move])
                ordered_move_eval.insert(insert_index(evaluation, [move_eval[1] for move_eval in ordered_move_eval]), (move, evaluation)) #optionally add Engine.find_ordered_move_eval(move_evaluation[move]
        return ordered_move_eval 

    @staticmethod
    def format_every_pair(dictionary, function_key) -> dict:
        def format_dict(dictionary, function_key) -> dict:
            for key, val in dictionary.items():
                if type(val) is dict:
                    dictionary[key] = format_dict(val, function_key)
                    dictionary[key] = function_key(dictionary[key])
            return dictionary
        return function_key(format_dict(dictionary, function_key))

if __name__ == "__main__":
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    engine = Engine(BitBoard(board))
    print(engine.bitboard.board_formatted)
    engine.display_progress = True
    engine.max_depth = int(input("Enter a max depth: "))
    engine.max_num_searched = int(input("Enter a max num searched: "))
    engine.max_time = int(input("Enter a max time: "))
    move_evaluation = engine.min_max_dict()
    
    format_dict_for_json = lambda dictionary: [{"key":((str(k[0][0]), str(k[0][1])), k[1], k[2]), "value" : v} for k, v in dictionary.items()]
    formatted = Engine.format_every_pair(move_evaluation, format_dict_for_json)
    
    """with open("test_evaluation.json", "w") as test_file:
        test_file.write(json.dumps(formatted))"""
        
"""
Note: Attach alternative Best frist search from github branch after developemtn for 2 types of engine choice, probably one very dumb one less dumb
"""