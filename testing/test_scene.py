import pygame, sys, time
sys.path.append("../A-Level-Chess-Algorithm")
from pygame_scene.scenehandler import SceneHandler, PyGameWindow
from pygame_scene.scenes.scene import Scene, SceneObserver
from pygame_scene.scenes.menu_scene import MenuScene, MenuObserver
from pygame_scene.scenes.game_scene import GameScene, GameObserver, PlayerVsPlayer, PlayerVsComputer, ComputerVsComputer, PlayerComponent, EvaluationComponent
from my_dataclass import Vector
from bitboard import BitBoard
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
        def __init__(self, scene:Scene) -> None:
            super().__init__(scene)
            self.detect_replace : bool = False
        
        def replace_signal(self, current:Scene, replacement:Scene) -> object:
            self.detect_replace = True
            return super().replace_signal()
            
    class TestSceneOverlay(Scene):
        def __init__(self, width:int=800, height:int=800, local_point:Vector=None) -> None:
            super().__init__(width, height, local_point)
            self.detect_while_event = False
            self.detect_while_update = False
            self.detect_draw = False
            
        def draw(self, window:pygame.surface.Surface) -> object:
            self.detect_draw = True
            return self
            
        def while_event(self, event:pygame.event.Event) -> object:
            self.detect_while_event = True
            return self
            
        def while_update(self) -> object:
            self.detect_while_update = True
            return self
            
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

def test_game_scene_init():
    window = SceneHandler((850,800), "test")
    window.add_scene(game_scene := GameScene(800, 800))
    assert game_scene

def test_game_scene_resize():
    window = SceneHandler((850,800), "test")
    window.add_scene(game_scene := GameScene(800, 800))
    game_scene.resize(600,700)
    extract_xy = lambda vector : (vector.x, vector.y)
    assert extract_xy(game_scene.dimensions) == (600, 600)

def test_game_scene_make_move():
    window = SceneHandler((850,800), "test")
    window.add_scene(game_scene := GameScene(800, 800, BitBoard(notation_board="k..............................................................K")))
    game_scene.make_move(((BitBoard.piece.KING, BitBoard.colour.WHITE), 0, 1))
    assert game_scene.bitboard.bitboard_dict[(BitBoard.piece.KING, BitBoard.colour.WHITE)] == 2

def test_game_scene_signals():
    class TestGameObserver(GameObserver):
        def __init__(self, game_scene: GameScene) -> None:
            super().__init__(game_scene)
            self.detect_game_end : bool = False
            self.detect_update_board : bool = False
            
        def game_end_signal(self, game_scene: GameScene) -> object:
            self.detect_game_end = True
            return super().game_end_signal(game_scene)
        
        def update_board_signal(self, parent: GameScene) -> object:
            self.detect_update_board = True
            return super().update_board_signal(parent)
        
    class TestGameSceneOverlay(GameScene):
        def __init__(self, width:int=800, height:int=800, local_point:Vector = None):
            super().__init__(width, height, local_point)
        
        def game_end(self) -> object:
            for observer in self.observers:
                observer.game_end_signal(self)
            return self
        
        def update_board(self) -> object:
            for observer in self.observers:
                observer.update_board_signal(self)
            return self
    
    window = SceneHandler((850, 800), "test")
    game_scene = TestGameSceneOverlay()
    test_observer = TestGameObserver(game_scene)
    
    game_scene.game_end()
    game_scene.update_board()
    
    assert test_observer.detect_game_end and test_observer.detect_update_board

"""
PlayerComponent Tests
"""

def test_player_component_init():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    player_componenet = PlayerComponent(game_scene)

def test_make_move_if_legal():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    player_componenet = PlayerComponent(game_scene)
    player_componenet.selected_tile = Vector(0,7)
    player_componenet.make_move_if_legal(Vector(1, 7), game_scene.bitboard.legal_move_dict[0])
    assert game_scene.bitboard.bitboard_dict[(BitBoard.piece.KING, BitBoard.colour.WHITE)] == 2

