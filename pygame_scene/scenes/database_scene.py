import sys, mysql.connector, pygame, time, bcrypt, re, json
from mysql.connector.cursor import CursorBase
from mysql.connector.connection import MySQLConnection
sys.path.append("../A-Level-Chess-Algorithm")
from bitboard import BitBoard
from pygame_scene.scenes.scene import Scene, SceneObserver, TextBox, TextBoxObserver, Button
from pygame_scene.scenes.game_scene import PlayerVsComputer, PlayerVsPlayer, ComputerVsComputer, GameScene, EvaluationBar
from enum import Enum
from my_dataclass import Vector, Queue

"""
ENTIRE FILE IN PROGRESS`
"""

class MenuScene(Scene, TextBoxObserver, SceneObserver):
    style = Enum("style", ["DARK", "LIGHT"])
    def __init__(self, width, height, font_size:int=40, inactive_colour:tuple=(255,255,255)):
        Scene.__init__(self, width, height)
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
    
    def load_authentication_menu(self):
        confirm_button = Button(50,50)
        self.text_match = {textReference : TextBox(400, 50, 50) for textReference in ["LoginUsername", "LoginPassword", "SignUpUsername", "SignUpPassword", "SignUpEmail"]}
        self.add_overlay(self.text_match["LoginUsername"], Vector(0, 50))
        self.add_overlay(self.text_match["LoginPassword"], Vector(0, 150))
        self.add_overlay(confirm_button, Vector(50, 250))
        self.button_match[confirm_button] = "LoginConfirm"
        
        confirm_button = Button(50, 50)
        self.add_overlay(self.text_match["SignUpUsername"], Vector(450, 50))
        self.add_overlay(self.text_match["SignUpPassword"], Vector(450, 150))
        self.add_overlay(self.text_match["SignUpEmail"], Vector(450, 250))
        self.add_overlay(confirm_button, Vector(450, 350))
        self.button_match[confirm_button] = "SignUpConfirm"
    
    def load_main_menu(self):
        if self.database_component.connection:
            if not(self.user_information):
                self.load_authentication_menu()
        else:
            self.add_overlay(TextBox(400, 50, 50, text="Database connection not secured"), Vector(200, 200))
        self.load_game_options()
    
    def load_game_options(self):
        game_scene_buttons = {
            Button(200, 200, self.__font_size, text="PvP") : "PvP", #temp numbers for sizes
            Button(200, 200, self.__font_size, text="PvC") : "PvC",
            Button(200, 200, self.__font_size, text="CvC") : "CvC"
        }
        self.button_match.update(game_scene_buttons)
        for ind, button in enumerate(game_scene_buttons.keys()):
            self.add_overlay(button, Vector(ind*300, self.dimensions.y-200))
    
    def add_overlay(self, overlay : Scene, local_point: Vector) -> object:
        match overlay:
            case TextBox():
                self.__text_box.append(overlay)
            case Button():
                self.__button.append(overlay)
        overlay.observers.append(self)
        return super().add_overlay(overlay, local_point)

    def reset_overlay(self):
        self.__text_box.clear()
        self.text_match.clear()
        self.__button.clear()
        self.button_match.clear()
        self._overlay_scene.clear()
    
    __game_scene_notation = {PlayerVsComputer : "PvC", PlayerVsPlayer : "PvP", ComputerVsComputer : "CvC"}
    __notation_game_scene = {value : key for key, value in __game_scene_notation.items()}
    def press_signal(self, button : Button):
        def handle_text_independance():
            for overlay in [ov for ov in self._overlay_scene if type(ov) is TextBox]:
                if button != overlay:
                    overlay.active = False
        match button:
            case TextBox():
                handle_text_independance()
            case Button():
                match self.button_match[button]:
                    case "ExitGameScene":
                        for overlay in self._overlay_scene:
                            if isinstance(overlay, GameScene): # need to stop storing duplicate games
                                self.database_component.save_game(overlay.bitboard.applied_moves, MenuScene.__game_scene_notation[type(overlay)], "name", game_id=self.__current_game_id, user_id=self.user_information["UserID"] if self.user_information else 1, engine_id=1)
                        self.reset_overlay()
                        self.load_main_menu()
                        if self.user_information and (user_id := self.user_information["UserID"]): self.load_user_information(user_id)
                        self.__display_user_information = True
                    case "LoginConfirm":
                        if user_id := self.authentication():
                            self.reset_overlay()
                            self.load_user_information(user_id)
                            self.load_game_options()
                        else:
                            self.failed_authentication()
                    case "SignUpConfirm":
                        self.signup()
                    case "PvP":
                        self.load_game(PlayerVsPlayer(self.dimensions.x-50, self.dimensions.y))
                    case "PvC":
                        self.load_game(PlayerVsComputer(self.dimensions.x-50, self.dimensions.y))
                    case "CvC":
                        self.load_game(ComputerVsComputer(self.dimensions.x-50, self.dimensions.y))
                    case int():
                        _, game_move, self.__current_game_id, game_type = self.user_information["SaveGame"][self.button_match[button]]
                        apply_move = BitBoard.convert_from_save_game(game_move)
                        game_scene = MenuScene.__notation_game_scene[game_type](self.dimensions.x-50, self.dimensions.y)
                        for move in apply_move: game_scene.make_move(move)
                        self.load_game(game_scene)
    
    def load_game(self, game_scene : GameScene):
        self.reset_overlay()
        self.button_match[button := Button(25, 25, 50, text="X")] = "ExitGameScene"
        self.add_overlay(game_scene, self.local_point)
        self.add_overlay(EvaluationBar(game_scene, 50), Vector(self.local_point.x+self.dimensions.x-50, self.local_point.y))
        self.add_overlay(button, Vector(self.local_point.x+self.dimensions.x-25, self.local_point.y+self.dimensions.y-25))
        self.__display_user_information = False
    
    def failed_authentication(self):
        print("auth failed")
        
    __email_regex = re.compile('[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}')
    def signup(self):
        if not(self.database_component.connection):
            self.text_match["SignUpUsername"].text = "No Connection"
            return
        username = self.text_match["SignUpUsername"].text
        password = self.text_match["SignUpPassword"].text
        email = self.text_match["SignUpEmail"].text
        if not(username or password or email): return
        if not(MenuScene.__email_regex.match(email)):
            self.__text_box[4].text = "invalid email"
            return
        hashed_password, salt = self.authentication_component.hash_password(password)
        upload_sql = f'INSERT INTO UserInformation(Username, Password, Salt, Email, EloRating) VALUES("{username}", "{hashed_password.decode("utf-8")}", "{salt.decode("utf-8")}", "{email}", 100)'
        self.database_component.upload(upload_sql)
        self.__text_box[2].text = self.__text_box[3].text = self.__text_box[4].text = ""
    
    def authentication(self):
        username = self.text_match["LoginUsername"].text
        password = self.text_match["LoginPassword"].text
        return self.authentication_component.verify_login(username, password) if username or password else -1
    
    def load_user_information(self, user_id):
        if user_id < 0:
            self.load_local_save_game()
            return
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
            self.user_information["SaveGame"].update({game_id: (game_name, json.loads(game_info), engine_id, game_type) \
                for (game_id, game_name, game_info, engine_id, game_type) in query_value})
        self.load_continue_button()
    
    def load_local_save_game(self):
        try:
            with open("local_save.json", "r") as save_file:
                local_save = json.loads(save_file.read())
        except Exception as e:
            print(e)
            local_save = {
                "UserID" : -1,
                "Username" : "Local",
                "EloRating" : 100,
                "SaveGame" : {}
            }
            with open("local_save.json", "w") as save_file:
                save_file.write(json.dumps(local_save, indent=4))
        if not(self.user_information):
            self.user_information = dict(zip(["UserID", "Username", "EloRating"], [local_save["UserID"], local_save["Username"], local_save["EloRating"]]))
        self.user_information["SaveGame"] = {}
        for game_id, game in local_save["SaveGame"].items():
            self.user_information["SaveGame"][int(game_id)] = (game["name"], game["gameinfo"], game["engine_id"], game["game_type"])
        self.load_continue_button()
    
    def load_continue_button(self):
        for (y, game) in enumerate(self.user_information["SaveGame"]):
            self.button_match[button := Button(50, 50, 20, text=self.user_information["SaveGame"][game][0])] = game
            self.add_overlay(button, Vector(0, y*70))
            
    def while_event(self, event):
        super().while_event(event)
    
    def draw(self, window):
        def display_at(ind, text):
            text_surface = self.__font.render(text, False, self.__font_color)
            window.blit(text_surface, (self.local_point.x+100, self.local_point.y+(self.__font_size*ind)))
        
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
                display_at(ind+save_ind, text) # temp number for sizes of UI
        super().draw(window)

