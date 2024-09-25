import customtkinter as ctk
import pyttsx3
import os
from pathlib import Path
import PyPDF2
import threading
from tkinter import filedialog as fd

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Global variables
filepath = None
rate = 150  # Default speech rate
voice_gender = 'male'  # Default voice gender

# Function to choose a file
def choose_file():
    global filepath
    filepath = fd.askopenfilename(title="Select a file")
    if filepath:
        file_path_label.configure(text=f"File selected: {filepath}")
        start_button.configure(state=ctk.NORMAL)  # Enable the start button

# Function to start processing
def start_process():
    if filepath:
        threading.Thread(target=convert_file, daemon=True).start()

# Function to convert file content to speech
def convert_file():
    set_busy_cursor()
    content = get_content()
    if content:
        try:
            filename = f"{Path(filepath).stem}.mp3"
            engine.setProperty('rate', rate)
            engine.save_to_file(content, filename)
            engine.runAndWait()
            os.startfile(filename)
        except Exception as e:
            error_label.configure(text=f"Error: {e}")
    else:
        error_label.configure(text="Error: Unable to read content from file.")
    reset_cursor()

# Function to get content from the selected file
def get_content():
    global filepath
    file_format = Path(filepath).suffix[1:]
    content = ""
    try:
        if file_format == "pdf":
            with open(filepath, 'rb') as pdf_file_obj:
                pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
                for page in pdf_reader.pages:
                    content += page.extract_text()
        else:
            with open(filepath, 'r') as file:
                content = file.read()
    except FileNotFoundError:
        pass
    return content

# Function to convert text input to speech
def convert_text_input():
    threading.Thread(target=convert_text, daemon=True).start()

# Function to convert typed text to speech
def convert_text():
    set_busy_cursor()
    input_text = text_input.get("1.0", "end-1c").strip()
    if input_text:
        try:
            filename = "typed_text.mp3"
            engine.setProperty('rate', rate)
            engine.save_to_file(input_text, filename)
            engine.runAndWait()
            os.startfile(filename)
            error_label.configure(text="")  # Clear previous error messages
        except Exception as e:
            error_label.configure(text=f"Error: {e}")
    else:
        error_label.configure(text="Error: The input text cannot be empty or consist only of spaces.")
    reset_cursor()

# Function to set the busy cursor
def set_busy_cursor():
    window.config(cursor="watch")

# Function to reset the cursor
def reset_cursor():
    window.config(cursor="")

# Function to set the voice gender
def set_voice():
    global voice_gender
    voices = engine.getProperty('voices')
    for voice in voices:
        if (voice_gender == 'female' and 'zira' in voice.name.lower()) or (voice_gender == 'male' and 'david' in voice.name.lower()):
            engine.setProperty('voice', voice.id)
            print(voice.id)
            break

# Function to update speech rate
def update_rate(value):
    global rate
    rate = int(value)
    rate_label.configure(text=f"Rate: {rate}")

# Function to change the voice gender
def set_voice_gender(selected_gender):
    global voice_gender
    voice_gender = selected_gender
    set_voice()

# Initialize the customtkinter window
ctk.set_appearance_mode("Dark")  # Dark mode for the application
ctk.set_default_color_theme("blue")  # Blue theme

window = ctk.CTk()
window.title('TTS Converter')

# Label to display the file path
file_path_label = ctk.CTkLabel(window, text="No file selected", wraplength=450)
file_path_label.pack(pady=10)

# Voice gender selection dropdown
gender_options = ['male', 'female']
selected_gender = ctk.StringVar(value=gender_options[0])
gender_menu = ctk.CTkOptionMenu(window, values=gender_options, variable=selected_gender, command=set_voice_gender)
gender_menu.pack(pady=10)

# File selection button
select_file_button = ctk.CTkButton(window, text='Select a file', command=choose_file)
select_file_button.pack(pady=5)

# Start button, initially disabled
start_button = ctk.CTkButton(window, text='Convert File', command=start_process, state=ctk.DISABLED)
start_button.pack(pady=5)

# Label to display error messages
error_label = ctk.CTkLabel(window, text="", text_color="red")
error_label.pack(pady=10)

# Text input box for typing text
text_input = ctk.CTkTextbox(window, height=180, width=350)
text_input.pack(padx=30, pady=5)

# Button to convert typed text to speech
convert_button = ctk.CTkButton(window, text='Convert Text', command=convert_text_input)
convert_button.pack(pady=(10,20))

# Slider for adjusting speech rate
rate_slider = ctk.CTkSlider(window, from_=50, to=300, command=update_rate, number_of_steps=25)
rate_slider.set(rate)  # Set the initial value of the slider
rate_slider.pack(padx=20, pady=(10, 5))

# Label to display the current rate
rate_label = ctk.CTkLabel(window, text=f"Rate: {rate}")
rate_label.pack(pady=5)

# Set the default voice
set_voice_gender(selected_gender.get())

window.mainloop()
