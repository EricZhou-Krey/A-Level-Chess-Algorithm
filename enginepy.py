import bitboard, math, time
from icecream import ic
class Engine:
    def __init__(self, bitboard:bitboard.BitBoard, PAWN_MATERIAL_WEIGHT:float=10, BISHOP_MATERIAL_WEIGHT:float=30, KNIGHT_MATERIAL_WEIGHT:float=30, ROOK_WIEGHT:float=50, QUEEN_MATERIAL_WEIGHT:float=100,
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
        In addition, the "max_num_searched", "max_depth" and "max_time" public variables can be used to terminate the mini-max search according to certain
        cretia, being the number of moves ahead of the current positon searched (depth) and amount of moves searched (time)
        """
        self.__PIECE_MATERIAL_WEIGHT = {
            "PAWN" : PAWN_MATERIAL_WEIGHT,
            "BISHOP" : BISHOP_MATERIAL_WEIGHT,
            "KNIGHT" : KNIGHT_MATERIAL_WEIGHT,
            "ROOK" : ROOK_WIEGHT,
            "QUEEN" : QUEEN_MATERIAL_WEIGHT
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
        self.bitboard = bitboard
        self.max_num_searched = math.inf
        self.__num_searched = 0
        self.max_depth = math.inf
        self.max_time = math.inf
        self.__start_time = None
        self.highest_depth = -1
        self.__current_best_eval = None
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
                    match key:
                        case "pawn":
                            w_material += self.__PIECE_MATERIAL_WEIGHT["PAWN"]
                        case "bishop":
                            w_material += self.__PIECE_MATERIAL_WEIGHT["BISHOP"]
                        case "knight":
                            w_material += self.__PIECE_MATERIAL_WEIGHT["KNIGHT"]
                        case "rook":
                            w_material += self.__PIECE_MATERIAL_WEIGHT["ROOK"]
                        case "queen":
                            w_material += self.__PIECE_MATERIAL_WEIGHT["QUEEN"]
                        case "Pawn":
                            d_material += self.__PIECE_MATERIAL_WEIGHT["PAWN"]
                        case "Bishop":
                            d_material += self.__PIECE_MATERIAL_WEIGHT["BISHOP"]
                        case "Knight":
                            d_material += self.__PIECE_MATERIAL_WEIGHT["KNIGHT"]
                        case "Rook":
                            d_material += self.__PIECE_MATERIAL_WEIGHT["ROOK"]
                        case "Queen":
                            d_material += self.__PIECE_MATERIAL_WEIGHT["QUEEN"]
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
                    match key:
                        case "pawn":
                            w_positional += self.__POSITION_WEIGHT["WPAWN"][board_index]
                            break
                        case "bishop":
                            w_positional += self.__POSITION_WEIGHT["BISHOP"][board_index]
                            break
                        case "knight":
                            w_positional += self.__POSITION_WEIGHT["KNIGHT"][board_index]
                            break
                        case "rook":
                            w_positional += self.__POSITION_WEIGHT["ROOK"][board_index]
                            break
                        case "queen":
                            w_positional += self.__POSITION_WEIGHT["QUEEN"][board_index]
                            break
                        case "king":
                            w_positional += self.__POSITION_WEIGHT["KING"][board_index]
                            break
                        case "Pawn":
                            d_positional += self.__POSITION_WEIGHT["DPAWN"][board_index]
                            break
                        case "Bishop":
                            d_positional += self.__POSITION_WEIGHT["BISHOP"][board_index]
                            break
                        case "Knight":
                            d_positional += self.__POSITION_WEIGHT["KNIGHT"][board_index]
                            break
                        case "Rook":
                            d_positional += self.__POSITION_WEIGHT["ROOK"][board_index]
                            break
                        case "Queen":
                            d_positional += self.__POSITION_WEIGHT["QUEEN"][board_index]
                            break
                        case "King":
                            d_positional += self.__POSITION_WEIGHT["KING"][board_index]
                            break
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
                      move_evaluation={}):
        def simulate_next_move(current_depth, current_colour, move_evaluation, bitboard):
            """
            Extends the move tree by finding the current best move on the current position,
            then simulating that best move, and recuring the mini max algorithm on the new position
            
            After the branch that is being searched becomes worse than the current best tree,
            move evaluation is updated, current best eval is updated, the simulated move is reverted
            and move evaluation is returned
            """
            
            search_move = current_min_max(move_evaluation, current_colour)[1]
            bitboard.apply_move(search_move)
            if current_colour == "WHITE":
                new_colour = "BLACK"
            else:
                new_colour = "WHITE"
            move_evaluation[search_move] = {}
            move_evaluation[search_move] = self.min_max_dict(
                        current_depth + 1,
                        new_colour, None, None, None,
                        move_evaluation[search_move])
            self.__current_best_eval = current_min_max(move_evaluation, current_colour)[0]
            bitboard.revert_move()
            return move_evaluation
        
        def get_moves_key_origin(bitboard:bitboard.BitBoard, colour:str) -> (dict, dict, list):
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
        
        def current_min_max(move_evaluation:dict, current_colour:str) -> (float, tuple):
            """
            Temporary, slow way to find the best move in a move dicitionary, can be improved by dynamically storing and insertion sorting
            an array, dictionary or object containing the best moves in a ordered manner that is updated during the function
            """
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
            if current_colour == "WHITE":
                self.__current_best_eval = -math.inf
            else:
                self.__current_best_eval = math.inf
        
        if len(current_origin_list) == {}:
            if not(self.bitboard.king_safe(False)) and current_colour == "WHITE":
                return -math.inf
            elif not(self.bitboard.king_safe()) and current_colour == "BLACK":
                return math.inf
            else:
                return 0.0
        
        """
        The highest depth is updated according to the current_depth
        """
        
        if self.highest_depth < current_depth:
            self.highest_depth = current_depth
            
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
                
                self.bitboard.revert_move()
        
        """
        Finally, while the current tree is the best possible tree, the algorithm recursively searchs through different branches appending the evaluation
        on the move evaluation dictionary until a base case is reached either the current time (amount of searched moves) exceeds that of the max time set
        by the user, the current max depth exceeds the max depth set by the user or the current time spent exceeds the max time set by the user
        """
        best = True
        while best and self.max_num_searched > self.__num_searched and self.max_depth > self.highest_depth and (time.time() - self.__start_time) < self.max_time:
            best, self.__current_best_eval = is_current_best(move_evaluation, current_colour, current_depth, self.__current_best_eval)
            move_evaluation = simulate_next_move(current_depth, current_colour, move_evaluation, self.bitboard)
        return move_evaluation
    
    def best_moves(self, move_evaluation:dict, current_colour="WHITE", max_length=999, arrays=3, min_length=2):
        
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
    engine.max_num_searched = int(input("Enter max searched moves: "))
    move_evaluation = engine.min_max_dict(current_colour="BLACK")
    ic(move_evaluation, engine.best_moves(move_evaluation, "BLACK", arrays=1, min_length=engine.highest_depth))
    
    """
    Should dynamically update a data form that stores the best moves and their evaluations
    """