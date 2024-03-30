import pygame, sys
sys.path.append("../A-Level-Chess-Algorithm")
from my_dataclass import Vector

class Scene:
    def __init__(self, width:int=800, height:int=800, local_point:Vector=None) -> None:
        """
        Parent class that stores the local points and dimensions in scenes that are needede to assign local points
        to each scene
        """

        self.local_point : Vector = local_point
        self.dimensions = Vector(width, height)
        self.vector_in_local_area = lambda vector : (self.local_point.x < vector.x < self.local_point.x + self.dimensions.x) and \
                        (self.local_point.y < vector.y < self.local_point.y + self.dimensions.y)
        self._overlay_scene : list[Scene] = []
        self.observers : list[SceneObserver] = []
    
    def add_overlay(self, overlay:object, local_point:Vector) -> object:
        """
        Assigns local point and appends to parent overlay_scenes when adding an overlay
        """
        overlay.local_point = local_point
        self._overlay_scene.append(overlay)
        return self

    def reset_overlay(self) -> object:
        """
        Clears overlays and associated object lists for buttons and text inputs via overriding this function
        """
        self._overlay_scene.clear()
        return self
        
    def scene_replace(self, scene:object=None, replacement:object=None) -> object:
        """
        Used to signal to observers that this scene want to replace a certain scene in the heriachy with another
        """
        for observer in self.observers:
            observer.replace_signal(scene, replacement)
        return self
    
    def while_update(self) -> object:
        for overlay in self._overlay_scene:
            overlay.while_update()
        return self
    
    def while_event(self, event:pygame.event.Event) -> object:
        for overlay in self._overlay_scene:
            overlay.while_event(event)
        return self
    
    def draw(self, window:pygame.surface.Surface) -> object:
        for overlay in self._overlay_scene:
            overlay.draw(window)
        return self


class Button(Scene):
    def __init__(self, width:int=100, height:int=100, font_size:int=0, \
        background_colour:tuple=(50,50,50), active_colour:tuple=(255,255,255), inactive_colour:tuple=(235,235,235), text:str="") -> None:
        super().__init__(width, height)
        """
        Button intialized with a background colour, text with colour and observer structure that signals whenever it is pressed
        """
        self.observers : list[ButtonObserver] = []
        self.background_colour : pygame.Color = pygame.Color(*background_colour)
        self.is_pressed : bool = False
        self.color_inactive : pygame.Color = pygame.Color(*inactive_colour)
        self.color_active : pygame.Color = pygame.Color(*active_colour)
        self.color : pygame.Color = self.color_inactive
        self.__font : pygame.font.Font = pygame.font.Font(None, font_size)
        self.text : str = text
    
    def pressed(self) -> object:
        """ Signals to observers if pressed and "self.is_pressed" remains True while held for observers to access """
        self.is_pressed = True
        for observer in self.observers:
            observer.press_signal(self)
        return self
    
    def release(self) -> object:
        """ Signals to observers if pressed and "self.is_pressed" remains False while not held for observers to access """
        self.is_pressed = False
        for observer in self.observers:
            observer.release_signal(self)
        return self
    
    def while_event(self, event:pygame.event.Event) -> object:
        """
        Handles events that press the button by checking if a "mouse vector" (named but not used for clarity) is within the buttons area
        pressing the button if clicked on within the area and releasing when leaving the area while held or releasing form held in area
        """
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
                    
        return super().while_event(event)
    
    def draw(self, window:pygame.surface.Surface) -> object:
        """
        Renders the button as a rectangle with a background colour and text that indicates its purpose
        """
        pygame.draw.rect(window, self.background_colour, pygame.Rect(self.local_point.x, self.local_point.y, self.dimensions.x, self.dimensions.y))
        text_surface = self.__font.render(self.text, True, self.color)
        window.blit(text_surface, (self.local_point.x, self.local_point.y))
        return super().draw(window)

class ButtonObserver():
    def press_signal(self, button : Button) -> object:
        return self
    
    def release_signal(self, button: Button) -> object:
        return self
    
class TextBox(Button):
    def __init__(self, width:int=100, height:int=100, font_size:int=50, \
        background_colour:tuple=(50,50,50), active_colour:tuple=(255,255,255), inactive_colour:tuple=(235,235,235), text:str="") -> None:
        super().__init__(width, height, font_size, background_colour, active_colour, inactive_colour, text=text)
        """
        Additionally to the button initalization, textboxes update the observer specification and have an active property for observers
        as it does not need to be held to listen to keyboard events 
        """
        self.observers : list[TextBoxObserver] = []
        self.active : bool = False
    
    def pressed(self) -> object:
        """ Signals and active to listen to keyboard events or observer access """
        self.active = True
        return super().pressed()
    
    def text_entered(self) -> object:
        """ Signals to observers that text is inputed """
        for observer in self.observers:
            observer.text_entered_signal(self, self.text)
        return self

    def switch(self) -> object:
        """ Signals that the textbox should be switched to the next """
        for observer in self.observers:
            observer.switch_signal(self)
        return self

    def while_event(self, event:pygame.event.Event) -> object:
        super().while_event(event)
        """ Listen to keyboard requests and acts like a text input """
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
        return self

    def draw(self, window) -> object:
        return super().draw(window)
        
    def while_update(self) -> object:
        return super().while_update()
    
class TextBoxObserver(ButtonObserver):
    def press_signal(self, scene:Scene) -> object:
        return self

    def text_entered_signal(self, scene:Scene, text:str) -> object:
        return self
    
    def switch_signal(self, scene:Scene) -> object:
        return self
                  
class SceneObserver():
    def __init__(self, scene : Scene) -> None:
        scene.observers.append(self)
    
    def resize_signal(self, parent:Scene) -> object:
        return object
    
    def replace_signal(self, current:Scene=None, replacement:Scene=None) -> object:
        return self

"""
Further development:
    -> Textbox when entering text and tabbing switching textbox functionality needed
"""