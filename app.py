from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import time
import subprocess
from ecapture import ecapture as ec
import wolframalpha
import requests
from bs4 import BeautifulSoup
import cohere
import random
import pygame
import uuid
import threading
from transformers import pipeline
from gtts import gTTS
import tempfile
import os
import re

hf_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


app = Flask(__name__)

pygame.init()
pygame.mixer.init()
music_dir = r"D:\Music"


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


co = cohere.Client("CNwF9GrjxcGAZ089DAkJDmtm1wWRuu0DRUFw2ovg")
wolfram_client = wolframalpha.Client("R2K75H-7ELALHR35X")


pygame.init()

def speak(text):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text=text, lang='en')
            tts.save(fp.name)
            mp3_path = fp.name

        # Play TTS using pygame
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.unload()
        os.remove(mp3_path)

    except Exception as e:
        print("Error in speak():", e)




def handle_specific_questions(question):
    tokens = word_tokenize(question.lower())
    if "hello" in tokens:
        greet()
        return "Hello! How can I assist you today?"
    elif "how" in tokens and "are" in tokens and "you" in tokens:
        return "I'm doing well, thank you for asking."
    elif "joke" in tokens:
        return "Why don't scientists trust atoms? Because they make up everything!"
    elif "fact" in tokens:
        return "A group of flamingos is called a flamboyance."
    elif "thank" in tokens:
        return "You are welcome!"
    elif "bye" in tokens:
        return "Goodbye!"
    elif "wake up daddy's home" in tokens:
        return "Welcome home sir"
    elif "happy" in tokens:
        return "Well sir, What's the reason for your happiness?"
    elif "know" in tokens and "me" in tokens:
        return "Yes sir, You are Mr. Sivaji."
    else:
        return None



def cohere_summarize(text):
    try:
        response = co.summarize(text=text, length='medium', format='paragraph', model='command')
        return response.summary
    except Exception as e:
        return f"Summarization failed: {e}"


def cohere_classify(text, labels):
    try:
        response = co.classify(inputs=[text], examples=[{"text": l, "label": l} for l in labels])
        return response.classifications[0].prediction
    except Exception as e:
        return f"Classification failed: {e}"


def analyze_sentiment(text):
    try:
        response = co.classify(
            inputs=[text],
            examples=[
                {"text": "I am very happy and excited today!", "label": "positive"},
                {"text": "I feel sad and depressed.", "label": "negative"},
                {"text": "I am okay, nothing special.", "label": "neutral"}
            ]
        )
        return response.classifications[0].prediction
    except:
        return "neutral"
    
def get_current_time():
    return datetime.datetime.now().strftime('%H:%M:%S')

def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def analyze_sentiment(text):
    return "neutral"

def search_google(command):
    try:
        # Extract query after the word 'search'
        query_match = re.search(r"search (?:for|on)? (.+)", command.lower())
        if query_match:
            query = query_match.group(1)
        else:
            return "Please specify what you'd like me to search."

        # Create search URL
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        # Open in browser
        webbrowser.open(search_url)
        
        return f"Searching Google for: {query}"
    except Exception as e:
        return f"Error while searching Google: {e}"


def get_fun_fact():
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient tombs that are over 3000 years old!",
        "A day on Venus is longer than a year on Venus.",
        "Octopuses have three hearts and blue blood."
    ]
    return random.choice(facts)

def get_quote():
    quotes = [
        "The best way to get started is to quit talking and begin doing. - Walt Disney",
        "Success is not in what you have, but who you are. - Bo Bennett",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson"
    ]
    return random.choice(quotes)

def get_greeting():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        return "Good morning, Sir. Ready to conquer the day?"
    elif 12 <= hour < 18:
        return "Good afternoon, Sir. Hope your day is going well."
    else:
        return "Good evening, Sir. Let’s wrap up the day with something productive."

country_capitals = {
    "india": "New Delhi",
    "united states": "Washington, D.C.",
    "france": "Paris",
    "germany": "Berlin",
    "canada": "Ottawa",
    "japan": "Tokyo",
    "china": "Beijing",
    "australia": "Canberra",
    "russia": "Moscow"
}

movie_recommendations = {
    "english": ["Inception", "The Matrix", "Interstellar", "Avengers: Endgame"],
    "hindi": ["3 Idiots", "Dangal", "Sholay", "Taare Zameen Par"],
    "telugu": ["Baahubali", "RRR", "Arjun Reddy", "Eega"]
}

jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the computer go to the doctor? Because it had a virus!",
    "I'm reading a book on anti-gravity. It's impossible to put down!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!"
]

