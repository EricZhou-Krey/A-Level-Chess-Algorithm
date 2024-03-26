from math import log2
from enum import Enum
import json
    
class IPiece():
    colour = Enum("colour", ["BLACK", "WHITE"])
    direction = Enum("direction", ["LEFT", "RIGHT"])
    piece = Enum("piece", ["ROOK", "BISHOP", "KNIGHT", "QUEEN", "KING", "PAWN"])
    enum_to_string = lambda enum : str(enum).split(".")[1]
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
        move = 0
        u_move_parameters = {
            "NNE" : (feb["H"]|feb["7"]|feb["8"], 17),
            "NNW" : (feb["A"]|feb["7"]|feb["8"], 15),
            "NEE" : (feb["H"]|feb["G"]|feb["8"], 10),
            "NWW" : (feb["A"]|feb["B"]|feb["8"], 6)
        }
        d_move_parameters = {
            "SSW" : (feb["A"]|feb["2"]|feb["1"], 17),
            "SSE" : (feb["H"]|feb["2"]|feb["1"], 15),
            "SWW" : (feb["A"]|feb["B"]|feb["1"], 10),
            "SEE" : (feb["H"]|feb["G"]|feb["1"], 6)
        }
        for border, shift in u_move_parameters.values():
            move |= ((board & ~(border)) << shift) & ~(similar)
        for border, shift in d_move_parameters.values():
            move |= ((board & ~(border)) >> shift) & ~(similar)
        return move

    def get_king_bitboard(self, board:int, similar:int=0, opposing:int=0) -> int:
        feb = self._file_edge_bitboard
        move = 0
        u_move_parameters = {
            "E" : (feb["H"], 1),
            "NW" : (feb["A"]|feb["8"], 7),
            "N" : (feb["8"], 8),
            "NE" : (feb["H"]|feb["8"], 9)
        }
        d_move_parameters = {
            "W" : (feb["A"], 1),
            "SE" : (feb["H"]|feb["1"], 7),
            "S" : (feb["1"], 8),
            "SW" : (feb["A"]|feb["1"], 9),
        }
        for border, shift in u_move_parameters.values():
            move |= ((board & ~(border)) << shift) & ~(similar)
        for border, shift in d_move_parameters.values():
            move |= ((board & ~(border)) >> shift) & ~(similar)
            
        move |= ((board & ~(feb["A"]|feb["B"])) >> 2) & ~(similar << 1| opposing << 1|similar|opposing|similar >> 1| opposing >> 1) #WW 
        move |= ((board & ~(feb["G"]|feb["H"])) << 2) & ~(similar|opposing|similar << 1| opposing << 1) #EE
        return move

    def get_pawn_bitboard(self, board:int, piece_colour:Enum, opposing:int=0, opposing_pawns:int=0, similar:int=0) -> int:
        feb = self._file_edge_bitboard
        if piece_colour == BitBoard.colour.WHITE:
            move = ((board & ~feb["8"]) << 8) & ~(similar|opposing) #N
            move |= ((board & feb["2"]) << 16) & ~(opposing|similar) & ~((similar|opposing & ~(feb["1"])) << 8) #NN
            move |= ((board & ~(feb["A"])) << 7) & (opposing|opposing_pawns << 8) #NW
            move |= ((board & ~(feb["H"])) << 9) & (opposing|opposing_pawns << 8) #NE
        else:
            move = ((board & ~feb["1"]) >> 8) & ~(similar|opposing) #S
            move |= ((board & feb["7"]) >> 16) & ~(opposing|similar) & ~((similar|opposing & ~(feb["8"])) >> 8) #SS
            move |= ((board & ~(feb["H"])) >> 7) & (opposing|opposing_pawns >> 8) #SE
            move |= ((board & ~(feb["A"])) >> 9) & (opposing|opposing_pawns >> 8) #SW
        return move

    def get_bishop_bitboard(self, board:int, opposing:int=0, similar:int=0) -> int:
        def singular_bishop(board:int, opposing:int=0, similar:int=0) -> int:
            feb = {
                "N" : self._file_edge_bitboard["8"],
                "S" : self._file_edge_bitboard["1"],
                "W" : self._file_edge_bitboard["A"],
                "E" : self._file_edge_bitboard["H"]
            }
            collided = {
                "N" : {
                    "F" : (False, 9),
                    "C" : (False, 7)
                    },
                "S" : {
                    "F" : (False, 9),
                    "C" : (False, 7)
                    }
            }
            #coilder not idenifying collsions on the east and west axis
            move = 0
            for index in range(1,9):
                for key, value in collided["N"].items():
                    _, shift = value
                    collided["N"][key] = (True, shift) \
                        if ((board << shift*(index-1)) & opposing) > 0 or ((board << shift*index) & similar) > 0 or collided["N"][key][0] else (False, shift)
                    collided["S"][key] = (True, shift) \
                        if ((board >> shift*(index-1)) & opposing) > 0 or ((board >> shift*index) & similar) > 0 or collided["S"][key][0] else (False, shift)
                
                if not(collided["N"]["F"][0]): move |= (board & ~(feb["N"]|feb["E"])) << 9*index
                if not(collided["N"]["C"][0]): move |= (board & ~(feb["N"]|feb["W"])) << 7*index
                if not(collided["S"]["F"][0]): move |= (board & ~(feb["S"]|feb["W"])) >> 9*index
                if not(collided["S"]["C"][0]): move |= (board & ~(feb["S"]|feb["E"])) >> 7*index
            
                feb["W"] |= feb["W"]|feb["W"] << 1
                feb["S"] |= feb["S"]|feb["S"] << 8
                feb["E"] |= feb["E"]|feb["E"] >> 1
                feb["N"] |= feb["N"]|feb["N"] >> 8
            return move
        
        move = 0
        for index, bit in enumerate(str(format(board, "064b"))[::-1]):
            if int(bit) == 1:
                move |= singular_bishop(2**index, opposing, similar)
        return move
    
    def get_rook_bitboard(self, board:int, opposing:int=0, similar:int=0) -> int:
        def singular_rook(board:int, opposing:int=0, similar:int=0) -> int:
            feb = {
                "N" : self._file_edge_bitboard["8"],
                "S" : self._file_edge_bitboard["1"],
                "W" : self._file_edge_bitboard["A"],
                "E" : self._file_edge_bitboard["H"]
            }
            collided = {
                "L" : {
                    "V" : (False, 8),
                    "H" : (False, 1)
                    },
                "R" : {
                    "H" : (False, 1),
                    "V" : (False, 8)
                    }
            }
            move = 0
            for index in range(1,9):
                for key, value in collided["L"].items():
                    done, shift = value
                    collided["R"][key] = (True, shift) \
                        if (((board << shift*(index-1)) & opposing) > 0 or ((board << shift*index) & similar) > 0) or collided["R"][key][0] else (False, shift)
                    collided["L"][key] = (True, shift) \
                        if (((board >> shift*(index-1)) & opposing) > 0 or ((board >> shift*index) & similar) > 0) or collided["L"][key][0] else (False, shift)
                
                if not(collided["R"]["V"][0]): move |= (board & ~(feb["N"])) << 8*index
                if not(collided["R"]["H"][0]): move |= (board & ~(feb["E"])) << index
                if not(collided["L"]["V"][0]): move |= (board & ~(feb["S"])) >> 8*index
                if not(collided["L"]["H"][0]): move |= (board & ~(feb["W"])) >> index
                
                feb["W"] |= feb["W"]|feb["W"] << 1
                feb["S"] |= feb["S"]|feb["S"] << 8
                feb["E"] |= feb["E"]|feb["E"] >> 1
                feb["N"] |= feb["N"]|feb["N"] >> 8
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
        """
        For engine evaluation purposes in order to analyse pawn connectivity
        """
        feb = self._file_edge_bitboard
        move = 0
        u_move_parameters = {
            "NW" : (feb["A"]|feb["8"], 7),
            "NE" : (feb["H"]|feb["8"], 9),
            "E" : (feb["H"], 1),
        }
        d_move_parameters = {
            "SW" : (feb["A"]|feb["1"], 9),
            "SE" :(feb["H"]|feb["1"], 7),
            "W" : (feb["A"], 1),
        }
        for border, shift in u_move_parameters.values():
            move |= ((board & ~(border)) << shift)
        for border, shift in d_move_parameters.values():
            move |= ((board & ~(border)) >> shift)
        return move

