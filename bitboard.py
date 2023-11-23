import math, time
from icecream import ic
    
class IPiece():
    def __init__(self) -> None:
        def init_edge() -> None:
            file_keys = ["A","B","C","D","E","F","G","H"]
            edge_keys = ["1","2","3","4","5","6","7","8"]
            file_values = [[(index_y*len(file_keys))+index_x for index_y in range(len(file_keys))] for index_x in range(len(edge_keys))]
            edge_values = [[index_x+(index_y*len(file_keys)) for index_x in range(len(edge_keys))] for index_y in range(len(file_keys))]
            
            file_values.extend(edge_values)
            file_keys.extend(edge_keys)
            file_edge_values = [self.index_board_to_int64(index_array) for index_array in file_values]
            
            self.file_edge_bitboard = dict(zip(file_keys, file_edge_values))
        init_edge()

    def index_board_to_int64(self, index_array:list[int]) -> int: #returns bitboard as integer from list of indexes
            bitBoard = int()
            for index in index_array:
                bitBoard += 2**index
            return bitBoard

    def get_knight_bitboard(self, board:int, similar:int=0) -> int:
        fileA = self.file_edge_bitboard["A"]
        fileB = self.file_edge_bitboard["B"]
        fileG = self.file_edge_bitboard["G"]
        fileH = self.file_edge_bitboard["H"]
        rankOne = self.file_edge_bitboard["1"]
        rankTwo = self.file_edge_bitboard["2"]
        rankSeven = self.file_edge_bitboard["7"]
        rankEight = self.file_edge_bitboard["8"]
        move = ((board & ~(fileH|rankSeven|rankEight)) << 17) & ~(similar) # NNE
        move |= ((board & ~(fileA|rankSeven|rankEight)) << 15) & ~(similar) # NNW
        move |= ((board & ~(fileH|fileG|rankEight)) << 10) & ~(similar) # NEE
        move |= ((board & ~(fileA|fileB|rankEight)) << 6) & ~(similar) # NWW
        move |= ((board & ~(fileA|rankTwo|rankOne)) >> 17) & ~(similar) # SSW
        move |= ((board & ~(fileH|rankTwo|rankOne)) >> 15) & ~(similar) # SSE
        move |= ((board & ~(fileA|fileB|rankOne)) >> 10) & ~(similar) # SWW
        move |= ((board & ~(fileH|fileG|rankOne)) >> 6) & ~(similar) # SEE
        return move

    def get_king_bitboard(self, board:int, similar:int=0, opposing:int=0) -> int:
        fileA = self.file_edge_bitboard["A"]
        fileB = self.file_edge_bitboard["B"]
        fileG = self.file_edge_bitboard["G"]
        fileH = self.file_edge_bitboard["H"]
        rankOne = self.file_edge_bitboard["1"]
        rankEight = self.file_edge_bitboard["8"]
        move = ((board & ~(fileH)) << 1) & ~(similar) #E
        move |= ((board & ~(fileA|rankEight)) << 7) & ~(similar) #NW
        move |= ((board & ~(rankEight)) << 8) & ~(similar) #N
        move |= ((board & ~(fileH|rankEight)) << 9) & ~(similar) #NE
        move |= ((board & ~(fileA)) >> 1) & ~(similar) #W
        move |= ((board & ~(fileH|rankOne)) >> 7) & ~(similar) #SE
        move |= ((board & ~(rankOne)) >> 8) & ~(similar) #S
        move |= ((board & ~(fileA|rankOne)) >> 9) & ~(similar) #SW
        move |= ((board & ~(fileA|fileB)) >> 2) & ~(similar|opposing|similar >> 1| opposing >> 1) #WW
        move |= ((board & ~(fileG|fileH)) << 2) & ~(similar|opposing|similar << 1| opposing << 1) # EE
        return move

    def get_pawn_bitboard(self, board:int, isWhite:bool=True, opposing:int=0, similar:int=0) -> int:
        fileA = self.file_edge_bitboard["A"]
        fileH = self.file_edge_bitboard["H"]
        rankOne = self.file_edge_bitboard["1"]
        rankTwo = self.file_edge_bitboard["2"]
        rankSeven = self.file_edge_bitboard["7"]
        rankEight = self.file_edge_bitboard["8"]
        if isWhite:
            move = (board << 8) & ~(similar) #N
            move |= ((board & ~(rankSeven) & rankTwo) << 16) & ~(opposing) & ~(similar) & ~((similar & ~(rankOne)) << 8) #NN
            move |= ((board & ~(fileA)) << 7) & (opposing|opposing << 8) #NW
            move |= ((board & ~(fileH)) << 9) & (opposing|opposing << 8) #NE
        else:
            move = (board >> 8) & ~(similar) #S
            move |= ((board & ~(rankTwo) & rankSeven) >> 16) & ~(opposing) & ~(similar) & ~((similar & ~(rankEight)) >> 8) #SS
            move |= ((board & ~(fileH)) >> 7) & (opposing|opposing >> 8) #SE
            move |= ((board & ~(fileA)) >> 9) & (opposing|opposing >> 8) #SW
        return move

    def get_bishop_bitboard(self, board:int, opposing:int=0, similar:int=0) -> int:
        def singular_bishop(board:int, opposing:int=0, similar:int=0) -> int:
            fileWEdge = self.file_edge_bitboard["A"]
            fileEEdge = self.file_edge_bitboard["H"]
            rankSEdge = self.file_edge_bitboard["1"]
            rankNEdge = self.file_edge_bitboard["8"]
            index = 1
            ne_done = False
            nw_done = False
            se_done = False
            sw_done = False
            move = 0
            for index in range(1,9):
                if ((board << 9*(index-1)) & opposing) > 0 or ((board << 9*index) & similar) > 0:
                    ne_done = True
                if ((board << 7*(index-1)) & opposing) > 0 or ((board << 7*index) & similar) > 0:
                    nw_done = True
                if ((board >> 9*(index-1)) & opposing) > 0 or ((board >> 9*index) & similar) > 0:
                    sw_done = True
                if ((board >> 7*(index-1)) & opposing) > 0 or ((board >> 7*index) & similar) > 0:
                    se_done = True
                if not(ne_done):
                    move |= (board & ~(rankNEdge|fileEEdge)) << 9*index #NE
                if not(nw_done):
                    move |= (board & ~(rankNEdge|fileWEdge)) << 7*index #NW
                if not(sw_done):
                    move |= (board & ~(fileWEdge|rankSEdge)) >> 9*index #SW
                if not(se_done):
                    move |= (board & ~(fileEEdge|rankSEdge)) >> 7*index #SE
                fileWEdge |= fileWEdge|fileWEdge << 1
                rankSEdge |= rankSEdge|rankSEdge << 8
                fileEEdge |= fileEEdge|fileEEdge >> 1
                rankNEdge |= rankNEdge|rankNEdge >> 8
            return move
        move = 0
        for index, bit in enumerate(str(format(board, "064b"))[::-1]):
            if int(bit) == 1:
                move |= singular_bishop(2**index, opposing, similar)
        return move
    
    def get_rook_bitboard(self, board:int, opposing:int=0, similar:int=0) -> int:
        def singular_rook(board:int, opposing:int=0, similar:int=0) -> int:
            fileWEdge = self.file_edge_bitboard["A"]
            fileEEdge = self.file_edge_bitboard["H"]
            rankSEdge = self.file_edge_bitboard["1"]
            rankNEdge = self.file_edge_bitboard["8"]
            n_done = False
            s_done = False
            w_done = False
            e_done = False
            move = 0
            for index in range(1,9):
                if ((board << 8*(index-1)) & opposing) > 0 or ((board << 8*index) & similar) > 0:
                    n_done = True
                if ((board >> 8*(index-1)) & opposing) > 0 or ((board >> 8*index) & similar) > 0:
                    s_done = True
                if ((board << (index-1)) & opposing) > 0 or ((board << index) & similar) > 0:
                    e_done = True
                if ((board >> (index-1)) & opposing) > 0 or ((board >> index) & similar) > 0:
                    w_done = True
                if not(n_done):
                    move |= (board & ~(rankNEdge)) << 8*index #N 
                if not(s_done):
                    move |= (board & ~(rankSEdge)) >> 8*index #S
                if not(e_done):
                    move |= (board & ~(fileEEdge)) << index #E
                if not(w_done):
                    move |= (board & ~(fileWEdge)) >> index #W
                fileWEdge |= fileWEdge|fileWEdge << 1
                rankSEdge |= rankSEdge|rankSEdge << 8
                fileEEdge |= fileEEdge|fileEEdge >> 1
                rankNEdge |= rankNEdge|rankNEdge >> 8
            return move
        move = 0
        for index, bit in enumerate(str(format(board, "064b"))[::-1]):
            if int(bit) == 1:
                move |= singular_rook(2**index, opposing, similar)
        return move

    def get_queen_bitboard(self, board:int, opposing:int=0, similar:int=0) -> int:
        move = self.get_bishop_bitboard(board, opposing, similar)
        move |= self.get_rook_bitboard(board, opposing, similar)
        return move

