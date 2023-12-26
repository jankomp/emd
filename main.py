import tkinter as tk
import threading
from video import run, stop
from voice.recognize_commands import recognize_command
import os
import atexit


def cleanup():
    if os.path.exists("dance/landmarks.csv"):
        os.remove("dance/landmarks.csv")

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

# Create a response label
response_label = tk.Label(window, text="")
response_label.pack(padx=10, pady=10)

listen_for_command()

# Start the main event loop
window.mainloop()