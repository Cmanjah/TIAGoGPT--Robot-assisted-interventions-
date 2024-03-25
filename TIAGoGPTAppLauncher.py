# This is the GUI interfacing both the controllers and the module
# Modified version of the original code to handle edge cases
# Changes: Added dict 'system' role and content to message property
import sys, time
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QSlider, QTextBrowser
from PyQt6.QtWidgets import QTabWidget, QTextEdit, QCheckBox, QLineEdit, QMenu, QMenuBar, QSplitter
from PyQt6.QtWidgets import QToolButton, QStatusBar,QHBoxLayout, QVBoxLayout, QFormLayout, QSizePolicy
from PyQt6.QtCore import Qt,pyqtSignal
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence, QPixmap
from modules.EndPointModule import ModelGPT, Synthesizer, Transcriber
from modules.AudioRecordingModule import AudioRecorder
from controller.AppController import FileManager, ChatManager, AudioManager
from controller.ThreadSignalController import *

class AIAssistedActivity(QWidget):
	def __init__(self, firstname, parent=None):
		super().__init__()
		self.mode = ""
		self.chat_holder= ''
		self.transcribed_string = ""
		# Initialize Components
		self.modelgpt = ModelGPT(start())
		self.thread_model = ModelGPTThread(self)
		# initialise the audio recorder
		self.recorder = AudioRecorder()
		self.audio_manager = AudioManager()
		# transcriber
		self.transcribe = Transcriber(start())
  		# synthesizer
		self.text_synthesis = Synthesizer()
		# Instantiate the threads
		self.thread_model = ModelGPTThread(self)
		self.thread_audio = AudioRecordingThread(self)
		self.thread_synthesis = SynthesisingThread(self)

		self.ai_firstname = firstname
		self.modelgpt.setUsername(firstname)

		self.layout = {}
		self.layout['main'] = QVBoxLayout()
		self.setLayout(self.layout['main'])
		self.splitter = QSplitter(Qt.Orientation.Vertical)		

		# Create widgets
		self.message_input = QTextEdit(placeholderText='Enter your prompt here')
		self.btn_vprompt = QPushButton('&Voice Prompt') #, clicked=self.voicePrompt)
		self.btn_tprompt = QPushButton('&Text Prompt') #, clicked=self.textPrompt)
		self.btn_voice = QPushButton('&Start voice', clicked=self.startListener)
		self.btn_submit = QPushButton('&Submit text', clicked=self.postMessage)
		self.btn_clear = QPushButton('&Clear', clicked=self.reset_input)
		self.btn_stop = QPushButton('&Stop voice', clicked=self.stopListener)

		self.initializeUserAIAssistanceUI()
		self.initializeUserAIAssistanceDefaultSettings()
		self.initializeSignalConfigAIAssistance()

		# activate thread signals
		self.thread_model.clear_input.connect(self.message_input.clear)
		self.thread_model.response_received.connect(self.updateChatGraphicDisplay)
		self.thread_audio.recordingEnded.connect(self.listeningEnded)  
		self.thread_synthesis.synthesiseAudio.connect(self.synAudio)

	# Initialize GUI for user ai-assistance
	def initializeUserAIAssistanceUI(self):
		# add sub layout manager
		self.layout['inputs'] = QFormLayout()

		# add sliders
		self.max_tokens = QSlider(Qt.Orientation.Horizontal, minimum=10, maximum=4096, singleStep=500, pageStep=500, value=50, toolTip='Maxium token the LL model can consume')
		self.temperature = QSlider(Qt.Orientation.Horizontal, minimum=0, maximum=200, value=10, toolTip='Randomness of the response')

		self.max_tokens.hide()
		self.temperature.hide()
  		
    	# organize widgets	  
		# ----------------	  
		# maximum token slider
		self.max_token_value = QLabel('0.0')
		self.layout['slider_layout'] = QHBoxLayout()
		self.layout['slider_layout'].addWidget(self.max_token_value)
		self.layout['slider_layout'].addWidget(self.max_tokens)
		self.layout['inputs'].addRow(self.layout['slider_layout'])


		# temperature slider
		self.temperature_value = QLabel('0.0')
		self.layout['slider_layout2'] = QHBoxLayout()
		self.layout['slider_layout2'].addWidget(self.temperature_value)
		self.layout['slider_layout2'].addWidget(self.temperature)
		self.layout['inputs'].addRow(self.layout['slider_layout2'])
		self.layout['main'].addLayout(self.layout['inputs'])

		self.max_token_value.hide()
		self.temperature_value.hide()
  
		self.layout['main'].addWidget(self.splitter)


		# Chat GUI
		self.chat_graphic_display = QTextBrowser(openExternalLinks=True)
		self.chat_graphic_display.setReadOnly(True)
		self.chat_graphic_display.setEnabled(False)
		self.splitter.addWidget(self.chat_graphic_display) 

		# message input field
		self.message_field = QWidget()
		self.layout['input entry'] = QHBoxLayout(self.message_field)
		self.message_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.layout['input entry'].addWidget(self.message_input)

		# submit text and clear input buttons
		self.layout['button'] = QVBoxLayout()
		self.layout['button'].addWidget(self.btn_submit)
		self.layout['button'].addWidget(self.btn_clear, alignment=Qt.AlignmentFlag.AlignTop)
		self.btn_submit.setFixedSize(170, 40)
		self.btn_clear.setFixedSize(170, 40)
		self.layout['input entry'].addLayout(self.layout['button'])

		# voice and text prompt mode button
		self.layout['buttons'] = QHBoxLayout()
		self.layout['buttons'].addWidget(self.btn_voice) #, alignment=Qt.AlignmentFlag.AlignTop)
		self.layout['buttons'].addWidget(self.btn_stop)
		self.layout['buttons'].addWidget(self.btn_vprompt)
		self.layout['buttons'].addWidget(self.btn_tprompt)
		self.layout['input entry'].addLayout(self.layout['buttons'])
  
		# Initial characteristics set
		self.btn_voice.setFixedSize(170, 40)
		self.btn_stop.setFixedSize(170, 40)
		self.btn_vprompt.setFixedSize(170, 40)
		self.btn_tprompt.setFixedSize(170, 40)
		self.message_input.hide()
		self.btn_voice.hide()
		self.btn_stop.hide()
		self.btn_submit.hide()
		self.btn_clear.hide()
		self.btn_vprompt.hide()
		self.btn_vprompt.setEnabled(False)
		self.message_input.setEnabled(False)
		self.btn_voice.setEnabled(False)
		self.btn_stop.setEnabled(False)
		self.btn_submit.setEnabled(False)
		self.btn_clear.setEnabled(False)

		if not self.ai_firstname == 'Anonymous':
			self.btn_vprompt.show()
			self.btn_vprompt.setEnabled(True)

		# Voice prompt action set
		self.btn_vprompt.clicked.connect(lambda:(
			self.voicePrompt()			
		))
		# Text prompt action set
		self.btn_tprompt.clicked.connect(lambda:(
			self.textPrompt(),
		))

		self.splitter.addWidget(self.message_field)
		self.splitter.setSizes([800, 200])

		# add status bar
		self.status = QStatusBar()
		self.status.setStyleSheet('font-size: 12px; color: white;')
		self.layout['main'].addWidget(self.status)

	# intialize user settings for the ai-assistance
	def initializeUserAIAssistanceDefaultSettings(self):
		# token slider
		self.max_tokens.setTickPosition(QSlider.TickPosition.TicksBelow)
		self.max_tokens.setTickInterval(500)
		self.max_tokens.setTracking(True)
		self.max_token_value.setText('{0:,}'.format(self.max_tokens.value()))

		# temperature slider
		self.temperature.setTickPosition(QSlider.TickPosition.TicksBelow)
		self.temperature.setTickInterval(10)
		self.temperature.setTracking(True)
		self.temperature_value.setText('{0:.2f}'.format(self.temperature.value() / 100))

	# initialize 
	def initializeSignalConfigAIAssistance(self):
		self.max_tokens.valueChanged.connect(lambda: self.max_token_value.setText('{0: ,}'.format(self.max_tokens.value())))
		self.temperature.valueChanged.connect(lambda: self.temperature_value.setText('{0: .2f}'.format(self.temperature.value() / 100)))


	def updateChatGraphicDisplay(self, message):			
		if 'error' in message:
			self.status.setStyleSheet('''
				color: red;
			''')
			self.clear_input()
			self.status.showMessage(message['error'].user_message)
			return
		
		self.btn_voice.setEnabled(False)
		self.btn_stop.setEnabled(True)
		self.btn_voice.setText("Please wait!")
		self.btn_voice.setStyleSheet('''
				color: red;
				border: 2px solid red;
			''')

		# TIAGo response placeholder container
