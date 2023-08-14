RELEASE v0.1 - Milestone within the 1st Month June - July 2023

Topic: Exploring the Potential of Tiago Robot-Assisted Interventions for Supporting Children in Need 

Name: Charles Anjah 
UB No: 22002066 

Module: Dissertation

Supervisor: Dr. Amr Rashad Ahmed Abdullatif

Date: July 2023

Project Aim
The aim of exploring the potential of Tiago robot-assisted interventions for supporting children in need project is to validate the potential of the Tiago robot in developing and implementing a robot-assisted intervention system that utilises voice transcription, generative text response, and text synthesis capabilities to assist children with social skill difficulties, such as autism spectrum disorder (ASD). By integrating voice transcription technology, a large language model (LLM) such as the generative pretrained transformer (GPT), and voice synthesis capabilities, the project aims to create a reliable and personalised response generator within the Tiago robot.

Project Objectives
The project specific objectives are:
1.	To develop a robust and reliable voice transcription module that accurately converts spoken prompt into text format using the Whisper large-v2 model API from OpenAI.
2.	To implement a response generation module utilising the generative pretrained transformer model (GPT-3.5-turbo) API to generate appropriate and contextually relevant responses based on the transcribed input.
3.	To integrate the Google Text-to-Speech API to synthesise the generated responses into natural-sounding speech.
4.	To design a user-friendly graphic interface to facilitate seamless interaction and the display of synthesised responses.
5.	 To integrate the developed AI systems onto the Tiago elite robot.
6.	To evaluate and test the AI systems deployed on the Tiago elite robot.

CURRENT SYSTEM FEATURES/ MODULES IMPLEMENTED
1. Speech Recognition and Processing Module
2. Dual Conversation mode Module - Text-based and Voice-based
3. Voice transcription Module - Whisper Model
4. Response generation Module - GPT3.5-Turbo
5. Text Synthesis Module - GoogleCloud TTS
6. Response Displaying and Sounding Module
7. Consent handling and managing Module
8. Storage management Module

EXPECTED UPDATE
RELEASE v0.1 - Milestone for the 2nd Month July - August 2023

From the Initial system design and the flowchart, we have the following section left:

1. Filter Module - Keyword filtering model from GPT4
2. Response Processing Module
3. Continuous interaction loop Module
4. Package Requirement Listing

HOW TO USE
1. Edit the api_key.ini file with your openai api key
2. Edit the googlecloud-tts-api.json file with your .json api obtained from GoogleCloud
3. Run the app.py file