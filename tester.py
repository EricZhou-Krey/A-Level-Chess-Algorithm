import unittest, bitboard
class TestBitBoard(unittest.TestCase):
    def setUp(self) -> None:
        board = ""
        for x in range(64): board += "."
        self.bitBoard = bitboard.BitBoard(board)
        
    def test_rook_move(self):
        for index in range(64):
            self.bitBoard.bitboard_dict["rook"]
            
            
test = TestBitBoard()
test.setUp()
test.test_output_bitboard()
#WIP