import sys, os, glob, json
from datetime import datetime
from handlers.db import RobotDatabase
from PyQt6.QtSql import QSqlDatabase, QSqlQuery


class FileManager:
    def __init__(self):
        self.next_id = 0
        self.base_path = ""
        self.con_filename='handlers/includes/consent'

        self.chat_log = ChatManager()		
        # Initialize the SQLite database
        self.lit_db = QSqlDatabase.addDatabase('QSQLITE')
        self.lit_db.setDatabaseName(self.con_filename+'.db')
        if  self.lit_db.open():
            print("DB Connection Established -----------------------------------SUCCESS")
#        else:
#            print(self.lit_db.lastError().text())
       

        # Execute the CREATE TABLE query
        self.create_table_query = QSqlQuery()
        self.create_table_query.exec("CREATE TABLE IF NOT EXISTS TBL_consent ("
                                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                     "content TEXT,"
                                     "accept_voice INTEGER,"
                                     "accept_text INTEGER,"
                                     "full_name TEXT,"
                                     "token TEXT,"
                                     "timestamp TEXT"
                                     ");")


    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)		

    def getCurrentTimestamp(self, format_pattern='%y_%m_%d_%H%M%S'):
        current_time =  datetime.now().strftime(format_pattern)
        return current_time
     
        
    def get_next_id(self,data):
        return len(data) + 1

    def save_to_json(self, data_dict):
        file_name = self.con_filename+'.json'
        self.data.append(data_dict)
        with open(file_name, 'w') as file:
            json.dump(self.data, file, indent=4)

    def load_data(self):
        try:
            filename = self.con_filename+'.json'
            with open(filename) as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = []
       
    # Determine the number of entries and return the next available 'id' auto-incremental
    def getNextID(self):
        try:
            file_name = self.con_filename+'.json'
            with open(file_name) as file:
                data = json.load(file)
                self.next_id =  len(self.data) + 1
                return self.next_id
        except FileNotFoundError:
            return 1

    # Generate token using two known values
    def generateToken(self, value1, value2, value3, value4, value5):
        import hashlib
        combined = str(value1) + str(value2) + str(value3) + str(value4) + str(value5)
        valued_token_object = hashlib.sha256(combined.encode())
        valued_token = valued_token_object.hexdigest()
        return valued_token

    # generate a random unique token of 'length' characters that includes both letters and numbers
    def generateUniqueToken(self, length):
        import secrets, string
        characters = string.ascii_letters + string.digits
        unique_token = ''.join(secrets.choice(characters) for _ in range(length))
        return unique_token
    
    # 
    def saveToJSON(self, data: dict):
        self.data = data
        filename = self.con_filename+'.json'
        self.data_m.append(data)
        with open(filename, 'w') as file:
            json.dump(self.data, file, indent=4)
            # file.write('\n')
            
    def loadData(self):
        try:
            filename = self.con_filename+'.json'
            with open(filename) as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data_m = []


    def saveToSqlite(self, content, accept_voice, accept_text, accept_minor, name ):
        # db = QSqlDatabase.addDatabase('QSQLITE')
        filename=self.con_filename+'.db'
