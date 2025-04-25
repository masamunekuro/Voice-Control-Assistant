import os
import requests
import speech_recognition as sr
import pyttsx3
import time
import webbrowser
import subprocess
import yt_dlp
import pyaudio
import keyboard

# Konuşma motoru
engine = pyttsx3.init()
language = "en"  # Varsayılan dil
hold = 0

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
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            video_url = info['webpage_url']
            print(f"Opening video: {video_url}")
            webbrowser.open(video_url)
            speak(f"{query} açılıyor." if language == "tr" else f"Opening {query} on YouTube.")
        except Exception as e:
            speak("Video bulunamadı." if language == "tr" else "Sorry, I couldn't find any video.")
            print(f"Error: {e}")

def get_command_from_user():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio, language='tr-TR' if language == "tr" else 'en-US')
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Anlayamadım." if language == "tr" else "Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Konuşma tanıma servisine ulaşılamıyor." if language == "tr" else "Speech recognition service is unavailable.")
            return ""


def ask_deepseek_for_action(command):
    system_prompt = {
        "en": "You are a helpful assistant. Help as possible for user.",
        "tr": "Sen yardımcı bir asistansın. Kullanıcıya elinden geldiğince yardım et."
    }
    user_prompt = {
        "en": f"The user said: '{command}'.",
        "tr": f"Kullanıcı dedi ki: '{command}'."
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt[language]},
            {"role": "user", "content": user_prompt[language]}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        action = response.json()["choices"][0]["message"]["content"].strip().lower()
        print(f"DeepSeek suggests action: {action}")
        return action
    except Exception as e:
        speak("DeepSeek'ten yanıt alınamadı." if language == "tr" else "Couldn't get response from DeepSeek.")
        print("DeepSeek error:", e)
        return ""


def execute_action(action):
    global language, hold

    if action in ["change language", "dili değiştir"]:
        language = "tr" if language == "en" else "en"
        speak("Dil Türkçe olarak ayarlandı." if language == "tr" else "Language set to English.")
        return

    if action in ["volume up", "sesi aç"]:
        os.system("nircmd.exe changesysvolume 5000")
        speak("Ses artırıldı." if language == "tr" else "Volume increased.")
    elif action in ["volume down", "Sesi kıs"]:
        os.system("nircmd.exe changesysvolume -8000")
        speak("Ses azaltıldı." if language == "tr" else "Volume decreased.")
    elif action in ["volume maximum", "maksimum ses"]:
        os.system("nircmd.exe changesysvolume 500000")
        speak("Ses maksimuma çıkarıldı." if language == "tr" else "Volume set to maximum.")
    elif action in ["mute", "sessize al"]:
        os.system("nircmd.exe mutesysvolume 1")
        speak("Ses kapatıldı." if language == "tr" else "Muted.")
    elif action in ["unmute", "sesi Geri aç"]:
        os.system("nircmd.exe mutesysvolume 0")
        speak("Ses açıldı." if language == "tr" else "Unmuted.")
    elif action in ["shut down", "Bilgisayarı kapat"]:
        speak("Bilgisayar kapatılıyor." if language == "tr" else "Shutting down the system.")
        os.system("shutdown /s /t 5")
    elif action in ["open youtube", "youtube aç"]:
        speak("YouTube açılıyor." if language == "tr" else "Opening YouTube.")
        webbrowser.open("https://youtube.com")
    elif "open youtube video" in action or "YouTube videosu aç" in action:
        speak("Hangi video?" if language == "tr" else "Which video?")
        query = get_command_from_user().lower()
        if not query:
            speak("Video ismini anlayamadım." if language == "tr" else "I didn't catch the video name.")
            return
        open_youtube_with_ytdlp(query)
    elif action == "holding" or action == "bekle":
        hold = 1
        speak("Bekleniyor. Ctrl+G ile çıkabilirsiniz." if language == "tr" else "Holding. Press Ctrl+G to stop.")
        while hold == 1:
            if keyboard.is_pressed('ctrl+g'):
                hold = 0
                break
    elif action.startswith("open video:"):
        filename = action.split(":", 1)[1].strip()
        video_path = f"{filename}.mp4"
        if os.path.exists(video_path):
            speak(f"{filename} açılıyor." if language == "tr" else f"Opening video {filename}.")
            subprocess.Popen(["start", video_path], shell=True)
        else:
            speak(f"{video_path} bulunamadı." if language == "tr" else f"Video file {video_path} not found.")
    elif action == "jarvis":
        speak("Ne yapabilirim?" if language == "tr" else "What can I do for you?")
        parts = ask_deepseek_for_action(get_command_from_user()).split('</think>')
        speak(parts[1].strip())



if __name__ == "__main__":
    speak("Sesli kontrol sistemi hazır." if language == "tr" else "Voice control system is ready.")
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