def fallback_huggingface_summary(text):
    try:
        summary = hf_summarizer(text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"HuggingFace fallback summarization failed: {e}"


def handle_command(command):
    command = command.lower()


    if command.startswith("summarize"):
        text_to_summarize = command.replace("summarize this", "").replace("summarize", "").strip()
        if len(text_to_summarize) < 100:
            return "Please provide a longer text (at least 100 characters) for a proper summary."
        try:
            response = co.summarize(text=text_to_summarize, length="medium", format="paragraph", model="command")
            return response.summary
        except:
            return fallback_huggingface_summary(text_to_summarize)

    elif "wikipedia" in command:
        try:
            return wikipedia.summary(command.replace("wikipedia", ""), sentences=3)
        except:
            return "Sorry, I couldn't find anything on Wikipedia."

    elif any(keyword in command for keyword in ["calculate", "what is", "who is", "define"]):
        try:
            res = wolfram_client.query(command)
            return next(res.results).text
        except:
            return "Sorry, I couldn't get an answer from WolframAlpha."

    elif "open youtube" in command:
        webbrowser.open_new_tab("https://www.youtube.com")
        return "YouTube is open now."

    elif "open google" in command:
        webbrowser.open_new_tab("https://www.google.com")
        return "Google is open now."

    elif "open gmail" in command:
        webbrowser.open_new_tab("https://gmail.com")
        return "Gmail is open now."

    elif 'time' in command:
        return f"The current time is {get_current_time()}."

    elif 'date' in command:
        return f"Today's date is {get_current_date()}."


    elif "who are you" in command or "what can you do" in command:
        return 'I am FRIDAY — your Functional Realtime Intelligence and Data Analytics Yielder.'

    elif "who made you" in command:
        return 'I was built by Sivaji.'

    elif "joke" in command:
        return random.choice(jokes)

    elif "recommend movies" in command:
        return "Here are some movie recommendations:\n" + "\n".join([f"{k.title()}: {', '.join(v)}" for k, v in movie_recommendations.items()])

    elif "capital of" in command:
        for country in country_capitals:
            if country in command:
                return f"The capital of {country.title()} is {country_capitals[country]}."
        return "Sorry, I couldn't find the capital of that country."
    
    elif 'quote' in command:
        return get_quote()
    
    elif "search" in command:
        return search_google(command)

    elif "news" in command:
        try:
            url = "https://timesofindia.indiatimes.com/home/headlines"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            headlines = soup.find_all('h2', class_='heading1')
            return '\n'.join([f"Headline {i+1}: {h.get_text().strip()}" for i, h in enumerate(headlines[:5])]) if headlines else "No headlines found."
        except:
            return "Error fetching news."

    elif "fun fact" in command:
        return get_fun_fact()

    elif "quote" in command:
        return get_quote()

    elif "greeting" in command:
        return get_greeting()
    elif "shutdown" in command:
        subprocess.call(["shutdown", "/l"])
        return "Logging off..."

    elif "play music" in command:
        return play_music()

    elif "pause music" in command or "pause the song" in command:
        return pause_music()

    elif "resume music" in command or "resume the song" in command:
        return resume_music()

    elif "next song" in command or "play next" in command:
        return next_song()

    elif "take photo" in command or "open camera" in command:
      ec.capture(0, "FRIDAY Camera", "photo.jpg")
      return "Photo captured."



    elif "classify" in command:
        text = command.replace("classify", "").strip()
        return f"Classification: {cohere_classify(text, ['sports', 'politics', 'technology', 'health'])}"

   

    return "I'm not sure how to help with that."

@app.route("/")
def index():
    return render_template("friday.html")

@app.route("/assistant", methods=['POST'])
def assistant():
    data = request.get_json()
    command = data.get('command', '').lower()
    sentiment = analyze_sentiment(command)
    response = handle_command(command)

    threading.Thread(target=speak, args=(response,), daemon=True).start()

    return jsonify({'response': response, 'sentiment': sentiment})

@app.route("/startup", methods=['GET'])
def startup_info():
    username = "Sivaji"
    greeting = f"Good {get_time_based_greeting()}, {username}!"
    quote = get_quote()
    riddle = get_riddle()
    history = get_today_in_history()

    return jsonify({
        'greeting': greeting,
        'quote': quote,
        'riddle': riddle,
        'history': history
    })
@app.route("/save_chat", methods=["POST"])
def save_chat():
    data = request.get_json()
    user = data.get("user")
    bot = data.get("bot")
    
    if not user or not bot:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    history = {"user": user, "bot": bot}
    filename = "chatHistory.json"

    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                chat_data = json.load(f)
        else:
            chat_data = []

        chat_data.append(history)

        with open(filename, "w") as f:
            json.dump(chat_data, f, indent=2)

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def get_time_based_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def get_riddle():
    riddles = [
        "What has keys but can't open locks? — A piano.",
        "I speak without a mouth and hear without ears. What am I? — An echo.",
        "What gets wetter the more it dries? — A towel."
    ]
    return random.choice(riddles)

def get_today_in_history():
    today = datetime.datetime.now()
    date_str = today.strftime("%B %d")
    events = {
        "June 13": [
            "In 1971, the New York Times began publishing the Pentagon Papers.",
            "In 1983, Pioneer 10 became the first manmade object to leave the central Solar System."
        ],
        "January 1": [
            "In 1801, the Act of Union came into effect, uniting Great Britain and Ireland.",
            "In 1959, Fidel Castro overthrew the Cuban government."
        ]
    }
    return random.choice(events.get(date_str, ["No significant event found for today."]))

@app.route("/weather", methods=['POST'])
def weather():
    data = request.get_json()
    city = data.get('city', 'Paris')
    api_key = "8ef61edcf1c576d65d836254e11ea420"
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city}"
    response = requests.get(complete_url)
    x = response.json()
    if x.get("cod") != "404":
        y = x["main"]
        current_temperature = y["temp"]
        current_humidity = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        result = f"Temperature: {current_temperature}K, Humidity: {current_humidity}%, Description: {weather_description}"
    else:
        result = "City not found"
    return jsonify({'weather': result})

if __name__ == "__main__":
    app.run(debug=True)