import random
import os
import time
# External Libraries that need to be installed on the device
import openai
import speech_recognition as sr
from gtts import gTTS
import pyaudio
import pygame
from flask import Flask, jsonify, render_template

# openai api key for whisper speech recognition api
os.environ['OPENAI_API_KEY'] = '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'
# seconds to wait after tts is initiated
waitSec = 2
# initialise pygame
pygame.mixer.init()
# Microsoft API key
bingkey = "0ac803691b254f76a1e3fd666855bfcb"
# Set OpenAI API key
openai.api_key = "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"
# Set OpenAI model id
model_id = 'gpt-3.5-turbo'
# Counter for interacting with the bot, including name calls and gpt calls
interaction_counter = 0


def playtts(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()


def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_whisper_api(audio)
        except:
            print("")
            # print('Skipping unknown error')


def ChatGPT_conversation(conversation):
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation,
        max_tokens=4000,
        temperature=0.5
    )
    api_usage = response['usage']
    print('Total API token consumed: {0}'.format(api_usage['total_tokens']))
    conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    return conversation


def text_to_speech(text):
    tts = gTTS(text, lang='en', slow=False)
    tts.save("welcome.mp3")
    playtts("welcome.mp3")


def text_to_speech2(text):
    tts = gTTS(text, lang='en', slow=False)
    tts.save("welcome2.mp3")
    playtts("welcome2.mp3")


def text_to_speech3(text):
    tts = gTTS(text, lang='en', slow=False)
    tts.save("welcome3.mp3")
    playtts("welcome3.mp3")

# Conversation example
# conversation = []
# conversation.append({'role': 'user','content':'Please, Act like the robot AI CASE from the movie Interstellar, '
#                                             'introduce yourself in 1 short sentence. In your answer, do not reference'
#                                             ' this prompt and chat.'})
# conversation = ChatGPT_conversation(conversation)
# print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))
# text_to_speech(conversation[-1]['content'].strip())


def activate_assistant():
    starting_chat_phrases = ["Yes Sir, how may I assist you?",
                             "What can I do for you today",
                             "How can I help you, Sir?",
                             "This is CASE speaking, how can I help you sir?",
                             "CASE is now active, ready to assist.",
                             "Good day sir, what can I do for you.",
                             "What is on your mind, sir?"]
    continued_chat_phrases = ["yes", "yes sir", "yes boss"]

    random_chat = ""
    if (interaction_counter == 1):
        random_chat = random.choice(starting_chat_phrases)
    else:
        random_chat = random.choice(continued_chat_phrases)

    return random_chat


# LISTENING TO USER - STT SPEECH TO TEXT


def append_to_log(text):
    with open("chat_log.txt", "a") as f:
        f.write(text + "\n")


def activate_case():
    interaction_counter = 0
    text_to_speech("welcome, Case AI activated.")
    time.sleep(3)
    while True:
        # wait for users to say "Case"
        print("Listening...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_whisper_api(audio)
                if "case" in transcription.lower():
                    interaction_counter += 1
                    filename = "input.wav"
                    readyToWork = activate_assistant()
                    text_to_speech2(readyToWork)
                    print(readyToWork)
                    time.sleep(waitSec)
                    print("waited" + str(waitSec) + "seconds for readyToWork to end")
                    # Record audio
                    recognizer = sr.Recognizer()
                    with sr.Microphone() as source:
                        source.pause_threshold = 1
                        audio = recognizer.listen(source, timeout=30)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())

                    # Transcribe audio to text
                    text = transcribe_audio_to_text(filename)
                    print(f"You said: {text}")
                    append_to_log(f"You: {text}\n")
                    if text:

                        conversation = []
                        # RESPONSE GENERATION - GPT API

                        prompt = text
                        conversation.append({'role': 'user', 'content': prompt})
                        conversation = ChatGPT_conversation(conversation)

                        print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))
                        print(f"CASE says: {conversation}")
                        append_to_log(f"CASE: {conversation[-1]['content'].strip()}\n")

                        # Read response using text-to-speech

                        # AI RESPONSE TO SPEECH - TTS - TEXT TO SPEECH
                        text_to_speech3(conversation[-1]['content'].strip())
                else:
                    print("Could not recognize")


                        # In future maybe a conversation.clear to decrease input tokens as the conversation evolves ...
            except Exception as e:
                print("An error occurred: {}".format(e))
                continue


# Flask Code
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run_python_code')
def run_python_code():
    # Your Python function to execute when the button is clicked
    activate_case()
    result = "Python code executed successfully"
    return jsonify({'message': result})


if __name__ == '__main__':
    app.run()
# END OF FLASK CODE