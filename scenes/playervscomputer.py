from scenehandler import Scene
class PlayerVsComputer(Scene):
    def __init__(self, engine, bitboard):
        super().__init__()
        self.engine = engine
        self.bitboard = bitboard
        
    def while_event(self, events):
        pass
    
    def draw(self, local_point):
        pass