class MenuObserver(SceneObserver):
    def __init__(self, menu_scene: MenuScene):
        super().__init__(menu_scene)
    
    def load_scene_signal(scene : GameScene):
        pass
    
class AuthenticationComponenet():
    def __init__(self, database_compoenet) -> None:
        self.database_component : DatabaseComponent = database_compoenet
    
    def verify_login(self, username:str, password:str) -> int:
        if not(self.database_component.connection): return -1
        load_parameter = {
            "table_name" : "UserInformation",
            "column" : "UserID, Password, Salt",
            "condition" : f"Username = '{username}'"
        }
        if loaded := self.database_component.load(load_parameter):
            loaded = loaded[0]
            user_id, hashed_password, salt = loaded
            rehash_password = bcrypt.hashpw(password.encode('ascii'), salt := salt.decode('utf-8').strip("\x00").encode('utf-8'))
            if rehash_password == hashed_password.decode('utf-8').strip("\x00").encode('utf-8'):
                return user_id
        return None
    
    @staticmethod
    def hash_password(password:str) -> tuple[str, str]:
        salt = bcrypt.gensalt(rounds=15)
        hashed_password = bcrypt.hashpw(password.encode('ascii'), salt)
        return hashed_password, salt

class DatabaseComponent():
    def __init__(self) -> None:
        self.connection : MySQLConnection = None
        self.cursor : CursorBase = None
        self.__config = {
            "host":"localhost",
            "user":"admin",
            "password":"testpassword",
            "database":"ChessDatabase"
            }
        def mysql_connect():
            try: 
                self.connection = mysql.connector.connect(**self.__config)
                self.cursor = self.connection.cursor()
            except Exception as e:
                print(f"Error while connecting to MySQL: {e} \nContinuing without database")
                
        def mysql_config():
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

        mysql_connect()
        if self.connection:
            mysql_config()
        
    @property
    def config(self):
        return self.__config
    
    """ example load_parameter: = {
        "table_name" : -table name for search or insert-
        "column" : -column(s) that are affected with a value-
        "condition" : condition for load-
    }"""
    
    def upload(self, sql:str):
        self.cursor.execute(sql)
        self.connection.commit()
    
    def load(self, load_parameter: dict):
        select_sql = f"SELECT {load_parameter['column']} FROM {load_parameter['table_name']} WHERE {load_parameter['condition']}"
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()
    
    def save_local(self, save_game:list[int], game_type:str, name:str, game_id:int, user_id:int, engine_id:int):
        try:
            with open("local_save.json", "r") as save_file:
                local_save = json.loads(save_file.read())
            game_id = max([int(g_id)+1 for g_id in local_save["SaveGame"].keys()]) if not(game_id) else game_id # error in list comp
            local_save["SaveGame"][game_id] = {
                "name" : name,
                "user_id" : user_id,
                "engine_id" : engine_id,
                "date_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
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
                    "date_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
                    "gameinfo" : save_game,
                    "game_type" : game_type
                }}
            }
        with open("local_save.json", "w") as save_file:
            save_file.write(json.dumps(local_save, indent=4))
    
    __game_sql = f"INSERT INTO Game(GameName, UserID, EngineID, DateTime, GameInformation, GameType) VALUES(%(name)s, %(user_id)s, %(engine_id)s, %(datetime)s, %(gameinfo)s, %(game_type)s)"
    def save_game(self, applied_moves:list[tuple], game_type:str, name:str, game_id:int=None, user_id:int=-1, engine_id:int=1): #local userID is always -1 and default engine id is 1
        if not(applied_moves): return
        save_game = BitBoard.convert_to_save_game(applied_moves)
        self.save_local(save_game, game_type, name, game_id, user_id, engine_id)
        if user_id < 0: return
        values = {
            "name" : name,
            "user_id" : user_id,
            "engine_id" : engine_id,
            "datetime" : time.strftime('%Y-%m-%d %H:%M:%S'),
            "gameinfo" : json.dumps(save_game, indent=4),
            "game_type" : game_type
            }
        self.cursor.execute(DatabaseComponent.__game_sql, values)
        self.connection.commit()
        
def main():
    pass
    
if __name__ == "__main__":
    main()

"""
Save game feature
Create menu button for each game scene
-> menu button collisions, reason unknown, temporary solution of moving buttons

Need to update sql and json file formatting to algin with each other, with the fucntions load save games, save_games etc
Save to sql database duplicates itself

Unhandled thread when closing game scene
"""