import random
import os
import time
import subprocess
# External Libraries that need to be installed on the device
from openai import OpenAI
import pyaudio
import speech_recognition as sr
from gtts import gTTS
import pygame
from flask import Flask, jsonify, render_template


# List of required pip plugins
required_plugins = ['openai', 'pyaudio', 'numpy', 'speechRecognition', 'gtts', 'pygame']
# Check if required plugins are installed
installed_plugins = []
for plugin in required_plugins:
    try:
        print('Checking if {0} is installed...'.format(plugin))
        # Check if the plugin is installed by running the command 'pip show <plugin>'
        subprocess.check_output(['pip', 'show', plugin])
        installed_plugins.append(plugin)
    except subprocess.CalledProcessError:
        # If the plugin is not installed, install it using the command 'pip install <plugin>'
        print('{0} is not installed. Installing now...'.format(plugin))
        subprocess.call(['pip', 'install', plugin])

if len(installed_plugins) == len(required_plugins):
    print("All plugins are installed successfully.")


# Set OpenAI API key
api_key = input("Please enter your OpenAI API key: ")
os.environ['OPENAI_API_KEY'] = api_key # YOUR OPENAI API KEY IN THE QUOTES
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set OpenAI model id
model_id = 'gpt-4o'
# Interaction counter to keep track of how many times the user has interacted with the assistant
interaction_counter = 0

def playtts(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    pygame.mixer.quit()


def speech_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except Exception as e:
            print(f"Error: {e}")


def output_audio(text):
    file = "output.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    response.stream_to_file(file)
    playtts(file)


interaction_counter = 0
def activate_assistant():
    starting_chat_phrases = ["Yes Sir, how may I assist you?",
                             "What can I do for you today",
                             "How can I help you Sir?",
                             "This is Case speaking, how can I help you sir?",
                             "Case is now active, ready to assist.",
                             "Good day sir, what can I do for you.",
                             "What is on your mind sir?"]
    continued_chat_phrases = ["yes?", "yes sir", "yes boss"]

    random_chat = ""
    if (interaction_counter <= 0):
        random_chat = random.choice(starting_chat_phrases)
    elif (interaction_counter > 0):
        random_chat = random.choice(continued_chat_phrases)
    else:
        print("Interaction counter error")

    return random_chat


def append_to_log(text):
    with open("chat_log.txt", "a") as f:
        f.write(text + "\n")



recognizer = sr.Recognizer()
def activate_case():
    loop_function = 0
    loop_threshold = 3 # runs voice recognition this many times
    output_audio("Welcome, Case AI activated.")
    while loop_function <= loop_threshold:
        # keyword detection
        print("Listening...")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio)
                print("\rYou said: " + transcription)
                if ("case" in transcription.lower().strip()):
                    global interaction_counter
                    ready_to_work = activate_assistant()
                    output_audio(ready_to_work)
                    print(ready_to_work)
                    interaction_counter += 1
                    print("Interaction counter: " + str(interaction_counter))
                    case_conversation()
                elif ("enough" in transcription.lower()) or ("stop" in transcription.lower()) or ("thank you" in transcription.lower()):
                    output_audio("Case AI is now shutting down. Goodbye!")
                    print("\nStop command received, exiting program.")
                    break
                else:
                    print("\nCould not recognize voice, please try again.")
                    loop_function += 1
            except Exception as e:
                print("An error occurred: {}".format(e))
            break


def case_conversation():
    filename = "input.wav"
    # Record GPT input audio
    print("Listening for prompt..")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        source.pause_threshold = 1
        # Change prompt recording timeout here. By default its set to 30 seconds. More recording, more tokens used.
        audio = recognizer.listen(source, timeout=30)
        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())

        # Transcribe audio to text - STT - SPEECH TO TEXT
        text = speech_to_text(filename)
        print(f"You said: {text}")
        append_to_log(f"You: {text}\n")
        if ("stop" in text.lower()):
            output_audio("Case AI is now shutting down. Goodbye!")
            print("\nStop command received, exiting program.")
        elif text:
            conversation = []
            # RESPONSE GENERATION - GPT API
            prompt = text + ". Make your answer at most 4 sentences long, prioritise giving only the most critical information related to my prompt when shortening your answer, and do not reference this instruction about conciseness in your answer."
            conversation.append({'role': 'user', 'content': prompt})
            response = client.chat.completions.create(
                model=model_id,
                messages=conversation,
                temperature=0.5,
            )
            response_message = response.choices[0].message.content
            print(f"CASE says: {response_message.strip()}")
            append_to_log(f"CASE: {response_message.strip()}\n")
            # AI RESPONSE TO SPEECH - TTS - TEXT TO SPEECH
            output_audio(response_message.strip())
            # Continue the conversation unless the user wants to stop it
            case_conversation()
        else:
            print("Could not convert speech to text, please try again.")

# Flask Code
app = Flask(__name__, static_folder='staticFiles')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run_python_code')
def run_python_code():
    # Your Python function to execute when the button is clicked
    activate_case()
    result = "Case has been run."
    return jsonify({'message': result})


if __name__ == '__main__':
    app.run()
# END OF FLASK CODE