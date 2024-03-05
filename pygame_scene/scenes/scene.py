import pygame, sys, time, threading, copy, math
sys.path.append("../A-Level-Chess-Algorithm")
from enum import Enum
from bitboard import BitBoard
from enginepy import Engine
class Vector():
    def __init__(self, *args) -> None:
        self.values = list(args)
    @property
    def x(self):
        return self.values[0]
    @x.setter
    def x(self, value:float):
        self.values[0] = value
    @property
    def y(self):
        return self.values[1]
    @y.setter
    def y(self, value:float):
        self.values[1] = value
    @property
    def z(self):
        return self.values[2]
    @z.setter
    def z(self, value:float):
        self.values[2] = value
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.__class__(*tuple(value*other for value in self.values))
        else:
            return self.__class__(*tuple(value*other_value for value, other_value in zip(self.values, other.values)))
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return self.__class__(*tuple(value/other for value in self.values))
        else:
            return self.__class__(*tuple(value/other_value for value, other_value in zip(self.values, other.values)))
            
    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            return self.__class__(*tuple(value//other for value in self.values))
        else:
            return self.__class__(*tuple(value//other_value for value, other_value in zip(self.values, other.values)))

    def __add__(self, other):
        return self.__class__(*tuple(value+other_value for value, other_value in zip(self.values, other.values)))
    def __sub__(self, other):
        return self.__class__(*tuple(value-other_value for value, other_value in zip(self.values, other.values)))

class Scene:
    def __init__(self, width, height):
        """
        Parent class that stores the local points and dimensions in scenes that are needede to assign local points
        to each of the scenes
        """
        self.local_point = None
        self.dimensions = Vector(width, height)
        
    def while_event(self, event):
        pass
    
    def draw(self, window):
        # Default white rect on dimensions area
        pygame.draw.rect(window, (255,255,255), pygame.Rect(self.local_point.x, self.local_point.y, self.dimensions.x, self.dimensions.y))

class GameScene(Scene):
    turn = Enum("turn", ["PLAYER", "COMPUTER"])
    update_type = Enum("update_type", ["EDIT", "APPLY", "REVERT"])
    def __init__(self, width, height, bitboard=None):
        super().__init__(width, height)
        self.observers : list[GameObserver] = []
        """
        Piece images are loaded, resized and stored in a dictionary with their associated display notation used by the notation board
        """
        
        self._updated_display_image = lambda self, image : pygame.transform.scale(image, (self.dimensions.x // 8, self.dimensions.y // 8))
        self.notation_to_image = {name:self._updated_display_image(self, image) for name, image in \
        zip(['p', 'r', 'b', 'n', 'q', 'k', 'P', 'R', 'B', 'N', 'Q', 'K'], \
            
        [pygame.image.load("Chess Piece Image/Chess_" + image_reference + ".svg").convert_alpha() for image_reference in \
        ["plt45", "rlt45", "blt45", "nlt45", "qlt45", "klt45", "pdt45", "rdt45", "bdt45", "ndt45", "qdt45", "kdt45"]])}
        
        """
        After loading files needed for the scene, input parameters are handled by linking or creating a new bitboard and engine
        class with this instance of the PlayerVsComputer scene
        """
        
        if not(bitboard):
            board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
            self.bitboard = BitBoard(board)
        else:
            self.bitboard = bitboard
        self._legal_moves = self.bitboard.legal_move_dict[0]
        
        """
        The notation board is extracted from the newly linked bitboard and formatted into a list with correct notation
        to refer to the images loaded previously
        """
        self.within_board = lambda vector : self.local_point.x < vector.x < self.local_point.x + self.dimensions.x and \
                                self.local_point.y < vector.y < self.local_point.y + self.dimensions.y
        self.vector_to_index = lambda vector : vector.x + (8 * (7 - vector.y))
        self.index_to_vector = lambda index : Vector((index % 8), (7 - (index//8)))
        self.vector_in_local_area = lambda vector : (self.local_point.x < vector.x < self.local_point.x + self.dimensions.x) and \
                        (self.local_point.y < vector.y < self.local_point.y + self.dimensions.y)
        
        self._updated_display_board = lambda self : [row[:15].split(" ") for row in self.bitboard.board_formatted[:141].split("\n")[:9]]
        self.notation_board = self._updated_display_board(self)
        
        self.current_turn = [BitBoard.colour.WHITE]
    
    @staticmethod
    def switch_colour(current_turn:list) -> None:
        current_turn[0] = current_turn[0] = BitBoard.colour.BLACK if current_turn[0] == BitBoard.colour.WHITE else BitBoard.colour.WHITE
        
    def resize(self, height, width):
        self.dimensions.x = self.dimensions.y = min(height, width)
        for key, image in self.notation_to_image.items(): self.notation_to_image[key] = self._updated_display_image(self, image)
        for observer in self.observers:
            observer.resize_signal(self)
            
    def update_board(self, move:tuple=None, type=None):
        type = type if type else self.update_type.APPLY
        match type:
            case self.update_type.APPLY:
                self.bitboard.apply_move(move)
                
            case self.update_type.EDIT:
                self.bitboard.edit_board(move)
    
            case self.update_type.REVERT:
                self.bitboard.revert_move()
                
        self._legal_moves = self.bitboard.split_move_dict[self.current_turn[0]][0]
        self.notation_board = self._updated_display_board(self)
        for observer in self.observers:
            observer.update_board_signal(self)

class PlayerVsComputer(GameScene):
    def __init__(self, width, height, bitboard=None):
        super().__init__(width, height, bitboard)
        
        self.evaluation_component = EvaluationComponent(self)
        
        """
        Values used in subroutines
        """
        
        self.DRAG_DELAY = 0.5
        self.__mouse_held_position = None
        self.__drag_start_time = None
        self.__selected_tile = None
        
        """
        GUI colours for different features of the scene will be moved to json file later
        """
        
        self.__light_tile_colour = (50,100,50)
        self.__dark_tile_colour = (255,255,150)
        self.__select_colour = (100,100,255)
        self.__possible_move_colour = (255,100,100)
    
    def while_event(self, event):
        mouse_to_vector = lambda mouse_x, mouse_y : Vector(mouse_x, mouse_y) // (self.dimensions // 8)
        def make_move_if_legal(to_vector : Vector):
            from_index = (7 - self.__selected_tile.y) * 8 + (self.__selected_tile.x)
            to_index = (7 - to_vector.y) * 8 + (to_vector.x)
            self.__selected_tile = None
            try: 
                move_piece, move_colour = self.bitboard.index_to_piece_key(from_index)
            except:
                return
            move = ((move_piece, move_colour), from_index, to_index)
            
            if move[1] in self._legal_moves.keys():
                if move[2] in self._legal_moves[move[1]]:
                    self.make_move(move)
            
        def click_event():
            match event.button:
                case 1: 
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.__mouse_held_position = Vector(mouse_x, mouse_y)
                    if self.vector_in_local_area(Vector(mouse_x, mouse_y)):
                        if self.__selected_tile:
                            make_move_if_legal(mouse_to_vector(mouse_x, mouse_y))
                        else:
                            self.__selected_tile = Vector(mouse_x, mouse_y) // (self.dimensions // 8)
                            self.__drag_start_time = time.time()
                case 3:
                    self.__selected_tile = None
                    
        def release_event():
            match event.button:
                case 1:
                    self.__mouse_held_position = None
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.vector_in_local_area(Vector(mouse_x, mouse_y)):
                        if (time.time() - self.__drag_start_time) > self.DRAG_DELAY:
                            if self.__selected_tile:
                                make_move_if_legal(mouse_to_vector(mouse_x, mouse_y))
                                
        def mouse_motion_event():
            if self.__selected_tile and self.__mouse_held_position:
                self.__mouse_held_position.x, self.__mouse_held_position.y = event.pos
        
        match event.type:
            case pygame.VIDEORESIZE:
                self.resize(event.h, event.w)
            case pygame.MOUSEBUTTONDOWN:
                click_event()
            case pygame.MOUSEBUTTONUP:
                release_event()
            case pygame.MOUSEMOTION:
                mouse_motion_event()
    
    def draw(self, window):
        def draw_board():
            tilesize = self.dimensions // 8
            if self.__selected_tile and self.vector_to_index(self.__selected_tile) in self._legal_moves.keys():
                legal_move_vectors = [self.index_to_vector(index) if type(index) is int else self.index_to_vector(index[0]) for index in self._legal_moves[self.vector_to_index(self.__selected_tile)]]
            else: legal_move_vectors = []
            
            selected_piece_drag_position = selected_notation = None
            for r_index, row in enumerate(self.notation_board):
                for c_index, notation in enumerate(row):
                    
                    tile_rect = pygame.Rect(c_index * tilesize.x, r_index * tilesize.y, tilesize.x, tilesize.y)
                    if (c_index, r_index) in [(vector.x, vector.y) for vector in legal_move_vectors]:
                        pygame.draw.rect(window, self.__possible_move_colour, tile_rect)
                    elif (c_index + r_index) % 2 == 0: pygame.draw.rect(window, self.__light_tile_colour, tile_rect)
                    else: pygame.draw.rect(window, self.__dark_tile_colour, tile_rect)
                    
                    if self.__selected_tile and (c_index, r_index) == (self.__selected_tile.x, self.__selected_tile.y):
                        pygame.draw.rect(window, self.__select_colour, tile_rect)
                        if notation != ".":
                            if self.__mouse_held_position and self.within_board(self.__mouse_held_position):
                                selected_piece_drag_position = (self.__mouse_held_position.x - ((self.dimensions.x // 8) // 2), self.__mouse_held_position.y - ((self.dimensions.y // 8) // 2))
                                selected_notation = notation
                            else:
                                window.blit(self.notation_to_image[notation], (c_index * (self.dimensions.x // 8), r_index * (self.dimensions.y // 8)))
                    elif notation != ".":
                        window.blit(self.notation_to_image[notation], (c_index * (self.dimensions.x // 8), r_index * (self.dimensions.y // 8)))
                        
            if selected_notation and selected_piece_drag_position:
                window.blit(self.notation_to_image[selected_notation], selected_piece_drag_position)
        
        draw_board()
    
    def make_move(self, move):
        self.switch_colour(self.current_turn)
        self.update_board(move)
        #vreating new thread too slowly in succession, should create queue system to manage the requests
        self.evaluation_component.update_thread(move)

class Queue():
    def __init__(self) -> None:
        pass
    
    #move evaluation could be used as reference
    
class EvaluationComponent():
    def __init__(self, parent : GameScene) -> None:
        self.bitboard = parent.bitboard
        self.current_turn = parent.current_turn
        self.update_queue = [] #
        self.__last_move = None # chage to list queue
        self.__evaluation_threads = [EvaluationThread(self)]
        self.__evaluation_threads[-1].start()
    
    def update_thread(self, move:tuple):
        self.__last_move = move
        self.__evaluation_threads[-1].engine.max_time = 0
        
    def create_new_thread(self, move_evaluation):
        self.__evaluation_threads.append(EvaluationThread(self, move_evaluation[self.__last_move] \
            if type(move_evaluation[self.__last_move]) is dict else None))
        self.__evaluation_threads[-1].start()
        
class EvaluationThread(threading.Thread):
    def __init__(self, evaluation_component : EvaluationComponent, move_evaluation : dict = None) -> None:
        super().__init__()
        self.parent = evaluation_component
        self.static_bitboard = self.parent.bitboard
        self.engine = Engine(copy.deepcopy(self.static_bitboard))
        self.move_evaluation = move_evaluation
        self.best_moves = Engine.find_ordered_move_eval(self.move_evaluation) if self.move_evaluation else []
        
    def run(self):
        self.engine.max_time = math.inf
        self.move_evaluation = self.engine.min_max_dict(current_colour=self.parent.current_turn[0])
        self.parent.create_new_thread(self.move_evaluation)

class GameObserver(Scene):
    def __init__(self, width, height, game_scene : Scene):
        super().__init__(width, height)
        game_scene.observers.append(self)
    
    def draw(self, window):
        pygame.draw.rect(window, (255,255,255), pygame.Rect(self.local_point.x, self.local_point.y, self.dimensions.x, self.dimensions.y))
    
    def resize_signal(self, parent : GameScene):
        pass
    
    def update_board_signal(self, parent : GameScene):
        pass
    
class EvaluationBar(GameObserver):
    def __init__(self, width, game_scene : Scene, height=0):
        super().__init__(width, height, game_scene)
        self.dimensions.y = game_scene.dimensions.y
        self.__current_move_eval = None
        self.__current_move = None