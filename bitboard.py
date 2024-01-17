from math import log2
from icecream import ic
    
class IPiece():
    def __init__(self) -> None:
        file_keys = ["A","B","C","D","E","F","G","H"]
        edge_keys = ["1","2","3","4","5","6","7","8"]
        
        file_values = [[(index_y*len(file_keys))+index_x for index_y in range(len(file_keys))] for index_x in range(len(edge_keys))]
        edge_values = [[index_x+(index_y*len(file_keys)) for index_x in range(len(edge_keys))] for index_y in range(len(file_keys))]
        
        file_edge_values = file_values + edge_values
        file_edge_keys = file_keys + edge_keys
        
        self.index_board_to_int64 = lambda array: sum([2**index for index in array])
        file_edge_values = [self.index_board_to_int64(index_array) for index_array in file_edge_values]
        
        self._file_edge_bitboard = dict(zip(file_edge_keys, file_edge_values))

    def get_knight_bitboard(self, board:int, similar:int=0) -> int:
        feb = self._file_edge_bitboard
        move = ((board & ~(feb["H"]|feb["7"]|feb["8"])) << 17) & ~(similar) # NNE
        move |= ((board & ~(feb["A"]|feb["7"]|feb["8"])) << 15) & ~(similar) # NNW
        move |= ((board & ~(feb["H"]|feb["G"]|feb["8"])) << 10) & ~(similar) # NEE
        move |= ((board & ~(feb["A"]|feb["B"]|feb["8"])) << 6) & ~(similar) # NWW
        move |= ((board & ~(feb["A"]|feb["2"]|feb["1"])) >> 17) & ~(similar) # SSW
        move |= ((board & ~(feb["H"]|feb["2"]|feb["1"])) >> 15) & ~(similar) # SSE
        move |= ((board & ~(feb["A"]|feb["B"]|feb["1"])) >> 10) & ~(similar) # SWW
        move |= ((board & ~(feb["H"]|feb["G"]|feb["1"])) >> 6) & ~(similar) # SEE
        return move

    def get_king_bitboard(self, board:int, similar:int=0, opposing:int=0) -> int:
        feb = self._file_edge_bitboard
        move = ((board & ~(feb["H"])) << 1) & ~(similar) #E
        move |= ((board & ~(feb["A"]|feb["8"])) << 7) & ~(similar) #NW
        move |= ((board & ~(feb["8"])) << 8) & ~(similar) #N
        move |= ((board & ~(feb["H"]|feb["8"])) << 9) & ~(similar) #NE
        move |= ((board & ~(feb["A"])) >> 1) & ~(similar) #W
        move |= ((board & ~(feb["H"]|feb["1"])) >> 7) & ~(similar) #SE
        move |= ((board & ~(feb["1"])) >> 8) & ~(similar) #S
        move |= ((board & ~(feb["A"]|feb["1"])) >> 9) & ~(similar) #SW
        move |= ((board & ~(feb["A"]|feb["B"])) >> 2) & ~(similar << 1| opposing << 1|similar|opposing|similar >> 1| opposing >> 1) #WW 
        move |= ((board & ~(feb["G"]|feb["H"])) << 2) & ~(similar|opposing|similar << 1| opposing << 1) #EE
        return move

    def get_pawn_bitboard(self, board:int, is_white:bool=True, opposing:int=0, similar:int=0) -> int:
        feb = self._file_edge_bitboard
        if is_white:
            move = (board << 8) & ~(similar) #N
            move |= ((board & ~(feb["7"]) & feb["2"]) << 16) & ~(opposing) & ~(similar) & ~((similar & ~(feb["1"])) << 8) #NN
            move |= ((board & ~(feb["A"])) << 7) & (opposing|opposing << 8) #NW
            move |= ((board & ~(feb["H"])) << 9) & (opposing|opposing << 8) #NE
        else:
            move = (board >> 8) & ~(similar) #S
            move |= ((board & ~(feb["2"]) & feb["7"]) >> 16) & ~(opposing) & ~(similar) & ~((similar & ~(feb["8"])) >> 8) #SS
            move |= ((board & ~(feb["H"])) >> 7) & (opposing|opposing >> 8) #SE
            move |= ((board & ~(feb["A"])) >> 9) & (opposing|opposing >> 8) #SW
        return move

    def get_bishop_bitboard(self, board:int, opposing:int=0, similar:int=0) -> int:
        def singular_bishop(board:int, opposing:int=0, similar:int=0) -> int:
            NEdge = self._file_edge_bitboard["8"]
            SEdge = self._file_edge_bitboard["1"]
            WEdge = self._file_edge_bitboard["A"]
            EEdge = self._file_edge_bitboard["H"]
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
                    move |= (board & ~(NEdge|EEdge)) << 9*index #NE
                if not(nw_done):
                    move |= (board & ~(NEdge|WEdge)) << 7*index #NW
                if not(sw_done):
                    move |= (board & ~(WEdge|SEdge)) >> 9*index #SW
                if not(se_done):
                    move |= (board & ~(EEdge|SEdge)) >> 7*index #SE
                WEdge |= WEdge|WEdge << 1
                SEdge |= SEdge|SEdge << 8
                EEdge |= EEdge|EEdge >> 1
                NEdge |= NEdge|NEdge >> 8
            return move
        move = 0
        for index, bit in enumerate(str(format(board, "064b"))[::-1]):
            if int(bit) == 1:
                move |= singular_bishop(2**index, opposing, similar)
        return move
    
    def get_rook_bitboard(self, board:int, opposing:int=0, similar:int=0) -> int:
        def singular_rook(board:int, opposing:int=0, similar:int=0) -> int:
            NEdge = self._file_edge_bitboard["8"]
            SEdge = self._file_edge_bitboard["1"]
            WEdge = self._file_edge_bitboard["A"]
            EEdge = self._file_edge_bitboard["H"]
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
                    move |= (board & ~(NEdge)) << 8*index #N 
                if not(s_done):
                    move |= (board & ~(SEdge)) >> 8*index #S
                if not(e_done):
                    move |= (board & ~(EEdge)) << index #E
                if not(w_done):
                    move |= (board & ~(WEdge)) >> index #W
                WEdge |= WEdge|WEdge << 1
                SEdge |= SEdge|SEdge << 8
                EEdge |= EEdge|EEdge >> 1
                NEdge |= NEdge|NEdge >> 8
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
    
    def get_pawn_mobility(self, board:int) -> int:
        feb = self._file_edge_bitboard
        move = ((board & ~(feb["H"])) << 1) #E
        move |= ((board & ~(feb["A"]|feb["8"])) << 7) #NW
        move |= ((board & ~(feb["H"]|feb["8"])) << 9) #NE
        move |= ((board & ~(feb["A"])) >> 1) #W
        move |= ((board & ~(feb["H"]|feb["1"])) >> 7) #SE
        move |= ((board & ~(feb["A"]|feb["1"])) >> 9) #SW
        return move
        
