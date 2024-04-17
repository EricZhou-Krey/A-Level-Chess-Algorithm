import sys, mysql.connector, pygame, socket
from threading import Thread
from random import choice
from json import dumps, loads
from re import compile
from bcrypt import gensalt, hashpw
from time import strftime
from mysql.connector.cursor import CursorBase
from mysql.connector.connection import MySQLConnection
sys.path.append("../A-Level-Chess-Algorithm")
from bitboard import BitBoard
from pygame_scene.scenes.scene import Scene, SceneObserver, TextBox, TextBoxObserver, Button
from pygame_scene.scenes.game_scene import OnlinePlayerVsPlayer, PlayerVsComputer, PlayerVsPlayer, ComputerVsComputer, GameScene, GameObserver, EvaluationBar
from my_dataclass import Vector


class MenuScene(Scene, TextBoxObserver, GameObserver):
    def __init__(self, width:int=850, height:int=800, font_size:int=40, inactive_colour:tuple=(255,255,255)) -> None:
        Scene.__init__(self, width, height)
        
        """ Initaizes components relating to user information adn database searching aswell as properties that help with clarity, searching
        through buttons and overalys later and UI colouring """
        self.observers : list[MenuObserver] = []
        self.database_component : DatabaseComponent = DatabaseComponent()
        self.authentication_component : AuthenticationComponenet = AuthenticationComponenet(self.database_component)
        
        self.__font_size = font_size
        self.__font = pygame.font.Font(None, font_size)
        self.__font_color = pygame.Color(*inactive_colour)
        
        self.__current_game_id = None
        self.__text_box : list[TextBox] = []
        self.__button : list[Button] = []
        self.__display_user_information = True
        
        self.user_information = {}
        self.user_fetch = {}
        self.button_match = {}
        self.text_match = {}
        
        self.load_main_menu()
    
    def load_authentication_menu(self) -> object:
        """ Setup for login buttons and text inputs """
        confirm_button = Button(50,50)
        text_reference_name = ["LoginUsername", "LoginPassword", "SignUpUsername", "SignUpPassword", "SignUpEmail"]
        text_label = {text_reference : TextBox(400, 50, 50, writable=False, background_colour=(0,0,0), active_colour=(255,255,255), \
            inactive_colour=(255,255,255), text=text_reference) for text_reference in text_reference_name}
        self.text_match = {text_reference : TextBox(400, 50, 50) for text_reference in text_reference_name}
        self.add_overlay(text_label["LoginUsername"], Vector(0, 0))
        self.add_overlay(self.text_match["LoginUsername"], Vector(0, 50))
        self.add_overlay(text_label["LoginPassword"], Vector(0, 100))
        self.add_overlay(self.text_match["LoginPassword"], Vector(0, 150))
        self.add_overlay(confirm_button, Vector(50, 250))
        self.button_match[confirm_button] = "LoginConfirm"
        
        """ Setup for registeration and signup text inputs """
        confirm_button = Button(50, 50)
        self.add_overlay(text_label["SignUpUsername"], Vector(450, 0))
        self.add_overlay(self.text_match["SignUpUsername"], Vector(450, 50))
        self.add_overlay(text_label["SignUpPassword"], Vector(450, 100))
        self.add_overlay(self.text_match["SignUpPassword"], Vector(450, 150))
        self.add_overlay(text_label["SignUpEmail"], Vector(450, 200))
        self.add_overlay(self.text_match["SignUpEmail"], Vector(450, 250))
        self.add_overlay(confirm_button, Vector(450, 350))
        self.button_match[confirm_button] = "SignUpConfirm"
        return self
    
    def load_main_menu(self) -> object:
        """ Identifies if the database connection was sucessful, if yes then loads inputs for connection else simply display that no connection
        was established """
        if self.database_component.connection:
            if not(self.user_information):
                self.load_authentication_menu()
        else:
            self.add_overlay(TextBox(400, 50, 50, text="Database connection not secured"), Vector(200, 200))
        """ Then loads game options for the player to use the application """
        self.load_game_options()
        return self
    
    __GAME_BUTTON_SIZE = 100
    __GAME_BUTTON_SPACING = 150
    def load_game_options(self) -> object:
        """ Creates 3 buttons relating to each of the game options that can be chosen and adds buttons to overlay and dictionary to 
        reference them when they are pressed later """
        gbs = MenuScene.__GAME_BUTTON_SIZE
        game_scene_buttons = {
            Button(gbs, gbs, self.__font_size, text="PvP") : "PvP", #UI number for sizes, can be alter in further development
            Button(gbs, gbs, self.__font_size, text="PvC") : "PvC",
            Button(gbs, gbs, self.__font_size, text="CvC") : "CvC",
            Button(gbs, gbs, self.__font_size, text="OPvP") : "OPvP"
        }
        self.button_match.update(game_scene_buttons)
        for ind, button in enumerate(game_scene_buttons.keys()):
            self.add_overlay(button, Vector(ind*MenuScene.__GAME_BUTTON_SPACING, self.dimensions.y-gbs))
        return self
    
    def add_overlay(self, overlay : Scene, local_point: Vector) -> object:
        """ In addition to just appending to observers and overlay, overlays are sorted into buttons and text inputs for 
        easy referencing later """
        match overlay:
            case TextBox():
                self.__text_box.append(overlay)
            case Button():
                self.__button.append(overlay)
        overlay.observers.append(self)
        return super().add_overlay(overlay, local_point)

    def reset_overlay(self) -> object:
        """ Clears all list that are appended to when an overlay is added """
        self.__text_box.clear()
        self.text_match.clear()
        self.__button.clear()
        self.button_match.clear()
        self._overlay_scene.clear()
        return self
    
    def exit_game_scene(self, game_scene : GameScene) -> object:
        """ When exit game button is pressed or upon a checkmate, the game is saved to local save and database if a connection was established
        then main menu is loaded again for other games and if the user was already logged in then user information is displayed again """
        self.database_component.save_game(game_scene.bitboard.applied_moves, MenuScene.__game_scene_notation[type(game_scene)], \
            "name", game_id=self.__current_game_id, user_id=self.user_information["UserID"] if self.user_information else -1, engine_id=1)
        if game_scene.evaluation_component: game_scene.evaluation_component.stop_thread()
        self.reset_overlay()
        self.load_main_menu()
        if self.user_information and (user_id := self.user_information["UserID"]): self.load_user_information(user_id)
        self.__display_user_information = True
        return self
    
    def game_end_signal(self, game_scene : GameScene) -> object:
        """ Decoupled from the exit game scene function for further development as this is distinct in that this call only occurs when
        a checkmate or stalemate is achieved and not when exit game button is pressed """
        white_safe, black_safe = game_scene.bitboard.king_safe(BitBoard.colour.WHITE), game_scene.bitboard.king_safe(BitBoard.colour.BLACK)
        if white_safe and not(black_safe):
            pass
            #update elo, for white win # marker
        elif not(white_safe) and black_safe:
            pass
            #update elo, for black win # marker
        return self.exit_game_scene(game_scene)
    
    """ Converting to and from objects for json save and database entries """
    __game_scene_notation = {PlayerVsComputer : "PvC", PlayerVsPlayer : "PvP", ComputerVsComputer : "CvC", OnlinePlayerVsPlayer : "OPvP"}
    __notation_game_scene = {value : key for key, value in __game_scene_notation.items()}
    def press_signal(self, button : Button) -> object:
        def handle_text_independance():
            """ Makes sure that only one textbox is accepting inputs at a time """
            for overlay in [ov for ov in self._overlay_scene if type(ov) is TextBox]:
                if button != overlay:
                    overlay.active = False
                    overlay.color = overlay.color_inactive
        """
        Depending on buttons are pressed on the menu applies the correct events:
        - If textbox is pressed make sure its the only textbox active and accept keyboard inputs to that box
        - If Button then:
            - If PvP, PvC or CvC game scene loading buttons load a game scene and follow the chess game that is dispalyed
            - If a previous game button is pressed load that game to a game scene and continue play
            - If signup or login confirm then handle signup and login request in functions
            - If exit game scene then terminate the current game scene and reload the main menu buttons
        """
        match button:
            case TextBox():
                handle_text_independance()
            case Button():
                match self.button_match[button]:
                    case "ExitGameScene":
                        for overlay in self._overlay_scene:
                            if isinstance(overlay, GameScene):
                                self.exit_game_scene(overlay)
                                break
                    case "Logout":
                        self.user_information.clear()
                        self.reset_overlay()
                        self.load_main_menu()
                    case "LoginConfirm":
                        if user_id := self.authentication():
                            self.reset_overlay()
                            self.load_user_information(user_id)
                            self.load_game_options()
                            self.button_match[button := Button(25, 25, 50, text="X")] = "Logout"
                            self.add_overlay(button, Vector(self.local_point.x+self.dimensions.x-25, self.local_point.y+self.dimensions.y-25))
                        else:
                            self.failed_authentication()
                    case "SignUpConfirm":
                        self.signup()
                    case "PvP":
                        self.load_game(PlayerVsPlayer(self.dimensions.x-50, self.dimensions.y))
                    case "PvC":
                        self.load_game(pvc := PlayerVsComputer(self.dimensions.x-50, self.dimensions.y))
                        pvc.player_colour = choice([BitBoard.colour.BLACK, BitBoard.colour.WHITE])
                    case "CvC":
                        self.load_game(ComputerVsComputer(self.dimensions.x-50, self.dimensions.y))
                    case "OPvP":
                        self.load_game(opvp := OnlinePlayerVsPlayer(self.dimensions.x-50, self.dimensions.y), with_eval=False)
                        if not(opvp.network_component.id): self.launch_server(opvp)
                        #marker
                    case int():
                        _, game_move, self.__current_game_id, game_type = self.user_information["SaveGame"][self.button_match[button]]
                        apply_move = BitBoard.convert_from_save_game(game_move)
                        game_scene = MenuScene.__notation_game_scene[game_type](self.dimensions.x-50, self.dimensions.y)
                        for move in apply_move: game_scene.make_move(move)
                        self.load_game(game_scene)
        return self
    
    def load_game(self, game_scene : GameScene, with_eval:bool=True) -> object:
        """ Loads the exit game scene button, game scene and evaluation bar to overlays """
        self.reset_overlay()
        self.button_match[button := Button(25, 25, 50, text="X")] = "ExitGameScene"
        self.add_overlay(game_scene, self.local_point)
        if with_eval: self.add_overlay(EvaluationBar(game_scene, 50), Vector(self.local_point.x+self.dimensions.x-50, self.local_point.y))
        self.add_overlay(button, Vector(self.local_point.x+self.dimensions.x-25, self.local_point.y+self.dimensions.y-25))
        self.__display_user_information = False
        return self
    
    def launch_server(self, online_game_scene : OnlinePlayerVsPlayer):
        self.game_server_component = GameServerComponent(self)
        online_game_scene.network_component.connect()
    
    def failed_authentication(self) -> object:
        """ For further development and access to local save when authentication is failed"""
        #print("auth failed") #debug message
        return self
        
    """ Regex to idenify the general form for a email """
    __email_regex = compile('[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}')
    def signup(self) -> object:
        """ Checks for databse connection again if not break imediately, else extract the username, password and email feilds from textboxes
        and verify the email is in a valid format, hash and save the password then upload the user into the database """
        if not(self.database_component.connection):
            self.text_match["SignUpUsername"].text = "No Connection"
            return self
        
        username = self.text_match["SignUpUsername"].text
        password = self.text_match["SignUpPassword"].text
        email = self.text_match["SignUpEmail"].text
        if not(username or password or email): return
        if not(MenuScene.__email_regex.match(email)):
            self.text_match["SignUpEmail"].text = "invalid email"
            return self
        
        hashed_password, salt = self.authentication_component.hash_password(password)
        upload_sql = f'INSERT INTO UserInformation(Username, Password, Salt, Email, EloRating) VALUES("{username}", "{hashed_password.decode("utf-8")}", "{salt.decode("utf-8")}", "{email}", 100)'
        self.database_component.upload(upload_sql)
        self.__text_box[2].text = self.__text_box[3].text = self.__text_box[4].text = ""
        return self
    
    def authentication(self) -> int:
        username = self.text_match["LoginUsername"].text
        password = self.text_match["LoginPassword"].text
        return self.authentication_component.verify_login(username, password) if username or password else -1
    
    def load_user_information(self, user_id:int) -> object:
        """ First verifies that the user is in the database as the local save has an id of -1 """
        if user_id < 0:
            self.load_local_save_game()
            return self
        """
        Then, fetches the UserInformation from the database and stores the values in the dictionary intializes on __init__,
        Finally loading all the games that can be loaded from the game table
        """
        if not(self.user_information):
            self.user_fetch["table_name"] = "UserInformation"
            self.user_fetch["column"] = "UserID, Username, EloRating"
            self.user_fetch["condition"] = f"UserID = {user_id}"
            if query_value := self.database_component.load(self.user_fetch):
                self.user_information = dict(zip(["UserID", "Username", "EloRating"], query_value[0])) # only loads staring information once
            
        self.user_fetch["table_name"] = "Game"
        self.user_fetch["column"] = "GameID, GameName, GameInformation, EngineID, GameType"
        self.user_information["SaveGame"] = {}
        if query_value := self.database_component.load(self.user_fetch):
            self.user_information["SaveGame"].update({game_id: (game_name, loads(game_info), engine_id, game_type) \
                for (game_id, game_name, game_info, engine_id, game_type) in query_value})
        self.load_continue_button()
        return self
    
    def load_local_save_game(self) -> object:
        """ Loads local save information into user information property by parsing the json dictionary in the local save """
        try:
            with open("local_save.json", "r") as save_file:
                local_save = loads(save_file.read())
        except Exception as e:
            print(e)
            local_save = {
                "UserID" : -1,
                "Username" : "Local",
                "EloRating" : 100,
                "SaveGame" : {}
            }
            with open("local_save.json", "w") as save_file:
                save_file.write(dumps(local_save, indent=4))
        if not(self.user_information):
            self.user_information = dict(zip(["UserID", "Username", "EloRating"], [local_save["UserID"], local_save["Username"], local_save["EloRating"]]))
        self.user_information["SaveGame"] = {}
        for game_id, game in local_save["SaveGame"].items():
            self.user_information["SaveGame"][int(game_id)] = (game["name"], game["gameinfo"], game["engine_id"], game["game_type"])
        self.load_continue_button()
        return self
    
    def load_continue_button(self) -> object:
        """ For each game loaded before, a button is instanced and assign to load each game when pressed going down the UI """
        for (y, game) in enumerate(self.user_information["SaveGame"]):
            self.button_match[button := Button(50, 50, 20, text=self.user_information["SaveGame"][game][0])] = game
            self.add_overlay(button, Vector(0, y*70))
        return self
            
    def while_event(self, event:pygame.event.Event) -> object:
        return super().while_event(event)
    
    def draw(self, window:pygame.surface.Surface) -> object:
        def display_at(ind, text):
            text_surface = self.__font.render(text, False, self.__font_color)
            window.blit(text_surface, (self.local_point.x+100, self.local_point.y+(self.__font_size*ind)))
            #number for offset on x to not collide with buttons
            
        """ For each element in the user information dictionary, draw user information text on the menu scene
        Specially for game information convert to readable notation instead of dicitionary indexes """
        
        save_ind = 0
        if self.user_information and self.__display_user_information:
            for ind, (key, value) in enumerate(self.user_information.items()):
                if key == "SaveGame":
                    for save_ind, (key, value) in enumerate(value.items()):
                        value = list(value)
                        value[1] = BitBoard.convert_to_notation_game(BitBoard.convert_from_save_game(value[1]))
                        text = f"{key}: {value}"
                        display_at(ind+save_ind, text)
                text = f"{key}: {value}"
                display_at(ind+save_ind, text)
        return super().draw(window)

