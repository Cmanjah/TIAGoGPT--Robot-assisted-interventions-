import glob
import os, sys
import soundfile as sf
from datetime import datetime


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
                print(f"Audio content written to file at {os.getcwd()}/{self.audio_path}/synthesized_audio_{timestamp}.mp3")
        elif filetype.lower() == "output":
            self.set_audio_path("synthesized")
            file_name = "synthesized_audio_"
            if not os.path.exists(self.audio_path):
                os.makedirs(self.audio_path)
            with open(f"{self.audio_path}/{file_name}{timestamp}.mp3", 'wb') as audio_output:
                audio_output.write(response)
                print(f"Audio content written to file at {os.getcwd()}/{self.audio_path}/synthesized_audio_{timestamp}.mp3")


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


class VoicePromptManager:
    def __init__(self) -> None:
        self.input
    
    

class ChatManager:
    def __init__(self):
        self.chat_log_path = "media/chat-log"
    
    
    # Getters and Setters
    def get_chat_log_path(self):
        return self.chat_log_path


    def set_chat_log_path(self, chat_log_path):
        self.chat_log_path = chat_log_path



class LogManager:
    def __init__(self) -> None:
        pass
    
    
class FileManager:
    def __init__(self,):
        self.base_path = ""
        
    
    def file_path(self, relative_path):
        try:
            self.base_path = sys._MEIPASS
        except Exception:
            self.base_path = os.path.abspath(".")
        return os.path.join(self.base_path, relative_path)	
    
    def consent(self):
        text_file_path = "media/system/template/consent.txt"  # Replace this with the path to your text file

        # Read the content of the text file
        with open(text_file_path, "r") as file:
            file_content = file.read()
        return file_content
	
