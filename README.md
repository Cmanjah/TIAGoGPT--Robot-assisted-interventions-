<<<<<<< Updated upstream
RELEASE v0.1.10-beta

Topic: Exploring the Potential of Tiago Robot-Assisted Interventions for Supporting Children in Need 
=======
# Exploring the Potential of LLMs in Tiago Robot-Assisted Interventions for Supporting Children with Social Skill Difficulties 
>>>>>>> Stashed changes

Date: July 2023

## Project Aim
The aim of exploring the potential of Tiago robot-assisted interventions for supporting children in need project is to validate the potential of the Tiago robot in developing and implementing a robot-assisted intervention system that utilises voice transcription, generative text response, and text synthesis capabilities to assist children with social skill difficulties, such as autism spectrum disorder (ASD). By integrating voice transcription technology, a large language model (LLM) such as the generative pretrained transformer (GPT), and voice synthesis capabilities, the project aims to create a reliable and personalised response generator within the Tiago robot.

<<<<<<< Updated upstream
Project Objectives
The project-specific objectives are:
=======
## Project Objectives
The project specific objectives are:
>>>>>>> Stashed changes
1.	To develop a robust and reliable voice transcription module that accurately converts spoken prompt into text format using the Whisper large-v2 model API from OpenAI.
2.	To implement a response generation module utilising the generative pretrained transformer model (GPT-3.5-turbo) API to generate appropriate and contextually relevant responses based on the transcribed input.
3.	To integrate the Google Text-to-Speech API to synthesise the generated responses into natural-sounding speech.
4.	To design a user-friendly graphic interface to facilitate seamless interaction and the display of synthesised responses.
5.	 To integrate the developed AI systems onto the Tiago elite robot.
6.	To evaluate and test the AI systems deployed on the Tiago elite robot.

## CURRENT SYSTEM FEATURES/ MODULES IMPLEMENTED
1. Speech Recognition and Processing Module
2. Dual Conversation mode Module - Text-based and Voice-based
3. Voice transcription Module - Whisper Model
4. Response generation Module - GPT3.5-Turbo
5. Text Synthesis Module - GoogleCloud TTS
6. Response Displaying and Sounding Module
7. Consent handling and managing Module
8. Storage management Module

<<<<<<< Updated upstream
RELEASE v0.1.10-beta
=======
## RELEASE v0.2.0: 
Milestone for the 3rd Month August 2023
1. Incorporating face detection 
        a. to identify previous user
        b. to welcome previous user
        c. for gesture detection

## RELEASE v0.1.11: 07/08/2023

From the Initial system design and the flowchart, we have the following section left:

1. TiagoGPT starts conversation with greetings
2. Starts and closing conversation filter
3. Special Token implementation
4. Change how conversation are displayed
5. Added third-party image and logo Disclaimer
6. log
7. Ending each session when the user say Thanks or goodbye.


## RELEASE v0.1.10: 25/07/2023
>>>>>>> Stashed changes
1. Updated menu list
2. Bug fixed in the dual conversion mode switching
3. Package requirement listed
4. Bug with voice mode recording fixed. Each voice input now requires clicking the start button to commence recording.
5. User personalisation using their names instead of generic name

<<<<<<< Updated upstream
EXPECTED UPDATE
RELEASE v0.1.11 - Milestone for the 2nd Month July - August 2023
=======
## RELEASE v0.1: 20/07/2023
1. Speech Recognition and Processing Module
2. Dual Conversation mode Module - Text-based and Voice-based
3. Voice transcription Module - Whisper Model
4. Response generation Module - GPT3.5-Turbo
5. Text Synthesis Module - GoogleCloud TTS
6. Response Displaying and Sounding Module
7. Consent handling and managing Module
8. Storage management Module
>>>>>>> Stashed changes


## HOW TO USE
### Windows OS
1. Install with the packages in requirement.txt as shown below: 
        (venv) $ python -m pip install -r requirements.txt
        where venv is your python virtual environment
2. Edit the api_key.ini file with your openai api key
3. Edit the googlecloud-tts-api.json file with your .json api obtained from GoogleCloud
4. Run the app.py file
<<<<<<< Updated upstream
=======

### Linux OS
1. Install with the packages in requirement.txt as shown below: 
        (venv) $ python -m pip install -r requirements.txt
        where venv is your python virtual environment
2. Edit the api_key.ini file with your openai api key
3. Edit the googlecloud-tts-api.json file with your .json api obtained from GoogleCloud
4. Run the app.py file


## Acknowledgement
We appreciate the open source of the following projects:

[ESPNet](https://github.com/espnet/espnet) &#8194;
[NATSpeech](https://github.com/NATSpeech/NATSpeech) &#8194;
[Visual ChatGPT](https://github.com/microsoft/visual-chatgpt) &#8194;
[Hugging Face](https://github.com/huggingface) &#8194;
[LangChain](https://github.com/hwchase17/langchain) &#8194;
[Stable Diffusion](https://github.com/CompVis/stable-diffusion) &#8194;
>>>>>>> Stashed changes