class MenuObserver(SceneObserver):
    """ Not necessary, used for later development """
    def __init__(self, menu_scene: MenuScene) -> None:
        super().__init__(menu_scene)
    
    def load_scene_signal(self, scene : GameScene) -> object:
        return self
    
class AuthenticationComponenet():
    def __init__(self, database_compoenet) -> None:
        self.database_component : DatabaseComponent = database_compoenet
    
    def verify_login(self, username:str, password:str) -> int:
        """ Fetches, if present, user with given username and hashed password adn returns their userid """
        if not(self.database_component.connection): return -1
        load_parameter = {
            "table_name" : "UserInformation",
            "column" : "UserID, Password, Salt",
            "condition" : f"Username = '{username}'"
        }
        if loaded := self.database_component.load(load_parameter):
            loaded = loaded[0]
            user_id, hashed_password, salt = loaded
            rehash_password = hashpw(password.encode('ascii'), salt := salt.decode('utf-8').strip("\x00").encode('utf-8'))
            if rehash_password == hashed_password.decode('utf-8').strip("\x00").encode('utf-8'):
                return user_id
        return None
    
    @staticmethod
    def hash_password(password:str) -> tuple[str, str]: #Returns a hashed password and salt
        salt = gensalt(rounds=15)
        hashed_password = hashpw(password.encode('ascii'), salt)
        return hashed_password, salt

