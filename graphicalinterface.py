import pygame
from scenehandler import Scene
def IGraphical():
    local_points = {}
    local_point = (0,0)
    def init(scenes:list[Scene]):
        for scene in scenes:
            local_points[scene] = local_point
            local_point += scene.dimensions
        
    @staticmethod
    def run(self):
        pass
        