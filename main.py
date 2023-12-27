import tkinter as tk
import threading
from video import run, stop
from voice.recognize_commands import recognize_command
import os
import pyttsx3


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
    while True:
        command = recognize_command()
        if command == "dance" or command == "copy":
            video_thread = threading.Thread(target=run, kwargs={'mode': command})
            video_thread.daemon = True
            video_thread.start()
        elif command == "stop":
            stop()

# Create the main window
window = tk.Tk()
window.title("Little Dance Copiers")

# Uncomment on release
#atexit.register(cleanup)

# Create a label
label_txt = "Welcome to Little Dance Copiers!\n\nPlease say 'dance' to start recording your dance moves.\nYou will get 5 moves.\nSay 'copy' to start copying the dance moves.";
label = tk.Label(window, text=label_txt)
label.pack(padx=10, pady=10)

# Initialize the speech engine
engine = pyttsx3.init()
text_to_speech(engine, label_txt)

# Create a response label
response_label = tk.Label(window, text="")
response_label.pack(padx=10, pady=10)

listen_for_command()

# Start the main event loop
window.mainloop()