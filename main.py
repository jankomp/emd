import tkinter as tk
import threading
from video import run
from voice.recognize_commands import recognize_command

def start_video():
    while True:
        command = recognize_command()
        if command == "start":
            run()

# Create the main window
window = tk.Tk()
window.title("Simple GUI")

# Create a label
label = tk.Label(window, text="Please say start")
label.pack(padx=10, pady=10)

# Start the voice recognition in a separate thread
voice_thread = threading.Thread(target=start_video)
voice_thread.daemon = True
voice_thread.start()

# Start the main event loop
window.mainloop()