def test_click_event():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    event = pygame.event.Event(1025, {
        "pos" : (1,1),
        "button" : 1,
        "touch" : False,
        "window" : None
    })
    player_component = PlayerComponent(game_scene)
    player_component.click_event(event, game_scene.bitboard.legal_move_dict[0])
    extract_xy = lambda vector : (vector.x, vector.y)
    assert extract_xy(player_component.selected_tile) == (0,0)

def test_release_event():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    event = pygame.event.Event(1026, {
        "pos" : (1,1),
        "button" : 1,
        "touch" : False,
        "window" : None
    })
    player_component = PlayerComponent(game_scene)
    player_component.mouse_held_position = Vector(1,1)
    player_component.release_event(event, game_scene.bitboard.legal_move_dict[0])
    assert not(player_component.mouse_held_position)
    

def test_mouse_motion_event():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    event = pygame.event.Event(1024, {
        "pos" : (1,1),
        "rel" : (0,0),
        "buttons" : (0,0,0),
        "touch" : False,
        "window" : None
    })
    player_component = PlayerComponent(game_scene)
    player_component.selected_tile = player_component.mouse_held_position = Vector(0,0)
    player_component.mouse_motion_event(event)
    extract_xy = lambda vector : (vector.x, vector.y)
    assert extract_xy(player_component.mouse_held_position) == (1,1)
    
"""
EvaluationComponent and EvalautionThread Tests
"""

def test_evaluation_component_init():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    evaluation_component = EvaluationComponent(game_scene)
    assert True
    
def test_evaluation_update_thread():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    evaluation_component = EvaluationComponent(game_scene)
    evaluation_component.update_thread(((BitBoard.piece.KING, BitBoard.colour.WHITE), 0, 1))
    assert evaluation_component._EvaluationComponent__evaluation_threads[-1].engine.max_time == 0

def test_evaluation_create_new_thread():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    evaluation_component = EvaluationComponent(game_scene)
    evaluation_component.create_new_thread()
    assert len(evaluation_component._EvaluationComponent__evaluation_threads) == 2

def test_evaluation_best_moves():
    window = SceneHandler((850, 800), "test")
    window.add_scene(game_scene := GameScene(bitboard=BitBoard(notation_board="k..............................................................K")))
    evaluation_component = EvaluationComponent(game_scene, auto_start=True)
    while not(evaluation_component.best_moves()):
        pass
    assert evaluation_component.best_moves()

"""
Component Intergration (in PvP, PvC and CvC) Evaluation Bar Tests
"""

def test_integration_scene_init():
    window = SceneHandler((850, 800), "test")
    window.add_scene(pvp := PlayerVsPlayer()).add_scene(pvc := PlayerVsComputer()).add_scene(cvc := ComputerVsComputer())
    assert len(window._SceneHandler__scenes) == 3
    
def test_player_componenet_integration():
    window = SceneHandler((850, 800), "test")
    window.add_scene(pvp := PlayerVsPlayer())
    click_event = pygame.event.Event(1025, {
        "pos" : (1,1),
        "button" : 1,
        "touch" : False,
        "window" : None
    })
    mouse_motion_event = pygame.event.Event(1024, {
        "pos" : (1,1),
        "rel" : (0,0),
        "buttons" : (0,0,0),
        "touch" : False,
        "window" : None
    })
    extract_xy = lambda vector : (vector.x, vector.y)
    
    pvp.while_event(click_event)
    assert extract_xy(pvp.player_componenet.selected_tile) == (0,0)
    
    pvp.while_event(mouse_motion_event)
    assert extract_xy(pvp.player_componenet.mouse_held_position) == (1,1)
    
    
"""
Menu Database and etc Tests
"""

def test_menu_scene_init():
    pygame.init()
    window = SceneHandler((850,800), "test")
    menu = MenuScene(850, 800)
    window.add_scene(menu)


if __name__ == "__main__":
    pass