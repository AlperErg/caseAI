import openai
import pyttsx3
import pyaudio
import speech_recognition as sr
import random

#set openai gpt api key
openai.api_key = "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"
model_id = 'gpt-3.5-turbo'

#STEP 1
#
#
#TTS engine initialisation
engine = pyttsx3.init()

#change speech rate here
engine.setProperty('rate', 180)

#get available voice
voices = engine.getProperty('voices')

#choose the voice with the voice id
engine.setProperty('voice', voices[1].id)

#interaction counter counting speech recognition, not ai interaction
interaction_counter = 0

def transcribe_audio_to_text(filename):
    recogniser = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recogniser.record(source)
        try:
            return recogniser.recognise_google(audio)
        except:
            print("")
            #print('Skipping unknown error')
#STEP 2
#
#
#ChatGPT input
def ChatGPT_conversation(conversation):
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation
    )
    apiusage = response['usage']
    print('Total token used: {0}'.format(apiusage['total_tokens']))
    conversation.append({'role': response.choices[0].messagee.role, 'content': response.choices[0].message.content})
    return conversation
def speak_text(text):
    engine.say(text)
    engine.runAndWait()



#start conversation
conversation = []
conversation.append({'role': 'user','content':'Please, Act like the robot AI TARS from the movie Interstellar, introduce yourself in 1 sentence. In your answer, do not reference this prompt and chat.'})
conversation = ChatGPT_conversation(conversation)
print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))
speak_text(conversation[-1]['content'].strip())

#Activation phrases
def activate_assistant():
    starting_chat_phrases = ["Yes Sir, how may I assist you?",
                             "What can I do for you today",
                             "How can I help you, Sir?",
                             "This is TARS speaking, how can I help you sir?",
                             "TARS is now active, ready to assist.",
                             "Good day sir, what can I do for you.",
                             "What is on your mind, sir?"]
    continued_chat_phrases = ["yes","yes sir", "yes boss"]
    random_chat= ""
    if(interaction_counter == 1):
        random_chat = random.choice(starting_chat_phrases)
    elif(interaction_counter > 1):
        random_chat = random.choice(continued_chat_phrases)
    else:
        print("I have encountered an error with the interaction counter, sir.")
    return random_chat


def append_to_log(text):
    with open("chat_log.txt", "a") as f:
        f.write(text + "\n")


#STEP 3
#Speech Recognition
#infinite loop waiting for user to say call prompt
while True:
    print("Say 'Case' to start...")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            transcription = recognizer.recognize_google(audio)
            if "case" in transcription.lower():
                interaction_counter += 1

                #record audio
                filename = "input.wav"

                readyToWork = activate_assistant()
                speak_text(readyToWork)
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    source.pause_threshold = 1
                    audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                    with open(filename, "wb") as f:
                        f.write(audio.get_wav_data())

                        #transcribe voice to text
                    text = transcribe_audio_to_text(filename)

                    if text:
                        print(f"You said: {text} as input")
                        append_to_log(f"You: {text}\n")

                        #STEP 4
                        #
                        #
                        #generate response using GPT

                        print(f"CASE says: {conversation}")

                        prompt = text

                        conversation.append({'role': 'user', 'content': prompt})
                        conversation = ChatGPT_conversation(conversation)

                        print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))

                        append_to_log(f"CASE: {conversation[-1]['content'].strip()}\n")

                        #STEP 5
                        #
                        #Text-to-Speech applied to the response
                        speak_text(conversation[-1]['content'].strip())

        except Exception as e:
            continue
            #print("An error
