import openai
import pyttsx3
import pyaudio
import speech_recognition as sr
import random

# Set OpenAI API key
openai.api_key = "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"
model_id = 'gpt-3.5-turbo'

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Change speech rate
engine.setProperty('rate', 150)

# Get the avaiable voices on the installed system
voices = engine.getProperty('voices')
# Print the available voices (optional)
for voice in voices:
    print(f"Voice ID: {voice.id}")
    print(f"Voice Name: {voice.name}")
    print(f"Voice Languages: {voice.languages}\n")

#Voice ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
#Voice Name: Microsoft Zira Desktop - English (United States)
#Voice Languages: []
#Voice ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0
#Voice Name: Microsoft Hazel Desktop - English (Great Britain)
#Voice Languages: []

#Voice ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0
#Voice Name: Microsoft David Desktop - English (United States)
#Voice Languages: []

#Voice ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_DE-DE_HEDDA_11.0
#Voice Name: Microsoft Hedda Desktop - German
#Voice Languages: []



# Select a specific voice based on its ID or name
# Replace 'desired_voice_name' with the name of the voice you want to use
desired_voice_name = "Microsoft Hazel Desktop - English (Great Britain)"
selected_voice = None

for voice in voices:
    if desired_voice_name in voice.name:
        selected_voice = voice
        break
# Check if the desired voice was found
if selected_voice is not None:
    # Set the selected voice as the active voice
    engine.setProperty('voice', selected_voice.id)

    # Test the voice by saying something
    engine.say("Augmented voice, selected.")
    engine.runAndWait()
    print("Selected:" + voices[0].id)
else:
    print(f"Voice '{desired_voice_name}' not found. Please select an available voice from the list.")
    exit()

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
        messages=conversation
    )
    api_usage = response['usage']
    print('Total API token consumed: {0}'.format(api_usage['total_tokens']))
    conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    return conversation


def speak_text(text):
    engine.say(text)
    engine.runAndWait()


# Starting conversation
conversation = []
conversation.append({'role': 'user','content':'Please, Act like the robot AI CASE from the movie Interstellar, '
                                              'introduce yourself in 1 sentence. In your answer, do not reference '
                                              'this prompt and chat.'})
conversation = ChatGPT_conversation(conversation)
print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))
speak_text(conversation[-1]['content'].strip())


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


def append_to_log(text):
    with open("chat_log.txt", "a") as f:
        f.write(text + "\n")


while True:

    # wait for users to say "Case"
    print("Say 'CASE' to start...")
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
                speak_text(readyToWork)
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

                    # Generate response using chatGPT
                    print(f"CASE says: {conversation}")

                    prompt = text
                    conversation.append({'role': 'user', 'content': prompt})
                    conversation = ChatGPT_conversation(conversation)

                    print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))

                    append_to_log(f"CASE: {conversation[-1]['content'].strip()}\n")

                    # Read response using text-to-speech
                    speak_text(conversation[-1]['content'].strip())

                    # In future maybe a conversation.clear to decrease input tokens as the conversation evolves ...

        except Exception as e:
            continue
            print("An error occurred: {}".format(e))