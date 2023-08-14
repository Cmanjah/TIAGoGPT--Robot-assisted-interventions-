import os
import openai
import nltk

nltk.download('punkt')  # Run this once to download the tokenizer data

def keyword_filter(text, keywords):
    tokens = nltk.word_tokenize(text.lower())
    return any(keyword.lower() in tokens for keyword in keywords)


def filter(prompt):
    # for now, let's return prompt
    return prompt

def chat(prompt):
    start_word = ['hi', 'hey', 'hello', 'hi there', 'hey there']
    first_time_chat = "Hi, my name is Tiago Robot aided by large language model from openAI! and what's your name?"
   
    for word in start_word:
        if prompt.lower() == word:
            chat_folder_path = 'chat_0001'
            os.mkdir(chat_folder_path)
            print(first_time_chat)
            response = input()
            # apply filter to the response input
            name = filter(response)
            print(f'Can I save your name as {name} and refer to you by name? \n Use "+" to Accept and "x" to Decline')
            response = input()
            if response == '+':
                # change the folder name to 'name'
                if os.path.exists(chat_folder_path): #and os.listdir(chat_folder_path):
                    # Check if the folder exists and is not empty
                    new_folder_path = os.path.join(os.path.dirname(chat_folder_path), name)
                    print('new_folder_path: ', new_folder_path)

                    # Rename the folder
                    os.rename(chat_folder_path, new_folder_path)
                    print(f"The folder '{chat_folder_path}' has been renamed to '{name}'.")
                else:
                    print(f"The folder '{chat_folder_path}' does not exist or is empty.")
                
            elif response == 'x':
                print("Permission to save the name not granted!")
                # Use 'Anonymous' to perform the transcription...
            else:
                print('Please use the provided command')
                
    # Display consent form for authorization or decline.
    
# chat('HEY')

# 1. Extract Keywords
# 2. Check if the word matches with the selected words.
# If there's a match, generate


# Filter audio input
# 1. Check the transcribed text for keywords


#  Filter the audio output
# 1. Check and extract keywords from the generated text using OpenAI