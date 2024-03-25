import sys, os, glob, json, logging, hashlib, pyaudio
from datetime import datetime
import soundfile as sf
from configparser import ConfigParser
from modules.DataStorageModule import RobotDatabase
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from cryptography.fernet import Fernet


class AppStartUp():
    def __init__(self):
        # Define the folder paths
        self.record_folder = "resources/audio/recorded"
        self.synthesis_folder = "resources/audio/synthesized"
        # Step 1: Choose a Secure Location
        self.storage_directory = 'resources/system'
        

    # Method to get the list of all input devices    
    def __isAudioInputDeviceFound(self):
        p = pyaudio.PyAudio()
        print("Available Audio Input Devices:")
        input_device_found = False
        for idx in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(idx)
            if device_info['maxInputChannels'] > 0:
                print(f"{idx + 1}. {device_info['name']}")
                input_device_found = True
        return input_device_found
        
    # Method to get the list of all output devices
    def __isAudioOutputDeviceFound(self):
        p = pyaudio.PyAudio()
        print("Available Audio Output Devices:")
        output_device_found = False
        for idx in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(idx)
            if device_info['maxOutputChannels'] > 0:
                print(f"{idx + 1}. {device_info['name']}")
                output_device_found = True
        return output_device_found
        
        
    # Method to Calculate the age of a file in hours
    def __getfileAgeInHours(self, file_path):
        now = datetime.now()
        file_timestamp = datetime.fromtimestamp(os.path.getctime(file_path))
        age = (now - file_timestamp).total_seconds() / 3600
        return age

   # Step 2: Use Hashing for File Names
    def _generateFileHash(self, file_content):
        return hashlib.sha256(file_content.encode()).hexdigest()

    # Step 3: Apply Access Controls: Read and write only for the file owner
    def _setFilePermissions(self, file_path):
        os.chmod(file_path, 0o600) 

    # Step 4: Implement Encryption and Decryption
    def _encryptFile(self, file_path, encryption_key):
        cipher = Fernet(encryption_key)
        with open(file_path, 'rb') as file:
            file_content = file.read()
        encrypted_content = cipher.encrypt(file_content)
        with open(file_path, 'wb') as file:
            file.write(encrypted_content)

    def _decryptFile(self, file_path, encryption_key):
        cipher = Fernet(encryption_key)
        with open(file_path, 'rb') as file:
            encrypted_content = file.read()
        decrypted_content = cipher.decrypt(encrypted_content)
        return decrypted_content

    # Step 6: Audit Logs
    def _logAuditEvent(self, event_type, event_description):
        log_path = 'resources/system/log'
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        time = self.getCurrentTimestamp(format_pattern="%y-%m-%d %H:%M:%S")
        logging.basicConfig(filename=log_path+'/audit_log.txt', level=logging.INFO)
        logging.info(f"{time} || Event Type || {event_type}, Description: {event_description}")

    # Method to securely delete a file
    # Step 7: Securely deleting file
    def _secureDeleteFile(self, file_path):
        # A. Overwrite file with random data
        with open(file_path, 'rb+') as file:
            file_size = os.path.getsize(file_path)
            file.seek(0)
            file.write(os.urandom(file_size))
            file.flush()
            os.fsync(file.fileno())
        # B. Delete File
        try:
            os.remove(file_path)
            self._logAuditEvent('Delete File Success', f'File {file_path} securely destroyed.')
        except OSError as e:
            print(f"Error deleting file: {e}")
            self._logAuditEvent('Delete File Failed', f'Error deleting file - {e}')


    # Method to delete audio file in a particular folder
    def _deleteAnyAudioFile(self, temp_path):
        try:
            # Iterate through the recorded folder
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if the file is a .audio file and older than 24 hours
                    if file.endswith(".wav") or file.endswith(".mp3"):
                        # Securely delete the file
                        self._secureDeleteFile(file_path)
                        print(f"Deleted {file_path}")
        except FileNotFoundError as e:
            print(f"Error: {e}")


    # Method to delete data that are older (in hours) on system startup
    def __deleteOldDataOnSystemStartUp(self):
        # Iterate through the recorded folder
        for root, dirs, files in os.walk(self.record_folder):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if the file is a .audio file and older than 24 hours
                if file.endswith(".audio") and self.__getfileAgeInHours(file_path) > 24:
                    # Securely delete the file
                    self._secureDeleteFile(file_path)
                    print(f"Deleted {file_path}")

        # Repeat the same process for the synthesized folder
        for root, dirs, files in os.walk(self.synthesis_folder):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if the file is a .audio file and older than 24 hours
                if file.endswith(".audio") and self.__getfileAgeInHours(file_path) > 24:
                    # Securely delete the file
                    self._secureDeleteFile(file_path)
                    print(f"Deleted {file_path}")
                    
    # Method to check for available and active audio devices
    def __audioIODeviceChecker(self):
        print("Device Checker")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("Checking for at least one microphone and one speaker...")
        
        input_device_found = self.__isAudioInputDeviceFound()
        output_device_found = self.__isAudioOutputDeviceFound()

        if input_device_found and output_device_found:
            print("\nAudio Input and output device found and active!")
            self._logAuditEvent('Audio Input and output device found and active!', \
                f' {input_device_found} \n {output_device_found}')
        else:
            print("\nNo Available or Active Input and output device!")    
            self._logAuditEvent('No Available or Active Input and output device!', \
                f' {input_device_found} \n {output_device_found}')
            
    
    def _systemStartUp(self):
        self.__deleteOldDataOnSystemStartUp()
        self.__audioIODeviceChecker()
        
                    
