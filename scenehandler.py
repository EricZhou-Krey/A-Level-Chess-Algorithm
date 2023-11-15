import pygame
from graphicalinterface import IGraphical
from scenes.playervscomputer import PlayerVsComputer
class Scene:
    def __init__(self, dimensions):
        self.local_point = 0
        self.dimensions = dimensions
    def while_event(self, events):
        pass
    def draw(self, local_point):
        pass

class PyGameWindow:
    def __init__(self, window_size, caption):
        pygame.init()
        self.window_size = window_size
        self.window = pygame.display.set_mode(window_size)
        self.caption = caption
        self.running = True
    
    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.display.flip()
        pygame.quit()
    
class SceneHandler(PyGameWindow):
    def __init__(self, window_size, caption, graphical_interface, scene_array:list[Scene]):
        super().__init__(window_size, caption)
        self.graphical_interface = graphical_interface
        self.scene_array = scene_array
        graphical_interface.init([scene for scene in self.scene_array])
            
    def while_event(self, events):
        for scene in self.scene_array:
            scene.while_event(events)
            
    def run(self):
        while self.running:
            events = pygame.event.get()
            self.while_event(events)
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.graphical_interface.run([scene.draw for scene in self.scene_array])
            pygame.display.flip()
        pygame.quit()
        
graphical_interface = IGraphical()
player_vs_computer_scene = PlayerVsComputer()
window = SceneHandler((900,900), "chess", graphical_interface, [player_vs_computer_scene])
window.run()