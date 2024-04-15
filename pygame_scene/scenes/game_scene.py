import sys, pygame
from math import inf
from copy import deepcopy
from threading import Thread
from time import time
sys.path.append("../A-Level-Chess-Algorithm")
from pygame_scene.scenes.scene import Scene, SceneObserver, Button, ButtonObserver
from enum import Enum
from my_dataclass import Vector, Queue
from bitboard import BitBoard
from enginepy import Engine
            
class GameScene(Scene):
    turn : Enum = Enum("turn", ["PLAYER", "COMPUTER"])
    def __init__(self, width:int=800, height:int=800, bitboard:BitBoard=None):
        super().__init__(width, height)
        self.observers : list[GameObserver] = []
        self.evaluation_component : EvaluationComponent = None
        """
        Piece images are loaded, resized and stored in a dictionary with their associated display notation used by the notation board
        """
        
        self._updated_display_image : function = lambda self, image : pygame.transform.scale(image, (self.dimensions.x // 8, self.dimensions.y // 8))
        self.notation_to_image : dict = {name:self._updated_display_image(self, image) for name, image in \
        zip(['p', 'r', 'b', 'n', 'q', 'k', 'P', 'R', 'B', 'N', 'Q', 'K'], \
            
        [pygame.image.load("Chess Piece Image/Chess_" + image_reference + ".svg").convert_alpha() for image_reference in \
        ["plt45", "rlt45", "blt45", "nlt45", "qlt45", "klt45", "pdt45", "rdt45", "bdt45", "ndt45", "qdt45", "kdt45"]])}
        
        """
        After loading files needed for the scene, input parameters are handled by linking or creating a new bitboard and engine
        class with this instance of the PlayerVsComputer scene
        """
        
        board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
        self.bitboard : BitBoard = bitboard if bitboard else BitBoard(board)
        self._legal_moves : dict = self.bitboard.legal_move_dict[0]
        
        """
        The notation board is extracted from the newly linked bitboard and formatted into a list with correct notation
        to refer to the images loaded previously
        """
        self.vector_to_index : function = lambda vector : vector.x + (8 * (7 - vector.y))
        self.index_to_vector : function = lambda index : Vector((index % 8), (7 - (index//8)))
        
        self._updated_display_board : function = lambda self : [row[:15].split(" ") for row in self.bitboard.board_formatted[:141].split("\n")[:9]]
        self.notation_board : list = self._updated_display_board(self)
        
        self.current_turn : list[Enum] = [BitBoard.colour.WHITE] # Using Python's list mutablity for turn tracking
        """
        GUI colours for different features of the scene will be moved to json file later
        """
        self._object_colour : dict = {
            "LIGHT" : (50, 100, 50),
            "DARK" : (255, 255, 150),
            "SELECT" : (100, 100, 255),
            "POSSIBLE_MOVE" : (255, 100, 100)
        }
        self._player_legal_move : function = lambda bitboard : bitboard.legal_move_dict[0]
    
    @staticmethod
    def switch_colour(current_turn:list) -> None:
        """ Switches an Enum to another, used for clarity """
        current_turn[0] = BitBoard.colour.BLACK if current_turn[0] == BitBoard.colour.WHITE else BitBoard.colour.WHITE
        
    def resize(self, height:int, width:int) -> object:
        """
        Automatically resizes game scene itself is loaded into a scene handler to fill the entire scene square based
        """
        self.dimensions.x = self.dimensions.y = min(height, width)
        for key, image in self.notation_to_image.items(): self.notation_to_image[key] = self._updated_display_image(self, image)
        for observer in self.observers:
            observer.resize_signal(self)
        return self
    
    def draw(self, window:pygame.surface.Surface) -> object:
        """
        Draws the chess board according to the notation board list stored as a property by alternating between black and white and 
        rendering an image of a peice on the xy-place coordinate approriate to said pieces location
        """
        tilesize = self.dimensions // 8
        for r_index, row in enumerate(self.notation_board):
            for c_index, notation in enumerate(row):
                
                tile_rect = pygame.Rect(c_index * tilesize.x, r_index * tilesize.y, tilesize.x, tilesize.y)
                if (c_index + r_index) % 2 == 1: pygame.draw.rect(window, self._object_colour["LIGHT"], tile_rect)
                else: pygame.draw.rect(window, self._object_colour["DARK"], tile_rect)
                if notation != ".":
                    window.blit(self.notation_to_image[notation], (c_index * (self.dimensions.x // 8), r_index * (self.dimensions.y // 8)))
        return super().draw(window)
    
    _update_type : Enum = Enum("update_type", ["EDIT", "APPLY", "REVERT"])
    def _update_board(self, move:tuple=None, u_type:Enum=None) -> object:
        """
        Depending on the update type of the board for valid, invalid and reverting moves stated above the move is applied and then
        the legal moves are updated and if empty i.e one player can no longer move the game is concluded and a signal is called
        """
        u_type = u_type if u_type else GameScene._update_type.APPLY
        match u_type:
            case self._update_type.APPLY:
                self.bitboard.apply_move(move)
                
            case self._update_type.EDIT:
                self.bitboard.edit_board(move)
    
            case self._update_type.REVERT:
                self.bitboard.revert_move()
                
        self._legal_moves = self._player_legal_move(self.bitboard)
        
        if not(self._legal_moves):
            for observer in self.observers:
                observer.game_end_signal(self)
                
        self.notation_board = self._updated_display_board(self)
        for observer in self.observers:
            if type(observer) is GameObserver:
                observer.update_board_signal(self)
        return self

    def make_move(self, move:tuple=None) -> object:
        self._update_board(move)
        return self
    
class GameObserver(SceneObserver):
    def __init__(self, game_scene : Scene) -> None:
        super().__init__(game_scene)
        
    def update_board_signal(self, parent : GameScene) -> object:
        return self
    
    def game_end_signal(self, game_scene : GameScene) -> object:
        return self

class PlayerComponent(ButtonObserver):
    def __init__(self, parent : GameScene) -> None:
        """ 
        Class that encapsulates all interactions with player inputs and events for easier access by game scenes
        Intializes objects and properties that will be used as inputs like time delay and button inputs used for promotion
        """
        self.parent : GameScene = parent
        
        self.promotion_input : list[Button] = None
        self.promote_to : Enum = None
        
        self.DRAG_DELAY : float = 0.5
        self.mouse_held_position : Vector = None
        self.drag_start_time : float = None
        self.selected_tile : Vector = None
    
    def press_signal(self, button: Button) -> object:
        """ Assigns which piece to promote to when moving a pawn to promotion rank, for either player """
        self.promote_to = BitBoard.piece[self.promotion_input[button]]
        return self
    
    def make_move_if_legal(self, to_vector : Vector, legal_moves : dict) -> object:
        """ Extracts and verifies whether a move is legal or not """
        from_index = (7 - self.selected_tile.y) * 8 + (self.selected_tile.x)
        to_index = (7 - to_vector.y) * 8 + (to_vector.x)
        self.selected_tile = None
        try:
            move_piece, move_colour = self.parent.bitboard.index_to_piece_key(from_index)
        except:
            return self
        """ Constructs the move and identifies whether the move is a promotion and handles approriately """
        move = ((move_piece, move_colour), from_index, to_index)
        
        if from_index in legal_moves.keys() and (to_index in legal_moves[from_index] if \
            type(legal_moves[from_index][0]) is int else [l_move[0] for l_move in legal_moves[from_index]]):
            if type(legal_moves[from_index][0]) is tuple: 
                self.promotion_input = {Button(100, 100, 30, text=t) : t for t in ["BISHOP", "KNIGHT", "ROOK", "QUEEN"]}
                for ind, button in enumerate(self.promotion_input.keys()):
                    button.observers.append(self)
                    self.parent.add_overlay(button, Vector(self.parent.local_point.x+(100*ind), self.parent.local_point.y+(self.parent.dimensions.y//2)))
                """ If promote selection is completed then reset the promotion picking buttons and make the move that involves the promotion """
                if self.promote_to:
                    move = ((move_piece, move_colour), from_index, (to_index, (self.promote_to, move_colour)))
                    self.parent.make_move(move)
                    self.promote_input = self.promote_to = None
                    self.parent.reset_overlay()
            else: self.parent.make_move(move)
        return self
        
    def click_event(self, event:pygame.event.Event, legal_moves:dict) -> object:
        """ Handles when the user clicks on a game scene """
        match event.button:
            case 1:
                """ If the user has not yet selected a piece: select the tile that they just clicked on, else check and make the move
                with the to tile that was just clicked on"""
                self.mouse_held_position = Vector(*event.pos)
                if self.parent.vector_in_local_area(self.mouse_held_position):
                    if self.selected_tile:
                        self.make_move_if_legal(self.mouse_held_position // (self.parent.dimensions // 8), legal_moves)
                    else:
                        self.selected_tile = self.mouse_held_position // (self.parent.dimensions // 8)
                        self.drag_start_time = time()
            case 3:
                """ Right click deselects current piece """
                self.selected_tile = None
        return self
                
    def release_event(self, event:pygame.event.Event, legal_moves:dict) -> object:
        """ If dragging a piece check for delay time and call make move is legal much like clicking on a finish tile for the click
        event """
        match event.button:
            case 1:
                self.mouse_held_position = None
                mouse_vector = Vector(*event.pos)
                if self.parent.vector_in_local_area(mouse_vector) and self.drag_start_time:
                    if (time() - self.drag_start_time) > self.DRAG_DELAY:
                        if self.selected_tile:
                            self.make_move_if_legal(mouse_vector // (self.parent.dimensions // 8), legal_moves)
        return self
                            
    def mouse_motion_event(self, event:pygame.event.Event) -> object:
        """ Move the sprite of the piece for draw board with selection function with the mouse if dragging """
        if self.selected_tile and self.mouse_held_position:
            self.mouse_held_position.x, self.mouse_held_position.y = event.pos
        return self

    def draw_board_with_selection(self, window:pygame.surface.Surface, legal_moves:dict, object_colour:dict) -> object:
        """
        Firstly, to draw the board while displaying the legal moves and currently selected tile, the legal moves indexes are taken from the dict
        and converted into xy-plane vectors if there are legal moves for said piece or tile
        """
        tilesize = self.parent.dimensions // 8
        if self.selected_tile and self.parent.vector_to_index(self.selected_tile) in legal_moves.keys():
            legal_move_vectors = [self.parent.index_to_vector(index) if type(index) is int else \
                self.parent.index_to_vector(index[0]) for index in legal_moves[self.parent.vector_to_index(self.selected_tile)]]
        else: legal_move_vectors = []
        
        """
        Then we iterate through each vector position on the xy-plane (column, row) and check 2 conditions that outline what should be drawn:
            - Is the selected tile in the legal move vectors, then render possible move tile 
            - Else render the background colour as either black or white depending on whether the vector is even or odd 
            - Does the current tile contain a piece:
                - If yes, then is it the selected piece and is the selection being dragged; if not render it like usual (below)
                - Else, render the piece centered on the tile that has been draw
            - Lastly, if a piece is being dragged over the board then render the piece centered on the mouse on top
            """
        selected_piece_drag_position = selected_notation = None
        for r_index, row in enumerate(self.parent.notation_board):
            for c_index, notation in enumerate(row):
                
                tile_rect = pygame.Rect(c_index * tilesize.x, r_index * tilesize.y, tilesize.x, tilesize.y)
                if (c_index, r_index) in [(vector.x, vector.y) for vector in legal_move_vectors]:
                    pygame.draw.rect(window, object_colour["POSSIBLE_MOVE"], tile_rect)
                elif (c_index + r_index) % 2 == 1: pygame.draw.rect(window, object_colour["LIGHT"], tile_rect)
                else: pygame.draw.rect(window, object_colour["DARK"], tile_rect)
                
                if self.selected_tile and (c_index, r_index) == (self.selected_tile.x, self.selected_tile.y):
                    pygame.draw.rect(window, object_colour["SELECT"], tile_rect)
                    if notation != ".":
                        if self.mouse_held_position and self.parent.vector_in_local_area(self.mouse_held_position):
                            selected_piece_drag_position = (self.mouse_held_position.x - ((self.parent.dimensions.x // 8) // 2), \
                                self.mouse_held_position.y - ((self.parent.dimensions.y // 8) // 2))
                            selected_notation = notation
                        else:
                            window.blit(self.parent.notation_to_image[notation], (c_index * (self.parent.dimensions.x // 8), \
                                r_index * (self.parent.dimensions.y // 8)))
                elif notation != ".":
                    window.blit(self.parent.notation_to_image[notation], (c_index * (self.parent.dimensions.x // 8), r_index * \
                        (self.parent.dimensions.y // 8)))
                    
        if selected_notation and selected_piece_drag_position:
            window.blit(self.parent.notation_to_image[selected_notation], selected_piece_drag_position) 
        return self
        
class EvaluationComponent():
    def __init__(self, parent : GameScene, auto_start:bool=False) -> None:
        """
        Class encapsulates how each game scene handles engine evaluation by using the threading module that allows 2 threads to be ran cocurrently
        with the main game loop and updated via properites and functions listed below to access evaluation of the board
        """
        self.bitboard = parent.bitboard
        self.current_turn = parent.current_turn
        self.played = False
        
        self.current_thread_depth = lambda : self.__evaluation_threads[-1].engine.current_highest_depth
        self.update_queue = Queue()
        self.__update_move = None
        self.auto_start = auto_start
        self.__evaluation_threads = [EvaluationThread(self, daemon=True)]
        self.__evaluation_threads[-1].start()
        
    def stop_thread(self) -> None:
        self.__evaluation_threads[-1].stop = True
        self.update_thread(None)

    def update_thread(self, move:tuple) -> object:
        """ Updates the thread when a move is applied by sending a halt request (setting evaluation time to 0) and once ended the thread will stop and
        a new thread will be created with the updated board, as these events can occur at inconsistent times, a queue system is used to stack requests
        if the user inputs many moves at a time """
        if self.__update_move:
            self.update_queue.push(move)
            self.__evaluation_threads[-1].engine.max_time = 0
            return self
        self.__update_move = move
        self.__evaluation_threads[-1].engine.max_time = 0
        return self

    def create_new_thread(self, move_evaluation:dict=[]) -> object:
        """ Called at the end of the thread that is halted and creates a thread with an updated board, if the update thread was used the latest 
        item on the queue is poped as it has finished its request """
        move_evaluation = move_evaluation[self.__update_move] if move_evaluation and self.__update_move in move_evaluation.keys() \
            and type(move_evaluation[self.__update_move]) is dict else {}
            
        self.__evaluation_threads.append(EvaluationThread(self, move_evaluation, self.current_turn[0], daemon=True))
        self.__evaluation_threads[-1].start()
        self.played = False
        self.__update_move = None
        if self.update_queue.has_values:
            self.update_thread(self.update_queue.pop())
        return self
            
    def best_moves(self) -> list:
        """ Fetches the best moves from the engine thread while its running using properties """
        return self.__evaluation_threads[-1].engine.find_ordered_move_eval(self.__evaluation_threads[-1].engine.move_evaluation.copy()) \
            if self.__evaluation_threads[-1].engine.move_evaluation else []
    
class EvaluationThread(Thread):
    def __init__(self, evaluation_component : EvaluationComponent, move_evaluation : dict = None, current_colour = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        """ Thread itself that runs the evaluation function of a engine by storing a copy of the static bitboard, used at the beginning and 
        an engine attached to a deepcopy (entirely seperate object pointer with same properties) that is used by the engine to simulate the game """
        self.stop = False
        self.parent = evaluation_component
        self.static_bitboard = self.parent.bitboard
        self.engine = Engine(deepcopy(self.static_bitboard))
        self.__move_evaluation = move_evaluation
        self.__current_colour = current_colour
        
    def run(self) -> None:
        """ Runs the evaluation function of the engine until otherwise halted then which it updates the board and move evaluation so it does not
        loses its current process of evaluation """
        self.engine.max_time = 0 if self.parent.auto_start else inf 
        self.parent.auto_start = False
        self.engine.min_max_dict(current_colour=self.__current_colour, move_evaluation=self.__move_evaluation)
        if not(self.stop): self.parent.create_new_thread(self.engine.move_evaluation)
            
class PlayerVsPlayer(GameScene):
    def __init__(self, width:int=800, height:int=800, bitboard:BitBoard=None) -> None:
        super().__init__(width, height, bitboard)
        """ Intializes with player and engine componenet for evlauation bar and user inputs
        and split lambda function so each player can see the correct legal moves """
        self.evaluation_component = EvaluationComponent(self, auto_start=True)
        self.player_componenet = PlayerComponent(self)
        self._player_legal_move = lambda bitboard: bitboard.split_move_dict[self.current_turn[0]][0]
        
    def while_event(self, event:pygame.event.Event) -> object:
        """ Sends events to approriate components or handles simply events like resizing and reverting a move """
        match event.type:
            case pygame.VIDEORESIZE:
                self.resize(event.h, event.w)
            case pygame.MOUSEBUTTONDOWN:
                self.player_componenet.click_event(event, self._legal_moves)
            case pygame.MOUSEBUTTONUP:
                self.player_componenet.release_event(event, self._legal_moves)
            case pygame.MOUSEMOTION:
                self.player_componenet.mouse_motion_event(event)
            case pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.switch_colour(self.current_turn)
                    self._update_board(u_type=GameScene._update_type["REVERT"])
        return Scene.while_event(self, event)
    
    def draw(self, window:pygame.surface.Surface) -> object:
        """ Draws regular board if no selected tile or selection board from player component """
        if self.player_componenet.selected_tile:
            self.player_componenet.draw_board_with_selection(window, self._legal_moves, self._object_colour)
            return Scene.draw(self, window)
        return GameScene.draw(self, window)
    
    def make_move(self, move:tuple) -> object:
        """ Updates base make move to switch colour and update evaluation thread """
        self.switch_colour(self.current_turn)
        self._update_board(move)
        self.evaluation_component.update_thread(move)
        return self

class PlayerVsComputer(GameScene):
    def __init__(self, width:int=800, height:int=800, bitboard:BitBoard=None) -> None:
        super().__init__(width, height, bitboard)
        """ Intializes with player and engine componenet for evlauation bar and user inputs,
        and split lambda function so the player can see the correct legal moves"""
        self.evaluation_component = EvaluationComponent(self, auto_start=True)
        self.player_componenet = PlayerComponent(self)
        self.player_colour = BitBoard.colour.WHITE
        self.computer_colour = BitBoard.colour.BLACK
        self._player_legal_move = lambda bitboard: bitboard.split_move_dict[self.current_turn[0]][0] if self.current_turn[0] == self.player_colour else {}

    def while_update(self) -> object:
        """ Fectches the best move from the evaluation component and if present and its the computer's moves applies said move """
        best_move = self.evaluation_component.best_moves()
        if self.computer_colour == self.current_turn[0] and best_move and \
            self.evaluation_component.current_thread_depth() > 0 and not(self.evaluation_component.played):
            self.make_move(best_move[-1][0] if self.computer_colour == BitBoard.colour.BLACK else best_move[0][0])
            self.evaluation_component.played = True
        return Scene.while_update(self)
        
    def while_event(self, event:pygame.event.Event) -> object:
        """ Sends events to approriate components or handles simply events like resizing """
        match event.type:
            case pygame.VIDEORESIZE:
                self.resize(event.h, event.w)
            case pygame.MOUSEBUTTONDOWN:
                self.player_componenet.click_event(event, self._legal_moves)
            case pygame.MOUSEBUTTONUP:
                self.player_componenet.release_event(event, self._legal_moves)
            case pygame.MOUSEMOTION:
                self.player_componenet.mouse_motion_event(event)
        return Scene.while_event(self, event)
    
    def draw(self, window:pygame.surface.Surface) -> object:
        """ Draws regular board if no selected tile or selection board from player component """
        if self.player_componenet.selected_tile:
            self.player_componenet.draw_board_with_selection(window, self._legal_moves, self._object_colour)
            return Scene.draw(self, window)
        return GameScene.draw(self, window)

    def make_move(self, move:tuple) -> object:
        """ Updates base make move to switch colour and update evaluation thread """
        self.switch_colour(self.current_turn)
        self._update_board(move)
        self.evaluation_component.update_thread(move)
        return self
    
class ComputerVsComputer(GameScene):
    def __init__(self, width:int=800, height:int=800, bitboard:BitBoard=None) -> None:
        """ Initalizes evaluation component needed for computer """
        super().__init__(width, height, bitboard)
        self.evaluation_component = EvaluationComponent(self, auto_start=True)
    
    def while_update(self) -> object:
        """ Fectches the best move from the evaluation component and if present and applies said move """
        best_move = self.evaluation_component.best_moves()
        if best_move and self.evaluation_component.current_thread_depth() > 0 and not(self.evaluation_component.played):
            self.make_move(best_move[-1][0] if self.current_turn[0] == BitBoard.colour.BLACK else best_move[0][0])
            self.evaluation_component.played = True
        return Scene.while_update(self)
    
    def while_event(self, event:pygame.event.Event) -> object:
        """ Listens for resive event """
        match event.type:
            case pygame.VIDEORESIZE:
                self.resize(event.h, event.w)
        return Scene.while_event(self, event)
    
    def draw(self, window:pygame.surface.Surface) -> object:
        return GameScene.draw(self, window)
    
    def make_move(self, move:tuple) -> object:
        """ Updates base make move to switch colour and update evaluation thread """
        self.switch_colour(self.current_turn)
        self._update_board(move)
        self.evaluation_component.update_thread(move)
        return self
        
class EvaluationBar(GameObserver, Scene):
    def __init__(self, game_scene : GameScene, width:int=50, height:int=0) -> None:
        GameObserver.__init__(self, game_scene)
        Scene.__init__(self, width, height)
        """ Adds parent and sets dimension property to its parent's class y dimension so its scaled approriately """
        self.parent : GameScene = game_scene
        self.dimensions.y = game_scene.dimensions.y
        
        self.TEXT_FONT : pygame.font.Font = pygame.font.Font("freesansbold.ttf", self.dimensions.x * 2 // 3)
        
    def resize_signal(self, parent: GameScene) -> object:
        """ Keeps scale consistent """
        self.dimensions.y = parent.dimensions.y
        return self

    def draw(self, window:pygame.surface.Surface) -> object:
        """ Draws evaluation by scaling a black bar and white bar that represent the advanatage of the best currrent move for each the player"""
        Scene.draw(self, window)
        evaluation = self.parent.evaluation_component.best_moves()
        if evaluation:
            number_eval = evaluation[0][1]
            advantage_scale = 0.5 - (number_eval / 10000) 
            pygame.draw.rect(window, (255,255,255), pygame.Rect(self.local_point.x, self.local_point.y + self.dimensions.y * advantage_scale,\
                self.dimensions.x, self.dimensions.y))
            
            text = self.TEXT_FONT.render(str(round(advantage_scale * 10, 1)), True, (255,255,255))
            text_rect = text.get_rect()
            text_rect.x, text_rect.y = self.local_point.x, self.local_point.y
            window.blit(text, text_rect)
        return self
            

"""
Notes: 
Further development:
    -> Promotion and UI is overall very janky
    -> The engine is utter trash and very, very slow (the engine evlauation function may be bugged
    -> Create a seperate thread for drawing, events and updates depending on the type of action to decouple checks
"""