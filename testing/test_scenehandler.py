import pygame, sys
sys.path.append("../A-Level-Chess-Algorithm")
from pygame_scene.scenehandler import SceneHandler, ComputerVsComputer, PlayerVsPlayer, PlayerVsComputer, EvaluationBar
def test_init():
    pygame.init()
    window = SceneHandler((850,800), "test")
    game_scene = ComputerVsComputer(800, 800)
    window.add_scene(game_scene).add_scene(EvaluationBar(game_scene, 50))
    window.run()

if __name__ == "__main__":
    pass