class BitBoard(IPiece):
    def __init__(self, notationBoard:str) -> None:
        def init_bitboard(index_board:{str:list[int]}) -> None:
            self.bitboard_dict = {}
            for key in index_board.keys():
                self.bitboard_dict[key] = self.index_board_to_int64(index_board[key])
                
        def init_index_board(notationBoard:str) -> {str:list[int]}:
            pieces = ["rook", "knight", "bishop", "queen", "king", "pawn", "Rook", "Pawn", "Bishop", "Knight", "Queen", "King"]
            piece_index_board = dict(zip(pieces, [[] for key in range(len(pieces))]))
            for index, notation in enumerate(notationBoard):
                match notation:
                    case "r":
                        piece_index_board["rook"].append(index)
                    case "n":
                        piece_index_board["knight"].append(index)
                    case "b":
                        piece_index_board["bishop"].append(index)
                    case "q":
                        piece_index_board["queen"].append(index)
                    case "p":
                        piece_index_board["pawn"].append(index)
                    case "k":
                        piece_index_board["king"].append(index)
                    case "R":
                        piece_index_board["Rook"].append(index)
                    case "N":
                        piece_index_board["Knight"].append(index)
                    case "B":
                        piece_index_board["Bishop"].append(index)
                    case "P":
                        piece_index_board["Pawn"].append(index)
                    case "K":
                        piece_index_board["King"].append(index)
                    case "Q":
                        piece_index_board["Queen"].append(index)
            return piece_index_board
        
        super().__init__()
        piece_index_board = init_index_board(notationBoard)
        init_bitboard(piece_index_board) #lowercase = white, Uppercase = Black
        self.castling = {
            "BLACK" : {"left": True, "right": True},
            "WHITE" : {"left": True, "right": True}
        }
        self.applied_moves = []

    def get_move(self, piece:str, opposing:int=0, similar:int=0) -> int:
        match piece.lower():
            case "pawn":
                return self.get_pawn_bitboard(self.bitboard_dict[piece], not(piece[0].isupper()), opposing, similar)
            case "king":
                return self.get_king_bitboard(self.bitboard_dict[piece], similar, opposing)
            case "knight":
                return self.get_knight_bitboard(self.bitboard_dict[piece], similar)
            case "bishop":
                return self.get_bishop_bitboard(self.bitboard_dict[piece], opposing, similar)
            case "rook":
                return self.get_rook_bitboard(self.bitboard_dict[piece], opposing, similar)
            case "queen":
                return self.get_queen_bitboard(self.bitboard_dict[piece], opposing, similar)
            case _:
                return 0

    def edit_board(self, move:tuple) -> None:
        if len(move) == 3:
            piece, origin_index, to_index = move
            promote_key = ""
        else:
            piece, origin_index, to_index, promote_key = move
            
        origin_bit = 2**origin_index
        to_bit = 2**to_index
        
        if promote_key == "":
            origin_to_bit = origin_bit | to_bit
        else:
            origin_to_bit = origin_bit
        
        pw_board, pd_board = self.combined_board
        combined_board = pw_board | pd_board
        if combined_board ^ to_bit < combined_board:
            for key in self.bitboard_dict.keys():
                if self.bitboard_dict[key] & to_bit > 0:
                    self.bitboard_dict[key] ^= to_bit
                    break
        
        if promote_key != "":
            self.bitboard_dict[promote_key] |= to_bit
        
        self.bitboard_dict[piece] ^= origin_to_bit

    def apply_move(self, move:tuple) -> None:
        if len(move) == 3:
            piece, origin_index, to_index = move
            promote_key = ""
        else:
            piece, origin_index, to_index, promote_key = move
            
        origin_bit = 2**origin_index
        to_bit = 2**to_index
        
        if promote_key == "":
            origin_to_bit = origin_bit | to_bit
        else:
            origin_to_bit = origin_bit
            
        pw_board, pd_board = self.combined_board
        combined_board = pw_board | pd_board
        captured = False
        if combined_board ^ to_bit < combined_board:
            for key in self.bitboard_dict.keys():
                if self.bitboard_dict[key] & to_bit > 0:
                    self.bitboard_dict[key] ^= to_bit
                    captured = True
                    break
                
        if promote_key != "":
            self.bitboard_dict[promote_key] |= to_bit
        self.bitboard_dict[piece] ^= origin_to_bit
        
        castle_capture = castle_rook = False
        if piece.lower() == "rook" and origin_index in [0,7,56,63]:
            castle_rook = True
            match origin_index:
                case 0:
                    castle_colour = "WHITE"
                    castle_direction = "left"
                case 7:
                    castle_colour = "WHITE"
                    castle_direction = "right"
                case 56:
                    castle_colour = "BLACK"
                    castle_direction = "left"
                case 63:
                    castle_colour = "BLACK"
                    castle_direction = "right"
        elif to_index in [0,7,56,63]:
            castle_capture = True
            match to_index:
                case 0:
                    castle_colour = "WHITE"
                    castle_direction = "left"
                case 7:
                    castle_colour = "WHITE"
                    castle_direction = "right"
                case 56:
                    castle_colour = "BLACK"
                    castle_direction = "left"
                case 63:
                    castle_colour = "BLACK"
                    castle_direction = "right"
        if castle_rook or castle_capture:
            self.castling[castle_colour][castle_direction] = (False, self.castling[castle_colour][castle_direction])
                    
        if piece.lower() == "king" and abs(origin_index - to_index) == 2:
            if piece[0].isupper():
                castle_piece = "Rook"
            else:
                castle_piece = "rook"
            if origin_index - to_index > 0: #to left
                castle_origin = origin_index - 4
                castle_to = origin_index - 1
            else: #to right
                castle_origin = origin_index + 3
                castle_to = origin_index + 1
            if castle_origin >= 0 and castle_to >= 0:
                self.edit_board((castle_piece, castle_origin, castle_to))
                if piece[0].isupper():
                    self.castling["BLACK"]["right"] = (False, self.castling["BLACK"]["right"])
                    self.castling["BLACK"]["left"] = (False, self.castling["BLACK"]["left"])
                else:
                    self.castling["WHITE"]["right"] = (False, self.castling["WHITE"]["right"])
                    self.castling["WHITE"]["left"] = (False, self.castling["WHITE"]["left"])
                
        if captured == True:
            self.applied_moves.append((move, (key, to_bit)))
        else:
            self.applied_moves.append(move)

    def revert_move(self) -> None:
        move = self.applied_moves.pop()
        captured = False
        if len(move) == 2:
            captured = True
            move, (capture_key, capture_bit) = move
            
        if len(move) == 3:
            piece, origin_index, to_index = move
            revert_move = (piece, to_index, origin_index)
        else:
            piece, origin_index, to_index, promote_key = move
            if piece[0].isupper():
                revert_move = (piece, to_index, origin_index, "Pawn")
            else:
                revert_move = (piece, to_index, origin_index, "pawn")
        
        self.edit_board(revert_move)
        
        if captured:
            self.bitboard_dict[capture_key] |= capture_bit
        castle_capture = castle_rook = False
        
        if piece.lower() == "rook" and origin_index in [0, 7, 56, 63]:
            castle_rook = True
            match origin_index:
                case 0:
                    castle_colour = "WHITE"
                    castle_direction = "left"
                case 7:
                    castle_colour = "WHITE"
                    castle_direction = "right"
                case 56:
                    castle_colour = "BLACK"
                    castle_direction = "left"
                case 63:
                    castle_colour = "BLACK"
                    castle_direction = "right"
        elif to_index in [0,7,56,63]:
            castle_capture = True
            match to_index:
                case 0:
                    castle_colour = "WHITE"
                    castle_direction = "left"
                case 7:
                    castle_colour = "WHITE"
                    castle_direction = "right"
                case 56:
                    castle_colour = "BLACK"
                    castle_direction = "left"
                case 63:
                    castle_colour = "BLACK"
                    castle_direction = "right"
        if castle_rook or castle_capture:
            self.castling[castle_colour][castle_direction] = self.castling[castle_colour][castle_direction][1]
            
        if piece.lower() == "king" and abs(origin_index - to_index) == 2:
            if piece[0].isupper():
                castle_piece = "Rook"
                self.castling["BLACK"]["left"] = self.castling["BLACK"]["left"][1]
                self.castling["BLACK"]["right"] = self.castling["BLACK"]["right"][1]
            else:
                castle_piece = "rook"
                self.castling["WHITE"]["left"] = self.castling["WHITE"]["left"][1]
                self.castling["WHITE"]["right"] = self.castling["WHITE"]["right"][1]
            
            if origin_index - to_index > 0: #back to left
                castle_to = origin_index - 4
                castle_origin = origin_index - 1 
            else: #back to right
                castle_to = origin_index + 3
                castle_origin = origin_index + 1
            if castle_to >= 0 and castle_origin >= 0:
                self.edit_board((castle_piece, castle_origin, castle_to))

    def king_safe(self, isWhite:bool=True) -> bool:
        if isWhite:
            if self.bitboard_dict["king"] == 0:
                return False
            else:
                king_origin = int(math.log2(self.bitboard_dict["king"]))
        else:
            if self.bitboard_dict["King"] == 0:
                return False
            else:
                king_origin = int(math.log2(self.bitboard_dict["King"]))
        move_dict = self.move_dict[0]
        for origin in move_dict.keys():
            for to in move_dict[origin]:
                if to == king_origin:
                    return False
        return True

    def output_bitboard_formatted(self, bitboard:int=-1) -> None:
        if bitboard == -1:
            bitboard = self.combined_board[0]|self.combined_board[1]
        board = format(bitboard, "064b")
        for row in range(0,(len(board)//8)):
            if row*8-1 < 0:
                print(" ".join(board[((row+1)*8)-1::-1]), row)
            else:
                print(" ".join(board[((row+1)*8)-1:row*8-1:-1]), row)
        print(" ".join("ABCDEFGH"))

    def number_to_algrebra_notation(self, move:tuple) -> tuple:
        if len(move) == 3:
            piece, origin, to = move
            promote = False
        else:
            piece, origin, to, promote_key = move
            promote = True
        files = "ABCDEFGH"
        origin_rank = str((origin//8) + 1)
        origin_file = str(files[origin%8])
        to_rank = str((to//8) + 1)
        to_file = str(files[to%8])
        if promote:
            return piece, origin_file+origin_rank, to_file+to_rank, promote_key
        else:
            return piece, origin_file+origin_rank, to_file+to_rank
    @property
    def output_board_formatted(self) -> None:
        board = ["." for x in range(64)]
        for piece_key in self.bitboard_dict.keys():
            for index, bit in enumerate(str(format(self.bitboard_dict[piece_key], "064b"))[::-1]):
                if int(bit) == 1:
                    match piece_key:
                        case "knight":
                            board[63-index] = piece_key[1]
                        case "Knight":
                            board[63-index] = piece_key[1].upper()
                        case _:
                            board[63-index] = piece_key[0]
        for row in range(0,(len(board)//8)):
            if row*8-1 < 0:
                print(" ".join(board[((row+1)*8)-1::-1]), row)
            else:
                print(" ".join(board[((row+1)*8)-1:row*8-1:-1]), row)
        print(" ".join("ABCDEFGH"))
    @property
    def move_dict(self) -> ({int:int}, {str:int}): #all move dictionaries below formatted as "origin:to" and "piece:origin"
        white, dark = self.combined_board
        key_to_index = {}
        move_dictionary = {}
        for key in self.bitboard_dict.keys():
            key_to_index[key] = []
            for index, bit in enumerate(str(format(self.bitboard_dict[key], "064b"))[::-1]):
                if int(bit) == 1:
                    key_to_index[key].append(index)
                    move_dictionary[index] = []
                    if key[0].isupper():
                        move_board = str(format(self.get_move(key, white, dark), "064b"))[::-1]
                    else:
                        move_board = str(format(self.get_move(key, dark, white), "064b"))[::-1]
                    for move_index, m_bit in enumerate(move_board):
                        if int(m_bit) == 1:
                            if key == "Pawn" and (2**move_index & self.file_edge_bitboard["1"]) > 0:
                                promote_keys = ["Knight", "Bishop", "Rook", "Queen"]
                                for promote_key in promote_keys:
                                    move_dictionary[index].append((move_index, promote_key))
                            elif key == "pawn" and (2**move_index & self.file_edge_bitboard["8"]) > 0:
                                promote_keys = ["knight", "bishop", "rook", "queen"]
                                for promote_key in promote_keys:
                                    move_dictionary[index].append((move_index, promote_key))
                            else:
                                move_dictionary[index].append(move_index)
        return move_dictionary, key_to_index
    @property
    def legal_move_dict(self) -> ({int:int}, {str:int}):
        move_dictionary, key_to_index = self.move_dict
        legal_move_dict = {}
        legal_key_index = {ki_piece_key:[] for ki_piece_key in key_to_index.keys()}
        for origin in move_dictionary.keys():
            for key in key_to_index.keys():
                if origin in key_to_index[key]:
                    piece_key = key
                    break
            if piece_key[0].isupper():
                isWhite = False
                colour = "BLACK"
            else:
                isWhite = True
                colour = "WHITE"
            for to_promote in move_dictionary[origin]:
                legal = True
                if type(to_promote) is tuple:
                    move = (piece_key, origin, to_promote[0], to_promote[1])
                else:
                    move = (piece_key, origin, to_promote)
                self.apply_move(move)
                
                legal = self.king_safe(isWhite)
                self.revert_move()
                
                if piece_key.lower() == "king" and abs(move[1] - move[2]) == 2:
                    if move[1] - move[2] > 0: #to left
                        to_tile_between = -1
                        if not(self.castling[colour]["left"]):
                            legal = False
                    else: #to right
                        to_tile_between = 1
                        if not(self.castling[colour]["right"]):
                            legal = False
                    legal = legal and self.king_safe(isWhite) #check if from in check
                    self.apply_move((piece_key , origin, origin+to_tile_between))
                    legal = legal and self.king_safe(isWhite) #check tile between to and from
                    self.revert_move() 
                    
                if piece_key.lower() == "pawn" and (abs(move[1] - move[2]) == 7 or abs(move[1] - move[2]) == 9):
                    last_piece, last_origin, last_to = self.applied_moves[len(self.applied_moves)-1][:3]
                    en_passant = last_to % 8 == move[2] % 8 and last_piece.lower() == "pawn" and abs(last_origin - last_to) == 16
                    taking = move[2] in move_dictionary.keys()
                    if en_passant or taking:
                        legal = True
                    else:
                        legal = False
                        
                if legal == True:
                    if not(origin in legal_move_dict.keys()):
                        legal_move_dict[origin] = []
                    legal_move_dict[origin].append(to_promote)
                    if not(origin in legal_key_index[piece_key]):
                        legal_key_index[piece_key].append(origin)
                        
        return legal_move_dict, legal_key_index
    @property
    def split_move_dict(self) -> (({int:int}, {str:int}), ({int:int}, {str:int})):
        move_dict, key_index = self.legal_move_dict
        w_move_dict = {}
        w_key = {}
        d_move_dict = {}
        d_key = {}
        for key in key_index.keys():
            if key[0].isupper():
                isWhite = False
            else:
                isWhite = True
            for origin in key_index[key]:
                if isWhite:
                    w_move_dict[origin] = move_dict[origin]
                    w_key[key] = key_index[key]
                else:
                    d_move_dict[origin] = move_dict[origin]
                    d_key[key] = key_index[key]
        return (w_move_dict, w_key), (d_move_dict, d_key)
    @property
    def move_board(self) -> (int, int):
        move_dict, key_index = self.move_dict
        w_move = 0
        d_move = 0
        for name_key in key_index.keys():
            for origin in key_index[name_key]:
                for pos_index in move_dict[origin]:
                    if type(pos_index) is int:
                        index = 2**pos_index
                    else:
                        index = 2**pos_index[0]
                    if name_key[0].isupper():
                        d_move |= index
                    else:
                        w_move |= index
        return w_move, d_move
    @property
    def combined_board(self) -> (int, int):
        pw_board = 0
        pd_board = 0
        for key in self.bitboard_dict.keys():
            if key[0].isupper():
                pd_board |= self.bitboard_dict[key]
            else:
                pw_board |= self.bitboard_dict[key]
        return pw_board, pd_board
    
if __name__ == "__main__":
    #board = "r...R...pp....k...p..p.pP.Pp..n..P...pP...P..N.P.....P....R...K."
    board = "r...k..rpppppppp....................pppp........PPPPPPPP.......K"
    bitBoard = BitBoard(board)
    while True:
        pass