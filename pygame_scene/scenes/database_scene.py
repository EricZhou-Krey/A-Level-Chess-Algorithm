import sys, mysql.connector, pygame, time
from mysql.connector.cursor import CursorBase
from mysql.connector.connection import MySQLConnection
sys.path.append("../A-Level-Chess-Algorithm")
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
        
        self.load_main_menu()
        
    def load_main_menu(self):
        if self.database_component.connection:
            self.add_overlay(TextBox(400, 50, 50), Vector(0, 50))
            self.add_overlay(TextBox(400, 50, 50), Vector(0, 150))
            self.confirm_button = Button(50,50)
            self.add_overlay(self.confirm_button, Vector(0, 250))
        self.button_match = {
            self.confirm_button : "Confirm"
        }
        self.load_game_options()
    
    def add_overlay(self, overlay : Scene, local_point: Vector) -> object:
        match overlay:
            case TextBox():
                self.__text_box.append(overlay)
            case Button():
                self.__button.append(overlay)
        overlay.observers.append(self)
        return super().add_overlay(overlay, local_point)

    def load_game_options(self):
        game_scene_buttons = {
            Button(200, 200, self.__font_size, text="PvP") : "PvP", #temp numbers for sizes
            Button(200, 200, self.__font_size, text="PvC") : "PvC",
            Button(200, 200, self.__font_size, text="CvC") : "CvC"
        }
        self.button_match.update(game_scene_buttons)
        for ind, button in enumerate(game_scene_buttons.keys()):
            self.add_overlay(button, Vector(ind*300, self.dimensions.y-200))

    def reset_overlay(self):
        self.__text_box.clear()
        self.__button.clear()
        self._overlay_scene.clear()
    
    def press_signal(self, button : Button):
        match button:
            case TextBox():
                for overlay in [ov for ov in self._overlay_scene if type(ov) is TextBox]:
                    if button != overlay:
                        overlay.active = False
            case Button():
                inst_game_scene = None
                match self.button_match[button]:
                    case "Confirm":
                        if user_id := self.authentication():
                            self.reset_overlay()
                            self.load_user_information(user_id)
                            self.load_game_options()
                        else:
                            self.failed_authentication()
                    case "PvP":
                        inst_game_scene = PlayerVsPlayer(self.dimensions.x-50, self.dimensions.y)
                    case "PvC":
                        inst_game_scene = PlayerVsComputer(self.dimensions.x-50, self.dimensions.y)
                    case "CvC":
                        inst_game_scene = ComputerVsComputer(self.dimensions.x-50, self.dimensions.y)
                if inst_game_scene:
                    self.reset_overlay()
                    eval_bar = EvaluationBar(inst_game_scene, 50) #temp numbers
                    self.add_overlay(eval_bar, Vector(self.local_point.x+self.dimensions.x-50, 0))
                    self.add_overlay(inst_game_scene, self.local_point)
                    
    def failed_authentication(self):
        print("auth failed")
    
    def authentication(self):
        username = self.__text_box[0].text
        password = self.__text_box[1].text # temp will add naming system to test boxes to reference them instead of direct indexes
        return self.authentication_component.verify_login(username, password)
    
    def load_user_information(self, user_id):
        self.user_fetch["table_name"] = "UserInformation"
        self.user_fetch["column"] = "Username, EloRating"
        self.user_fetch["condition"] = f"UserID = {user_id}"
        if query_value := self.database_component.load(self.user_fetch):
            self.user_information = dict(zip(["Username", "EloRating"], query_value[0]))
        
        self.user_fetch["table_name"] = "Game"
        self.user_fetch["column"] = "GameID, GameName, GameInformation, EngineID"
        if query_value := self.database_component.load(self.user_fetch):
            self.user_information.update({game_name: (game_id, game_info, engine_id) for (game_id, game_name, game_info, engine_id) in query_value}) #loading IDS temp, will load elo and description instead later
            
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
    
    def verify_login(self, username, password) -> int:
        load_parameter = {
            "table_name" : "UserInformation",
            "column" : "UserID",
            "condition" : f"Username = '{username}' AND Password = '{password}'"
        }
        if userid := self.database_component.load(load_parameter):
            return userid[0][0]
        return None

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
    """
    example load_parameter: = {
        "table_name" : -table name for search or insert-
        "column" : -none default to every- else -column(s) that are affected with a value-
        "values" : -none for select-
        "condition" : -none for upload, condition for load-
    }
    """
    def load(self, load_parameter: dict):
        select_sql = f"SELECT {load_parameter['column']} FROM {load_parameter['table_name']} WHERE {load_parameter['condition']}"
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()
    
    def upload(self, upload_parameter : dict):
        insert_sql = f"INSERT INTO {upload_parameter['table_name']}({str(upload_parameter['column']).strip('[]')}) VALUES({str(upload_parameter['values']).strip('[]')})"
        self.cursor.execute(insert_sql)
    
    def __delete__(self):
        self.cursor.close()
        self.connection.close()
        
def main():
    test_dbc = DatabaseComponent()
    test_ac = AuthenticationComponenet(test_dbc)
    pass
    
if __name__ == "__main__":
    main()

"""
name: alevelchessdb
username: admin
password: testpassword
"""

"""
Planning, menu scene will have a few text inputs for the user ot input authentication details - requires textbox and button setup
then verified according to database - practically done just need to link to the menu scene itself
scene is loaded with game information around the edge of the screen where a gamescene will be contained within need to create view and collect user information
"""