class BitBoard(IPiece):
    def __init__(self, notation_board:str) -> None:
        super().__init__()
        self.__notation_to_key = {"r":(BitBoard.piece.ROOK, BitBoard.colour.WHITE), "n":(BitBoard.piece.KNIGHT, BitBoard.colour.WHITE), "b":(BitBoard.piece.BISHOP, BitBoard.colour.WHITE), \
                "q":(BitBoard.piece.QUEEN, BitBoard.colour.WHITE), "k":(BitBoard.piece.KING, BitBoard.colour.WHITE), "p":(BitBoard.piece.PAWN, BitBoard.colour.WHITE), \
                "R":(BitBoard.piece.ROOK, BitBoard.colour.BLACK), "P":(BitBoard.piece.PAWN, BitBoard.colour.BLACK), "B":(BitBoard.piece.BISHOP, BitBoard.colour.BLACK), \
                "N":(BitBoard.piece.KNIGHT, BitBoard.colour.BLACK), "Q":(BitBoard.piece.QUEEN, BitBoard.colour.BLACK), "K":(BitBoard.piece.KING, BitBoard.colour.BLACK)}
        
        def init_index_to_bitboard(index_board:{str, list[int]}) -> None:
            self.__bitboard_dict = {}
            for key in index_board.keys():
                self.__bitboard_dict[key] = self.index_board_to_int64(index_board[key])
                
        def notation_to_index_board(notation_board:str) -> {str, list[int]}:
            pieces = [(piece, colour) for piece in list(BitBoard.piece) for colour in list(BitBoard.colour)]
            
            piece_index_board = dict(zip(pieces, [[] for key in range(len(pieces))]))
            
            for index, notation in enumerate(notation_board):
                if notation in self.__notation_to_key.keys():
                    piece_index_board[self.__notation_to_key[notation]].append(index)
            return piece_index_board
        
        init_index_to_bitboard(notation_to_index_board(notation_board))
        self.can_castle = {
            BitBoard.colour.BLACK : {BitBoard.direction.LEFT : True, BitBoard.direction.RIGHT : True},
            BitBoard.colour.WHITE : {BitBoard.direction.LEFT : True, BitBoard.direction.RIGHT : True}
        }
        self.__applied_moves = []
    @property
    def applied_moves(self) -> list:
        return self.__applied_moves
    @property
    def bitboard_dict(self) -> dict:
        return self.__bitboard_dict
    
    def _get_move(self, piece:tuple, opposing:int=0, similar:int=0, singular_piece_index:int=-1) -> int:
        if singular_piece_index > 0:
            piece_bitboard = 2**singular_piece_index
        else:
            piece_bitboard = self.__bitboard_dict[piece]
        piece_name, piece_colour = piece
        opposing_colour = BitBoard.colour.BLACK if piece_colour == BitBoard.colour.WHITE else BitBoard.colour.WHITE
        piece_movement_bitboard = {
            BitBoard.piece.PAWN : (self.get_pawn_bitboard, (piece_bitboard, piece_colour, opposing, \
                self.bitboard_dict[(BitBoard.piece.PAWN, opposing_colour)], similar)),
            BitBoard.piece.KING : (self.get_king_bitboard, (piece_bitboard, similar, opposing)),
            BitBoard.piece.KNIGHT : (self.get_knight_bitboard, (piece_bitboard, similar)),
            BitBoard.piece.BISHOP : (self.get_bishop_bitboard, (piece_bitboard, opposing, similar)),
            BitBoard.piece.ROOK : (self.get_rook_bitboard, (piece_bitboard, opposing, similar)),
            BitBoard.piece.QUEEN : (self.get_queen_bitboard, (piece_bitboard, opposing, similar)),
        }
        move_function, args = piece_movement_bitboard[piece_name]
        return move_function(*args)
    
    @staticmethod
    def _extract_move(move:tuple) -> tuple[str, str, int, int, int, int, int]:
        """
        Move is extracted as this could be formated as:
        The piece moving, the origin from which is moving, the location to which it is moving
        And optionally, if the piece is a promoting pawn the promotion piece
        
        Bitwise operations are performed to create a mask of the to and from location of the moving piece
        such that when a bitwise XOR is applied the bitboard is updated to the correct bitboard
        """
        
        piece, origin_index, to_index = move
        promote_key = None
        if type(to_index) is tuple: to_index, promote_key = to_index
        if type(origin_index) is tuple: origin_index, promote_key = origin_index
        
        origin_bit = 2**origin_index
        to_bit = 2**to_index
        
        if not(promote_key):
            origin_to_bit = origin_bit | to_bit
        else:
            origin_to_bit = origin_bit
            
        return piece, promote_key, origin_bit, to_bit, origin_to_bit, origin_index, to_index
    
    @staticmethod
    def number_to_algebra_notation(move:tuple) -> tuple:
        
        piece, promote_key, _, _, _, origin, to = BitBoard._extract_move(move)
        
        files = "ABCDEFGH"
        origin_rank = str((origin//8) + 1)
        origin_file = str(files[origin%8])
        to_rank = str((to//8) + 1)
        to_file = str(files[to%8])
        if promote_key:
            return piece, origin_file+origin_rank, to_file+to_rank, promote_key
        else:
            return piece, origin_file+origin_rank, to_file+to_rank  
    
    @staticmethod
    def bitboard_formatted(bitboard:int) -> str:
        """
        For debugging purposes, outputs 64bit integers as an 8 by 8 chess grid of 0s and 1s 
        Defaults to display the location of pieces on the bitboard
        """
        
        result = ""
        board = format(bitboard, "064b")
        for row in range(len(board)//8):
            result += " ".join(board[((row+1)*8)-1:(row*8)-1 if (row*8)-1 > 0 else None:-1]) + " " + str(row) + "\n"
        result += " ".join("ABCDEFGH") + "\n"
        return result
    
    with open("save_move_mapping.json", "r") as move_mapping:
        move_mapping = json.loads(move_mapping.read())
        
    @staticmethod
    def __convert_from_save_move(con_move:int|tuple) -> tuple: #untested, probably broken
        promote_key = None
        if type(con_move) is tuple:
            con_move, promote_key = con_move
        con_move = BitBoard.move_mapping[str(con_move)]
        (piece, colour), from_index, to_index = con_move
        
        colour = IPiece.colour(colour)
        piece = IPiece.piece(piece)
        return ((piece, colour), from_index, (to_index, promote_key) if promote_key else to_index)
    
    @staticmethod
    def convert_from_save_game(con_moves:list[int|tuple]) -> list[tuple]:
        return [BitBoard.__convert_from_save_move(con_move) for con_move in con_moves]
    
    @staticmethod
    def __convert_to_save_move(move:tuple):
        (piece, colour), promote_key, _, _, _, from_index, to_index = BitBoard._extract_move(move)
        move = (piece.value-1)*2*64*64 + (colour.value-1)*64*64 + from_index*64 + to_index
        return (move, promote_key) if promote_key else move

    @staticmethod
    def convert_to_save_game(move_list:list[tuple]):
        return [BitBoard.__convert_to_save_move(move) if len(move) == 3 else BitBoard.__convert_to_save_move(move[0]) for move in move_list]
      
    def edit_board(self, move:tuple) -> object:
        """
        Promote piece board is updated if promotion is assigned
        The to location is checked to replace a captured piece and the bitwise XOR is applied
        """
            
        piece, promote_key, _, to_bit, origin_to_bit, *_ = self._extract_move(move)
            
        pw_board, pd_board = self.combined_board
        combined_board = pw_board | pd_board
        if combined_board ^ to_bit < combined_board:
            for key in self.__bitboard_dict.keys():
                if self.__bitboard_dict[key] & to_bit > 0:
                    self.__bitboard_dict[key] ^= to_bit
                    break
        
        if promote_key:
            self.__bitboard_dict[promote_key] |= to_bit
        
        if piece:
            self.__bitboard_dict[piece] ^= origin_to_bit
        return self

    def apply_move(self, move:tuple) -> object:
        """
        Promote piece board is updated if promotion is assigned
        
        Finally the to location is checked to replace a captured piece and the bitwise XOR is applied
        """
        
        piece, promote_key, _, to_bit, origin_to_bit, origin_index, to_index = self._extract_move(move)
        piece_name, piece_colour = piece

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
        
        if promote_key:
            self.__bitboard_dict[promote_key] |= to_bit
        
        if not(captured) and piece_name == BitBoard.piece.PAWN and not(origin_index % 8 == to_index % 8):
            if piece_colour == BitBoard.colour.BLACK:
                capture_key = (BitBoard.piece.PAWN, BitBoard.colour.WHITE)
                capture_to_bit = to_bit << 8
                self.__bitboard_dict[capture_key] ^= capture_to_bit
                captured = True
            else:
                capture_key = (BitBoard.piece.PAWN, BitBoard.colour.BLACK)
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
        capture_piece, capture_colour = capture_key if capture_key else (None, None)
        if piece_name == BitBoard.piece.ROOK:
            castle_rook = True
            castle_colour = BitBoard.colour.WHITE if origin_index in [0, 7] else BitBoard.colour.BLACK
            castle_direction = BitBoard.direction.LEFT if origin_index in [0, 56] else BitBoard.direction.RIGHT
        elif capture_key and capture_piece == BitBoard.piece.ROOK:
            castle_capture = True
            castle_colour = BitBoard.colour.WHITE if to_index in [0, 7] else BitBoard.colour.BLACK
            castle_direction = BitBoard.direction.LEFT if to_index in [0, 56] else BitBoard.direction.RIGHT
        
        if castle_rook or castle_capture:
            self.can_castle[castle_colour][castle_direction] = (False, self.can_castle[castle_colour][castle_direction])
        
        if piece_name == BitBoard.piece.KING:
            if abs(origin_index - to_index) == 2:
                castle_piece = (BitBoard.piece.ROOK, BitBoard.colour.BLACK) if piece_colour == BitBoard.colour.BLACK else (BitBoard.piece.ROOK, BitBoard.colour.WHITE)
                if origin_index - to_index > 0: #to left
                    castle_origin = origin_index - 4
                    castle_to = origin_index - 1
                else: #to right
                    castle_origin = origin_index + 3
                    castle_to = origin_index + 1
                if castle_origin >= 0 and castle_to >= 0:
                    self.edit_board((castle_piece, castle_origin, castle_to))
                    if piece_colour == BitBoard.colour.BLACK:
                        self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.RIGHT] = (False, self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.RIGHT])
                        self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.LEFT] = (False, self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.LEFT])
                    else:
                        self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.RIGHT] = (False, self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.RIGHT])
                        self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.LEFT] = (False, self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.LEFT])
                        
            elif origin_index == 60:
                self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.RIGHT] = (False, self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.RIGHT])
                self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.LEFT] = (False, self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.LEFT])
            elif origin_index == 4:
                self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.RIGHT] = (False, self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.RIGHT])
                self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.LEFT] = (False, self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.LEFT])        
        
        """
        Lastly, appends the applied move, with or without captured piece to "self.__applied_moves"
        """
        if captured == True:
            self.__applied_moves.append((move, (capture_key, capture_to_bit)))
        else:
            self.__applied_moves.append(move)
        return self

    def revert_move(self) -> object:
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
            capture_piece, capture_colour = capture_key
            
        piece, promote_key, _, _, _, origin_index, to_index = self._extract_move(move)
        piece_name, piece_colour = piece
        if promote_key:
            origin_index = (origin_index, (BitBoard.piece.PAWN, piece_colour))
            revert_move = (promote_key, to_index, origin_index)
        else:
            revert_move = (piece, to_index, origin_index)
        
        self.edit_board(revert_move)
        
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
        if piece_name == BitBoard.piece.ROOK:
            castle_rook = True
            castle_colour = BitBoard.colour.WHITE if origin_index in [0, 7] else BitBoard.colour.BLACK
            castle_direction = BitBoard.direction.LEFT if origin_index in [0, 56] else BitBoard.direction.RIGHT
        elif capture_key and capture_piece == BitBoard.piece.ROOK:
            castle_capture = True
            castle_colour = BitBoard.colour.WHITE if to_index in [0, 7] else BitBoard.colour.BLACK
            castle_direction = BitBoard.direction.LEFT if to_index in [0, 56] else BitBoard.direction.RIGHT
                    
        if castle_rook or castle_capture:
            self.can_castle[castle_colour][castle_direction] = self.can_castle[castle_colour][castle_direction][1]
            
        if piece_name == BitBoard.piece.KING:
            if abs(origin_index - to_index) == 2:
                if piece_colour == BitBoard.colour.BLACK:
                    castle_piece = (BitBoard.piece.ROOK, BitBoard.colour.BLACK)
                    self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.LEFT] = self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.LEFT][1]
                    self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.RIGHT] = self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.RIGHT][1]
                else:
                    castle_piece = (BitBoard.piece.ROOK, BitBoard.colour.WHITE)
                    self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.LEFT] = self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.LEFT][1]
                    self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.RIGHT] = self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.RIGHT][1]
                
                if origin_index - to_index > 0: #back to left
                    castle_to = origin_index - 4
                    castle_origin = origin_index - 1 
                else: #back to right
                    castle_to = origin_index + 3
                    castle_origin = origin_index + 1
                if castle_to >= 0 and castle_origin >= 0:
                    self.edit_board((castle_piece, castle_origin, castle_to))
            elif origin_index == 60:
                self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.LEFT] = self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.LEFT][1]
                self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.RIGHT] = self.can_castle[BitBoard.colour.BLACK][BitBoard.direction.RIGHT][1]
            elif origin_index == 4:
                self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.LEFT] = self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.LEFT][1]
                self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.RIGHT] = self.can_castle[BitBoard.colour.WHITE][BitBoard.direction.RIGHT][1]
        return self
                
    def king_safe(self, colour:Enum) -> bool:
        """
        Compares all to locations of a move dictionary to the king origin to verify if the king can be taken or not
        """
        
        if self.__bitboard_dict[(BitBoard.piece.KING, colour)] == 0:
            return False
        else:
            king_origin = int(log2(self.__bitboard_dict[(BitBoard.piece.KING, colour)]))
                
        move_dict = self.move_dict[0]
        for origin in move_dict.keys():
            for to in move_dict[origin]:
                if to == king_origin:
                    return False
        return True
    
    def index_to_piece_key(self, index:int) -> str:
        index_bit = 2**index
        w_board, d_board = self.combined_board
        
        is_white = True if index_bit & w_board > 0 else None
        is_white = False if index_bit & d_board > 0 else is_white
        if is_white == None: return None
                    
        for key, bitboard in self.bitboard_dict.items():
            key_name, key_colour = key
            if (key_colour == BitBoard.colour.WHITE) == is_white and bitboard & index_bit > 0:
                return key
        return None
    

        
    @property
    def board_formatted(self) -> str:
        """
        For debugging purposes, outputs pieces as an 8 by 8 chess board where:
        pawn = p, knight = n, bishop = b, rook = r, queen = q, king = k and black pieces have a starting captial
        """
        result = ""
        board = ["." for x in range(64)]
        key_to_notation = {key:notation for notation, key in self.__notation_to_key.items()}
        for piece_key in self.__bitboard_dict.keys():
            for index, bit in enumerate(str(format(self.__bitboard_dict[piece_key], "064b"))[::-1]):
                if int(bit) == 1:
                    board[63-index] = key_to_notation[piece_key]
                            
        for row in range(0,(len(board)//8)):
            if row*8-1 < 0:
                result += " ".join(board[((row+1)*8)-1::-1]) + " " + str(row) + "\n"
            else:
                result += " ".join(board[((row+1)*8)-1:row*8-1:-1]) + " " + str(row) + "\n"
        result += " ".join("ABCDEFGH") + "\n"
        return result
    @property
    def move_dict(self) -> tuple[{int, int}, {str,int}]:
        """
        Complies the movement bit board of each piece into a dictionary
        by having a key for each origin location and a list of values being possible moves from said origin
        
        Lastly, key_to_index is a dictionary with a list of origins for every piece type, seperated into black and white with capital 
        """
        
        white, dark = self.combined_board
        key_to_index = {key:[] for key in self.__bitboard_dict.keys()}
        move_dictionary = {}
        
        for key, bitboard in self.__bitboard_dict.items():
            piece_name, piece_colour = key
            for index, bit in enumerate(str(format(bitboard, "064b"))[::-1]):
                if int(bit) == 1:
                    key_to_index[key].append(index)
                    move_dictionary[index] = []
                    
                    move_board = str(format(self._get_move(key, white, dark, index), "064b"))[::-1] if piece_colour == BitBoard.colour.BLACK \
                        else str(format(self._get_move(key, dark, white, index), "064b"))[::-1]
                        
                    for move_index, m_bit in enumerate(move_board):
                        if int(m_bit) == 1:
                            if piece_name == BitBoard.piece.PAWN and (2**move_index & \
                                (self._file_edge_bitboard["1"] if piece_colour == BitBoard.colour.BLACK else self._file_edge_bitboard["8"])) > 0:
                                promote_keys = [(BitBoard.piece.KNIGHT, piece_colour), (BitBoard.piece.BISHOP, piece_colour), \
                                    (BitBoard.piece.ROOK, piece_colour), (BitBoard.piece.QUEEN, piece_colour)]
                                for promote_key in promote_keys:
                                    move_dictionary[index].append((move_index, promote_key))
                            else:
                                move_dictionary[index].append(move_index)
                                
        return move_dictionary, key_to_index
    @property
    def legal_move_dict(self) -> tuple[{int,int}, {str,int}]:
        """
        Accesses the "move_dict" for a dictionary of possible moves
        
        Then checks if the friendly king is in danger for each move to verify legality
        Finally special rules are checked - noted later
        """
        move_dictionary, key_to_index = self.move_dict
        legal_move_dict = {}
        legal_key_index = {ki_piece_key:[] for ki_piece_key in key_to_index.keys()}
        for origin, to_indexes in move_dictionary.items():
            for key, indexes in key_to_index.items():
                if origin in indexes:
                    piece_name, piece_colour = key
                    break
                
            for to_index in to_indexes:
                legal = True
                move = ((piece_name, piece_colour), origin, to_index)
                promote_key = None
                if type(to_index) is tuple: to_index, promote_key = to_index
                
                """
                Caslting requirements:
                - King is moving 2 east or west then check if: 
                - Rook and king has not moved from starting position (stored in "self.can_castle")
                - King is not moving though check
                """
                
                if piece_name == BitBoard.piece.KING and abs(origin - to_index) == 2:
                    if origin - to_index > 0: #to left
                        to_tile_between = -1
                        if not(self.can_castle[piece_colour][BitBoard.direction.LEFT] == True):
                            legal = False
                    else: #to right
                        to_tile_between = 1
                        if not(self.can_castle[piece_colour][BitBoard.direction.RIGHT] == True):
                            legal = False
                    move = ((piece_name, piece_colour), origin, origin+to_tile_between)
                    legal = legal and self.king_safe(piece_colour)
                    self.apply_move(move)
                    legal = legal and self.king_safe(piece_colour)
                    self.revert_move()
                
                """
                Regular check move legality
                """
                if legal:
                    self.apply_move(move)
                    legal = self.king_safe(piece_colour)
                    self.revert_move()
                    
                """
                En-passant requirements:
                - Pawn is moving diagonally north-east/west or south-eat/west
                - Last move was a pawn moving 
                - Last move was on the same file as the move to location and same rank as the current origin
                - Last move moved exactly 2 north or 2 south (shift of +-16 indexes)
                """
                
                if piece_name == BitBoard.piece.PAWN and ((abs(origin - to_index) == 7 or abs(origin - to_index) == 9)):
                    if len(self.__applied_moves) > 0:
                        if len(self.__applied_moves[-1]) == 3:
                            last_piece, last_origin, last_to = self.__applied_moves[-1][:3]
                            last_piece_name, last_piece_colour = last_piece
                            
                            en_passant = (last_to % 8 == to_index % 8 and last_to // 8 == origin // 8) \
                                and last_piece_name == BitBoard.piece.PAWN and abs(last_origin - last_to) == 16
                                
                            taking = to_index in move_dictionary.keys()
                            if not(en_passant or taking):
                                legal = False
                    else:
                        legal = False
                        
                if legal == True:
                    if not(origin in legal_move_dict.keys()):
                        legal_move_dict[origin] = []
                    legal_move_dict[origin].append((to_index, promote_key) if promote_key else to_index)
                    if not(origin in legal_key_index[(piece_name, piece_colour)]):
                        legal_key_index[(piece_name, piece_colour)].append(origin)
                        
        return legal_move_dict, legal_key_index
    @property
    def split_move_dict(self) -> dict[Enum, (dict[int,int], dict[str,int])]:
        move_dict, key_index = self.legal_move_dict
        w_move_dict = {}
        w_key = {}
        d_move_dict = {}
        d_key = {}
        for key, indexes in key_index.items():
            key_name, key_colour = key
            for origin in indexes:
                if key_colour == BitBoard.colour.WHITE:
                    w_move_dict[origin] = move_dict[origin]
                    w_key[key] = key_index[key]
                else:
                    d_move_dict[origin] = move_dict[origin]
                    d_key[key] = key_index[key]
                    
        result_dict = {
            BitBoard.colour.WHITE : (w_move_dict, w_key),
            BitBoard.colour.BLACK : (d_move_dict, d_key)
        }
        return result_dict
    @property
    def move_board(self) -> tuple[int, int]:
        """
        For debugging purposes and engine evaluation, outputs the combined movement for each colour as a 64 bit integer
        """
        move_dict, key_index = self.legal_move_dict
        w_move = 0
        d_move = 0
        for key, indexes in key_index.items():
            key_name, key_colour = key
            for origin in indexes:
                for pos_index in move_dict[origin]:
                    if type(pos_index) is int:
                        index = 2**pos_index
                    else:
                        index = 2**pos_index[0]
                    if key_colour == BitBoard.colour.BLACK:
                        d_move |= index
                    else:
                        w_move |= index
        return w_move, d_move
    @property
    def combined_board(self) -> tuple[int, int]:
        pw_board = 0
        pd_board = 0
        for key in self.__bitboard_dict.keys():
            key_name, key_colour = key
            if key_colour == BitBoard.colour.BLACK:
                pd_board |= self.__bitboard_dict[key]
            else:
                pw_board |= self.__bitboard_dict[key]
        return pw_board, pd_board
    
if __name__ == "__main__":
    board = "rnbqkbnrpppppppp...............................qPPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board).apply_move(((BitBoard.piece.QUEEN, BitBoard.colour.WHITE), 47, 55))
    pass
    legal = bitBoard.legal_move_dict
    pass