class BitBoard(IPiece):
    def __init__(self, notation_board:str) -> None:
        def init_index_to_bitboard(index_board:{str:list[int]}) -> None:
            self.__bitboard_dict = {}
            for key in index_board.keys():
                self.__bitboard_dict[key] = self.index_board_to_int64(index_board[key])
                
        def notation_to_index_board(notation_board:str) -> {str:list[int]}:
            pieces = ["rook", "knight", "bishop", "queen", "king", "pawn", "Rook", "Pawn", "Bishop", "Knight", "Queen", "King"]
            piece_index_board = dict(zip(pieces, [[] for key in range(len(pieces))]))
            notation_to_key = {"r":"rook", "n":"knight", "b":"bishop", "q":"queen", "k":"king", "p":"pawn", "R":"Rook", "P":"Pawn", "B":"Bishop", "N":"Knight", "Q":"Queen", "K":"King"}
            for index, notation in enumerate(notation_board):
                if notation in notation_to_key.keys():
                    piece_index_board[notation_to_key[notation]].append(index)
            return piece_index_board
        
        super().__init__()
        init_index_to_bitboard(notation_to_index_board(notation_board)) #lowercase = white, Uppercase = Black
        self.can_castle = {
            "BLACK" : {"left": True, "right": True},
            "WHITE" : {"left": True, "right": True}
        }
        self.__applied_moves = []
    @property
    def applied_moves(self) -> list:
        return self.__applied_moves
    @property
    def bitboard_dict(self) -> dict:
        return self.__bitboard_dict
    
    def _get_move(self, piece:str, opposing:int=0, similar:int=0, singular_piece_index:int=-1) -> int:
        if singular_piece_index > 0:
            piece_bitboard = 2**singular_piece_index
        else:
            piece_bitboard = self.__bitboard_dict[piece]
        match piece.lower():
            case "pawn":
                return self.get_pawn_bitboard(piece_bitboard, not(piece[0].isupper()), opposing, similar)
            case "king":
                return self.get_king_bitboard(piece_bitboard, similar, opposing)
            case "knight":
                return self.get_knight_bitboard(piece_bitboard, similar)
            case "bishop":
                return self.get_bishop_bitboard(piece_bitboard, opposing, similar)
            case "rook":
                return self.get_rook_bitboard(piece_bitboard, opposing, similar)
            case "queen":
                return self.get_queen_bitboard(piece_bitboard, opposing, similar)
            case _:
                return -1

    def _edit_board(self, move:tuple) -> None:
        """
        Move is extracted as this could be formated as:
        The piece moving, the origin from which is moving, the location to which it is moving
        And optionally, if the piece is a promoting pawn the promotion piece
        
        Then bitwise operations are performed to create a mask of the to and from location of the moving piece
        such that when a bitwise XOR is applied the bitboard is updated to the correct bitboard
        
        Then promote piece board is updated if promotion is assigned
        
        Finally the to location is checked to replace a captured piece and the bitwise XOR is applied
        """
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
            
        if promote_key != "":
            self.__bitboard_dict[promote_key] |= to_bit
        
        pw_board, pd_board = self.combined_board
        combined_board = pw_board | pd_board
        if combined_board ^ to_bit < combined_board:
            for key in self.__bitboard_dict.keys():
                if self.__bitboard_dict[key] & to_bit > 0:
                    self.__bitboard_dict[key] ^= to_bit
                    break
                
        self.__bitboard_dict[piece] ^= origin_to_bit

    def apply_move(self, move:tuple) -> None:
        """
        Move is extracted as this could be formated as:
        The piece moving, the origin from which is moving, the location to which it is moving
        And optionally, if the piece is a promoting pawn the promotion piece
        
        Then bitwise operations are performed to create a mask of the to and from location of the moving piece
        such that when a bitwise XOR is applied the bitboard is updated to the correct bitboard
        
        Then promote piece board is updated if promotion is assigned
        
        Finally the to location is checked to replace a captured piece and the bitwise XOR is applied
        """
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
        
        if promote_key != "":
            self.__bitboard_dict[promote_key] |= to_bit

        pw_board, pd_board = self.combined_board
        combined_board = pw_board | pd_board
        captured = False
        capture_key = None
        if combined_board ^ to_bit < combined_board:
            for capture_key in self.__bitboard_dict.keys():
                if self.__bitboard_dict[capture_key] & to_bit > 0:
                    capture_to_bit = to_bit
                    self.__bitboard_dict[capture_key] ^= capture_to_bit
                    captured = True
                    break
                
        if not(captured) and piece.lower() == "pawn" and not(origin_index % 8 == to_index % 8):
            if piece[0].isupper():
                capture_key = "pawn"
                capture_to_bit = to_bit << 8
                self.__bitboard_dict[capture_key] ^= capture_to_bit
                captured = True
            else:
                capture_key = "Pawn"
                capture_to_bit = to_bit >> 8
                self.__bitboard_dict[capture_key] ^= capture_to_bit
                captured = True
        
        self.__bitboard_dict[piece] ^= origin_to_bit
        
        """
        Next, castling validity is updated if:
        - Rook has been moved from its starting position or
        - Rook was taken from its starting position
        - King is moved from starting position or castled
        In which case, the "self.can_castle" is updated with a nested False that can be unpack to see when someone can castle
        """
        
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
        elif (to_index in [0,7] and capture_key == "rook") or (to_index in [56,63] and capture_key == "Rook"):
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
            self.can_castle[castle_colour][castle_direction] = (False, self.can_castle[castle_colour][castle_direction])
        
        if piece.lower() == "king":
            if abs(origin_index - to_index) == 2:
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
                    self._edit_board((castle_piece, castle_origin, castle_to))
                    if piece[0].isupper():
                        self.can_castle["BLACK"]["right"] = (False, self.can_castle["BLACK"]["right"])
                        self.can_castle["BLACK"]["left"] = (False, self.can_castle["BLACK"]["left"])
                    else:
                        self.can_castle["WHITE"]["right"] = (False, self.can_castle["WHITE"]["right"])
                        self.can_castle["WHITE"]["left"] = (False, self.can_castle["WHITE"]["left"])
                        
            elif origin_index == 60:
                self.can_castle["BLACK"]["right"] = (False, self.can_castle["BLACK"]["right"])
                self.can_castle["BLACK"]["left"] = (False, self.can_castle["BLACK"]["left"])
            elif origin_index == 4:
                self.can_castle["WHITE"]["right"] = (False, self.can_castle["WHITE"]["right"])
                self.can_castle["WHITE"]["left"] = (False, self.can_castle["WHITE"]["left"])        
        
        """
        Lastly, appends the applied move, with or without captured piece to "self.__applied_moves"
        """
        if captured == True:
            self.__applied_moves.append((move, (capture_key, capture_to_bit)))
        else:
            self.__applied_moves.append(move)

    def revert_move(self) -> None:
        """
        Move is extracted as this could be formated as:
        The piece moving, the origin from which is moving, the location to which it is moving
        And optionally, if the piece is a promoting pawn the promotion piece
        
        Then the origin and to locations are fliped into a packed "revert_move" that is passed to the edit the board
        and additionaly if a promotion was unpacked the revert_move also contains a depromotion to a pawn or the correct colour
        
        Lastly, the captured piece is added back to where it used to be
        """
        move = self.__applied_moves.pop()
        captured = False
        capture_key = None
        if len(move) == 2:
            captured = True
            move, (capture_key, capture_bit) = move
        if len(move) == 3:
            piece, origin_index, to_index = move
            revert_move = (piece, to_index, origin_index)
        else:
            piece, origin_index, to_index = move[:3]
            if piece[0].isupper():
                revert_move = (piece, to_index, origin_index, "Pawn")
            else:
                revert_move = (piece, to_index, origin_index, "pawn")
        
        self._edit_board(revert_move)
        
        if captured:
            self.__bitboard_dict[capture_key] |= capture_bit
        
        """
        Next, castling validity is updated if:
        - Rook has been moved from its starting position or
        - Rook was taken from its starting position
        - King is moved from starting position or castled
        In which case, the "self.can_castle" is updated to upack itself to the next boolean
        """
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
        elif (to_index in [0,7] and capture_key == "rook") or (to_index in [56,63] and capture_key == "Rook"):
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
            self.can_castle[castle_colour][castle_direction] = self.can_castle[castle_colour][castle_direction][1]
            
        if piece.lower() == "king":
            if abs(origin_index - to_index) == 2:
                if piece[0].isupper():
                    castle_piece = "Rook"
                    self.can_castle["BLACK"]["left"] = self.can_castle["BLACK"]["left"][1]
                    self.can_castle["BLACK"]["right"] = self.can_castle["BLACK"]["right"][1]
                else:
                    castle_piece = "rook"
                    self.can_castle["WHITE"]["left"] = self.can_castle["WHITE"]["left"][1]
                    self.can_castle["WHITE"]["right"] = self.can_castle["WHITE"]["right"][1]
                
                if origin_index - to_index > 0: #back to left
                    castle_to = origin_index - 4
                    castle_origin = origin_index - 1 
                else: #back to right
                    castle_to = origin_index + 3
                    castle_origin = origin_index + 1
                if castle_to >= 0 and castle_origin >= 0:
                    self._edit_board((castle_piece, castle_origin, castle_to))
            elif origin_index == 60:
                self.can_castle["BLACK"]["left"] = self.can_castle["BLACK"]["left"][1]
                self.can_castle["BLACK"]["right"] = self.can_castle["BLACK"]["right"][1]
            elif origin_index == 4:
                self.can_castle["WHITE"]["left"] = self.can_castle["WHITE"]["left"][1]
                self.can_castle["WHITE"]["right"] = self.can_castle["WHITE"]["right"][1]
                
    def king_safe(self, isWhite:bool=True) -> bool:
        """
        Compares all to locations of a move dictionary to the king origin to verify if the king can be taken or not
        """
        
        if isWhite:
            if self.__bitboard_dict["king"] == 0:
                return False
            else:
                king_origin = int(log2(self.__bitboard_dict["king"]))
        else:
            if self.__bitboard_dict["King"] == 0:
                return False
            else:
                king_origin = int(log2(self.__bitboard_dict["King"]))
                
        move_dict = self.move_dict[0]
        for origin in move_dict.keys():
            for to in move_dict[origin]:
                if to == king_origin:
                    return False
        return True

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
    
    def index_to_piece_key(self, index:int) -> str:
        index_bit = 2**index
        w_board, d_board = self.combined_board
        if index_bit & w_board > 0:
            is_white = True
        elif index_bit & d_board > 0:
            is_white = False
        else:
            return "No piece there"
        for key, bitboard in self.bitboard_dict.items():
            if not(key[0].isupper) == is_white and bitboard & index_bit > 0:
                return key
            
    def bitboard_formatted(self, bitboard:int=-1) -> str:
        """
        For debugging purposes, outputs 64bit integers as an 8 by 8 chess grid of 0s and 1s 
        Defaults to display the location of pieces on the bitboard
        """
        result = ""
        if bitboard == -1:
            w_board, d_board = self.combined_board
            bitboard = w_board|d_board
            
        board = format(bitboard, "064b")
        for row in range(0,(len(board)//8)):
            if row*8-1 < 0:
                result += " ".join(board[((row+1)*8)-1::-1]) + " " + str(row) + "\n"
            else:
                result += " ".join(board[((row+1)*8)-1:row*8-1:-1]) + " " + str(row) + "\n"
        result += " ".join("ABCDEFGH") + "\n"
        return result
    @property
    def board_formatted(self) -> str:
        """
        For debugging purposes, outputs pieces as an 8 by 8 chess board where:
        pawn = p, knight = n, bishop = b, rook = r, queen = q, king = k and black pieces have a starting captial
        """
        result = ""
        board = ["." for x in range(64)]
        for piece_key in self.__bitboard_dict.keys():
            for index, bit in enumerate(str(format(self.__bitboard_dict[piece_key], "064b"))[::-1]):
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
                result += " ".join(board[((row+1)*8)-1::-1]) + " " + str(row) + "\n"
            else:
                result += " ".join(board[((row+1)*8)-1:row*8-1:-1]) + " " + str(row) + "\n"
        result += " ".join("ABCDEFGH") + "\n"
        return result
    @property
    def move_dict(self) -> ({int:int}, {str:int}):
        """
        Complies the movement bit board of each piece into a dictionary
        by having a key for each origin location and a list of values being possible moves from said origin
        
        Lastly, key_to_index is a dictionary with a list of origins for every piece type, seperated into black and white with capital 
        """
        white, dark = self.combined_board
        key_to_index = {}
        move_dictionary = {}
        for key in self.__bitboard_dict.keys():
            key_to_index[key] = []
            for index, bit in enumerate(str(format(self.__bitboard_dict[key], "064b"))[::-1]):
                if int(bit) == 1:
                    key_to_index[key].append(index)
                    move_dictionary[index] = []
                    if key[0].isupper():
                        move_board = str(format(self._get_move(key, white, dark, index), "064b"))[::-1]
                    else:
                        move_board = str(format(self._get_move(key, dark, white, index), "064b"))[::-1]
                    for move_index, m_bit in enumerate(move_board):
                        if int(m_bit) == 1:
                            if key == "Pawn" and (2**move_index & self._file_edge_bitboard["1"]) > 0:
                                promote_keys = ["Knight", "Bishop", "Rook", "Queen"]
                                for promote_key in promote_keys:
                                    move_dictionary[index].append((move_index, promote_key))
                            elif key == "pawn" and (2**move_index & self._file_edge_bitboard["8"]) > 0:
                                promote_keys = ["knight", "bishop", "rook", "queen"]
                                for promote_key in promote_keys:
                                    move_dictionary[index].append((move_index, promote_key))
                            else:
                                move_dictionary[index].append(move_index)
                                
        return move_dictionary, key_to_index
    @property
    def legal_move_dict(self) -> ({int:int}, {str:int}):
        """
        Accesses the "move_dict" for a dictionary of possible moves
        
        Then checks if the friendly king is in danger for each move to verify legality
        Finally special rules are checked - noted later
        """
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
                
                """
                Caslting requirements:
                - King is moving 2 east or west then check if: 
                - Rook and king has not moved from starting position (stored in "self.can_castle")
                - King is not moving though check
                """
                
                if piece_key.lower() == "king" and abs(move[1] - move[2]) == 2:
                    if move[1] - move[2] > 0: #to left
                        to_tile_between = -1
                        if not(self.can_castle[colour]["left"]):
                            legal = False
                    else: #to right
                        to_tile_between = 1
                        if not(self.can_castle[colour]["right"]):
                            legal = False
                    move = (piece_key, origin, origin+to_tile_between)
                    legal = legal and self.king_safe(isWhite)
                    self.apply_move(move)
                    legal = legal and self.king_safe(isWhite)
                    self.revert_move()
                
                """
                Regular check move legality
                """
                if legal:
                    self.apply_move(move)
                    legal = self.king_safe(isWhite)
                    
                    self.revert_move()
                    
                """
                En-passant requirements:
                - Pawn is moving diagonally north-east/west or south-eat/west
                - Last move was a pawn moving 
                - Last move was on the same file as the move to location and same rank as the current origin
                - Last move moved exactly 2 north or 2 south (shift of +-16 indexes)
                """
                
                if piece_key.lower() == "pawn" and ((abs(move[1] - move[2]) == 7 or abs(move[1] - move[2]) == 9)):
                    if len(self.__applied_moves) > 0:
                        if len(self.__applied_moves[len(self.__applied_moves)-1]) == 3:
                            last_piece, last_origin, last_to = self.__applied_moves[len(self.__applied_moves)-1][:3]
                            en_passant = (last_to % 8 == move[2] % 8 and last_to // 8 == move[1] // 8) and last_piece.lower() == "pawn" and abs(last_origin - last_to) == 16
                            taking = move[2] in move_dictionary.keys()
                            if not(en_passant or taking):
                                legal = False
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
        """
        For debugging purposes, outputs the combined movement for each colour as a 64 bit integer
        """
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
        for key in self.__bitboard_dict.keys():
            if key[0].isupper():
                pd_board |= self.__bitboard_dict[key]
            else:
                pw_board |= self.__bitboard_dict[key]
        return pw_board, pd_board
    
if __name__ == "__main__":
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    pass