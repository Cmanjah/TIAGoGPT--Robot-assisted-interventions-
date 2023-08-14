import os
import sys, time
from datetime import datetime
from configparser import ConfigParser
# import markdown
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QSlider,
							 QTabWidget, QTextEdit, QCheckBox, QLineEdit, QTextBrowser, QMenu, QMenuBar, QSplitter, 
							 QToolButton, QStatusBar,
							 QHBoxLayout, QVBoxLayout, QFormLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QEvent, QThread
from PyQt6.QtGui import QIcon, QTextCursor, QShortcut, QKeySequence, QPixmap
from handlers.endpoint import ModelGPT, Synthesizer, Transcriber, openai_api
from handlers.db import RobotDatabase
from handlers.manager import ChatManager, FileManager
from handlers.recorder import AudioRecorder


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)		

def current_timestamp(format_pattern='%y_%m_%d_%H%M%S'):
	return datetime.now().strftime(format_pattern)

class ModelGPTThread(QThread):
	clear_input = pyqtSignal()
	response_received = pyqtSignal(dict)	

	def __init__(self, parent):
		super().__init__(parent)
		self.ai_assistant = parent
		
	def run(self):
		text_string = ""
		if not self.ai_assistant.transcribed_string and self.ai_assistant.message_input.toPlainText():
			text_string = self.ai_assistant.message_input.toHtml()
		elif self.ai_assistant.transcribed_string and not self.ai_assistant.message_input.toPlainText():
			text_string = self.ai_assistant.transcribed_string
		self.clear_input.emit()
		
		# make an api call to OpenAI ModelGPT model
		max_tokens = self.ai_assistant.max_tokens.value()
		temperature = float('{0:.2f}'.format(self.ai_assistant.temperature.value() / 100))
		response = self.ai_assistant.modelgpt.send_request(text_string.strip(), max_tokens=max_tokens, temperature=temperature)
		self.clear_input.emit()
		self.response_received.emit(response)



class TranscriberThread(QThread):
	clear_input = pyqtSignal()
	response_received = pyqtSignal(dict)	

	def __init__(self, parent):
		super().__init__(parent)
		self.ai_assistant = parent
		
	def run(self):
		text_string = self.ai_assistant.message_input.toHtml()
		# self.clear_input.emit()
		
		# make an api call to OpenAI ModelGPT model
		# max_tokens = self.ai_assistant.max_tokens.value()
		# temperature = float('{0:.2f}'.format(self.ai_assistant.temperature.value() / 100))
		# response = self.ai_assistant. modelgpt.send_request(text_string.strip(), max_tokens=max_tokens, temperature=temperature)
		# self.clear_input.emit()
		# self.response_received.emit(response)



