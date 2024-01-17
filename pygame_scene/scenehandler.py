import pygame
from scenes.scene import Scene, PlayerVsComputer, Vector

class PyGameWindow:
    def __init__(self, window_size, caption):
        pygame.init()
        self._window_size = Vector(window_size[0], window_size[1])
        self.window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.caption = caption
        self.running = True
    
    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._window_size = Vector(event.w, event.h)
            pygame.display.flip()
        pygame.quit()
    
class SceneHandler(PyGameWindow):
    def __init__(self, window_size, caption, scenes:list[Scene]):
        super().__init__(window_size, caption)
        self.__scenes = scenes
        self.__max_point = [Vector(0,0)]
        self.scene_to_locations = {}
        for scene in scenes: scene.local_point = self.assign_local_point(scene)
        
    def __get_new_local_point(self, scene:Scene):
        local_point = Vector(0,0)
        if self.__max_point[-1].x + scene.dimensions.x >= self.__window_size.x:
            self.__max_point = sorted(self.__max_point, key = lambda vector: vector.y)
            
            for index_y, min_point in enumerate(self.__max_point[1:-1:]):
                x_gap_range = self.__max_point[index_y+1].x - self.__max_point[index_y-1].x
                if x_gap_range < scene.dimensions.x:
                    local_point.y = min_point.y
                    
            if not(local_point.y):
                local_point.y = self.__max_point[-1].y
                local_point.x = 0
        else: 
            local_point.x = self.__max_point[-1].x
        return local_point
    
    def assign_local_point(self, scene:Scene):
        local_point = self.__get_new_local_point(scene)
        self.scene_to_locations[scene] = (local_point, scene.dimensions)
        self.__max_point.append(Vector(self.__max_point[-1].x + scene.dimensions.x, self.__max_point[-1].y + scene.dimensions.y))
        return local_point
    
    def while_event(self, events):
        for scene in self.__scenes:
            scene.while_event(events)
            
    def run(self):
        while self.running:
            events = pygame.event.get()
            self.while_event(events)
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._window_size = Vector(event.w, event.h)
            for scene in self.__scenes: scene.draw(self.window)
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    window = SceneHandler((900,900), "test", [Scene(x*100, x*100) for x in range(1,7)])
    window.run()