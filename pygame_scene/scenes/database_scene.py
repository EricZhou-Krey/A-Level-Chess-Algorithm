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
        
        self.__text_box : list[TextBox] = []
        self.__button : list[Button] = []
        self.user_information = {}
        self.user_fetch = {}
        self.button_match = {}
        self.text_match = {}
        
        self.load_main_menu()
        
    def load_main_menu(self):
        if self.database_component.connection:
            confirm_button = Button(50,50)
            self.text_match = {textReference : TextBox(400, 50, 50) for textReference in ["LoginUsername", "LoginPassword", "SignUpUsername", "SignUpPassword", "SignUpEmail"]}
            self.add_overlay(self.text_match["LoginUsername"], Vector(0, 50))
            self.add_overlay(self.text_match["LoginPassword"], Vector(0, 150))
            self.add_overlay(confirm_button, Vector(0, 250))
            self.button_match[confirm_button] = "LoginConfirm"
            
            confirm_button = Button(50, 50)
            self.add_overlay(self.text_match["SignUpUsername"], Vector(450, 50))
            self.add_overlay(self.text_match["SignUpPassword"], Vector(450, 150))
            self.add_overlay(self.text_match["SignUpEmail"], Vector(450, 250))
            self.add_overlay(confirm_button, Vector(450, 350))
            self.button_match[confirm_button] = "SignUpConfirm"
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
    
    def press_signal(self, button : Button):
        def handle_text_independance():
            for overlay in [ov for ov in self._overlay_scene if type(ov) is TextBox]:
                    if button != overlay:
                        overlay.active = False
        
        match button:
            case TextBox():
                handle_text_independance()
            case Button():
                inst_game_scene = None
                match self.button_match[button]:
                    case "ExitGameScene":
                        for overlay in self._overlay_scene:
                            if isinstance(overlay, GameScene):
                                self.database_component.save_game(overlay.bitboard.applied_moves, "example_name", self.user_information["UserID"] if self.user_information else 1, 1)
                        self.reset_overlay()
                        self.load_main_menu()
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
                        inst_game_scene = PlayerVsPlayer(self.dimensions.x-50, self.dimensions.y)
                    case "PvC":
                        inst_game_scene = PlayerVsComputer(self.dimensions.x-50, self.dimensions.y)
                    case "CvC":
                        inst_game_scene = ComputerVsComputer(self.dimensions.x-50, self.dimensions.y)
                        
                if inst_game_scene:
                    self.reset_overlay()
                    self.button_match[button := Button(25, 25, 50, text="X")] = "ExitGameScene"
                    self.add_overlay(inst_game_scene, self.local_point)
                    self.add_overlay(EvaluationBar(inst_game_scene, 50), Vector(self.local_point.x+self.dimensions.x-50, 0))
                    self.add_overlay(button, Vector(0,0))
                    
                    
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
        self.user_fetch["table_name"] = "UserInformation"
        self.user_fetch["column"] = "UserID, Username, EloRating"
        self.user_fetch["condition"] = f"UserID = {user_id}"
        if query_value := self.database_component.load(self.user_fetch):
            self.user_information = dict(zip(["UserID", "Username", "EloRating"], query_value[0]))
        
        self.user_fetch["table_name"] = "Game"
        self.user_fetch["column"] = "GameID, GameName, GameInformation, EngineID"
        if query_value := self.database_component.load(self.user_fetch):
            self.user_information.update({game_name: (game_id, json.loads(game_info), engine_id) for (game_id, game_name, game_info, engine_id) in query_value}) #loading IDS temp, will load elo and description instead later
    
    def load_local_save_game(self):
        with open("local_save.json", "w") as save_file:
            local_save = json.loads(save_file.read())
        self.user_information = dict(zip(["UserID", "Username", "EloRating"], [local_save["UserID"], local_save["Username"], local_save["EloRating"]]))
        for game in local_save["SaveGame"]:
            self.user_information[game["name"]] = (game["gameinfo"], game["engine_id"])
    
    def while_event(self, event):
        super().while_event(event)
    
    def draw(self, window):
        if self.user_information:
            for ind, (key, value) in enumerate(self.user_information.items()):
                text = f"{key}: {value}"
                text_surface = self.__font.render(text, False, self.__font_color)
                window.blit(text_surface, (self.local_point.x+100, self.local_point.y+(self.__font_size*ind))) # temp number for sizes of UI
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
        if loaded := self.database_component.load(load_parameter)[0]:
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
    """
    example load_parameter: = {
        "table_name" : -table name for search or insert-
        "column" : -column(s) that are affected with a value-
        "condition" : condition for load-
    }
    """
    def upload(self, sql:str):
        self.cursor.execute(sql)
        self.connection.commit()
    
    def load(self, load_parameter: dict):
        select_sql = f"SELECT {load_parameter['column']} FROM {load_parameter['table_name']} WHERE {load_parameter['condition']}"
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()
    
    __game_sql = f"INSERT INTO Game(GameName, UserID, EngineID, DateTime, GameInformation) VALUES(%(name)s, %(user_id)s, %(engine_id)s, %(datetime)s, %(gameinfo)s)"
    def save_game(self, applied_moves:list[tuple], name:str, user_id:int, engine_id:int=1): #local userID is always -1
        if not(applied_moves): return
        save_game = BitBoard.convert_to_save_game(applied_moves)
        try:
            with open("local_save.json", "r") as save_file:
                local_save = json.loads(save_file.read())
                local_save["SaveGame"].append({
                    "name" : name,
                    "user_id" : user_id,
                    "engine_id" : engine_id,
                    "date_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
                    "gameinfo" : save_game
                })
        except Exception as e:
            print(e)
            local_save = {
                "UserID" : -1,
                "Username" : "Local",
                "EloRating" : 100,
                "SaveGame" : [{
                    "name" : name,
                    "user_id" : user_id,
                    "engine_id" : engine_id,
                    "date_time" : time.strftime('%Y-%m-%d %H:%M:%S'),
                    "gameinfo" : save_game
                }]
            }
        with open("local_save.json", "w") as save_file:
            save_file.write(json.dumps(local_save))
            
        values = {
            "name" : name, 
            "user_id" : user_id, 
            "engine_id" : engine_id,
            "datetime" : time.strftime('%Y-%m-%d %H:%M:%S'),
            "gameinfo" : json.dumps(save_game)
            }
        self.cursor.execute(DatabaseComponent.__game_sql, values)
        self.connection.commit()
        
def main():
    pass
    
if __name__ == "__main__":
    main()

"""
Planning, menu scene will have a few text inputs for the user ot input authentication details - requires textbox and button setup
-> need to slow hash using bcryt with slating to store passwords and potentially link account to email verifictition secondary
Need to create representation of past games via list of move that can be replayed to reproduce or continue a previous game, when closed saves game state
Save game feature
Create menu button for each game scene
Unhandled thread when closing game scene
"""

"""   
    def update_user_information(self): #marker
        if not(self.user_information): return
        
        CREATE VIEW view_name AS
        SELECT column1, column2, ...
        FROM table_name
        WHERE condition;
        
        FROM Orders
        INNER JOIN Customers ON Orders.CustomerID=Customers.CustomerID;
        
        
        user_with_id_view = f"CREATE VIEW {self.user_information['UserID']}_user_view AS SELECT Username, EloRating, GameID, \
            GameName, GameInformation, EngineID FROM UserInformation INNER JOIN Game ON UserInformation.UserID=Game.UserID"
        self.cursor.execute(user_with_id_view)
        
        self.user_information["UserView"] = f"{self.user_information['UserID']}_user_view"
        self.config["tables"][self.user_information["UserView"]]
    """