class DatabaseComponent():
    def __init__(self) -> None:
        """ Basic sql connector setup """
        self.connection : MySQLConnection = None
        self.cursor : CursorBase = None
        self.__config = {
            "host":"localhost",
            "user":"admin",
            "password":"testpassword",
            "database":"ChessDatabase"
            }
        
        def mysql_connect() -> None:
            """ Attempts connection if failed, print debug exception """
            try: 
                self.connection = mysql.connector.connect(**self.__config)
                self.cursor = self.connection.cursor()
            except Exception as e:
                print(f"Error while connecting to MySQL: {e} \nContinuing without database")
                
        def mysql_config() -> None:
            """ Extracts the table names and columns from sql database for use later and adds them to the config dictionary """
            try:
                table_name_sql = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema = 'ChessDatabase'"
                self.cursor.execute(table_name_sql)
                self.__config["tables"] = {table_name[0]:None for table_name in self.cursor.fetchall()}
                
                for table_name in self.__config["tables"].keys():
                    column_name_sql = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
                    self.cursor.execute(column_name_sql)
                    self.__config["tables"][table_name] = [value[0] for value in self.cursor.fetchall()]
            except Exception as e:
                print(f"Error while setting up config: {e} \nContinuing without config setup completion")

        """ Attempt connection and grab configuration if successful """
        mysql_connect()
        if self.connection:
            mysql_config()
        
    @property
    def config(self):
        """ Make sure the config cannot be edited """
        return self.__config
    
    """ example load_parameter: = {
        "table_name" : -table name for search or insert-
        "column" : -column(s) that are affected with a value-
        "condition" : condition for load-
    }"""
    
    def upload(self, sql:str) -> object:
        """ Centralizes uploads to this componenet so that sql statment are decoupled from each class which uses them """
        self.cursor.execute(sql)
        self.connection.commit()
        return self
    
    def load(self, load_parameter:dict) -> list:
        """ Formats sql statments for loading into a dictionary instead of formatting an sql statment differnetly each time something is loaded """
        select_sql = f"SELECT {load_parameter['column']} FROM {load_parameter['table_name']} WHERE {load_parameter['condition']}"
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()
    
    def save_local(self, save_game:list[int], game_type:str, name:str, game_id:int, user_id:int, engine_id:int) -> object:
        """ Loads and appends or creates local save if not present and writes to local save file with the saved game """
        try:
            with open("local_save.json", "r") as save_file:
                local_save = loads(save_file.read())
            game_id = max([int(g_id)+1 for g_id in local_save["SaveGame"].keys()]) if not(game_id) else game_id
            local_save["SaveGame"][game_id] = {
                "name" : name,
                "user_id" : user_id,
                "engine_id" : engine_id,
                "date_time" : strftime('%Y-%m-%d %H:%M:%S'),
                "gameinfo" : save_game,
                "game_type" : game_type
            }
        except Exception as e:
            print(e)
            local_save = {
                "UserID" : -1,
                "Username" : "Local",
                "EloRating" : 100,
                "SaveGame" : { 1 : {
                    "name" : name,
                    "user_id" : user_id,
                    "engine_id" : engine_id,
                    "date_time" : strftime('%Y-%m-%d %H:%M:%S'),
                    "gameinfo" : save_game,
                    "game_type" : game_type
                }}
            }
        with open("local_save.json", "w") as save_file:
            save_file.write(dumps(local_save, indent=4))
            
        return self
    
    __new_game_sql = f"INSERT INTO Game(GameName, UserID, EngineID, DateTime, GameInformation, GameType) VALUES(%(name)s, %(user_id)s, %(engine_id)s, %(datetime)s, %(gameinfo)s, %(game_type)s)"
    __update_game_sql = f"UPDATE Game SET GameInformation = %(gameinfo)s WHERE GameID = %(game_id)s"
    def save_game(self, applied_moves:list[tuple], game_type:str, name:str, game_id:int=None, user_id:int=-1, engine_id:int=1) -> object: #local userID is always -1 and default engine id is 1
        """ Similar to saving local saves, updates Game table with the game that was played """
        if not(applied_moves): return self
        save_game = BitBoard.convert_to_save_game(applied_moves)
        if user_id < 0: return self.save_local(save_game, game_type, name, game_id, user_id, engine_id)
        values = {
            "game_id" : game_id,
            "name" : name,
            "user_id" : user_id,
            "engine_id" : engine_id,
            "datetime" : strftime('%Y-%m-%d %H:%M:%S'),
            "gameinfo" : dumps(save_game, indent=4),
            "game_type" : game_type
            }
        self.cursor.execute(DatabaseComponent.__update_game_sql if game_id else DatabaseComponent.__new_game_sql, values)
        self.connection.commit()
        return self
    
