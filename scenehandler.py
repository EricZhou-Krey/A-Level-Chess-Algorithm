import pygame

class Scene:
    def while_event(self, events):
        pass
    def draw(self, local_point):
        pass
    
class PyGameWindow:
    def __init__(self, window_size, caption, graphical_interface):
        pygame.init()
        self.graphical_interface = graphical_interface
        self.window_size = window_size
        self.window = pygame.display.set_mode(window_size)
        self.caption = caption
        self.running = True
    
    def while_event(self, events):
        pass
    
    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.display.flip()
        pygame.quit()
    
class SceneHandler(PyGameWindow):
    def __init__(self, window_size, caption, graphical_interface, scene_array:list[Scene], scene_init_dict:dict):
        super().__init__(window_size, caption, graphical_interface)
        self.scene_array = scene_array
        for scene in scene_array:
            scene.__init__(scene_init_dict[scene])
            
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
            self.graphical_interface.run([x.draw for x in self.scene_array])
            pygame.display.flip()
        pygame.quit()