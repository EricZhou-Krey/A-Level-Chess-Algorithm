import pygame
class Vector():
    def __init__(self, x:float=0, y:float=0, z:float=0) -> None:
        self.x, self.y, self.z = x,y,z
    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)
    def __sub__(self, other):
        return Vector(self.x-other.x, self.y-other.y, self.z-other.z) 

class Scene:
    def __init__(self, width, height):
        self.local_point = None
        self.dimensions = Vector(width, height)
        
    def while_event(self, events):
        pass
    def draw(self, window):
        pygame.draw.rect(window, (255,255,255), pygame.Rect(self.local_point.x, self.local_point.y, self.dimensions.x, self.dimensions.y))

class PlayerVsComputer(Scene):
    def __init__(self, width, height, engine, bitboard):
        super().__init__(width, height)
        self.engine = engine
        self.bitboard = bitboard
        
    def while_event(self, events):
        pass
    
    def draw(self):
        pass
    
class AuthenticationScene(Scene):
    def __init__(self):
        super().__init__()
        
    def while_event(self, events):
        pass
    
    def draw(self):
        pass