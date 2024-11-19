import time
import speech_recognition as sr
import google.generativeai as genai
import tkinter as tk
from tkinter import messagebox, ttk
from gtts import gTTS
import os
import pygame
import tempfile
import re
import datetime
import webbrowser
import requests

# Initialize pygame mixer for playing audio
pygame.mixer.init()

# Set up the Google Gemini API
genai.configure(api_key="AIzaSyBSB1232QiIMG0iBdKDfi1RO9-tzkko518")
#1st api_key:AIzaSyDQMjD-naVimUalsohcqxu3NScWOuqi4iI
#2nd api_key:AIzaSyBSB1232QiIMG0iBdKDfi1RO9-tzkko518
# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings
)

convo = model.start_chat(history=[])

def get_response(user_input, retries=3):
    """Get response from Google Gemini API with retry logic."""
    for attempt in range(retries):
        try:
            convo.send_message(user_input)
            gemini_reply = convo.last.text
            print(gemini_reply)
            return gemini_reply
        except Exception as e:
            if attempt < retries - 1:
                print(f"Error: {e}. Retrying... ({attempt + 1}/{retries})")
                time.sleep(2)  # Wait before retrying
            else:
                print(f"Failed after {retries} attempts. Error: {e}")
                return "Sorry, I couldn't process your request at this time."

def clean_text(text):
    """Clean up unwanted symbols from the text."""
    text = re.sub(r'\*', '', text)
    return text

def say_in_language(text, selected_lang):
    """Convert text to speech in the selected language and play it."""
    lang_codes = {
        "Kannada": "kn",
        "Hindi": "hi",
        "Tamil": "ta",
        "Telugu": "te",
        "English": "en"
    }
    
    language_code = lang_codes.get(selected_lang, "en")
    
    cleaned_text = clean_text(text)
    
    try:
        tts = gTTS(text=cleaned_text, lang=language_code, slow=False)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            temp_filename = temp_file.name
        
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(1)

        pygame.mixer.music.unload()
        os.remove(temp_filename)
    except Exception as e:
        print(f"Error generating speech: {e}")
        messagebox.showerror("TTS Error", f"Failed to convert text to speech: {e}")

def search_query():
    user_input = search_entry.get()
    if user_input:
        special_response = handle_special_commands(user_input)
        if special_response:
            say_in_language(special_response, lang_combobox.get())
            messagebox.showinfo("Assistant Response", special_response)
        else:
            response_from_gemini = get_response(user_input)
            say_in_language(response_from_gemini, lang_combobox.get())
            messagebox.showinfo("Gemini Response", response_from_gemini)
    else:
        messagebox.showwarning("Input Error", "Please enter a query in the search bar.")

def voice_query():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Listening for voice input...")
            audio = recognizer.listen(source)

            selected_lang = lang_combobox.get()
            lang_codes = {
                "Kannada": "kn-IN",
                "Hindi": "hi-IN",
                "Tamil": "ta-IN",
                "Telugu": "te-IN",
                "English": "en-US"
            }
            language_code = lang_codes.get(selected_lang, "en-US")

            user_input = recognizer.recognize_google(audio, language=language_code)
            print(f"Voice Input ({selected_lang}): {user_input}")

            response_from_gemini = get_response(user_input)
            say_in_language(response_from_gemini, selected_lang)
            messagebox.showinfo("Gemini Response", response_from_gemini)
        except sr.UnknownValueError:
            messagebox.showerror("Speech Error", "Sorry, I did not understand the audio.")
        except sr.RequestError:
            messagebox.showerror("Request Error", "Could not request results; check your internet connection.")

def get_weather():
    """Fetch the current weather using an API."""
    api_key = "a55c9aec30b765d92ffcb783931def26"  # Replace with your OpenWeatherMap API key
    city = "Bengaluru"  # Replace with your city
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"Current weather in {city}: {weather} with a temperature of {temp}°C."
        else:
            return "Weather information not available."
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "Unable to fetch weather information."

def get_time():
    """Get the current time."""
    now = datetime.datetime.now()
    return now.strftime("Current time: %I:%M %p")

def get_date():
    """Get the current date."""
    now = datetime.datetime.now()
    return now.strftime("Current date: %Y-%m-%d")

def play_audio():
    """Play a specific audio file."""
    audio_file = "path_to_your_audio_file.mp3"  # Replace with your audio file path
    try:
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    except Exception as e:
        print(f"Error playing audio: {e}")
        messagebox.showerror("Audio Error", f"Failed to play audio: {e}")

def open_browser(url):
    """Open a URL in the web browser."""
    webbrowser.open(url)

def handle_special_commands(command):
    """Handle special commands for weather, time, date, and audio playback."""
    if "weather" in command.lower():
        return get_weather()
    elif "time" in command.lower():
        return get_time()
    elif "date" in command.lower():
        return get_date()
    elif "play" in command.lower():
        play_audio()
        return "Playing audio."
    elif "youtube" in command.lower():
        open_browser("https://www.youtube.com")
        return "Opening YouTube."
    elif "google" in command.lower():
        open_browser("https://www.google.com")
        return "Opening Google."
    else:
        return None

# Create Tkinter UI
root = tk.Tk()
root.title("Virtual Assistant")

search_label = tk.Label(root, text="Enter your query:")
search_label.pack(pady=5)

search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=5)

search_button = tk.Button(root, text="Ask Gemini (Text)", command=search_query)
search_button.pack(pady=5)

voice_button = tk.Button(root, text="Ask Gemini (Voice)", command=voice_query)
voice_button.pack(pady=5)

lang_label = tk.Label(root, text="Select language for voice input:")
lang_label.pack(pady=5)

lang_combobox = ttk.Combobox(root, values=["English", "Kannada", "Hindi", "Tamil", "Telugu"])
lang_combobox.set("English")  # Default selection
lang_combobox.pack(pady=5)

root.mainloop()
