import sys, mysql.connector
from mysql.connector.cursor import CursorBase
from mysql.connector.connection import MySQLConnection
sys.path.append("../A-Level-Chess-Algorithm")
from pygame_scene.scenes.scene import Scene, SceneObserver
from enum import Enum
from my_dataclass import Vector, Queue

"""
ENTIRE FILE IN PROGRESS
"""

class MenuScene(Scene):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.observers : list[MenuObserver] = []
        self.database_component : DatabaseComponent = DatabaseComponent()
        self.authentication_component : AuthenticationComponenet = AuthenticationComponenet(self.database_component)
    
    def draw(self, window):
        return super().draw(window)

class MenuObserver(SceneObserver):
    def __init__(self, menu_scene: MenuScene):
        super().__init__(menu_scene)
    """
    def signals(self, parameters):
        pass
    """
    
class AuthenticationComponenet():
    def __init__(self, database_compoenet) -> None:
        self.database_component : DatabaseComponent = database_compoenet
    
    def verify_login(self, username, password) -> int:
        fetch_userid_sql = f"SELECT UserID FROM UserInformation WHERE Username = {username} AND Password = {password}"
        self.database_component.cursor.execute(fetch_userid_sql)
        return self.database_component.cursor.fetchall()
    
    

class DatabaseComponent():
    def __init__(self) -> None:
        self.connection : MySQLConnection = None
        self.cursor : CursorBase = None
        self.__clean_string = lambda cursor_fetch : [str(table).strip("(',')") for table in cursor_fetch]
        self.__config = {"host":"localhost",
                "user":"admin",
                "password":"testpassword",
                "database":"ChessDatabase"}
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
                self.__config["tables"] = {table_name:None for table_name in self.__clean_string(self.cursor.fetchall())}
                
                for table_name in self.__config["tables"].keys():
                    column_name_sql = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
                    self.cursor.execute(column_name_sql)
                    self.__config["tables"][table_name] = self.__clean_string(self.cursor.fetchall())
            except Exception as e:
                print(f"Error while setting up config: {e} \nContinuing without config setup, completion")

        mysql_connect()
        if self.connection:
            mysql_config()
    @property
    def config(self):
        return self.__config
    
    """
    example load_parameter:
    up = {
        "table_name" : -table name for search or insert-
        "column" : -none default to every- else -column(s) that are affected with a value-
        "values" : -none for select-
        "condition" : -none for upload, condition for load-
    }
    """
    """def load(self, load_parameter: dict):
        select_sql = f"SELECT {load_parameter['column']} FROM {load_parameter['table_name']} WHERE {load_parameter['condition']}"
        self.cursor.execute(select_sql)
        return self.cursor.fetchall()"""
    
    def upload(self, upload_parameter : dict):
        insert_sql = f"INSERT INTO {upload_parameter['table_name']}({str(upload_parameter['column']).strip('[]')}) VALUES({str(upload_parameter['values']).strip('[]')})"
        self.cursor.execute(insert_sql)
    
    def __delete__(self):
        self.cursor.close()
        self.connection.close()
        
def main():
    test_dbc = DatabaseComponent()
    pass
    
if __name__ == "__main__":
    main()

"""
name: alevelchessdb
username: admin
password: testpassword
"""

"""
CREATE DATABASE ChessDatabase;
CREATE TABLE UserInformation (
		UserID int AUTO_INCREMENT,
		Username varchar(255) NOT NULL UNIQUE,
		Password varchar(255) NOT NULL,
		EloRating int,
		PRIMARY KEY (UserID)
);
CREATE TABLE Game (
		GameID int AUTO_INCREMENT,
		GameName varchar(255),
		GameInformation varchar(500) NOT NULL,
		UserID int,
		EngineID int,
		PRIMARY KEY (GameID),
		FOREIGN KEY (EngineID) REFERENCES Engine(EngineID),
		FOREIGN KEY (UserID) REFERENCES UserInformation(UserID)
);
CREATE TABLE Engine (
		EngineID int AUTO_INCREMENT,
		Name varchar(255) NOT NULL,
		EloRating int NOT NULL
);
#For register proccess
INSERT INTO User(input_name, encrypt_password, staring_elo) VALUES;

#For login proccess
CREATE VIEW login_information AS
SELECT Username, Password, UserID
FROM User
WHERE Username = input_name;

#For loading game from database
CREATE VIEW game_information AS
SELECT *
FROM Game
WHERE user_id = Game.UserID;
... #similiar for other other views
"""