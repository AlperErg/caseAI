import openai
import pyttsx3
import speech_recognition as sr
import random
from gtts import gTTS
import pyaudio
import wave
import pygame


# initialise pygame
pygame.mixer.init()


def playtts(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()


# Set OpenAI API key
openai.api_key = "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"
# Set model id
model_id = 'gpt-3.5-turbo'

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Change speech rate
engine.setProperty('rate', 150)
engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0")

# Get the avaiable voices on the installed system
voices = engine.getProperty('voices')
# Print the available voices (optional)
for voice in voices:
    print(f"Voice ID: {voice.id}")
    print(f"Voice Name: {voice.name}")
    print(f"Voice Languages: {voice.languages}\n")

# Counter for interacting with the bot, including name calls and gpt calls
interaction_counter = 0


def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
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


def speak_text(text):
    engine.say(text)
    engine.runAndWait()


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

# Starting conversation
# conversation = []
# conversation.append({'role': 'user','content':'Please, Act like the robot AI CASE from the movie Interstellar, '
#                                             'introduce yourself in 1 short sentence. In your answer, do not reference'
#                                             ' this prompt and chat.'})
# conversation = ChatGPT_conversation(conversation)
# print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))
# speak_text(conversation[-1]['content'].strip())
text_to_speech("welcome, Case AI activated.")


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


while True:

    # wait for users to say "Case"
    print("Listening...")
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            transcription = recognizer.recognize_google(audio)
            if "case" in transcription.lower():
                interaction_counter += 1
                # Record audio
                filename = "input.wav"
                readyToWork = activate_assistant()
                text_to_speech2(readyToWork)
                print(readyToWork)
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    source.pause_threshold = 1
                    audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                    with open(filename, "wb") as f:
                        f.write(audio.get_wav_data())

                # Transcribe audio to text
                text = transcribe_audio_to_text(filename)
                if text:
                    print(f"You said: {text}")
                    append_to_log(f"You: {text}\n")

                    conversation = []
                    # RESPONSE GENERATION - GPT API
                    print(f"CASE says: {conversation}")

                    prompt = text
                    conversation.append({'role': 'user', 'content': prompt})
                    conversation = ChatGPT_conversation(conversation)

                    print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))

                    append_to_log(f"CASE: {conversation[-1]['content'].strip()}\n")

                    # Read response using text-to-speech

                    # AI RESPONSE TO SPEECH - TTS - TEXT TO SPEECH
                    text_to_speech3(conversation[-1]['content'].strip())

                    # In future maybe a conversation.clear to decrease input tokens as the conversation evolves ...
        except Exception as e:
            print("An error occurred: {}".format(e))
            continue
