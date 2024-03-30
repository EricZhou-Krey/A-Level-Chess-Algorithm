import pygame, sys
from enum import Enum
sys.path.append("../A-Level-Chess-Algorithm")
from my_dataclass import Vector

class Scene:
    def __init__(self, width, height, local_point:Vector=None):
        """
        Parent class that stores the local points and dimensions in scenes that are needede to assign local points
        to each of the scenes
        """

        self.local_point : Vector = local_point
        self.dimensions = Vector(width, height)
        self.vector_in_local_area = lambda vector : (self.local_point.x < vector.x < self.local_point.x + self.dimensions.x) and \
                        (self.local_point.y < vector.y < self.local_point.y + self.dimensions.y)
        self._overlay_scene : list[Scene] = []
        self.observers : list[SceneObserver] = []
    
    def add_overlay(self, overlay, local_point:Vector) -> object:
        overlay.local_point = local_point
        self._overlay_scene.append(overlay)
        return self

    def reset_overlay(self):
        self._overlay_scene.clear()
        
    def scene_replace(self, scene, replacement):
        for observer in self.observers:
            observer.replace_signal(scene, replacement)
    
    def while_update(self):
        for overlay in self._overlay_scene:
            overlay.while_update()
    
    def while_event(self, event):
        for overlay in self._overlay_scene:
            overlay.while_event(event)
    
    def draw(self, window):
        for overlay in self._overlay_scene:
            overlay.draw(window)


class Button(Scene):
    def __init__(self, width, height, font_size:int=0, background_colour:tuple=(50,50,50), active_colour:tuple=(255,255,255), inactive_colour:tuple=(235,235,235), text:str=""):
        super().__init__(width, height)
        self.observers : list[ButtonObserver] = []
        self.background_colour = pygame.Color(*background_colour)
        self.is_pressed : bool = False
        self.color_inactive = pygame.Color(*inactive_colour)
        self.color_active = pygame.Color(*active_colour)
        self.color = self.color_inactive
        self.__font = pygame.font.Font(None, font_size)
        self.text = text
    
    def pressed(self):
        self.is_pressed = True
        for observer in self.observers:
            observer.press_signal(self)
    
    def release(self):
        self.is_pressed = False
        for observer in self.observers:
            observer.release_signal(self)
    
    def while_event(self, event):
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                match event.button:
                    case 1:
                        if self.vector_in_local_area(mouse_vector := Vector(*pygame.mouse.get_pos())):
                            self.pressed()
            case pygame.MOUSEBUTTONUP:
                match event.button:
                    case 1:
                        if self.vector_in_local_area(mouse_vector := Vector(*pygame.mouse.get_pos())):
                            self.release()
                            
            case pygame.MOUSEMOTION:
                if not(self.vector_in_local_area(Vector(*event.pos))) and self.is_pressed:
                    self.release()
    
    def draw(self, window):
        pygame.draw.rect(window, self.background_colour, pygame.Rect(self.local_point.x, self.local_point.y, self.dimensions.x, self.dimensions.y))
        text_surface = self.__font.render(self.text, True, self.color)
        window.blit(text_surface, (self.local_point.x, self.local_point.y))
        return super().draw(window)

class ButtonObserver():
    def __init__(self) -> None:
        pass
    
    def press_signal(self, button : Button):
        pass
    
    def release_signal(self, button: Button):
        pass
    
class TextBox(Button):
    def __init__(self, width, height, font_size:int, background_colour:tuple=(50,50,50), active_colour:tuple=(255,255,255), inactive_colour:tuple=(235,235,235), text:str=""):
        super().__init__(width, height, font_size, background_colour, active_colour, inactive_colour, text=text)
        self.observers : list[TextBoxObserver] = []
        self.active = False
    
    def pressed(self):
        self.active = True
        self.is_pressed = True
        for observer in self.observers:
            observer.press_signal(self)
    
    def text_entered(self):
        for observer in self.observers:
            observer.text_entered_signal(self, self.text)

    def switch(self):
        for observer in self.observers:
            observer.switch_signal(self)

    def while_event(self, event):
        super().while_event(event)
        if event.type == pygame.KEYDOWN:
            if self.active:
                match event.key:
                    case pygame.K_TAB:
                        self.switch()
                    case pygame.K_RETURN:
                        self.text_entered()
                    case pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    case _:
                        self.text += event.unicode

    def draw(self, window):
        super().draw(window)
        
    def while_update(self):
        return super().while_update()
    
class TextBoxObserver(ButtonObserver):
    def __init__(self):
        super().__init__()
        
    def press_signal(self, scene):
        pass

    def text_entered_signal(self, scene, text : str):
        pass
    
    def switch_signal(self, scene):
        pass
                  
class SceneObserver():
    def __init__(self, scene : Scene):
        scene.observers.append(self)
    
    def resize_signal(self, parent):
        pass
    
    def replace_signal(self, current, replacement):
        pass
    