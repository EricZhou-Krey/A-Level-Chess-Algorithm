import bitboard, time, math
class Engine:
    def __init__(self, PAWN_MATERIAL_WEIGHT=1, BISHOP_MATERIAL_WEIGHT=3, KNIGHT_MATERIAL_WEIGHT=3, ROOK_WIEGHT=5, QUEEN_MATERIAL_WEIGHT=10,
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
                ]):
        self.PEICE_MATERIAL_WEIGHT = {
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
            "QUEEN" : QUEEN_POSITIONAL_WEIGHT
        }
    def get_material_advantage(self, piece_bitboard):
        d_material = 0
        w_material = 0
        for key in piece_bitboard.keys():
            for board in piece_bitboard[key]:
                match key:
                    case "pawn":
                        w_material += self.PEICE_MATERIAL_WEIGHT["PAWN"]
                    case "bishop":
                        w_material += self.PEICE_MATERIAL_WEIGHT["BISHOP"]
                    case "knight":
                        w_material += self.PEICE_MATERIAL_WEIGHT["KNIGHT"]
                    case "rook":
                        w_material += self.PEICE_MATERIAL_WEIGHT["ROOK"]
                    case "queen":
                        w_material += self.PEICE_MATERIAL_WEIGHT["QUEEN"]
                    case "Pawn":
                        d_material += self.PEICE_MATERIAL_WEIGHT["PAWN"]
                    case "Bishop":
                        d_material += self.PEICE_MATERIAL_WEIGHT["BISHOP"]
                    case "Knight":
                        d_material += self.PEICE_MATERIAL_WEIGHT["KNIGHT"]
                    case "Rook":
                        d_material += self.PEICE_MATERIAL_WEIGHT["ROOK"]
                    case "Queen":
                        d_material += self.PEICE_MATERIAL_WEIGHT["QUEEN"]
        return w_material, d_material
    def get_positional_advantage(self, piece_bitboard,):
        w_positional = 0
        d_positional = 0
        for key in piece_bitboard.keys():
            for board in piece_bitboard[key]:
                board_index = int(math.log2(board))
                match key:
                    case "pawn":
                        w_positional += self.POSITIONAL_WEIGHT["WPAWN"][board_index]
                    case "bishop":
                        w_positional += self.POSITIONAL_WEIGHT["BISHOP"][board_index]
                    case "knight":
                        w_positional += self.POSITIONAL_WEIGHT["KNIGHT"][board_index]
                    case "rook":
                        w_positional += self.POSITIONAL_WEIGHT["ROOK"][board_index]
                    case "queen":
                        w_positional += self.POSITIONAL_WEIGHT["QUEEN"][board_index]
                    case "Pawn":
                        d_positional += self.POSITIONAL_WEIGHT["DPAWN"][board_index]
                    case "Bishop":
                        d_positional += self.POSITIONAL_WEIGHT["BISHOP"][board_index]
                    case "Knight":
                        d_positional += self.POSITIONAL_WEIGHT["KNIGHT"][board_index]
                    case "Rook":
                        d_positional += self.POSITIONAL_WEIGHT["ROOK"][board_index]
                    case "Queen":
                        d_positional += self.POSITIONAL_WEIGHT["QUEEN"][board_index]
        return w_positional, d_positional
    def get_strategical_advantage(self, piece_bitboard):
        w_strategical = 0
        d_strategical = 0
        return w_strategical, d_strategical
if __name__ == "__main__":
    board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    bitBoard = bitboard.BitBoard(board)
    engine = Engine()
    print(engine.get_material_advantage(bitBoard.piece_bitboard))
    print(engine.get_positional_advantage(bitBoard.piece_bitboard))
    