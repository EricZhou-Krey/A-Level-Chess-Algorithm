import pygame, sys
sys.path.append("../A-Level-Chess-Algorithm")
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

class PlayerVsComputer(Scene):
    def __init__(self, width, height, input_engine=None, input_bitboard=None):
        super().__init__(width, height)
        
        """
        Piece images are loaded, resized and stored in a dictionary with their associated display notation used by the notation board
        """
        
        self.__updated_display_image = lambda self, image : pygame.transform.scale(image, (self.dimensions.x // 8, self.dimensions.y // 8))
        self.notation_to_image = {name:self.__updated_display_image(self, image) for name, image in \
        zip(['p', 'r', 'b', 'n', 'q', 'k', 'P', 'R', 'B', 'N', 'Q', 'K'], \
            
        [pygame.image.load("Chess Piece Image/Chess_" + image_reference + ".svg").convert_alpha() for image_reference in \
        ["plt45", "rlt45", "blt45", "nlt45", "qlt45", "klt45", "pdt45", "rdt45", "bdt45", "ndt45", "qdt45", "kdt45"]])}
        
        """
        After loading files needed for the scene, input parameters are handled by linking or creating a new bitboard and engine
        class with this instance of the PlayerVsComputer scene
        """
        
        if not(input_bitboard or input_engine):
            board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
            self.bitboard = BitBoard(board)
            self.engine = Engine(self.bitboard)
        else:
            self.bitboard = input_bitboard
            self.engine = input_engine
        
        """
        Then the notation board is extracted from the newly linked bitboard and formatted into a list with correct notation
        to refer to the images loaded previously
        """
            
        self.__updated_display_board = lambda self : [row[:15].split(" ") for row in self.bitboard.board_formatted[:141].split("\n")[:9]]
        self.notation_board = self.__updated_display_board(self)
        
        """
        Values used in subroutines
        """
        
        self.__selected_tile = None
        
        """
        GUI colours for different features of the scene
        """
        
        self.__light_tile_colour = (50,100,50)
        self.__dark_tile_colour = (255,255,150)
        self.__select_colour = (100,100,255)
        
    def while_event(self, event):
        def resize_event():
            self.dimensions.x = self.dimensions.y = min(event.h, event.w)
            for key, image in self.notation_to_image.items(): self.notation_to_image[key] = self.__updated_display_image(self, image)
        
        def click_event():
            match event.button:
                case 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if (self.local_point.x < mouse_x < self.local_point.x + self.dimensions.x) and \
                        (self.local_point.y < mouse_y < self.local_point.y + self.dimensions.y):
                            if not self.__selected_tile:
                                self.__selected_tile = Vector(mouse_x, mouse_y) // (self.dimensions // 8)
                            else:
                                from_index = (7 - self.__selected_tile.y) * 8 + (self.__selected_tile.x)
                                to_vector = Vector(mouse_x, mouse_y) // (self.dimensions // 8)
                                to_index = (7 - to_vector.y) * 8 + (to_vector.x)
                                move = (self.bitboard.index_to_piece_key(from_index), from_index, to_index)
                                legal_moves = self.bitboard.legal_move_dict[0]
                                if move[1] in legal_moves.keys():
                                    if move[2] in legal_moves[move[1]]:
                                        self.bitboard.apply_move(move)
                                        self.notation_board = self.__updated_display_board(self)
                                        self.__selected_tile = None
                case 3:
                    self.__selected_tile = None
        
        match event.type:
            case pygame.VIDEORESIZE:
                resize_event()
            case pygame.MOUSEBUTTONDOWN:
                click_event()
                
    def draw(self, window):
        def draw_board():
            tilesize = self.dimensions // 8
            for r_index, row in enumerate(self.notation_board):
                for c_index, notation in enumerate(row):
                    
                    tile_rect = pygame.Rect(c_index * tilesize.x, r_index * tilesize.y, tilesize.x, tilesize.y)
                    if self.__selected_tile:
                        if c_index == self.__selected_tile.x and r_index == self.__selected_tile.y: pygame.draw.rect(window, self.__select_colour, tile_rect)
                    elif (c_index + r_index) % 2 == 0: pygame.draw.rect(window, self.__light_tile_colour, tile_rect)
                    else: pygame.draw.rect(window, self.__dark_tile_colour, tile_rect)
                    
                    if notation != ".":
                        window.blit(self.notation_to_image[notation], (c_index * (self.dimensions.x // 8), r_index * (self.dimensions.y // 8)))
        
        draw_board()
    
class EvaluationBar(Scene):
    def __init__(self, width, height, engine):
        super().__init__(width, height)
        self.engine = engine
        self.__current_move_eval = None
        self.__current_move = None
    
    def draw(self, window):
        pass