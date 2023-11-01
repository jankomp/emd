import tkinter as tk

def on_button_click():
    label.config(text="Button Clicked!")

# Create the main window
window = tk.Tk()
window.title("Simple GUI")

# Create a label
label = tk.Label(window, text="Hello, GUI!")
label.pack(padx=10, pady=10)

# Create a button
button = tk.Button(window, text="Click Me", command=on_button_click)
button.pack(pady=10)

# Start the main event loop
window.mainloop()
