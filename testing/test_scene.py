import pygame, sys
sys.path.append("../A-Level-Chess-Algorithm")
from pygame_scene.scenehandler import SceneHandler, ComputerVsComputer, PlayerVsPlayer, PlayerVsComputer, EvaluationBar, PyGameWindow
from pygame_scene.scenes.scene import Scene, SceneObserver
from my_dataclass import Vector

"""
Scene & Scene Observer Tests
"""
    
def test_scene_init():
    scene = Scene(100, 100)
    assert scene

def test_add_overlay():
    scene = Scene(100, 100)
    scene.add_overlay(Scene(50, 50), Vector(50, 50))
    assert scene._overlay_scene

def test_scene_observer_init():
    scene = Scene(100, 100)
    scene_observer = SceneObserver(scene)
    assert scene_observer

def test_signals():
    class TestSceneObserver(SceneObserver):
        def __init__(self, scene: Scene):
            super().__init__(scene)
            self.detect_replace = False
        
        def replace_signal(self, current, replacement):
            self.detect_replace = True
            
    class TestSceneOverlay(Scene):
        def __init__(self, width, height, local_point: Vector = None):
            super().__init__(width, height, local_point)
            self.detect_while_event = False
            self.detect_while_update = False
            self.detect_draw = False
            
        def draw(self, window):
            self.detect_draw = True
            
        def while_event(self, event):
            self.detect_while_event = True
            
        def while_update(self):
            self.detect_while_update = True
            
    pygame.init()
    window = pygame.display.set_mode((100,100), pygame.RESIZABLE)
            
    scene = Scene(100,100)
    test_scene_observer = TestSceneObserver(scene)
    scene.add_overlay(test_scene_overlay := TestSceneOverlay(50, 50), Vector(50, 50))
    
    scene.while_event(None)
    scene.while_update()
    scene.scene_replace(None, None)
    scene.draw(window)
    assert test_scene_observer.detect_replace and test_scene_overlay.detect_draw and test_scene_overlay.detect_while_event and test_scene_overlay.detect_while_update

"""
Scene Handler & PyGameWindow Tests
"""
def test_pygame_window():
    pygame.init()
    window = PyGameWindow((100,100), "test")
    assert window

def test_pygame_run():
    pygame.init()
    window = PyGameWindow((100,100), "test")
    window.run()
    assert window

def test_handler_initalisation():
    pygame.init()
    window = SceneHandler((850,800), "test")
    assert window

def test_add_scene():
    pygame.init()
    extract_xy = lambda vector : (vector.x, vector.y)
    window = SceneHandler((850,800), "test")
    window.add_scene(Scene(800, 800)).add_scene(Scene(50, 800))
    assert window._SceneHandler__scenes
    assert extract_xy(window._SceneHandler__scenes[0].local_point) == (0,0)
    assert extract_xy(window._SceneHandler__scenes[1].local_point) == (800, 0)

"""
GameScene & GameObserver Tests
"""

"""
PlayerComponent Tests
"""

"""
EvaluationComponent and EvalautionThread Tests
"""

"""
PvP, PvC, CvC and EvlauationBar Tests
"""

    
if __name__ == "__main__":
    pass