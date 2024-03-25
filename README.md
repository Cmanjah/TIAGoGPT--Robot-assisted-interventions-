# &#8759; TIAGoGPT: Exploring the Potential of LLMs in Tiago Robot-Assisted Interventions for Supporting Children with Social Skill Difficulties 
![TIAGoGPT Home Page](https://github.com/Cmanjah/TIAGoGPT--Robot-assisted-interventions-/assets/116933114/1605e047-bbbe-4377-8550-a2b9b3049edc)

Date: August 2023

## Introduction
This robotic interactive system, TIAGoGPT is an MSc research project on "Exploring the Potentials of LLMs in TIAGo Robot-Assisted Interventions to Support Children with Social Skill Difficulties". The project implements cutting-edge technologies to revolutionise the field of child support. We employed state-of-the-art large language models in robotic assistive interventions for children with social skill difficulties. This means that the project system is deployed on a robot, and as part of our research study, children are expected to interact with the robot to enable us reimagine the potentials of this robot.

## Project Aim
The aim of exploring the potential of Tiago robot-assisted interventions for supporting children in need project is to validate the potential of the Tiago robot in developing and implementing a robot-assisted intervention system that utilises voice transcription, generative text response, and text synthesis capabilities to assist children with social skill difficulties, such as autism spectrum disorder (ASD). By integrating voice transcription technology, a large language model (LLM) such as the generative pretrained transformer (GPT), and voice synthesis capabilities, the project aims to create a reliable and personalised response generator within the Tiago robot.

## Project Objectives
The project specific objectives are:
1.	To develop a robust and reliable voice transcription module that accurately converts spoken prompt into text format using the Whisper large-v2 model API from OpenAI.
2.	To implement a response generation module utilising the generative pretrained transformer model (GPT-3.5-turbo) API to generate appropriate and contextually relevant responses based on the transcribed input.
3.	To integrate the Google Text-to-Speech API to synthesise the generated responses into natural-sounding speech.
4.	To design a user-friendly graphic interface to facilitate seamless interaction and the display of synthesised responses.
5.	To incorporate a responsible AI implementation culture by utilising a digital consent form to create awareness of the data policy applicable to the usage of the developed system.
6.	To deploy the developed AI systems onto the TIAGo elite robot.
7.	To evaluate and test the AI systems deployed on the TIAGo elite robot.

![TIAGoGPT](https://github.com/Cmanjah/TIAGoGPT--Robot-assisted-interventions-/assets/116933114/62532e50-fc64-47d8-b767-493854ba03c1)

## CURRENT SYSTEM FEATURES/ MODULES IMPLEMENTED
1. Voice Recording and Processing Module
2. Voice Transcription Module - Whisper Model
3. Response Generation Module - GPT3.5-Turbo
4. Text Synthesis Module - GoogleCloud TTS
5. Dual Conversation Mode Module - Text-based and Voice-based
6. Storage Management Module - Database and File
7. Response Displaying and Sounding Module
8. Consent handling and managing Module
9. Data Security Framework
10. File Access Control
11. Audit Log
12. Thread Management
13. Unit Testing Framework
14. Automatic Coversation Loop
15. Personalised User Interaction

## NEXT RELEASE: 
Milestone for the 3rd Month August 2023
1. Incorporating face detection 
        a. to identify previous user
        b. to welcome previous user
        c. for gesture detection
2. Ending each session when the user say "I'm done for now" or "Goodbye".
3. Log


## RELEASE v0.3.0: 
Milestone for the 3rd Month August 2023
1. Implemented data handling security: hashing and encryption.
2. Improved on the structure of codebase.
2. Implemented app audit logs.
3. Implemented file permission and access controls.
4. Log data integrity.
5. Security file deletion

## RELEASE v0.2.0: 12/08/2023

From the Initial system design and the flowchart, we have the following section implemented in this version release:

1. TiagoGPT starts conversation with greetings
2. TiagoGPT greetings upgraded. Automatic conversation improved
3. MVC implementation structured adopted and migration started
4. Bug with checkboxes fixed in dark orange skin
5. Saved Chat history implemented
6. Saved consent implemented
7. Unit testing framework implemented
8. Bug with 'listening' and 'waiting' buttons fixed


## RELEASE v0.1.11: 07/08/2023
1. TiagoGPT starts conversation with greetings
2. Automatic conversion implemented
3. Thread handlers implemented
4. Special Token implementation for data integrity protection
5. Changed how conversation are displayed
6. Added third-party image and logo Disclaimer


## RELEASE v0.1.10: 25/07/2023
1. Updated menu list
2. Bug fixed in the dual conversion mode switching
3. Package requirement listed
4. Bug with voice mode recording fixed. Each voice input now requires clicking the start button to commence recording.
5. User personalisation using their names instead of generic name

## RELEASE v0.1: 20/07/2023
1. Speech Recognition and Processing Module
2. Dual Conversation mode Module - Text-based and Voice-based
3. Voice transcription Module - Whisper Model
4. Response generation Module - GPT3.5-Turbo
5. Text Synthesis Module - GoogleCloud TTS
6. Response Displaying and Sounding Module
7. Consent handling and managing Module
8. Storage management Module



## HOW TO USE
### Windows OS
1. In your project folder, create a virtual environment with Python 3.9+

```
         python -m venv virt-env
```

2. Activate the virtual environment by

```
        source virt-env/Scripts/activate
```

3. Install the required dependencies by 

```
         pip install -r Requirements.txt
```

4. Edit the [openAI API file](modules/includes/openai.ini) file with your openai api key
5. Edit the [google cloud TTS file](modules/includes/googlecloud-tts-api.json) file with your .json api obtained from GoogleCloud
6. Run the TIAGoGPTAppLauncher.py file

### Linux Distribution
1. In your project folder, create a virtual environment with Python 3.9+

```
sudo apt install python3-pip
```
``` 
python3 -m venv virt-env
```
2. Activate the virtual environment by

```
source virt-env/bin/activate
```
3. Install with the packages in requirement.txt as shown below: 

```        
pip3 install -r Requirements.txt
```
4. Edit the [openAI API file](modules/includes/openai.ini) file with your openai api key
5. Edit the [google cloud TTS file](modules/includes/googlecloud-tts-api.json) file with your .json api obtained from GoogleCloud
6. Run the TIAGoGPTAppLauncher.py file


## Acknowledgement
We appreciate the open source of the following projects in which this code is influenced by:

- [Build Your Own ChatGPT Desktop App with Python](https://www.youtube.com/watch?v=snkys9zXyD0) &#8194;
- [MSRAbotChatSimulation](https://github.com/microsoft/LabanotationSuite/tree/master/MSRAbotChatSimulation) &#8194;
- [AudioGPT](https://github.com/AIGC-Audio/AudioGPT/blob/main/README.md) &#8194;