class GameServerComponent():
    def __init__(self, parent : GameScene) -> None:
        self.__config = {
            "server":"127.0.0.1",
            "port": 5555
            }
        self.server_thread = GameServerThread(self.__config)
        self.server_thread.start()
        #marker
        
class GameServerThread(Thread):
    def __init__(self, config, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__config = config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.__config["server"], self.__config["port"]))
        except Exception as e:
            print(e)
            
        self.socket.listen(2)
        self.server_thread_connections = []
        print("waiting for connection")
    
    def run(self) -> None:
        while True:
            connection, address = self.socket.accept()
            
            self.server_thread_connections.append(ServerConnection(connection))
            self.server_thread_connections[-1].start()
            
class ServerConnection(Thread):
    def __init__(self, connection : socket.socket, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.connection = connection
    
    def run(self):
        self.connection.send(str.encode("Connected"))
        relpy = ""
        while True:
            try:
                data = self.connection.recv(2048)
                reply = data.decode("utf-8")
                if not(data):
                    break
                else:
                    print("Receieved:", reply)
                    print("Sending:", reply)
                    
                self.connection.sendall(str.encode(reply))
            except Exception as e:
                print(e)
                break
            
        print("Lost connection")
        self.connection.close()
                    
            
def main():
    pass
    
if __name__ == "__main__":
    main()

"""
For further development problems:
    -> menu button collisions, reason unknown, temporary solution of moving buttons
    -> Unhandled thread when closing game scene
"""