#		self.text_synthesis.synthesizeText(message['content'])
		self.chat_holder+=  '<div style="margin-bottom: 15px; padding:2px 5px 2px 5px; border-radius: 25px; border: 5px solid #fd9620; width:100px; float:left">'
		self.chat_holder+=  '<span style="color:#fd9620; float:left; font-style:italic; font-weight:bold;">TiagoGPT</span>'
		self.chat_holder+=  '<br/>' +message['content'].strip() + '</div>'
		self.chat_graphic_display.setMarkdown(self.chat_holder)		
		self.status.showMessage('Tokens used status: {0}'.format(message['usage']))
			
		self.btn_submit.setEnabled(True)
		self.btn_clear.setEnabled(True)
		self.btn_submit.setText('&Submit text')
  

		if self.mode == 'voice':
			self.btn_voice.setEnabled(True)
			self.btn_stop.setEnabled(False)
			self.btn_voice.setText("&Start voice")
			# Listening Loop
			time.sleep(2)
			self.startListener()

	# Submit user inputted text
	def postMessage(self): 
		if not self.message_input.toPlainText():
			self.btn_clear.setEnabled(True)
			self.status.showMessage('Prompt field is empty.')
			return
		else:
			self.status.clearMessage()
			self.btn_clear.setEnabled(True)

		self.chat_graphic_display.setEnabled(True)
		self.btn_submit.setEnabled(False)
		self.btn_submit.setText('Please wait!')
		self.btn_clear.setEnabled(False)
		text_string = self.message_input.toPlainText()

		self.chat_holder+=  '<div style="margin-bottom: 15px; padding:2px 5px 2px 5px; border-radius: 25px; border: 5px solid #5caa00; width:300px; float:right">'
		self.chat_holder+= f'<span style="color:#5caa00; float: left; font-style: italic; font-weight: bold;">{self.ai_firstname}</span>'	
		self.chat_holder+= '<br/>' + text_string + '</div>'
		self.chat_graphic_display.setMarkdown(self.chat_holder)

		self.thread_model.start()
		self.thread_model.quit()


	# Voice prompt button action
	def voicePrompt(self):
		self.btn_vprompt.setEnabled(False)
		self.btn_vprompt.hide()
		self.btn_tprompt.hide()
		
		self.chat_graphic_display.setEnabled(True)
		self.btn_voice.show(),
		self.btn_stop.show(),
		self.btn_voice.setText('Please wait!')
		self.btn_voice.setStyleSheet('''
				color: red;
				border: 2px solid red;
			''')
		self.btn_voice.setEnabled(False)
		self.btn_stop.setEnabled(True)
		self.message_input.hide(),
		self.btn_submit.hide(),
		self.btn_clear.hide(),
		self.btn_stop.show(),
		self.status.showMessage('Voice mode activated!'), 

		self.mode = 'voice'
		self.thread_synthesis.start()
		self.thread_synthesis.quit()
  
	def synAudio(self, greetings):
		self.updateChatGraphicDisplay(greetings)

	def textPrompt(self):
		self.btn_vprompt.setEnabled(False)
		self.btn_tprompt.setEnabled(False)
		self.btn_vprompt.hide()
		self.btn_tprompt.hide()			
		self.btn_voice.hide(),
		self.btn_stop.hide(),
		self.chat_graphic_display.setEnabled(True)
		self.message_input.setEnabled(True)
		self.btn_submit.setEnabled(False),
		self.btn_submit.setText('Please Wait!')
		self.btn_clear.setEnabled(True),
		self.message_input.show(),
		self.btn_submit.show(),
		self.btn_clear.show(),
		self.btn_stop.hide(),
		self.status.showMessage('Text mode activated!'), 

		self.mode = 'text'
		self.thread_synthesis.start()
		self.thread_synthesis.quit()
    
	def startListener(self):
		self.status.showMessage('Conversation in progress...'), 
		self.btn_voice.setText('Listening...')
		self.btn_voice.setStyleSheet('''
				color: green;
				border: 2px solid green;
			''')
		self.btn_voice.setEnabled(False)
		self.btn_stop.setEnabled(True)
		self.btn_vprompt.hide()
		self.btn_tprompt.hide()

		self.thread_audio.start()
		self.thread_audio.quit()	

	def listeningEnded(self, transcribed_string):

		self.transcribed_string = transcribed_string
		text_string = transcribed_string

		self.btn_voice.setText('Please wait!')
		self.btn_voice.setStyleSheet('''
				color: red;
				border: 2px solid red;
			''')
		self.btn_voice.setEnabled(False)
		self.btn_stop.setEnabled(False)

		self.chat_holder+=  '<div style="margin-bottom: 15px; padding:2px 5px 2px 5px; border-radius: 25px; border: 5px solid #5caa00; width:300px; float:right">'
		self.chat_holder+= f'<span style="color:#5caa00; float: right; font-style: italic;'
		self.chat_holder+= f'font-weight: bold;">{self.ai_firstname}</span>'		
		self.chat_holder+= '<br />' + text_string + '</div>'
		self.chat_graphic_display.setMarkdown(self.chat_holder)

		self.thread_model.start()
		self.thread_model.quit()
     
          
	def stopListener(self):
		if self.thread_audio:
			self.status.showMessage('Conversation stopped!')
			self.btn_voice.setText("&Start voice")
			self.btn_voice.setEnabled(True)
			self.btn_voice.setStyleSheet('''
				border: 2px solid green;
			''')
			self.btn_stop.setEnabled(False)
			self.thread_audio.endListening()
			# return self.recorder.stopRecording()
		# else:
			# self.btn_stop.hide()
			# self.status.showMessage('Listening has not started')

	def reset_input(self):
		self.message_input.clear()		
		self.status.clearMessage()

	def clear_input(self):
		self.btn_submit.setEnabled(True)
		self.btn_submit.setText('&Submit text')
		self.message_input.clear()

	def zoomIn(self):
		font = self.message_input.font()
		# increase font size only when current size is less than 30 pixel
		if font.pixelSize() < 30:
			self.message_input.setStyleSheet('font-size: {0}px'.format(font.pixelSize() + 2))
			self.chat_graphic_display.setStyleSheet('font-size: {0}px;'.format(font.pixelSize() + 2))

	def zoomOut(self):		
		font = self.message_input.font()
		# decrease font size only when current size is smaller than 5
		if font.pixelSize() > 5:
			self.message_input.setStyleSheet('font-size: {0}px'.format(font.pixelSize() - 2))
			self.chat_graphic_display.setStyleSheet('font-size: {0}px;'.format(font.pixelSize() - 2))		
	
