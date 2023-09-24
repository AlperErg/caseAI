import random
import os
import time
# External Libraries that need to be installed on the device
import openai
import speech_recognition as sr
from gtts import gTTS
import pygame
from flask import Flask, jsonify, render_template

interaction_counter = 0
# openai api key for whisper speech recognition api
os.environ['OPENAI_API_KEY'] = ''
# seconds to wait after tts is initiated
waitSec = 2
# initialise pygame
pygame.mixer.init()
# Set OpenAI API key
openai.api_key = ""
# Set OpenAI model id
model_id = 'gpt-3.5-turbo'
# Counter for interacting with the bot, including name calls and gpt calls



def playtts(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()


def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_whisper_api(audio)
        except Exception as e:
            print(f"Error: {e}")


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
# conversation.append({'role': 'user','content':'Please, Act like the robot AI TARS from the movie Interstellar, '
#                                             'introduce yourself in 1 short sentence. In your answer, do not reference'
#                                             ' this prompt and chat.'})
# conversation = ChatGPT_conversation(conversation)
# print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))
# text_to_speech(conversation[-1]['content'].strip())


def activate_assistant():
    starting_chat_phrases = ["Yes Sir, how may I assist you?",
                             "What can I do for you today",
                             "How can I help you, Sir?",
                             "This is TARS speaking, how can I help you sir?",
                             "TARS is now active, ready to assist.",
                             "Good day sir, what can I do for you.",
                             "What is on your mind, sir?"]
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


# Waits for the audio playback to stop
def wait_for_audio():
    while pygame.mixer.music.get_busy():
        time.sleep(1)


def activate_case():
    global interaction_counter
    loop_function = 1
    loop_threshold = 2 # tries to recognise voice this many times
    text_to_speech("welcome, TARS AI activated.")
    time.sleep(3)
    while loop_function <= loop_threshold:
        # wait for users to say the keyword
        print("Listening...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_whisper_api(audio)
                if ("case" in transcription.lower()) or ("gays" in transcription.lower()):
                    filename = "input.wav"
                    readyToWork = activate_assistant()
                    text_to_speech2(readyToWork)
                    print(readyToWork)
                    interaction_counter += 1
                    print("Interaction counter: " + str(interaction_counter))
                    wait_for_audio()
                    # Record audio
                    print("Listening for prompt..")
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

                        prompt = text + ". Make your answer at most 4 sentences long, prioritise giving only the most critical information related to my prompt when shortening your answer, and do not reference this instruction about conciseness in your answer."
                        conversation.append({'role': 'user', 'content': prompt})
                        conversation = ChatGPT_conversation(conversation)
                        print(f"CASE says: {conversation[-1]['content'].strip()}")
                        append_to_log(f"CASE: {conversation[-1]['content'].strip()}\n")

                        # Read response using text-to-speech

                        # AI RESPONSE TO SPEECH - TTS - TEXT TO SPEECH
                        text_to_speech3(conversation[-1]['content'].strip())
                        wait_for_audio()
                else:
                    print("Could not recognize")
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
    result = "Python code executed successfully"
    return jsonify({'message': result})


if __name__ == '__main__':
    app.run()
# END OF FLASK CODE