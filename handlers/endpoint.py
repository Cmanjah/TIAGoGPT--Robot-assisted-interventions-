import os, pygame
from google.cloud import texttospeech
import openai
from handlers.manager import AudioManager
# from handlers.synthesizer import Synthesizer


def googlecloudAPI():
    return  'handlers/includes/googlecloud-tts-api.json'

def openaiAPI():
    return   'handlers/includes/api_key.ini'  

class ModelGPT:
    def __init__(self, api_key):
        self.openai = openai
        self.openai.api_key = api_key
        self.messages = []
        # self.text_synthesis = Synthesizer()

    def sendRequest(self, prompt, max_tokens=100, temperature=1.0):  # max_tokens reduced from 1000 to 100
        try:
            self.messages.append({'role': 'user', 'content': prompt})
            response = self.openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                # model = "text-davinci-003",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=self.messages
            )
            self.messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
            # self.text_synthesis.synthesizeText(response.choices[0].message.content)
            return {'usage': response.usage.total_tokens, 'content': response.choices[0].message.content}
        except Exception as e:
            return {'error': e}
        
        
# Conversion Agent
class ChatAI: 
    def __init__(self, api_key):
        self.openai = openai
        self.openai.api_key = api_key
        self.prompt = []
        
    def requestSendToAI(self, prompt, max_token=150, temperature=0.9):
        try:
            self.prompt.append({'role': 'user', 'content': prompt})
            response = openai.Completion.create(
                model="text-davinci-003",
                # model='gpt-3.5-turbo',
                prompt=self.prompt,
                temperature=temperature,
                max_tokens=max_token,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                stop=[" Username:", " Tiago:"]
            )
            self.prompt.append({'role': 'assistant', 'content': response})
            return {'usage': response.usage.total_tokens, 'content': response}
        except Exception as e:
            return {'error': e}

    
class Transcriber:
    def __init__(self, api_key):
        # pass
        self.api_key = api_key
        self.model_id = 'whisper-1'

    def transcribeVoice(self, prompt):
        media_file_path = prompt
        media_file = open(file=media_file_path, mode='rb')

        response = openai.Audio.transcribe(
            api_key=self.api_key,
            model=self.model_id,
            file=media_file,
            response_format = 'text'    # text, json, srt, vtt
        )
        return response

# print(response)
    
class Synthesizer:
    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS']= googlecloudAPI()
        self.client = texttospeech.TextToSpeechClient()
        pygame.init()
        # Initialize the pygame mixer module
        # pygame.mixer.init()
        self.audio_manager = AudioManager()
        
 
    def autoplay(self, audio_file):
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        # pygame.time.wait(2000)  # Wait for the playback to finish: for  seconds (adjust as needed)
        
        while pygame.mixer.music.get_busy():
            continue  # Wait until the audio finishes playing
        pygame.quit()


    def synthesizeText(self, text):
        """Synthesizes speech from the input string of text."""
        input_text = texttospeech.SynthesisInput(text=text)
        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-C",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )

        # The response's audio_content is binary.        
        # with open("media/data/output.mp3", "wb") as out:
        #     out.write(response.audio_content)
        #     print('Audio content written to file "output.mp3"')
        
        self.audio_manager.save_output(response.audio_content, filetype="output")       
        # Play the recently saved audio content
        self.autoplay(self.audio_manager.recent_file_finder())
        
