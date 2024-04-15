import json
from enum import Enum

def convert_move(move):
    piece = Enum("piece", ["ROOK", "BISHOP", "KNIGHT", "QUEEN", "KING", "PAWN"])

def write_json_mapping():
    move_mapping = {}
    count = 0
    for u in range(1, 7):
        for x in range(1, 3):
            for y in range(64):
                for z in range(64):
                    move_mapping[count] = ((u, x), y, z)
                    count += 1
    with open("save_move_mapping.json", "w") as json_mapping:
        json_mapping.write(json.dumps(move_mapping))
        
def main():
    write_json_mapping()
    with open("save_move_mapping.json", "r") as json_mapping:
        move_mapping = json.loads(json_mapping.read())  
    pass
    # colour, piece, from, to
    # promotion saved with string as tuple
    # piece = (n-1)*2*64*64
    # colour = peice + (n-1)*64*64
    # from = colour + piece + n*64
    # to = colour + piece + from + n
    
    
    #going to make mapping for every possible move, by outlining from index (64 - 6 bits), to index (64 - 6 bits) and piece (6 - 3 bits)
    
if __name__ == "__main__":    
    main()