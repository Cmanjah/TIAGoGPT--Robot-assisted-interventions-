from PyQt6.QtCore import pyqtSignal, QThread

# Code borrowed from https://www.youtube.com/watch?v=snkys9zXyD0
# Author: Jie Jenn
# Date: March 2023
# Modified version of the original code to synthesize text
# Changes: Added dict 'system' role and content to message property
class ModelGPTThread(QThread):
	clear_input = pyqtSignal()
	response_received = pyqtSignal(dict)
	

	def __init__(self, parent):
		super().__init__(parent)
		self.ai_assistance = parent
		
	def run(self):
		text_string = ""
		if not self.ai_assistance.transcribed_string and self.ai_assistance.message_input.toPlainText():
			text_string = self.ai_assistance.message_input.toHtml()
		elif self.ai_assistance.transcribed_string and not self.ai_assistance.message_input.toPlainText():
			text_string = self.ai_assistance.transcribed_string
		self.clear_input.emit()
		
		# make an api call to OpenAI ModelGPT model
		max_tokens = self.ai_assistance.max_tokens.value()
		temperature = float('{0:.2f}'.format(self.ai_assistance.temperature.value() / 100))
		response = self.ai_assistance.modelgpt.generateResponse(text_string.strip(), max_tokens=max_tokens, temperature=temperature)
		self.clear_input.emit()
		self.ai_assistance.text_synthesis.synthesizeText(response['content'])
		self.response_received.emit(response)

     
class SynthesisingThread(QThread):
    synthesiseAudio = pyqtSignal(dict)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.ai_assistance = parent
        
    def run(self):
        greetings = self.ai_assistance.modelgpt.greetResponse(self.ai_assistance.mode)
        self.ai_assistance.text_synthesis.synthesizeText(greetings['content'])
        self.synthesiseAudio.emit(greetings)
        
  
  
class AudioRecordingThread(QThread):
    recordStarted = pyqtSignal()
    recordStopped = pyqtSignal()
    recordingEnded = pyqtSignal(str)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.ai_assistance = parent
    
    def run(self):
        self.recordStarted.emit()
        prompt = self.ai_assistance.recorder.startRecording()
        try:
            transcribed_string = self.ai_assistance.transcribe.transcribeVoice(prompt)
            self.recordingEnded.emit(transcribed_string)
        except Exception as e:
            print(f'Voice transcription could not be done. Start Voice recording again! \n \error: {e}')
        # Securely delete the audio file 
        self.ai_assistance.audio_manager.secureDeleteFile(prompt)
    
        
    def endListening(self):
        try:
            self.ai_assistance.recorder.stopRecording()
        except Exception as e:
            print(f"Could not stop: {e}")
        