#         self.lit_db.setDatabaseName(filename)
#         if not self.lit_db.open():
# #            print(self.lit_db.lastError().text())
#             return False
        query = QSqlQuery()
        query.prepare("INSERT INTO TBL_consent (content, accept_voice, accept_text, is_minor, full_name, token, timestamp) VALUES (:content, :accept_voice, :accept_text, :is_minor, :full_name, :token, :timestamp)")
        query.bindValue(":content", content)
        query.bindValue(":accept_voice", accept_voice)
        query.bindValue(":accept_text", accept_text)
        query.bindValue(":is_minor", accept_minor)
        query.bindValue(":full_name", name)
        query.bindValue(":token", self.generateToken(name, accept_minor, accept_text, accept_voice, self.getCurrentTimestamp()))
        query.bindValue(":timestamp", self.getCurrentTimestamp())
        if not query.exec():
            print(query.lastError().text())
            return False
        return True

   

    def saveToDB(self, messages):		
        timestamp = self.getCurrentTimestamp('%Y-%m-%d %H:%M:%S')		
        # active_tab = self.tab_manager.currentWidget()
        # messages = str(active_tab.modelgpt.messages).replace("'", "''")
        values = f"'{messages}','{timestamp}'"

        # init ModelGPT SQLite database
        db = RobotDatabase('handlers/includes/modelgpt.db')
        db.create_table(
            'message_logs ',
            '''
                message_log_no INTEGER PRIMARY KEY AUTOINCREMENT,
                messages TEXT,
                created TEXT
            '''
        )

        db.insert_record('message_logs', 'messages, created', values)
        print('Chat saved!')
        # active_tab.status.showMessage('Chat saved!')


    def file_path(self, relative_path):
        try:
            self.base_path = sys._MEIPASS
        except Exception:
            self.base_path = os.path.abspath(".")
        return os.path.join(self.base_path, relative_path)	
    
    
    def consent(self):
        text_file_path = "Consent.md" 

        # Read the content of the text file
        with open(text_file_path, "r") as file:
            file_content = file.read()
        return file_content

    # def show(self):
    #     self.window.show()
    #     sys.exit(self.app.exec())

# if __name__ == '__main__':
#     ex = Filemanager()
#     ex.show()

class ChatManager:
    def __init__(self):
        self.chat_log_path = "media/chat-log"
    
    
    # Getters and Setters
    def get_chat_log_path(self):
        return self.chat_log_path


    def set_chat_log_path(self, chat_log_path):
        self.chat_log_path = chat_log_path

class AudioManager:
    def __init__(self, file_folder = "synthesized", format_pattern = '%d%m%y_%H%M%S', date_time = datetime.now()):
        self.root = "media/audio"
        self.audio_path = self.root+'/'+file_folder
        self.format_pattern = format_pattern
        self.date_time = date_time
        self.sample_rate = 44100

    # Setters and Getters
    def get_audio_path(self):
        return self.audio_path


    def set_audio_path(self, file_folder):
        self.audio_path = self.root+'/'+file_folder


    def current_timestamp(self):
        return datetime.now().strftime(self.format_pattern)



    def save_output(self, response, filetype="input"):
        timestamp = self.current_timestamp()
        if filetype.lower() == "input":
            self.set_audio_path("recorded")
            file_name = "recorded_audio_"
            output_file = f"{self.audio_path}/{file_name}{timestamp}.mp3"
            if not os.path.exists(self.audio_path):
                os.makedirs(self.audio_path)
            # sf.write(output_file, response, 'PCM_16', samplerate=44100)
            # print(f"Audio content written to file at {os.getcwd()}/{self.audio_path}/synthesized_audio_{timestamp}.mp3")
            with open(output_file, 'wb') as audio_output:
                audio_output.write(response)
                print(f"Audio content written to file at {self.audio_path}/synthesized_audio_{timestamp}.mp3")
        elif filetype.lower() == "output":
            self.set_audio_path("synthesized")
            file_name = "synthesized_audio_"
            if not os.path.exists(self.audio_path):
                os.makedirs(self.audio_path)
            with open(f"{self.audio_path}/{file_name}{timestamp}.mp3", 'wb') as audio_output:
                audio_output.write(response)
                print(f"Audio content written to file at {self.audio_path}/synthesized_audio_{timestamp}.mp3")


    def recent_file_finder(self, path="media/audio/synthesized", ext="mp3"):
        # Path to the folder containing the audio files
        folder_path = path + "/"
        # Get the list of audio files in the folder sorted by modification time
        audio_files = sorted(glob.glob(os.path.join(folder_path, f"*.{ext}")), key=os.path.getmtime)
        # Get the path to the most recently saved audio file
        recent_audio_file = audio_files[-1] if audio_files else None
        # Return the path to the most recently saved audio file
        if recent_audio_file:
            return recent_audio_file
        else:
            print("No audio files found in the folder.")


if __name__ == '__main__':
    ex = FileManager()
    ex.load_data()
    ex.show()
