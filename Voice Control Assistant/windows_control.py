import os
import requests
import speech_recognition as sr
import pyttsx3
import time
from youtubesearchpython import VideosSearch
import webbrowser
import subprocess
import yt_dlp
import webbrowser
import pyttsx3
import speech_recognition as sr
import time
# Konuşma motoru
engine = pyttsx3.init()

# LM Studio API ayarı
API_URL = "http://localhost:1234/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json"
}

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()
def open_youtube_with_ytdlp(query):
    # yt_dlp ile YouTube araması yapma
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # ytsearch ile YouTube'da arama
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            video_url = info['webpage_url']
            print(f"Opening video: {video_url}")
            webbrowser.open(video_url)
            speak(f"Opening {query} on YouTube.")
        except Exception as e:
            speak("Sorry, I couldn't find any video.")
            print(f"Error: {e}")
def get_command_from_user():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = r.listen(source)

        try:
            command = r.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Speech recognition service is unavailable.")
            return ""


def ask_deepseek_for_action(command):
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Help as possible for user."},
            {"role": "user", "content": f"The user said: '{command}'."}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        action = response.json()["choices"][0]["message"]["content"].strip().lower()
        print(f"DeepSeek suggests action: {action}")
        return action
    except Exception as e:
        speak("Couldn't get response from DeepSeek.")
        print("DeepSeek error:", e)
        return ""



def execute_action(action):
    if action == "volume up":
        os.system("nircmd.exe changesysvolume 5000")
        speak("Volume increased.")
    elif action == "volume down":
        os.system("nircmd.exe changesysvolume -5000")
        speak("Volume decreased.")
    elif action == "volume maximum":
        os.system("nircmd.exe changesysvolume 500000 ")
        speak("Volume maximum decreased.")
    elif action == "shut down":
        speak("Shutting down the system.")
        os.system("shutdown /s /t 5")
    elif action == "mute":
        os.system("nircmd.exe mutesysvolume 1")
        speak("Muted.")
    elif action == "unmute":
        os.system("nircmd.exe mutesysvolume 0")
        speak("Unmuted.")
    elif action == "open youtube":
        speak("Opening YouTube.")
        webbrowser.open("https://youtube.com")
    elif action.startswith("open video:"):
        filename = action.split(":", 1)[1].strip()
        video_path = f"{filename}.mp4"
        if os.path.exists(video_path):
            speak(f"Opening video {filename}.")
            subprocess.Popen(["start", video_path], shell=True)
        else:
            speak(f"Video file {video_path} not found.")

    elif "open youtube video" in action.lower():
        speak("Which video do you want to open?")
        # Burada tekrar dinle
        query = get_command_from_user().lower()
        if not query:
            speak("I didn't catch the video name.")
            return
        print(f"User wants to search: {query}")
        speak(f"Searching YouTube for {query}.")
        try:
            '''
             results = VideosSearch(query, limit=1).result()
            video_url = results['result'][0]['link']
            speak("Opening video now.")
            webbrowser.open(video_url)
            '''
            open_youtube_with_ytdlp(query)

        except Exception as e:
            speak("Could not open YouTube video.")
            print("YouTube error:", e)
    elif action == "Jarvis":
        speak("what can i do for you?")
        parts = ask_deepseek_for_action(get_command_from_user()).split('</think>')
        speak(parts[1].strip())




# Ana döngü
if __name__ == "__main__":
    speak("Voice control system is ready.")
    while True:
        command = get_command_from_user()
        '''
                if command:
            action = ask_deepseek_for_action(command)
            if action:
                execute_action(action)
        '''
        execute_action(command)
        time.sleep(1)

