import tkinter as tk
import threading
from video import run, stop
from voice.recognize_commands import recognize_command

def listen_for_command():
    # Start the voice recognition in a separate thread
    voice_thread = threading.Thread(target=voice_command)
    voice_thread.daemon = True
    voice_thread.start()

def voice_command():
    while True:
        command = recognize_command()
        if command == "start":
            video_thread = threading.Thread(target=run)
            video_thread.daemon = True
            video_thread.start()
        elif command == "stop":
            stop()

# Create the main window
window = tk.Tk()
window.title("Simple GUI")

# Create a label
label = tk.Label(window, text="Please say start")
label.pack(padx=10, pady=10)

# Create a response label
response_label = tk.Label(window, text="Listening...")
response_label.pack(padx=10, pady=10)

listen_for_command()

# Start the main event loop
window.mainloop()