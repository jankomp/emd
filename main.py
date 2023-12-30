import tkinter as tk
import threading
from video import run, stop
from voice.recognize_commands import recognize_command
import os
import word2number.w2n as w2n
import pyttsx3

moves = 5
bpm = 60
happy_face = False
response_text = ""
settings_text = f"{moves} moves, {bpm} bpm"

def cleanup():
    if os.path.exists("dance/copy_landmarks.csv"):
        os.remove("dance/copy_landmarks.csv")

def read_aloud(engine, text):
    engine.say(text)
    engine.runAndWait()

def text_to_speech(engine, text):
    engine.setProperty('rate', 180)
    engine.setProperty('volume', 0.9)

    # Get all voices
    voices = engine.getProperty('voices')

    # Use an English voice
    english_voices = [voice for voice in voices if "EN-US" in voice.id]
    if english_voices:
        engine.setProperty('voice', english_voices[-1].id)
    else:
        print("No English voice found")
        
    # Read label_txt aloud in a separate thread
    tts_thread = threading.Thread(target=read_aloud, args=(engine, text,))
    tts_thread.daemon = True
    tts_thread.start()

def listen_for_command():
    # Start the voice recognition in a separate thread
    voice_thread = threading.Thread(target=voice_command)
    voice_thread.daemon = True
    voice_thread.start()

def voice_command():
    global moves, bpm, happy_face
    global response_text
    while True:
        command = str(recognize_command())
        if command == "dance" or command == "copy":
            video_thread = threading.Thread(target=run, kwargs={'mode': command, 'moves': moves, 'bpm': bpm, 'happy_face': happy_face})
            video_thread.daemon = True
            video_thread.start()
            response_text = f"Starting to {command}!"
        elif command == "stop":
            stop()
            response_text = "Stopping!"
        elif command.find("moves") != -1:
            try:
                new_moves = w2n.word_to_num(command.split(" ")[0])
                if new_moves > 20 or new_moves < 1:
                    raise ValueError
                else:
                    moves = new_moves
                print(f'moves: {moves}')
                response_text = f"Setting number of moves to {moves}"
            except ValueError:
                print("Invalid number of moves")
                response_text = "Invalid number of moves"
        elif command.find("beats per minute") != -1:
            try:
                new_bpm = w2n.word_to_num(command.split(" ")[0])
                if new_bpm > 120 or new_bpm < 10:
                    raise ValueError
                else:
                    bpm = new_bpm
                print(f'bpm: {bpm}')
                response_text = f"Setting bpm to {bpm}"
            except ValueError:
                print("Invalid number of moves")
                response_text = "Invalid number of moves"
        elif command == "happy face on":
            happy_face = True
            response_text = "Happy face on"
        elif command == "happy face off":
            happy_face = False
            response_text = "Happy face off"
        else:
            response_text = "Invalid command"
            
        response_label.config(text=response_text)
        settings_label.config(text=f"{moves} moves, {bpm} bpm")

# Create the main window
window = tk.Tk()
window.title("Little Dance Copiers")

# Uncomment on release
#atexit.register(cleanup)

# Create a label
label_txt = """Welcome to Little Dance Copiers!\n\n
    Please say 'dance' to start recording your dance moves.\n
    Say 'copy' to start copying the dance moves.\n
    Say '{1...20} moves' to set the number of moves.\n
    Say '{10...120} beats per minute' to set the bpm.\n
    Say 'happy face on' to turn on the happy face detector.\n
    Say 'happy face off' to turn off the happy face detector.\n"""
label = tk.Label(window, text=label_txt)
label.pack(padx=10, pady=10)

# Uncomment on release
# Initialize the speech engine
#engine = pyttsx3.init()
#text_to_speech(engine, label_txt)

# Create a response label
response_label = tk.Label(window, text=response_text)
response_label.pack(padx=10, pady=10)

# Create a response label
settings_label = tk.Label(window, text=settings_text)
settings_label.pack(padx=10, pady=10)

listen_for_command()

# Start the main event loop
window.mainloop()