# start = AppStartUp()
# start._deviceIOChecker()

class Manager(AppStartUp):
    def __init__(self):
        super().__init__()
        self.configuration()
        self.db = RobotDatabase('modules/includes/modelgpt.db')
        
 
    # Search for file with file name and directory
    def _getfile(self,filename, search_path):
        for root, dirs, files in os.walk(search_path):
            if filename in files:
                return os.path.join(root, filename)
        return None

    # get current timestamp
    def getCurrentTimestamp(self, format_pattern='%y_%m_%d_%H%M%S'):
        current_time =  datetime.now().strftime(format_pattern)
        return current_time
     
 
    # Generate token using multiple values
    def generateToken(self, value1, value2, value3, value4, value5):
        import hashlib
        combined = str(value1) + str(value2) + str(value3) + str(value4) + str(value5)
        valued_token_object = hashlib.sha256(combined.encode())
        valued_token = valued_token_object.hexdigest()
        return valued_token

   # Step 2: Use Hashing for File Names
    def generateFileHash(self, file_content):
        return self._generateFileHash(file_content)

    # Step 3: Apply Access Controls: Read and write only for the file owner
    def setFilePermissions(self, file_path):
        return self._setFilePermissions(file_path) 

    # Step 4: Implement Encryption and Decryption
    def encodeDecodeFile(self, file_path, encryption_key, type='e'):
        if type == 'e':
            return self._encryptFile(file_path, encryption_key)
        elif type == 'd':
            return self._decryptFile(file_path, encryption_key)
        else:
            print(ReferenceError)

    # Step 5: Prevent Directory Traversal
    def sanitize_file_name(self, file_name):
        return os.path.basename(file_name)

    # Step 6: Audit Logs
    def logAuditEvent(self, event_type, event_description):
        return self._logAuditEvent(event_type, event_description)

    # Step 7: Securely deleting file
    def secureDeleteFile(self, file_path):
        return self._secureDeleteFile(file_path)

    # set config variables
    def configuration(self):
        # load openai API key
        config = ConfigParser()
        config.read(openaiAPI())
        api_key = config.get('openai', 'APIKEY')
        return api_key


def googlecloudAPI():
    return  'modules/includes/googlecloud-tts-api.json'

def openaiAPI():
    return   'modules/includes/openai.ini'  


class FileManager(Manager):
    def __init__(self):
        super().__init__()
        self.next_id = 0
        self.base_path = ""
        self.con_filename='modules/includes/consent'
        self.chat_log = ChatManager()		
        # Initialize the SQLite database
        self.lit_db = QSqlDatabase.addDatabase('QSQLITE')
        self.lit_db.setDatabaseName(self.con_filename+'.db')
        if  self.lit_db.open():
            print("DB Connection Established -----------------------------------SUCCESS")
