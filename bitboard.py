import math
class BitBoard:
    def __init__(self, notationBoard): #lowercase = white, Uppercase = black
        self.init_index_board(notationBoard) # self.piece_index_board[peice]
        self.init_bitboard(self.piece_index_board) #self.piece_bitboard[piece][p_index]
        self.init_edge() # self.file_edge_index, self.file_edge_bitboard
    def init_edge(self):
        self.file_edge_index = {
            "A" : [0,8,16,24,32,40,48,56],
            "B" : [1,9,17,25,33,41,49,57],
            "G" : [6,14,22,30,38,46,54,62],
            "H" : [7,15,23,31,39,47,55,63],
            "1" : [0,1,2,3,4,5,6,7],
            "2" : [8,9,10,11,12,13,14,15],
            "7" : [48,49,50,51,52,53,54,55],
            "8" : [56,57,58,59,60,61,62,63]
        }
        self.file_edge_bitboard = {
            "A" : self.index_board_to_uint64(self.file_edge_index["A"]),
            "B" : self.index_board_to_uint64(self.file_edge_index["B"]),
            "G" : self.index_board_to_uint64(self.file_edge_index["G"]),
            "H" : self.index_board_to_uint64(self.file_edge_index["H"]),
            "1" : self.index_board_to_uint64(self.file_edge_index["1"]),
            "2" : self.index_board_to_uint64(self.file_edge_index["2"]),
            "7" : self.index_board_to_uint64(self.file_edge_index["7"]),
            "8" : self.index_board_to_uint64(self.file_edge_index["8"]),
        }
    def index_board_to_uint64(self, index_array):
        bitBoard = int()
        for index in index_array:
            bitBoard += 2**index
        return bitBoard
    def init_bitboard(self, index_board):
        self.piece_bitboard = {
            "rook" : [self.index_board_to_uint64([index]) for index in index_board["rook"]],
            "pawn" : [self.index_board_to_uint64([index]) for index in index_board["pawn"]],
            "bishop" : [self.index_board_to_uint64([index]) for index in index_board["bishop"]],
            "knight" : [self.index_board_to_uint64([index]) for index in index_board["knight"]],
            "queen" : [self.index_board_to_uint64([index]) for index in index_board["queen"]],
            "king" : [self.index_board_to_uint64([index]) for index in index_board["king"]],
            "Rook" : [self.index_board_to_uint64([index]) for index in index_board["Rook"]],
            "Pawn" : [self.index_board_to_uint64([index]) for index in index_board["Pawn"]],
            "Bishop" : [self.index_board_to_uint64([index]) for index in index_board["Bishop"]],
            "Knight" : [self.index_board_to_uint64([index]) for index in index_board["Knight"]],
            "Queen" : [self.index_board_to_uint64([index]) for index in index_board["Queen"]],
            "King" : [self.index_board_to_uint64([index]) for index in index_board["King"]],
        }
    def init_index_board(self, board):
        self.piece_index_board = {
            "rook" : [],
            "pawn" : [],
            "bishop" : [],
            "knight" : [],
            "queen" : [],
            "king" : [],
            "Rook" : [],
            "Pawn" : [],
            "Bishop" : [],
            "Knight" : [],
            "Queen" : [],
            "King" : [],
        }
        for index, notation in enumerate(board):
            match notation:
                case "r":
                    self.piece_index_board["rook"].append(index)
                case "n":
                    self.piece_index_board["knight"].append(index)
                case "b":
                    self.piece_index_board["bishop"].append(index)
                case "q":
                    self.piece_index_board["queen"].append(index)
                case "p":
                    self.piece_index_board["pawn"].append(index)
                case "k":
                    self.piece_index_board["king"].append(index)
                case "R":
                    self.piece_index_board["Rook"].append(index)
                case "N":
                    self.piece_index_board["Knight"].append(index)
                case "B":
                    self.piece_index_board["Bishop"].append(index)
                case "P":
                    self.piece_index_board["Pawn"].append(index)
                case "K":
                    self.piece_index_board["King"].append(index)
                case "Q":
                    self.piece_index_board["Queen"].append(index)
    def get_knight_bitboard(self, board, similar=0):
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
    def get_king_bitboard(self, board, similar=0):
        fileA = self.file_edge_bitboard["A"]
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
        return move
    def get_pawn_bitboard(self, board, isWhite=True, opposing=0, similar=0):
        fileA = self.file_edge_bitboard["A"]
        fileH = self.file_edge_bitboard["H"]
        rankTwo = self.file_edge_bitboard["2"]
        rankSeven = self.file_edge_bitboard["7"]
        if isWhite:
            move = (board << 8) & ~(similar) #N
            move |= ((board & ~(rankSeven)) << 16) & ~(similar) #NN
            move |= ((board & ~(fileA)) << 7) & opposing #NW
            move |= ((board & ~(fileH)) << 9) & opposing #NE
        else:
            move = (board >> 8) & ~(similar) #S
            move |= ((board & ~(rankTwo)) >> 16) & ~(similar) #SS
            move |= ((board & ~(fileH)) >> 7) & opposing #SE
            move |= ((board & ~(fileA)) >> 9) & opposing #SW
        return move
    def get_bishop_bitboard(self, board, opposing=0, similar=0):
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
    def get_rook_bitboard(self, board, opposing=0, similar=0):
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
    def get_queen_bitboard(self, board, opposing=0, similar=0):
        move = self.get_bishop_bitboard(board, opposing, similar)
        move |= self.get_rook_bitboard(board, opposing, similar)
        return move 
    def get_move(self, piece, p_index, opposing=0, similar=0):
        match piece.lower():
            case "pawn":
                return self.get_pawn_bitboard(self.piece_bitboard[piece][p_index], not(piece[0].isupper()), opposing, similar)
            case "king":
                return self.get_king_bitboard(self.piece_bitboard[piece][p_index], similar)
            case "knight":
                return self.get_knight_bitboard(self.piece_bitboard[piece][p_index], similar)
            case "bishop":
                return self.get_bishop_bitboard(self.piece_bitboard[piece][p_index], opposing, similar)
            case "rook":
                return self.get_rook_bitboard(self.piece_bitboard[piece][p_index], opposing, similar)
            case "queen":
                return self.get_queen_bitboard(self.piece_bitboard[piece][p_index], opposing, similar)
            case _:
                return 0
    def correct_format(self, board):
        old = format(board, "064b")
        new = str()
        for x in range(1,9):
            for y in range(1,9):
                new += old[(8-x)*8+(8-y)]
        return new
    def output_bitboard_formatted(self, bitboard):
        array = format(bitboard, "064b")
        file = "ABCDEFGH"
        for x in range(1,9):
            for y in range(1,9):
                print(array[x*8-y], end=" ")
            print((8-x), "\n", end="")
        for y in range(0,8):
            print(file[y], end=" ")
        print("")
    def get_move_dict(self, white=0, dark=0):
        key_to_index = {}
        move_dictionary = {}
        for key in self.piece_bitboard.keys():
            key_to_index[key] = []
            for p_index, position_board in enumerate(self.piece_bitboard[key]):
                index = int(math.log2(position_board))
                key_to_index[key].append(index)
                move_dictionary[index] = []
                if key[0].isupper():
                    move_board = self.correct_format(self.get_move(key, p_index, white, dark))
                else:
                    move_board = self.correct_format(self.get_move(key, p_index, dark, white))
                for move_index, bit in enumerate(move_board):
                    if int(bit) == 1:
                        move_dictionary[index].append(move_index)
        return move_dictionary, key_to_index
    def get_piece_board(self):
        pw_board = 0
        pd_board = 0
        for key in self.piece_bitboard.keys():
            if key[0].isupper():
                for p_index in range(len(self.piece_bitboard[key])):
                    pd_board |= self.piece_bitboard[key][p_index]
            else:
                for p_index in range(len(self.piece_bitboard[key])):
                    pw_board |= self.piece_bitboard[key][p_index]
        return pw_board, pd_board
    def get_move_board(self, white=0, dark=0):
        move_dict, key_to_index = self.get_move_dict(white, dark)
        w_move = 0
        d_move = 0
        for name_key in key_to_index.keys():
            for origin in key_to_index[name_key]:
                for pos_index in move_dict[origin]:
                    index = 2**pos_index
                    if name_key[0].isupper():
                        d_move |= index
                    else:
                        w_move |= index
        return w_move, d_move
    
if __name__ == "__main__":
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = BitBoard(board)
    white, dark = bitBoard.get_piece_board()
    bitBoard.output_bitboard_formatted(bitBoard.get_move_board(white, dark)[1])