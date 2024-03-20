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


os.environ['OPENAI_API_KEY'] = "sk-" # YOUR OPENAI API KEY IN THE QUOTES
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set OpenAI model id
model_id = 'gpt-3.5-turbo'
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


def activate_case():
    global interaction_counter
    loop_function = 0
    loop_threshold = 5 # runs voice recognition this many times
    output_audio("Welcome, Case AI activated.")
    while loop_function <= loop_threshold:
        # keyword detection
        print("Listening...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio)
                print("\rYou said: " + transcription)
                if ("case" in transcription.lower().strip()):
                    filename = "input.wav"
                    ready_to_work = activate_assistant()
                    output_audio(ready_to_work)
                    print(ready_to_work)
                    interaction_counter += 1
                    print("Interaction counter: " + str(interaction_counter))
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
                    if text:
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
                        loop_function = 0       
                # If the user says "enough", "stop" or "thank you" in their sentence while the program is waiting for the activation phrase, the program will stop
                elif ("enough" in transcription.lower()) or ("stop" in transcription.lower()) or ("thank you" in transcription.lower()):
                    output_audio("Case AI is now shutting down. Goodbye!")
                    print("\nStop command received, exiting program.")
                    break
                else:
                    print("\nCould not recognize voice, please try again.")
                    loop_function += 1
                    # In future maybe a conversation.clear to decrease input tokens as the conversation evolves
                    continue
            except Exception as e:
                print("An error occurred: {}".format(e))
                break


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