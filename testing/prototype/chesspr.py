import pygame
class PyGameWindow:
    def __init__(self, window_size, caption):
        self.window_size = window_size
        self.window = pygame.display.set_mode(window_size)
        self.caption = caption
        self.running = True
    def whileEvent(self, events):
        pass
    def whileDrawing(self):
        pass
    def run(self):
        while self.running:
            events = pygame.event.get()
            self.whileEvent(events)
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.whileDrawing()
            pygame.display.flip()
        pygame.quit()
        
class Interface(PyGameWindow):
    def __init__(self, window_size, caption):
        super().__init__(window_size, caption)

class ChessBoard(Interface):
    def __init__(self, window_size, caption, tile_size):
        super().__init__(window_size, caption)
        (self.columnsize, self.rowsize) = tile_size
        self.selectedPeice = ((-1,-1), "__")
        self.previousMoveTo = (-1,-1)
        self.castlePeiceTile = [(0,0),(0,7),(7,0),(7,7),(0,4),(7,4)]
        self.kingTile = {
            "WKing" : (7,3),
            "DKing" : (0,3)
        }
        self.turnCount = 0
        self.board = [
            ["rd", "nd", "bd", "kd", "qd", "bd", "nd", "rd"],
            ["pd", "pd", "pd", "pd", "pd", "pd", "pd", "pd"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["__", "__", "__", "__", "__", "__", "__", "__"],
            ["pw", "pw", "pw", "pw", "pw", "pw", "pw", "pw"],
            ["rw", "nw", "bw", "kw", "qw", "bw", "nw", "rw"]
            ]
        self.peiceImage = {
            "WPawn": pygame.image.load("Chess Piece Image/Chess_plt45.svg").convert_alpha(),
            "WRook": pygame.image.load("Chess Piece Image/Chess_rlt45.svg").convert_alpha(),
            "WBishop": pygame.image.load("Chess Piece Image/Chess_blt45.svg").convert_alpha(),
            "WKnight": pygame.image.load("Chess Piece Image/Chess_nlt45.svg").convert_alpha(),
            "WQueen": pygame.image.load("Chess Piece Image/Chess_qlt45.svg").convert_alpha(),
            "WKing": pygame.image.load("Chess Piece Image/Chess_klt45.svg").convert_alpha(),
            "DPawn": pygame.image.load("Chess Piece Image/Chess_pdt45.svg").convert_alpha(),
            "DRook": pygame.image.load("Chess Piece Image/Chess_rdt45.svg").convert_alpha(),
            "DBishop": pygame.image.load("Chess Piece Image/Chess_bdt45.svg").convert_alpha(),
            "DKnight": pygame.image.load("Chess Piece Image/Chess_ndt45.svg").convert_alpha(),
            "DQueen": pygame.image.load("Chess Piece Image/Chess_qdt45.svg").convert_alpha(),
            "DKing": pygame.image.load("Chess Piece Image/Chess_kdt45.svg").convert_alpha()
        }
        
        for key in self.peiceImage:
            self.peiceImage[key] = pygame.transform.scale(self.peiceImage[key], (self.columnsize, self.rowsize))
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                match self.board[row][column]:
                    case "pd":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["DPawn"])
                    case "bd":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["DBishop"])
                    case "nd":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["DKnight"])
                    case "rd":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["DRook"])
                    case "qd":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["DQueen"])
                    case "kd":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["DKing"])
                    case "pw":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["WPawn"])
                    case "bw":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["WBishop"])
                    case "nw":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["WKnight"])
                    case "rw":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["WRook"])
                    case "qw":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["WQueen"])
                    case "kw":
                        self.board[row][column] = (self.board[row][column], self.peiceImage["WKing"])
    
    def promote(self, coordinate):
        (coordiantey, coordinatex) = coordinate
        (notation, image) = self.board[coordiantey][coordinatex]
        notation = str(input("Please enter what you want to promote to with the piece first and the colour next in notation: "))
        self.board[coordiantey][coordinatex] = (notation, image)
        
    def checkKingSafe(self, coordinate, otherColour):
        (coordinatey, coordinatex) = coordinate
        tileToSouthEdge = abs(coordinatey - len(self.board[0]))
        tileToEastEdge = abs(coordinatex - len(self.board))
        tileToUpLeft = min([coordinatex, coordinatey])
        tileToUpRight = min([tileToEastEdge, coordinatey])
        tileToDownLeft =  min([coordinatex, tileToSouthEdge])
        tileToDownRight = min([tileToEastEdge, tileToSouthEdge])
        for (maxIndex, (indexYModifier, indexXModifier)) in [(coordinatex+1, (0,-1)), (coordinatey+1, (-1,0)), (tileToEastEdge, (0,1)), (tileToSouthEdge, (1,0)), (tileToUpLeft, (-1,-1)), (tileToDownLeft, (1,-1)), (tileToDownRight, (1,1)), (tileToUpRight, (-1,1))]:
            for index in range(1, maxIndex):
                (notation, image) = self.board[coordinatey+(index*indexYModifier)][coordinatex+(index*indexXModifier)]
                if otherColour in notation and ("r" in notation or "q" in notation) and (indexXModifier == 0 or indexYModifier == 0):
                    return False
                if otherColour in notation and ("b" in notation or "q" in notation or ("p" in notation and index == 1)) and (abs(indexYModifier) == abs(indexXModifier)):
                    return False
                elif notation == "_" or (not(otherColour in notation) and "k" in notation):
                    pass
                else: break
        for x in range(-2, 3):
            for y in range(-2, 3):
                if -1 < coordinatey+y < 8 and -1 < coordinatex+x < 8 and abs(x)+abs(y) == 3:
                    (notation, image) = self.board[coordinatey+y][coordinatex+x]
                    if otherColour in notation and "n" in notation:
                        return False
        return True
    
    def updateKingTile(self, position, ownColour):
        if ownColour == "w":
            self.kingTile["WKing"] = position
        else:
            self.kingTile["DKing"] = position
            
    def checkCollide(self, start, end):
        (starty, startx) = start
        (endy, endx) = end
        tileIndexModifier = 1
        if starty == endy:
            numberOfTiles = abs(startx - endx) - 1
            if startx > endx:
                tileIndexModifier = -1
            for tileIndex in range(1, numberOfTiles+1):
                if self.board[starty][startx+(tileIndex*tileIndexModifier)] != "__":
                    return True
        elif startx == endx:
            numberOfTiles = abs(starty - endy) - 1
            if starty > endy:
                tileIndexModifier = -1
            for tileIndex in range(1, numberOfTiles+1):
                    if self.board[starty+(tileIndex*tileIndexModifier)][startx] != "__":
                        return True
        else:
            moveDifferencey = starty - endy
            moveDifferencex = startx - endx
            numberOfTiles = abs(moveDifferencey) - 1
            tileIndexXModifier = 1
            tileIndexYModifier = 1
            if moveDifferencey > 0:
                tileIndexYModifier = -1
            if moveDifferencex > 0:
                tileIndexXModifier = -1
            for tileIndex in range(1, numberOfTiles+1):
                if self.board[starty+(tileIndex*tileIndexYModifier)][startx+(tileIndex*tileIndexXModifier)] != "__":
                    return True
        return False       
    
    def checkValidMove(self, selectedPeice, moveCoordinate):
        ((peiceCoordinatey, peiceCoordinatex), peice) = selectedPeice
        (moveCoordinatey, moveCoordinatex) = moveCoordinate
        (notation, image) = peice
        moveDifferencey = moveCoordinatey - peiceCoordinatey
        moveDifferencex = moveCoordinatex - peiceCoordinatex
        totalMoveDifference = abs(moveDifferencex) + abs(moveDifferencey)
        onPeice = False
        if self.board[moveCoordinatey][moveCoordinatex] != "__":
            onPeice = True
        (attackedPeiceNotation, image) = self.board[moveCoordinatey][moveCoordinatex]
        attackingOwnPeice = False
        if ("w" in notation and "w" in attackedPeiceNotation) or ("d" in notation and "d" in attackedPeiceNotation):
            attackingOwnPeice = True
        if ("n" in notation):
            collide = False
        else:
            collide = self.checkCollide((peiceCoordinatey, peiceCoordinatex), moveCoordinate)
            
        if not (collide or attackingOwnPeice):
            match notation:
                case str(type) if "p" in type:
                    distance = 1
                    if (notation == "pw") and peiceCoordinatey > moveCoordinatey:
                        if (peiceCoordinatey == 6):
                            distance = 2
                        if ((moveCoordinatex == peiceCoordinatex) and (moveCoordinatey + distance >= peiceCoordinatey > moveCoordinatey) and not onPeice):
                            return True
                        elif (totalMoveDifference / 2 == 1) and totalMoveDifference > 0 and not (moveCoordinatey == peiceCoordinatey or moveCoordinatex == peiceCoordinatex):
                            if self.board[moveCoordinatey+1][moveCoordinatex] != "__":
                                (pawnNotation, image) = self.board[moveCoordinatey+1][moveCoordinatex]
                            else:
                                pawnNotation = "__"
                            if (moveCoordinatey == 2 and pawnNotation == "pd" and self.previousMoveTo == (moveCoordinatey+1, moveCoordinatex)):
                                self.board[moveCoordinatey+1][moveCoordinatex] = "__"
                                return True
                            elif onPeice:
                                return True
                    elif (notation == "pd") and peiceCoordinatey < moveCoordinatey:
                        if (peiceCoordinatey == 1):
                            distance = 2
                        if ((moveCoordinatex == peiceCoordinatex) and (moveCoordinatey - distance <= peiceCoordinatey < moveCoordinatey) and not onPeice):
                            return True
                        elif (totalMoveDifference / 2 == 1) and totalMoveDifference > 0 and not (moveCoordinatey == peiceCoordinatey or moveCoordinatex == peiceCoordinatex):
                            if self.board[moveCoordinatey-1][moveCoordinatex] != "__":
                                (pawnNotation, image) = self.board[moveCoordinatey-1][moveCoordinatex]
                            else:
                                pawnNotation = "__"
                            if (moveCoordinatey == 5 and pawnNotation == "pw" and self.previousMoveTo == (moveCoordinatey-1, moveCoordinatex)):
                                self.board[moveCoordinatey-1][moveCoordinatex] = "__"
                                return True
                            elif onPeice:
                                return True
                case str(type) if "b" in type:
                    tileMoved = totalMoveDifference // 2
                    if totalMoveDifference % 2 == 0 and (peiceCoordinatey + tileMoved == moveCoordinatey or peiceCoordinatey - tileMoved == moveCoordinatey) and (peiceCoordinatex + tileMoved == moveCoordinatex or peiceCoordinatex - tileMoved == moveCoordinatex):
                        return True
                case str(type) if "n" in type:
                    if (moveDifferencex / 2 == 1 or moveDifferencex / 2 == -1) and (moveCoordinatey + 1 == peiceCoordinatey or moveCoordinatey - 1 == peiceCoordinatey):
                        return True
                    elif (moveDifferencey / 2 == 1 or moveDifferencey / 2 == -1) and (moveCoordinatex + 1 == peiceCoordinatex or moveCoordinatex - 1 == peiceCoordinatex):
                        return True
                case str(type) if "r" in type:
                    if peiceCoordinatex == moveCoordinatex or peiceCoordinatey == moveCoordinatey:
                        return True
                case str(type) if "q" in type:
                    tileMoved = totalMoveDifference // 2
                    if peiceCoordinatex == moveCoordinatex or peiceCoordinatey == moveCoordinatey:
                        return True
                    elif totalMoveDifference % 2 == 0 and (peiceCoordinatey + tileMoved == moveCoordinatey or peiceCoordinatey - tileMoved == moveCoordinatey) and (peiceCoordinatex + tileMoved == moveCoordinatex or peiceCoordinatex - tileMoved == moveCoordinatex):
                        return True
                case str(type) if "k" in type:
                    if "d" in notation:
                        otherColour = "w"
                        ownColour = "d"
                    else:
                        otherColour = "d"
                        ownColour = "w"
                    if self.checkKingSafe((moveCoordinatey, moveCoordinatex), otherColour):
                        tileMoved = totalMoveDifference / 2
                        if tileMoved == 1:
                            if totalMoveDifference % 2 == 0 and (peiceCoordinatey + tileMoved == moveCoordinatey or peiceCoordinatey - tileMoved == moveCoordinatey) and (peiceCoordinatex + tileMoved == moveCoordinatex or peiceCoordinatex - tileMoved == moveCoordinatex):
                                return True
                            elif ((peiceCoordinatey, peiceCoordinatex) in self.castlePeiceTile) and peiceCoordinatey == moveCoordinatey:
                                if (peiceCoordinatex + 2 == moveCoordinatex and (peiceCoordinatey, 7) in self.castlePeiceTile) and not self.checkCollide((peiceCoordinatey, peiceCoordinatex), (peiceCoordinatey, 7)):
                                    self.board[peiceCoordinatey][peiceCoordinatex+1] = self.board[peiceCoordinatey][7]
                                    self.board[peiceCoordinatey][7] = "__"
                                    return True
                                elif (peiceCoordinatex - 2 == moveCoordinatex and (peiceCoordinatey, 0) in self.castlePeiceTile) and not self.checkCollide((peiceCoordinatey, peiceCoordinatex), (peiceCoordinatey, 0)):
                                    self.board[peiceCoordinatey][peiceCoordinatex-1] = self.board[peiceCoordinatey][0]
                                    self.board[peiceCoordinatey][0] = "__"
                                    return True
                        elif (peiceCoordinatex == moveCoordinatex or peiceCoordinatey == moveCoordinatey) and tileMoved == 0.5:
                                return True
                case _:
                    print("couldn't find peice type")
                    return False
        return False
            
    def whileDrawing(self):
        Interface.whileDrawing(self)
        self.drawBackground(self.window)
        self.drawPeice(self.window)
        
    def whileEvent(self, events):
        Interface.whileEvent(self, events)
        if self.selectedPeice == ((-1,-1), "__"):
            self.eventSelect(events)
        else:
            self.eventMovePeice(events)
            
    def eventSelect(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                (mousePositionx, mousePositiony) = pygame.mouse.get_pos()
                mouseCoordinatex = mousePositionx // self.columnsize
                mouseCoordinatey = mousePositiony // self.rowsize
                if -1 < mouseCoordinatex < len(self.board[0]) and -1 < mouseCoordinatey < len(self.board) and self.board[mouseCoordinatey][mouseCoordinatex] != "__":
                    (notation, image) = self.board[mouseCoordinatey][mouseCoordinatex]
                    if (self.turnCount % 2 == 0 and "w" in notation) or (self.turnCount % 2 == 1 and "d" in notation):
                        self.selectedPeice = ((mouseCoordinatey, mouseCoordinatex) ,self.board[mouseCoordinatey][mouseCoordinatex])
                    
    def eventMovePeice(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                (mousePositionx, mousePositiony) = pygame.mouse.get_pos()
                mouseCoordinatex = mousePositionx // self.columnsize
                mouseCoordinatey = mousePositiony // self.rowsize
                if -1 < mouseCoordinatex < len(self.board[0]) and -1 < mouseCoordinatey < len(self.board):
                    if self.checkValidMove(self.selectedPeice, (mouseCoordinatey, mouseCoordinatex)):
                        ((peiceCoordinatey, peiceCoordinatex), peice) = self.selectedPeice
                        peiceOnMovedTile = self.board[peiceCoordinatey][peiceCoordinatex]
                        (notation, image) = peice
                        self.board[mouseCoordinatey][mouseCoordinatex] = peice
                        self.board[peiceCoordinatey][peiceCoordinatex] = "__"
                        if ((not(self.checkKingSafe(self.kingTile["DKing"], "w")) and self.turnCount % 2 == 1) or (not(self.checkKingSafe(self.kingTile["WKing"], "d")) and self.turnCount % 2 == 0)) and not("k" in notation):
                            self.board[mouseCoordinatey][mouseCoordinatex] = "__"
                            self.board[peiceCoordinatey][peiceCoordinatex] = peiceOnMovedTile
                        else:
                            if "k" in notation:
                                if "w" in notation:
                                    self.updateKingTile((mouseCoordinatey, mouseCoordinatex), "w")
                                else:
                                    self.updateKingTile((mouseCoordinatey, mouseCoordinatex), "d")
                            if "pw" == notation and mouseCoordinatey == 0 or ("pd" == notation and mouseCoordinatey == 7):
                                self.promote((mouseCoordinatey, mouseCoordinatex))
                            if (peiceCoordinatey, peiceCoordinatex) in self.castlePeiceTile:
                                self.castlePeiceTile.remove((peiceCoordinatey, peiceCoordinatex))
                            self.previousMoveTo = (mouseCoordinatey, mouseCoordinatex)
                            self.turnCount += 1
                    self.selectedPeice = ((-1,-1), "__")
                        
    def drawBackground(self, window):
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                if (column + row) % 2 == 0:
                    pygame.draw.rect(window, (50,100,0), (column * self.columnsize, row * self.rowsize, self.columnsize, self.rowsize))
                else:
                    pygame.draw.rect(window, (255,255,150), (column * self.columnsize, row * self.rowsize, self.columnsize, self.rowsize))
    
    def drawPeice(self, window):
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                if self.board[row][column] != "__":
                    (notation, image) = self.board[row][column]
                    window.blit(image, (column * self.columnsize, row * self.rowsize))

if __name__ == "__main__":
    chess_window = ChessBoard((800,800), "chess", (100,100))
    chess_window.run()