#        else:
#            print(self.lit_db.lastError().text())

        # init ModelGPT SQLite database
       

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

    # Perform startup initialisation
    def tiagoGPTOnStartUp(self):
        self._systemStartUp()
        self._loadConnection()

    # Loads connection to DB
    def _loadConnection(self):
        self.db = RobotDatabase('modules/includes/modelgpt.db')
        self.db.create_table(
            'message_logs ',
            '''
                message_log_no INTEGER PRIMARY KEY AUTOINCREMENT,
                messages TEXT,
                created TEXT
            '''
        )
        
    # Get system resources
    def getSystemResource(self, filename):
        system_path = 'resources/system'        
        return super()._getfile(filename, system_path)

    # App themes selector
    def tiagoGPTTheme(self, install, name):
         # style 1
        if name =='dark':
            install.setStyle('fusion')
        # style 2 - load css skin
        if name == 'dOrange':
            qss_style = open(self.getSystemResource('dark_orange_style.qss'), 'r')
            install.setStyleSheet(qss_style.read())
        # style 3 - load css skin
        if name == 'dBlue':
            qss_style = open(self.getSystemResource('dark_blue_style.qss'), 'r')
            install.setStyleSheet(qss_style.read())
        # # style 4 - load css skin
        if name == 'light':
            qss_style = open(self.getSystemResource('lightstyle.qss'), 'r')
            install.setStyleSheet(qss_style.read())
            
    # Close connection
    def close(self):
        self.db.close()

    # generate a random unique token of 'length' characters that includes both letters and numbers
    def generateUniqueToken(self, length):
        import secrets, string
        characters = string.ascii_letters + string.digits
        unique_token = ''.join(secrets.choice(characters) for _ in range(length))
        return unique_token
    
    # save data to JSON file
    def saveToJSON(self, data: dict):
        self.data = data
        filename = self.con_filename+'.json'
        self.data_m.append(data)
        with open(filename, 'w') as file:
            json.dump(self.data, file, indent=4)
            # file.write('\n')
            
   
    def file_path(self, relative_path):
        try:
            self.base_path = sys._MEIPASS
        except Exception:
            self.base_path = os.path.abspath(".")
        return os.path.join(self.base_path, relative_path)	
    
    # read and return consent document
    def consent(self):
        text_file_path = "Consent.md" 

        # Read the content of the text file
        with open(text_file_path, "r") as file:
            file_content = file.read()
        return file_content

    # def show(self):
    #     self.window.show()
    #     sys.exit(self.app.exec())


class ChatManager(Manager):
    def __init__(self):
        super().__init__()
        self.chat_log_path = "resources/chat-log"
        self.con_filename='modules/includes/consent'
        self.loadData()
    
    # Getters and Setters
    def getChatLogPath(self):
        return self.chat_log_path

    def setChatLogPath(self, chat_log_path):
        self.chat_log_path = chat_log_path

 
    # Determine the number of entries and return the next available 'id' auto-incremental
    def getNextID(self, data):
        return len(data) + 1
        
    # Load the file 
    def loadData(self):
        try:
            filename = self.con_filename+'.json'
            with open(filename) as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = []

    # Save chat history to all storage location
    def saveChatToAll(self, active_tab, first_name):
		# Save Chat to db
        self.active_tab = active_tab
        chat_gui_log = active_tab.chat_graphic_display.toPlainText()
        timestamp = self.getCurrentTimestamp()
        messages = str(active_tab.modelgpt.messages).replace("'", "''")
        values = f"'{messages}','{timestamp}'"
        self.db.insert_record('message_logs', 'messages, created', values)
        print(f'Chat history saved to DB by {first_name} -------------------------------SUCCESS')    
		# wrapping up the message
        chat_history = "'''"+active_tab.chat_graphic_display.toPlainText()+"'''"
		# Save chat to text file
        self.saveChatHistoryToFile(chat_gui_log, timestamp)
		# This will be saved to a json file not text in a different directory
        self.saveChatHistoryToJSON(chat_history,f'''{self.getChatLogPath()}/chatDB/{timestamp}_{first_name}.json''', first_name)
        active_tab.status.showMessage('Chat saved!')

    # Save chat to text file
    def saveChatHistoryToFile(self, chat_gui_log, timestamp):
		# This will be saved to a json file not text in a different directory
        with open(f'{self.getChatLogPath()}/{timestamp}_Chat Log.txt', 'w', encoding='UTF-8') as _f:
            _f.write(chat_gui_log)
        print('''File saved at {0}/{1}_Chat Log.txt ----------------------------------------SUCCESS'''.format(self.getChatLogPath(), timestamp))
        self.active_tab.status.showMessage('''File saved at {0}/{1}_Chat Log.txt'''.format(self.getChatLogPath(), timestamp))

    # Saved chat to json file 
    def saveChatHistoryToJSON(self, data, filename, username):
        dialogues = []
        current_dialogue = None
        for line in data.split('\n'):
            if line.startswith("TiagoGPT"):
                if current_dialogue:
                    dialogues.append(current_dialogue)
                current_dialogue = {"user": "TiagoGPT", "messages": []}
            elif line.startswith(username):
                if current_dialogue:
                    dialogues.append(current_dialogue)
                current_dialogue = {"user": username, "messages": []}
            elif current_dialogue:
                current_dialogue["messages"].append(line.strip())
        if current_dialogue:
            dialogues.append(current_dialogue)
        with open(filename, 'w') as file:
            json.dump(dialogues, file, indent=4)

    # Save consent to all databases
    def saveConsentToAll(self, content,checkbox_voice, checkbox_text, checkbox_minor, name ):
        timestamp = self.getCurrentTimestamp('%Y-%m-%d %H:%M:%S')
        token = self.generateToken(name, checkbox_minor, checkbox_text, checkbox_voice, timestamp)
        data = {
            "id": self.getNextID(self.data),
            "content": content,
            "accept_voice": checkbox_voice,
            "accept_text": checkbox_text,
            "Is_minor": checkbox_minor,
            "full_name": name,
            "token": token,
            "timestamp": timestamp
        }
		# Save Consent to JSON file
        self.data.append(data)
        filename = self.con_filename+'.json'
        with open(filename, 'w') as file:
            json.dump(self.data, file, indent=4)
        print('Consent saved at 1st location -------------------------------------SUCCESS')

		# Save Consent to SQLite
        self.saveToSQL(content, checkbox_voice, checkbox_text, checkbox_minor, name)
        print('Consent saved at 2nd location -------------------------------------SUCCESS')

    # Save data to SQL
    def saveToSQL(self, content, accept_voice, accept_text, accept_minor, name ):
        pass


