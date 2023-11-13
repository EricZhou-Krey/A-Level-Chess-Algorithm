import mysql.connector
#WIP
class DataLogger():
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="zhoue_chess_admin",
            password="Eri(Zh0u1101"
        )
        print(self.db)
datalogger = DataLogger()