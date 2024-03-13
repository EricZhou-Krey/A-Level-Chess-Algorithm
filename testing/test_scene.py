import pygame, sys
sys.path.append("../A-Level-Chess-Algorithm")
from pygame_scene.scenehandler import SceneHandler, ComputerVsComputer, PlayerVsPlayer, PlayerVsComputer, EvaluationBar

def test_initalisation():
    pygame.init()
    window = SceneHandler((850,800), "test")
    assert True

def test_addscene():
    pygame.init()
    window = SceneHandler((850,800), "test")
    window.add_scene(game_scene := ComputerVsComputer(800, 800)).add_scene(EvaluationBar(game_scene, 50))
    assert True

if __name__ == "__main__":
    pass