class AIAssistant(QWidget):
	def __init__(self, parent=None):
		super().__init__()
		self.modelgpt = ModelGPT(API_KEY)
		self.t = ModelGPTThread(self)
		self.conversation_track = ''
		# initialise the audio recorder
		self.recorder = AudioRecorder()
		# transcriber
		self.transcript = Transcriber(API_KEY)
		self.tc = TranscriberThread(self)
  		# synthesizer
		self.text_synthesis = Synthesizer()
 
		self.layout = {}
		self.layout['main'] = QVBoxLayout()
		self.setLayout(self.layout['main'])

		self.message_input = QTextEdit(placeholderText='Enter your prompt here')
		# create buttons
		self.btn_voice = QPushButton('&Start voice') #, clicked=self.start_listener)
		self.btn_submit = QPushButton('&Submit text', clicked=self.post_message)
		self.btn_clear = QPushButton('&Clear', clicked=self.reset_input)
		self.btn_stop = QPushButton('&Stop voice', clicked=self.stop_listener)

		self.init_ui()
		self.init_set_default_settings()
		self.init_configure_signals()

		self.t = ModelGPTThread(self)
		self.t.clear_input.connect(self.message_input.clear)
		self.transcribed_string = ""
		self.t.response_received.connect(self.update_conversation_window)

  
		# Newly added: Transcript
		self.tc = TranscriberThread(self)
	

	def init_ui(self):
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
		# self.layout['inputs'].addRow(QLabel('Token Limit:'), self.layout['slider_layout'])
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
  
		splitter = QSplitter(Qt.Orientation.Vertical)		
		self.layout['main'].addWidget(splitter)


		# conversation window
		self.conversation_window = QTextBrowser(openExternalLinks=True)
		self.conversation_window.setReadOnly(True)
		# self.conversation_window.setStyleSheet('background-color:#1d2b3a; color: white')
		# self.conversation_window.set
		splitter.addWidget(self.conversation_window) 

		self.intput_window = QWidget()
		self.layout['input entry'] = QHBoxLayout(self.intput_window)

		# Input goes here
		self.message_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.layout['input entry'].addWidget(self.message_input)

		self.layout['buttons'] = QVBoxLayout()
		self.layout['buttons'].addWidget(self.btn_submit)
		self.layout['buttons'].addWidget(self.btn_stop)
		self.layout['buttons'].addWidget(self.btn_clear, alignment=Qt.AlignmentFlag.AlignTop)
		self.layout['buttons'].addWidget(self.btn_voice, alignment=Qt.AlignmentFlag.AlignTop)
		self.layout['input entry'].addLayout(self.layout['buttons'])
  
		self.btn_stop.hide()

		self.btn_voice.clicked.connect(lambda:(
			self.btn_voice.setText('Listening...'),
			self.btn_voice.setEnabled(False),
			# if self.message_input.:
			self.message_input.hide(),
			self.btn_submit.hide(),
			self.btn_clear.hide(),
			self.btn_stop.show(),
			self.status.showMessage('Text Prompt field disabled!'), 
			self.start_listener()
			
		))

		splitter.addWidget(self.intput_window)
		splitter.setSizes([800, 200])

		# add status bar
		self.status = QStatusBar()
		self.status.setStyleSheet('font-size: 12px; color: white;')
		self.layout['main'].addWidget(self.status)

	def init_set_default_settings(self):
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

	def init_configure_signals(self):
		self.max_tokens.valueChanged.connect(lambda: self.max_token_value.setText('{0: ,}'.format(self.max_tokens.value())))
		self.temperature.valueChanged.connect(lambda: self.temperature_value.setText('{0: .2f}'.format(self.temperature.value() / 100)))

	def update_conversation_window(self, message):			
		if 'error' in message:
			self.status.setStyleSheet('''
				color: red;
			''')
			self.clear_input()
			self.status.showMessage(message['error'].user_message)
			return
		
		self.status.setStyleSheet('''
			color: white;
		''')

		# Tiago response placeholder container
		# print("Message: ", message['content'])
		# try:
		# 	self.text_synthesis.synthesizeText(message['content'])
		# except:
		# 	self.status.showMessage("Voice failed status!")
		# print()
		self.text_synthesis.synthesizeText(message['content'])
		self.conversation_track += '<br /><span style="color:#fd9620"><strong>[Tiago]:</strong></span>'		
		self.conversation_track +=  '<br/>' + message['content'].strip() + '<br /> <br />'
		self.conversation_window.setMarkdown(self.conversation_track)		
		self.status.showMessage('Tokens used status: {0}'.format(message['usage']))
			
		self.btn_submit.setEnabled(True)
		self.btn_submit.setText('&Submit')
  
		self.btn_voice.setEnabled(True)
		self.btn_voice.setText("&Start voice")
		# self.btn_clear.


	def post_message(self):
		if not self.message_input.toPlainText():
			self.status.showMessage('Prompt field is empty.')
			return
		else:
			self.status.clearMessage()

		self.btn_submit.setEnabled(False)
		self.btn_submit.setText('Waiting...')

		text_string = self.message_input.toPlainText()

		# cursor = self.conversation_window.textCursor()
		# cursor.movePosition(QTextCursor.MoveOperation.End)
		# self.conversation_window.setTextCursor(cursor)

		
		self.conversation_track += '<span style="color:#5caa00"><strong>[Username#]:</strong></span>'
		# self.conversation_track = '<p style="color:#5caa00"> <strong>[User]:</strong><br>'
		self.conversation_track += '<br />' + text_string + '<br />'
		self.conversation_window.setMarkdown(self.conversation_track)


		# self.conversation_window.insertHtml('<p style="color:#5caa00"> <strong>[User]:</strong><br>')
		# self.conversation_window.insertHtml(text_string)
		# self.conversation_window.insertHtml('<br')
		# self.conversation_window.insertHtml('<br')
	
		self.t.start()
		self.t.quit()

	def start_listener(self):
		if self.btn_voice.isEnabled():
			self.btn_voice.setText('Listening...')
			self.btn_voice.setEnabled(False)
		if self.message_input.isVisible():
			self.message_input.hide(),
			self.btn_submit.hide(),
			self.btn_clear.hide(),
			self.btn_stop.show(),
			self.status.showMessage('Text Prompt field disabled!'), 
			

		# time.sleep(2)
		# self.start_listener()
			# return
		# else:
		# self.status.clearMessage()

		# self.btn_submit.setEnabled(False)
		self.btn_stop.clicked.connect(lambda:(
			self.stop_listener()
		))

		# self.voice_prompt=""
		# if not self.recorder.start_recording():
		# 	self.voice_prompt = self.recorder.start_recording()
   
		# text_string = self.message_input.toPlainText()
		self.transcribed_string = self.transcript.transcribe_voice(prompt = self.recorder.start_recording())
		text_string = self.transcribed_string
  
		self.conversation_track += '<span style="color:#5caa00"><strong>[Username#]:</strong></span>'
		# self.conversation_track = '<p style="color:#5caa00"> <strong>[User]:</strong><br>'
		self.conversation_track += '<br />' + text_string + '<br />'
		self.conversation_window.setMarkdown(self.conversation_track)


		self.t.start()
		self.t.quit()
     
	def stop_listener(self):
		if  self.recorder.start_recording():
			self.status.showMessage('Listening stopped!')
			self.btn_voice.setText("&Start voice")
			return self.recorder.stop_recording()
		else:
			self.btn_stop.hide()
			self.status.showMessage('Listening has not started')


	def reset_input(self):
		self.message_input.clear()		
		self.status.clearMessage()

	def clear_input(self):
		self.btn_submit.setEnabled(True)
		self.btn_submit.setText('&Submit text')
		self.message_input.clear()

	def zoom_in(self):
		font = self.message_input.font()
		# increase font size only when current size is less than 30 pixel
		if font.pixelSize() < 30:
			self.message_input.setStyleSheet('font-size: {0}px'.format(font.pixelSize() + 2))
			self.conversation_window.setStyleSheet('font-size: {0}px;'.format(font.pixelSize() + 2))

	def zoom_out(self):		
		font = self.message_input.font()
		# decrease font size only when current size is smaller than 5
		if font.pixelSize() > 5:
			self.message_input.setStyleSheet('font-size: {0}px'.format(font.pixelSize() - 2))
			self.conversation_window.setStyleSheet('font-size: {0}px;'.format(font.pixelSize() - 2))		
	
 
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
		if self.count() == 1:
			return  
		self.removeTab(tab_index)


class AppWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.window_width, self.window_height = 720, 520
		self.setMinimumSize(self.window_width, self.window_height)
		self.setWindowIcon(QIcon(resource_path('media/system/image/tiago.png')))
		# self.setWindowIcon(QIcon(os.path.join(os.getcwd(), 'robot.png')))
		self.setWindowTitle('Chat with Tiago Robot')
		self.setStyleSheet('''
			QWidget {
				font-size: 13px;				
			}
		''') 

		self.file_manager = FileManager()
		self.tab_index_tracker = 1	
		self.layout = {}


		self.layout['main'] = QVBoxLayout()
		self.setLayout(self.layout['main'])

		self.layout['main'].insertSpacing(0, 19)
		
		self.menu_bar = QMenuBar(self)
		self.menu_bar.hide()
		self.init_menu()
		self.init_shortcut_assignment()

		self.btn_vprompt = QPushButton('&Voice Prompt', clicked=self.voice_consent_ui)

		self.vsplitter = QSplitter(Qt.Orientation.Vertical)		
		self.vconsent_window = QTextBrowser(openExternalLinks=True, placeholderText='[Consent Form Placeholder - Voice Prompt]')
		self.vconsent_1_CheckBox = QCheckBox('&I hereby GIVE my consent for the collection and use of my data as described in the consent request above.', clicked=self.consent_check_voice)
		self.vconsent_2_CheckBox = QCheckBox('&I hereby WITHHOLD my consent', clicked=self.consent_check_text)
		self.vinput_window = QWidget()
		self.vsign_input = QLineEdit(placeholderText='Enter your fullname to sign')
		self.vbtn_decline = QPushButton('&Decline', clicked=self.decline_chat_ui)
		# self.vbtn_agree = QPushButton('&Agree', clicked=self.start_voice_listener)
		self.vbtn_agree = QPushButton('&Agree', clicked=self.agree_chat_ui)


		self.dashboard()
		# self.init_ui()
		# self.init_configure_signal()
  
	def dashboard(self):
			
		image_path = "media/system/image/tiago.png"  # Replace this with the method from the FileManager object
		pixmap = QPixmap(image_path)
		# Set the desired width and height for the displayed image
		desired_width = 350
		desired_height = 450
		# Scale the image to the desired dimensions while maintaining aspect ratio
		scaled_pixmap = pixmap.scaled(desired_width, desired_height, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
		image = QLabel()
		image.setPixmap(scaled_pixmap)
		# Align the image to the center of the QLabel
		image.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.layout['pix'] = QVBoxLayout()
		self.layout['pix'].addWidget(image)
		self.layout['main'].addLayout(self.layout['pix'])

		# organize widgets	  
		# ----------------	  	
		self.btn_start = QPushButton('&Start') #, clicked=self.voice_consent_ui)
		self.btn_start.setFixedSize(170, 40)
		self.layout['app_start'] = QHBoxLayout()
		self.layout['app_start'].addWidget(self.btn_start)
		self.layout['main'].addLayout(self.layout['app_start'])


		self.btn_start.clicked.connect(lambda:(
			image.hide(),
			self.btn_start.hide(),
   			self.voice_consent_ui(),
		))
  
		# self.show()

	def voice_consent_ui(self):

		# add sub layout manager
		self.layout['dashboard'] = QFormLayout()

		# self.vsplitter = QSplitter(Qt.Orientation.Vertical)		
		self.layout['main'].addWidget(self.vsplitter)


		# consent window
		# self.vconsent_window = QTextBrowser(openExternalLinks=True, placeholderText='[Consent Form Placeholder]')
		self.vconsent_window.setHtml(f"<pre>{self.file_manager.consent()}</pre>")  # Wrap the content in <pre> tag to preserve formatting
		self.vconsent_window.setReadOnly(True)
		self.vsplitter.addWidget(self.vconsent_window) 

 		# add checkboxes
		# self.vconsent_1_CheckBox = QCheckBox('&[Consent option #1]', clicked=self.start_voice_listener)
		# self.vconsent_2_CheckBox = QCheckBox('&[Consent option #2]', clicked=self.start_chat_ui)

		# set initial states of the checkboxes
		self.vconsent_1_CheckBox.setChecked(False)
		self.vconsent_2_CheckBox.setChecked(True)

		# self.vinput_window = QWidget()
		self.layout['vconsent_entry'] = QHBoxLayout(self.vinput_window)
		self.layout['vconsent_options'] = QVBoxLayout()
		self.layout['vconsent_options'].addWidget(self.vconsent_1_CheckBox)
		self.layout['vconsent_options'].addWidget(self.vconsent_2_CheckBox)
		self.layout['vconsent_entry'].addLayout(self.layout['vconsent_options'])

 
		# Input goes here
		# self.vmessage_input = QLineEdit(placeholderText='Enter your name to sign')
		self.vsign_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.vsign_input.setEnabled(False)
		self.layout['vconsent_options'].addWidget(self.vsign_input)


		# add buttons
		# self.vbtn_decline = QPushButton('&Decline', clicked=self.start_chat_ui)
		# self.vbtn_agree = QPushButton('&Agree', clicked=self.start_chat_ui)

		# set initial state of the buttons
		self.vbtn_agree.setEnabled(True)
		self.vbtn_decline.setEnabled(True)

		self.layout['vbuttons'] = QVBoxLayout()
		self.layout['vbuttons'].addWidget(self.vbtn_agree, alignment=Qt.AlignmentFlag.AlignTop)
		self.layout['vbuttons'].addWidget(self.vbtn_decline, alignment=Qt.AlignmentFlag.AlignTop)
		self.layout['vconsent_entry'].addLayout(self.layout['vbuttons'])


		self.vsplitter.addWidget(self.vinput_window)
		self.vsplitter.setSizes([800, 200])
  
  		# add status bar
		self.status = QStatusBar()
		self.status.setStyleSheet('font-size: 12px; color: red;')
		self.layout['status_message'] = QVBoxLayout()
		self.layout['status_message'].addWidget(self.status)
		self.layout['main'].addLayout(self.layout['status_message'])
  
	def start_voice_listener(self):
		if self.btn_vprompt.isEnabled(True):
			self.btn_vprompt.isEnabled(False)
		if self.btn_tprompt.isVisible():
			self.btn_tprompt.hide()

		widgets = [
			self.splitter,
			self.consent_window,
			self.consent_1_CheckBox,
			# self.consent_2_CheckBox,
			self.input_window,
			self.message_input,
			self.btn_decline,
			self.btn_agree
		]

		for widget in widgets:
			if widget.isVisible():
				widget.hide()


		widgets = [
			self.vsplitter,
			self.vconsent_window,
			self.vconsent_1_CheckBox,
			self.vconsent_2_CheckBox,
			self.vinput_window,
			self.vsign_input,
			self.vbtn_decline,
			self.vbtn_agree
		]

		for widget in widgets:
			if widget.isVisible():
				widget.hide()

	def consent_check_voice(self):
		pass

	def consent_check_text(self):
		pass

	def decline_chat_ui(self):
		pass

	def agree_chat_ui(self):
		if not self.vconsent_1_CheckBox.isChecked():
			self.status.showMessage('Please provide your consent by checking the box.')
			return
		elif not self.vsign_input.isEnabled():
			self.vconsent_2_CheckBox.setChecked(False)
			self.vsign_input.setEnabled(True)
			self.status.showMessage('Please type in your fullname in the field to sign.')
			return
		elif not self.vsign_input.text():
			self.status.showMessage('Field is empty.')
			return
		else:
			self.status.clearMessage()
			# save the consent as pdf to file
   
			widgets = [
				self.vsplitter,
				self.vconsent_window,
				self.vconsent_1_CheckBox,
				self.vconsent_2_CheckBox,
				self.vinput_window,
				self.vsign_input,
				self.vbtn_decline,
				self.vbtn_agree
			]

			for widget in widgets:
				if widget.isVisible():
					widget.hide()
		
			self.menu_bar.show()
			self.init_ui()
			self.init_configure_signal()
        

	def init_ui(self):
		# add tab  manager
		self.tab_manager = TabManager()
		self.layout['main'].addWidget(self.tab_manager)

		# ai_assistant = AIAssistant()
		self.tab_manager.addTab(AIAssistant(), ' Conversion #{0}'.format(self.tab_index_tracker))
		self.set_tab_focus()

	def init_menu(self):

		file_menu = QMenu('&File', self.menu_bar)
		file_menu.addAction('&Save output', self.save_output)
		file_menu.addAction('S&ave log do DB', self.save_conversation_log_to_db)
		self.menu_bar.addMenu(file_menu)

		# view menu
		view_menu = QMenu('&View', self.menu_bar)
		view_menu.addAction('Zoom &in', self.zoom_in)
		view_menu.addAction('Zoom &out', self.zoom_out)
		self.menu_bar.addMenu(view_menu)

	def init_shortcut_assignment(self):
		shortcut_add_tab = QShortcut(QKeySequence('Ctrl+Shift+A'), self)
		shortcut_add_tab.activated.connect(self.add_tab)

	def init_configure_signal(self):
		self.tab_manager.plusClicked.connect(self.add_tab)

	def set_tab_focus(self):
		activate_tab = self.tab_manager.currentWidget()
		activate_tab.message_input.setFocus()

	def add_tab(self):
		self.tab_index_tracker += 1
		# ai_assistant = AIAssistant()
  
		# This section will show the persons name as the name of the tab. when conversion begins
		self.tab_manager.addTab(AIAssistant(), 'Conversation #{0}'.format(self.tab_index_tracker))
		self.tab_manager.setCurrentIndex(self.tab_manager.count()-1)
		self.set_tab_focus()

	def save_output(self):
		active_tab = self.tab_manager.currentWidget()
		conversation_window_log = active_tab.conversation_window.toPlainText()
		timestamp = current_timestamp()

		chat_log = ChatManager()		
		# This will be saved to a json file not text in a different directory
		with open(f'{chat_log.get_chat_log_path()}/{timestamp}_Chat Log.txt', 'w', encoding='UTF-8') as _f:
			_f.write(conversation_window_log)
		active_tab.status.showMessage('''File saved at {0}/{1}_Chat Log.txt'''.format(os.getcwd(), timestamp))

	def save_conversation_log_to_db(self):		
		timestamp = current_timestamp('%Y-%m-%d %H:%M:%S')		
		active_tab = self.tab_manager.currentWidget()
		messages = str(active_tab.modelgpt.messages).replace("'", "''")
		values = f"'{messages}','{timestamp}'"

		db.insert_record('message_logs', 'messages, created', values)
		active_tab.status.showMessage('Record inserted')

	def closeEvent(self, event):
		"""
		QWidget Close event
		"""
		db.close()

		# close threads
		for window in self.findChildren(AIAssistant):
			window.t.quit()

	def zoom_in(self):
		active_tab = self.tab_manager.currentWidget()
		active_tab.zoom_in()
   
	def zoom_out(self):
		active_tab = self.tab_manager.currentWidget()
		active_tab.zoom_out()

if __name__ == '__main__':
	# load openai API key
	config = ConfigParser()
	config.read(openai_api())
	API_KEY = config.get('openai', 'APIKEY')

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

	# construct application instance
	app = QApplication(sys.argv)
	app.setStyle('fusion')

	# load css skin
	qss_style = open(resource_path('media/system/template/css_skins/dark_orange_style.qss'), 'r')
	app.setStyleSheet(qss_style.read())

	# launch app window
	app_window = AppWindow()
	app_window.show()

	sys.exit(app.exec())