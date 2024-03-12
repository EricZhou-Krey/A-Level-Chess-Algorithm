import pygame, sys
sys.path.append("../A-Level-Chess-Algorithm")
from my_dataclass import Vector

class Scene:
    def __init__(self, width, height):
        """
        Parent class that stores the local points and dimensions in scenes that are needede to assign local points
        to each of the scenes
        """
        self.local_point : Vector = None
        self.dimensions = Vector(width, height)
        
        self.observers : list[SceneObserver] = []
  
    def while_update(self):
        pass
    
    def while_event(self, event):
        pass
    
    def draw(self, window):
        # Default white rect on dimensions area
        pygame.draw.rect(window, (255,255,255), pygame.Rect(self.local_point.x, self.local_point.y, self.dimensions.x, self.dimensions.y))
    
    def stop(self):
        print("Ended scene:", self.__class__)
        for observer in self.observers:
            observer.stop_signal(self)
            
class SceneObserver():
    def __init__(self, scene : Scene):
        scene.observers.append(self)
    
    def resize_signal(self, parent):
        pass