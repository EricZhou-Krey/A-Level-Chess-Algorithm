import pygame, sys
from scenes.scene import Scene, PlayerVsComputer, EvaluationBar, Vector
sys.path.append("../A-Level-Chess-Algorithm")
from bitboard import BitBoard
from enginepy import Engine

class PyGameWindow:
    def __init__(self, window_size, caption) -> None:
        self._window_size = Vector(window_size[0], window_size[1])
        self.window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self._caption = caption
        self._running = True
    
    def run(self) -> None:
        while self._running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._window_size = Vector(event.w, event.h)
            pygame.display.flip()
        pygame.quit()
    
class SceneHandler(PyGameWindow):
    def __init__(self, window_size, caption) -> None:
        super().__init__(window_size, caption)
        self.__scenes = []
        self.__max_point = [Vector(0,0)]
        self.update_local_points()
        
    def add_scene(self, scene:Scene) -> object:
        self.__scenes.append(scene)
        scene.local_point = self._assign_local_point(scene)
        return self
        
    def __get_new_local_point(self, scene:Scene) -> Vector:
        local_point = Vector(0,0)
        if self.__max_point[-1].x + scene.dimensions.x > self._window_size.x:
            self.__max_point = sorted(self.__max_point, key = lambda vector: vector.y)
            
            for index_y, min_point in enumerate(self.__max_point[1:-1:]):
                x_gap_range = self.__max_point[index_y+1].x - self.__max_point[index_y-1].x
                if x_gap_range <= scene.dimensions.x:
                    local_point.y = min_point.y
                    
            if not(local_point.y):
                local_point.y = self.__max_point[-1].y
                local_point.x = 0
        else: 
            local_point.x = self.__max_point[-1].x
        return local_point
    
    def update_local_points(self) -> object:
        self._scene_to_locations = {}
        self.__max_point = [Vector(0,0)]
        for scene in self.__scenes: scene.local_point = self._assign_local_point(scene)
        return self
    
    def _assign_local_point(self, scene:Scene) -> Vector:
        local_point = self.__get_new_local_point(scene)
        self._scene_to_locations[scene] = (local_point, scene.dimensions)
        self.__max_point.append(Vector(self.__max_point[-1].x + scene.dimensions.x, self.__max_point[-1].y + scene.dimensions.y))
        return local_point
    
    def while_event(self, event) -> object:
        for scene in self.__scenes:
            scene.while_event(event)
        return self
            
    def run(self) -> None:
        while self._running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._window_size = Vector(event.w, event.h)
                    self.update_local_points()
                self.while_event(event)
            for scene in self.__scenes: scene.draw(self.window)
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    pygame.init()
    window = SceneHandler((850,800), "test")
    pvc = PlayerVsComputer(800, 800)
    window.add_scene(pvc).add_scene(EvaluationBar(50, pvc))
    window.run()