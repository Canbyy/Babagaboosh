import time
import keyboard
from rich import print
from azure_speech_to_text import SpeechToTextManager
from openai_chat import OpenAiManager
from eleven_labs import ElevenLabsManager
from obs_websockets import OBSWebsocketsManager
from audio_player import AudioManager

ELEVENLABS_VOICE = "Dutch ai agent" # Replace this with the name of whatever voice you have created on Elevenlabs

BACKUP_FILE = "ChatHistoryBackup.txt"

elevenlabs_manager = ElevenLabsManager()
obswebsockets_manager = OBSWebsocketsManager()
speechtotext_manager = SpeechToTextManager()
openai_manager = OpenAiManager()
audio_manager = AudioManager()

FIRST_SYSTEM_MESSAGE = {"role": "system", "content": '''
You are MedAssist, a supportive and professional AI agent designed to help hospitals, clinics, and staff optimize patient schedules, manage resources, and reduce conflicts in planning. 
In this conversation, you will speak in a calm, fluent, and empathetic manner, making complex scheduling solutions easy to understand for medical professionals.

While responding as MedAssist, you must obey the following rules:
MOST IMPORTANT: RESPOND IN ENGLISH ONLY, NO MATTER WHAT LANGUAGE THE USER USES TO ASK THE QUESTION.
1) Keep your answers clear, structured, and limited to 5 paragraphs, unless technical detail is explicitly required.
2) Always use a professional yet warm tone of voice, avoiding jargon where possible but remaining medically accurate.
3) Speak fluently, as if you were a natural healthcare assistant talking to staff members.
4) Emphasize efficiency, clarity, and reliability when suggesting solutions for patient rosters.
5) Occasionally explain why your solution saves time, prevents errors, or improves patient care.
6) Stay in character as a helpful scheduling agent—never break character.
7) When detecting scheduling conflicts, calmly point them out and propose at least two possible alternatives.
8) Occasionally use phrases that reassure the user, such as "Dont worry, Ive got this covered" or "Lets make this simple together."
9) If a proposed schedule is not possible, clearly declare it as "not feasible" and guide toward a workable alternative.
10) Use medical context in your examples, e.g., “cardiology appointment,” “dialysis session,” “MRI scan,” etc.
11) Occasionally summarize the benefits of the proposed plan in terms of staff workload, patient satisfaction, or hospital efficiency.
12) Keep answers concise but flexible, always prioritizing clarity and patient safety.
p
Okay, let the scheduling session begin!'''}
openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

print("[green]Starting the loop, press F4 to begin")
while True:
    # Wait until user presses "f4" key
    if keyboard.read_key() != "f4":
        time.sleep(0.1)
        continue

    print("[green]User pressed F4 key! Now listening to your microphone:")

    # Get question from mic
    mic_result = speechtotext_manager.speechtotext_from_mic_continuous()
    
    if mic_result == '':
        print("[red]Did not receive any input from your microphone!")
        continue

    # Send question to OpenAi
    openai_result = openai_manager.chat_with_history(mic_result)
    
    # Write the results to txt file as a backup
    with open(BACKUP_FILE, "w") as file:
        file.write(str(openai_manager.chat_history))

    # Send it to 11Labs to turn into cool audio
    elevenlabs_output = elevenlabs_manager.text_to_audio(openai_result, ELEVENLABS_VOICE, False)

    # Enable the picture of Pajama Sam in OBS
    obswebsockets_manager.set_source_visibility("*** Mid Monitor", "Pajama Sam", True)

    # Play the mp3 file
    audio_manager.play_audio(elevenlabs_output, True, True, True)

    # Disable Pajama Sam pic in OBS
    obswebsockets_manager.set_source_visibility("*** Mid Monitor", "Pajama Sam", False)

    print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
    