class AudioManager(Manager):
    def __init__(self, file_folder = "synthesized", format_pattern = '%d%m%y_%H%M%S', date_time = datetime.now()):
        super().__init__()
        self.root = "resources/audio"
        self.storage_directory = 'resources/audio/recorded'
        self.audio_path = self.root+'/'+file_folder
        self.format_pattern = format_pattern
        self.date_time = date_time
        self.sample_rate = 44100
        # Encryption key
        self.encryption_key = Fernet.generate_key()

    # Setters and Getters
    def get_audio_path(self):
        return self.audio_path

    def set_audio_path(self, file_folder):
        self.audio_path = self.root+'/'+file_folder

    def current_timestamp(self):
        return datetime.now().strftime(self.format_pattern)
    
    def audioTempDir(self,audio_name):
        temp_path = 'resources/system/temp'
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        self._deleteAnyAudioFile(temp_path)
        audio_path = os.path.join(temp_path, audio_name)
        return audio_path
        
    # Save the input recorded audio securely
    def saveAudio(self, output_file, audio_data='', sample_rate='', response=''):
        # save audio recording content
        if not response or (audio_data and sample_rate):
            self.storage_directory = 'resources/audio/recorded'
            sf.write(output_file, audio_data, sample_rate, 'PCM_16')
        elif not (audio_data and sample_rate) or response:
            self.storage_directory = 'resources/audio/synthesized'
            with open(self.audioTempDir(output_file), 'wb') as audio_output:
                audio_output.write(response)
                
        # Generate a unique file name using hashing for the saved audio
        audio_hash = self.generateFileHash(output_file)
        audio_name = f"{audio_hash}.audio"

        # Create new full file path for the hashed audio
        audio_path = os.path.join(self.storage_directory, audio_name)

        # Open the hashed audio file and encode the original content of the .wav file into it
        with open(audio_path, 'wb') as file:
            file.write(output_file.encode())

        # Set file permissions of the hashed file
        self.setFilePermissions(audio_path)

        # Encrypt the audio recording
        self.encodeDecodeFile(audio_path, self.encryption_key)
        self.logAuditEvent('Audio File Created', f"File {output_file} created and encrypted")



    def openAudioInput(self, file_path):
        # Decrypt the file
        decrypted_content = self.decryptFile(file_path, self.encryption_key)
        return decrypted_content
        

    def save_output(self, response, filetype="input"):
        timestamp = self.getCurrentTimestamp()
        if filetype.lower() == "input":
            self.set_audio_path("recorded")
            file_name = "recorded_audio_"
            output_file = f"{self.audio_path}/{file_name}{timestamp}.mp3"
            if not os.path.exists(self.audio_path):
                os.makedirs(self.audio_path)
            with open(output_file, 'wb') as audio_output:
                audio_output.write(response)
                print(f"Audio content written to file. ")
        elif filetype.lower() == "output":
            self.set_audio_path("synthesized")
            file_name = "synthesized_audio_"
            if not os.path.exists(self.audio_path):
                os.makedirs(self.audio_path)
            output_file = f"{file_name}{timestamp}.mp3"
            self.saveAudio(output_file=output_file, response=response)
            # with open(self.audioTempDir(), 'wb') as audio_output:
            #     audio_output.write(response)
            print(f"Synthesized audio written to file") # at {self.audio_path}/synthesized_audio_{timestamp}.mp3")


    def recent_file_finder(self, path="resources/system/temp", ext="mp3"):
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


class LogManager(Manager):
    def __init__(self):
        super().__init__()
        # Create a logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        directory = 'resources/system/log/log.txt'
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Create a file handler
        self.file_handler = logging.FileHandler(directory)
        self.file_handler.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        self.logger.addHandler(self.file_handler)


