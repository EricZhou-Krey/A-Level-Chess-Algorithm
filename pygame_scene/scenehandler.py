import pygame, sys
sys.path.append("../A-Level-Chess-Algorithm")
from pygame_scene.scenes.menu_scene import MenuScene
from pygame_scene.scenes.game_scene import Scene, Vector, SceneObserver

class PyGameWindow:
    def __init__(self, window_size:tuple=(800,800), caption:str="") -> None:
        """
        Creates simple pygame display with caption that is rendered upon later
        """
        self._window_size : Vector = Vector(*window_size)
        self.window : pygame.surface.Surface = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self._caption : str = caption
        self._running : bool = True
    
    def run(self) -> None:
        """
        Runs pygame loop without scene interupts to display a blank screen
        """
        while self._running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._window_size = Vector(event.w, event.h)
            pygame.display.flip()
        pygame.quit()

class SceneHandler(PyGameWindow, SceneObserver):
    def __init__(self, window_size:tuple=(800,800), caption:str="") -> None:
        PyGameWindow.__init__(self, window_size, caption)
        """
        Creates lists that group overlays and scenes aswell as automatically scaling and placing scene via local points
        """
        self.__scenes : list[Scene] = []
        self.__overlay_scene : list[Scene] = []
        self.__max_point : list[Vector] = [Vector(0,0)]
        self.__update_local_points()
        
    def add_scene(self, scene:Scene) -> object:
        """
        Adds a scene and assigns a local point from which it can reference event from and draw to, also observes for signals like resize
        """
        self.__scenes.append(scene)
        scene.local_point = self._assign_local_point(scene)
        scene.observers.append(self)
        return self
    
    def add_overlay(self, overlay:Scene, local_point:Vector) -> object:
        """ Assigns local point and appends to parent overlay_scenes when adding an overlay """
        self.__overlay_scene.append(overlay)
        overlay.local_point = local_point
        return self
        
    def __get_new_local_point(self, scene:Scene) -> Vector:
        """ From previously assigned local points assigns a location that is free to be place into on a scene"""
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
    
    def __update_local_points(self) -> object:
        """ Updates all local points assigned to scene, called when resizing of scenes or the pygame window occurs"""
        self._scene_to_locations = {}
        self.__max_point = [Vector(0,0)]
        for scene in self.__scenes: scene.local_point = self._assign_local_point(scene)
        return self
    
    def _assign_local_point(self, scene:Scene) -> Vector:
        """ Links local point to a scene that is currently being updated"""
        local_point = self.__get_new_local_point(scene)
        self._scene_to_locations[scene] = (local_point, scene.dimensions)
        self.__max_point.append(Vector(self.__max_point[-1].x + scene.dimensions.x, self.__max_point[-1].y + scene.dimensions.y))
        return local_point
    
    def while_event(self, event:pygame.event.Event) -> object:
        for scene in self.__scenes:
            scene.while_event(event)
        for overlay in self.__overlay_scene:
            overlay.while_event(event)
        return self
    
    def resize_signal(self, _) -> object:
        self.__update_local_points()
        return SceneObserver.resize_signal(self, _)
    
    def replace_signal(self, current:Scene, replacement:Scene) -> object:
        """
        Accepts replacement call from child scenes are replaces a scene with another
        """
        if current: self.__scenes.remove(current)
        self.__scenes.append(replacement)
        return SceneObserver.replace_signal(self, current, replacement)
    
    def while_update(self) -> object:
        for scene in self.__scenes:
            scene.while_update()
        for overlay in self.__overlay_scene:
            overlay.while_update()
        return self
    
    def run(self) -> None:
        """
        Hold the main game loop while calling all scenes in the heriarchy underneath the scene handler when they need to draw, update or
        an event occurs and updates local points when resizing window
        """
        while self._running:
            events = pygame.event.get()
            self.while_update()
            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._window_size = Vector(event.w, event.h)
                    self.__update_local_points()
                self.while_event(event)
            self.window.fill((0,0,0))
            for scene in self.__scenes: scene.draw(self.window)
            for overlay in self.__overlay_scene: overlay.draw(self.window)
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    window = SceneHandler((850,800), "test")
    menu = MenuScene(850, 800)
    window.add_scene(menu)
    window.run()