def start():
    return file_manager.configuration()
 
class TabManager(QTabWidget):
	# add customized signals
	plusClicked = pyqtSignal()

	def __init__(self, parent=None):
		super().__init__(parent)
		# add tab close button
		self.setTabsClosable(True)

		# Create the add tab button and implement signals
		self.add_tab_button = QToolButton(self, text='+')
		self.add_tab_button.clicked.connect(self.plusClicked)
		self.setCornerWidget(self.add_tab_button)

		self.tabCloseRequested.connect(self.closeTab)

	def closeTab(self, tab_index):
		# self.tab_index_tracker += 1
		if self.count() == 1:
			return  
		self.removeTab(tab_index)


class TIAGoGPTAppActivity(QWidget):
	def __init__(self):
		super().__init__()
		self.app_width, self.app_height = 1020, 600
		self.setMinimumSize(self.app_width, self.app_height)
		self.setWindowIcon(QIcon(file_manager.getSystemResource("tiago.png")))
		self.setWindowTitle('TiagoGPT Chatting Software')
		self.setStyleSheet('''
			QWidget {
				font-size: 13px;				
			}
		''') 
		self.first_name = 'Anonymous'
		self.tab_index_tracker = 1	
		self.layout = {}  
		self.layout['main'] = QVBoxLayout()
		self.setLayout(self.layout['main'])
		self.layout['main'].insertSpacing(0, 19)
		
		# initialize menu 
		self.menu_bar = QMenuBar(self)
		self.menu_bar.hide()
		self.initMenu()
		self.initShortcutKeys()
  
		# Initialize the Widget
		self.btn_vprompt = QPushButton('Voice Prompt', clicked=self.consentPageInterface)
		self.vhorizontal_divider = QSplitter(Qt.Orientation.Vertical)		
		self.vconsent_display = QTextBrowser(openExternalLinks=True, placeholderText='[Consent Form Placeholder - Voice Prompt]')
		self.vconsent_1_CheckBox = QCheckBox('I hereby give my consent for the collection and use of my data as described above.', clicked=self.consent_check_voice)
		self.vconsent_2_CheckBox = QCheckBox('I hereby with hold my consent', clicked=self.consent_check_text)
		self.vconsent_minor = QCheckBox("Legal guardian providing consent on behalf of a minor? (if yes, please select)", clicked=self.consent_minor)
		self.vmessage_field = QWidget()
		self.vsign_input = QLineEdit(placeholderText='Enter your full name to sign')
		self.vbtn_decline = QPushButton('Decline', clicked=self.declineConsentReducedFunctionality)
		self.vbtn_agree = QPushButton('Agree', clicked=self.acceptConsentFullFunctionality)
	
 		# initialize dashboard
		self.dashboard()
 
	
 	######## Home Page: Entry Point of the TAIGoGPT App ########
	# 
	def dashboard(self):
		print("Component Initialisation ------------------------------------------------SUCCESS")	
		image_path = file_manager.getSystemResource("tiago.png")  # Replace this with the method from the FileManager object
		pixmap = QPixmap(image_path)
		# Set the desired width and height for the displayed image
		desired_width = 350
		desired_height = 450
		# Scale the image to the desired dimensions while maintaining aspect ratio
		scaled_pixmap = pixmap.scaled(desired_width, desired_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
		image = QLabel()
		image.setPixmap(scaled_pixmap)
		# Set Image to the center of the QLabel
		image.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.layout['pix'] = QVBoxLayout()
		self.layout['pix'].addWidget(image)
		self.layout['main'].addLayout(self.layout['pix'])

		# organize widgets	  
		self.btn_start = QPushButton('Start') #, clicked=self.consentPageInterface)
		self.btn_start.setFixedSize(170, 40)
		self.layout['start_tiagogpt'] = QHBoxLayout()
		self.layout['start_tiagogpt'].addWidget(self.btn_start)
		self.layout['main'].addLayout(self.layout['start_tiagogpt'])

		# Start Button Action
		self.btn_start.clicked.connect(lambda:(
			image.hide(),
			self.btn_start.hide(),
			print(">>Consent Request Form presented"),
			# Initialize the Consent Form
   			self.consentPageInterface(),
		))
  
 	######## Page Two: Consent and Disclaimer Page of the TAIGoGPT App ########
	# 
	def consentPageInterface(self):
		# add sub layout manager
		self.layout['dashboard'] = QFormLayout()

		# self.vhorizontal_divider = QSplitter(Qt.Orientation.Vertical)		
		self.layout['main'].addWidget(self.vhorizontal_divider)

		# Consent display customization
		self.vconsent_display.setMarkdown(f"{file_manager.consent()}")  # Wrap the content in <pre> tag to preserve formatting
		self.vconsent_display.setReadOnly(True)
		self.vhorizontal_divider.addWidget(self.vconsent_display) 

		# set initial states of the checkboxes
		self.vconsent_1_CheckBox.setChecked(False)
		self.vconsent_2_CheckBox.setChecked(True)
		self.vconsent_minor.hide()

		# Checkboxes layout customization
		self.layout['vconsent_entry'] = QHBoxLayout(self.vmessage_field)
		self.layout['vconsent_options'] = QVBoxLayout()
		self.layout['vconsent_options'].addWidget(self.vconsent_1_CheckBox)
		self.layout['vconsent_options'].addWidget(self.vconsent_minor)
		self.layout['vconsent_options'].addWidget(self.vconsent_2_CheckBox)
		self.layout['vconsent_entry'].addLayout(self.layout['vconsent_options'])
 
		# Message field layout customization
		self.vsign_input.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.vsign_input.setFixedSize(250, 40)
		self.vsign_input.setEnabled(False)
		self.layout['vconsent_options'].addWidget(self.vsign_input)

		# Consent page checkbox actions
		# ACTION-1
		self.vconsent_1_CheckBox.clicked.connect(lambda:(
			self.vsign_input.setEnabled(True),
			self.vconsent_2_CheckBox.setChecked(False),
			self.vconsent_minor.show(),
			self.vconsent_minor.setChecked(False),
			print(">> Consent for Minor indicated")
		))
		# ACTION-2
		self.vconsent_2_CheckBox.clicked.connect(lambda:(
			self.vsign_input.setEnabled(False),
			self.vconsent_1_CheckBox.setChecked(False),
			self.vconsent_minor.setChecked(False),
			self.vconsent_minor.hide(),
			print(">> Consent still on default: withhold")
		))
		# ACTION-3
		self.vconsent_minor.clicked.connect(lambda:(
			self.vconsent_1_CheckBox.setChecked(True),
			self.vconsent_2_CheckBox.setChecked(False),
			self.vsign_input.setEnabled(True),
			print(">> Consent for Minor indicated")
		))

		# set initial state of the buttons
		self.vbtn_agree.setEnabled(True)
		self.vbtn_decline.setEnabled(True)

		# Decline and Agree buttons layout customization
		self.layout['vbuttons'] = QVBoxLayout()
		self.layout['vbuttons'].addWidget(self.vbtn_agree, alignment=Qt.AlignmentFlag.AlignTop)
		self.vbtn_agree.setFixedSize(170, 40)
		self.layout['vbuttons'].addWidget(self.vbtn_decline, alignment=Qt.AlignmentFlag.AlignTop)
		self.vbtn_decline.setFixedSize(170, 40)
		self.layout['vconsent_entry'].addLayout(self.layout['vbuttons'])


		# Add vhorizontal_divider
		self.vhorizontal_divider.addWidget(self.vmessage_field)
		self.vhorizontal_divider.setSizes([800, 200])
  
  		# add status bar
		self.status = QStatusBar()
		# self.status.setStyleSheet('font-size: 12px; color: red;')
		self.layout['status_message'] = QVBoxLayout()
		self.layout['status_message'].addWidget(self.status)
		self.layout['main'].addLayout(self.layout['status_message'])

	def consent_check_voice(self):
		pass

	def consent_check_text(self):
		pass
	
	# User decline consent
	def declineConsentReducedFunctionality(self):
		if self.vconsent_1_CheckBox.isChecked() or self.vsign_input.text() or self.vconsent_minor.isChecked() or self.acceptConsentFullFunctionality():
			self.status.showMessage('To decline, please check the withhold consent box.')
			return
		elif self.vconsent_2_CheckBox.isChecked():
			print(">> Consent not given")

			widgets = [
				self.vhorizontal_divider,
				self.vconsent_display,
				self.vconsent_1_CheckBox,
				self.vconsent_2_CheckBox,
				self.vmessage_field,
				self.vsign_input,
				self.vbtn_decline,
				self.vbtn_agree
			]
			for widget in widgets:
				if widget.isVisible():
					widget.hide()
		
			print(">>Consent Request completed!")
			self.status.clearMessage()
			self.menu_bar.show()
			self.initializeTIAGoGPTAppUI()
			self.btn_vprompt.hide()
			self.initializeSignalConfig()
			# Use default user name for declined consent
			self.username()
		else:
			print("No more option available!")
			return

	def consent_minor(self):
		pass

	def username(self, fullname = 'anonymous user'):    
		name_parts = fullname.split()
		self.first_name = name_parts[0].capitalize()
		self.surname = name_parts[-1].capitalize()
		return (self.first_name +' '+ self.surname)
    
	def acceptConsentFullFunctionality(self):
		if not self.vconsent_1_CheckBox.isChecked():
			self.status.showMessage('Please provide your consent by checking the box.')
			return
		elif not self.vsign_input.isEnabled():
			self.vconsent_2_CheckBox.setChecked(False)
			self.vsign_input.setEnabled(True)
			self.status.showMessage('Please type in your full name in the field to sign.')
			return
		elif not self.vsign_input.text():
			self.status.showMessage('Field is empty.')
			return
		else:
			self.status.clearMessage()
			print(">> Consent given!")

			# Get the user name
			self.username(fullname=self.vsign_input.text())
   
			# save consent 
			self.saveConsent()
   
			widgets = [
				self.vhorizontal_divider,
				self.vconsent_display,
				self.vconsent_1_CheckBox,
				self.vconsent_2_CheckBox,
				self.vmessage_field,
				self.vsign_input,
				self.vbtn_decline,
				self.vbtn_agree
			]
			for widget in widgets:
				if widget.isVisible():
					widget.hide()
		
			print(">> Consent Request completed!")
			self.menu_bar.show()
			self.initializeTIAGoGPTAppUI()
			self.initializeSignalConfig()
        
 	######## Page Three: Conversation Mode Selection Page of the TAIGoGPT App ########

	# Initialize application UI
	def initializeTIAGoGPTAppUI(self):
		# add tab  manager
		self.tab_manager = TabManager()
		self.layout['main'].addWidget(self.tab_manager)
		self.ai_assistance = AIAssistedActivity(self.first_name)
#		print('ai_assistance.ai_firstname: ',ai_assistance.ai_firstname)
		self.tab_manager.addTab(AIAssistedActivity(self.first_name), ' Mode #{0}'.format(self.ai_assistance.mode, self.tab_index_tracker))
		self.setTabFocus()
	
	# Initialize menu
	def initMenu(self):
		file_menu = QMenu('&File', self.menu_bar)
		file_menu.addAction('&New mode', self.addPageTab)
		file_menu.addAction('&Continue from previous')
		file_menu.addAction('&Open recent')
		file_menu.addSeparator()
		file_menu.addAction('&Save chat history', self.saveChat)
		file_menu.addAction('&Close current tab', self.close_tab)
		file_menu.addSeparator()
		file_menu.addAction('&Settings', self.tiagoGPTSettings)
		file_menu.addAction('&Exit', self.exitApp)
		self.menu_bar.addMenu(file_menu)

		# view menu
		view_menu = QMenu('&View', self.menu_bar)
		view_menu.addAction('Zoom &in', self.zoomIn)
		view_menu.addAction('Zoom &out', self.zoomOut)
		self.menu_bar.addMenu(view_menu)

		# help menu
		help_menu = QMenu('&Help', self.menu_bar)
		help_menu.addAction('&External link')
		help_menu.addAction('&Update')
		help_menu.addAction('&About')
		self.menu_bar.addMenu(help_menu)

	# Initialize ShortcutKeys
	def initShortcutKeys(self):
		shortcut_add_tab = QShortcut(QKeySequence('Ctrl+T'), self)
		shortcut_close_tab = QShortcut(QKeySequence('Ctrl+Shift+T'), self)
		
		shortcut_add_tab.activated.connect(self.addPageTab)
		shortcut_close_tab.activated.connect(self.close_tab)

	def initializeSignalConfig(self):
		self.tab_manager.plusClicked.connect(self.addPageTab)

	def setTabFocus(self):
		activate_tab = self.tab_manager.currentWidget()
		activate_tab.message_input.setFocus()

	def close_tab(self):
		self.tab_manager.closeTab

	def addPageTab(self):
		self.tab_index_tracker += 1
		# This section will show the persons name as the name of the tab. when conversion begins
		self.tab_manager.addTab(AIAssistedActivity(self.first_name),'Mode #{0}'.format(self.tab_index_tracker))
		self.tab_manager.setCurrentIndex(self.tab_manager.count()-1)
		self.setTabFocus()

	# Save consent 
	def saveConsent(self):
		chat_log = ChatManager()
        # Get the content of the QTextBrowser
		content = self.vconsent_display.toPlainText()
        # Get the state of the QCheckBox (checked or unchecked)
		checkbox_voice = self.vconsent_1_CheckBox.isChecked()
		checkbox_text = self.vconsent_2_CheckBox.isChecked()
		checkbox_minor = self.vconsent_minor.isChecked()
        # Get the text in the QLineEdit
		name = self.username(fullname=self.vsign_input.text())
		chat_log.saveConsentToAll(content,checkbox_voice, checkbox_text, checkbox_minor, name )


	# Save chat history
	def saveChat(self):
		# Save chat to text file
		active_tab = self.tab_manager.currentWidget()
		chat_log = ChatManager()
		chat_log.saveChatToAll(active_tab, self.first_name)


	def tiagoGPTSettings(self):
		self.ai_assistance = AIAssistedActivity(self.first_name)
		self.ai_assistance.max_token_value.show()
		self.ai_assistance.temperature_value.show()

	def exitApp(self):
		return self.close()

	def closeEvent(self, event):
		"""
		QWidget Close event
		"""
		file_manager.close()
		# close threads
		for window in self.findChildren(AIAssistedActivity):
			window.thread_model.quit()

	def zoomIn(self):
		active_tab = self.tab_manager.currentWidget()
		active_tab.zoomIn()
   
	def zoomOut(self):
		active_tab = self.tab_manager.currentWidget()
		active_tab.zoomOut()

if __name__ == '__main__':
	file_manager = FileManager()
	file_manager.tiagoGPTOnStartUp()

	# construct application instance
	app = QApplication(sys.argv)

	# install themes
	file_manager.tiagoGPTTheme(install=app, name = 'dOrange')

	# launch app window
	app_window = TIAGoGPTAppActivity()
	app_window.show()

	sys.exit(app.exec())