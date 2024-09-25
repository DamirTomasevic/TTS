import customtkinter as ctk
import os
from pathlib import Path
import PyPDF2
import threading
from tkinter import filedialog as fd
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Global variables
filepath = None
rate = 150  # Default speech rate
api_key = ""
url = ""
tts = None  # Initialize tts as None

# Function to initialize IBM Watson Text-to-Speech
def initialize_ibm_watson():
    global tts
    if api_key and url:
        try:
            authenticator = IAMAuthenticator(api_key)
            tts = TextToSpeechV1(authenticator=authenticator)
            tts.set_service_url(url)
            return True
        except Exception as e:
            error_label.configure(text=f"Error initializing IBM Watson: {e}")
            return False
    else:
        error_label.configure(text="Error: API key and URL must be provided.")
        return False

# Function to choose a file
def choose_file():
    global filepath
    filepath = fd.askopenfilename(title="Select a file")
    if filepath:
        file_path_label.configure(text=f"File selected: {filepath}")
        start_button.configure(state=ctk.NORMAL)  # Enable the start button

# Function to start processing
def start_process():
    if filepath and initialize_ibm_watson():
        threading.Thread(target=convert_file, daemon=True).start()

# Function to convert file content to speech
def convert_file():
    set_busy_cursor()
    content = get_content()
    if content:
        try:
            filename = f"{Path(filepath).stem}.mp3"
            with open(filename, 'wb') as audio_file:
                response = tts.synthesize(
                    content,
                    voice='en-US_MichaelV3Voice',  # Use a default voice
                    accept='audio/mp3'
                ).get_result()
                audio_file.write(response.content)
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
    if initialize_ibm_watson():
        threading.Thread(target=convert_text, daemon=True).start()

# Function to convert typed text to speech
def convert_text():
    set_busy_cursor()
    input_text = text_input.get("1.0", "end-1c").strip()
    if input_text:
        try:
            filename = "typed_text.mp3"
            with open(filename, 'wb') as audio_file:
                response = tts.synthesize(
                    input_text,
                    voice='en-US_MichaelV3Voice',  # Use a default voice
                    accept='audio/mp3'
                ).get_result()
                audio_file.write(response.content)
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

# Function to update speech rate (not directly supported by IBM Watson TTS)
def update_rate(value):
    global rate
    rate = int(value)
    rate_label.configure(text=f"Rate: {rate}")

# Function to update global variables with user inputs in real-time
def on_api_key_change(event):
    global api_key
    api_key = api_key_input.get()

def on_url_change(event):
    global url
    url = url_input.get()

# Initialize the customtkinter window
ctk.set_appearance_mode("Dark")  # Dark mode for the application
ctk.set_default_color_theme("blue")  # Blue theme

window = ctk.CTk()
window.title('TTS Converter')

# Label to display the file path
file_path_label = ctk.CTkLabel(window, text="No file selected", wraplength=450)
file_path_label.pack(pady=10)

# Input for IBM Watson API Key
api_key_label = ctk.CTkLabel(window, text="IBM Watson API Key:")
api_key_label.pack(pady=5)
api_key_input = ctk.CTkEntry(window, width=400)
api_key_input.pack(pady=5)
api_key_input.bind("<KeyRelease>", on_api_key_change)  # Update API key on input

# Input for IBM Watson Service URL
url_label = ctk.CTkLabel(window, text="IBM Watson Service URL:")
url_label.pack(pady=5)
url_input = ctk.CTkEntry(window, width=400)
url_input.pack(pady=5)
url_input.bind("<KeyRelease>", on_url_change)  # Update URL on input

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

# Slider for adjusting speech rate (not directly supported by IBM Watson TTS)
rate_slider = ctk.CTkSlider(window, from_=50, to=300, command=update_rate, number_of_steps=25)
rate_slider.set(rate)  # Set the initial value of the slider
rate_slider.pack(padx=20, pady=(10, 5))

# Label to display the current rate
rate_label = ctk.CTkLabel(window, text=f"Rate: {rate}")
rate_label.pack(pady=5)

window.mainloop()
