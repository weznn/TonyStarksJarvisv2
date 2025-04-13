pip install pyttsx3 sounddevice numpy SpeechRecognition tweepy spotipy

import subprocess
import pyttsx3
import sounddevice as sd
import numpy as np
import wave
import speech_recognition as sr
import tweepy
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ---- 1. Sesli Yanıt (Text-to-Speech) Motoru Başlatma ----
engine = pyttsx3.init()
voices = engine.getProperty('voices')


# ---- 2. Sesli Yanıt Fonksiyonu ----
def speak(text, language="tr"):
    # Türkçe ve İngilizce sesler arasında geçiş yap
    if language == "en":
        engine.setProperty('voice', voices[1].id)  # İngilizce ses
    else:
        engine.setProperty('voice', voices[0].id)  # Türkçe ses

    engine.say(text)
    engine.runAndWait()


# ---- 3. Ses Kaydetme Fonksiyonu ----
def record_audio(duration=5, fs=16000):
    print("🎤 Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    audio_data = np.squeeze(recording)

    # Save the recording as a WAV file
    file_path = "audio.wav"
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(audio_data.tobytes())
    return file_path


# ---- 4. Sesli Soruları Yazıya Döndürme ----
def transcribe_audio(audio_file_path, language="tr"):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio = recognizer.record(source)

    try:
        print(f"🧠 Transcribing audio to text in {language}...")
        # Dil parametresi ile sesli komutları yazıya dökme
        if language == "en":
            text = recognizer.recognize_google(audio, language="en-US")
        else:
            text = recognizer.recognize_google(audio, language="tr-TR")
        print(f"🗨️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("😕 Could not understand the audio.")
        return ""
    except sr.RequestError:
        print("🤖 There was an error connecting to the Google Speech API.")
        return ""


# ---- 5. Uygulama Açma Fonksiyonu ----
def open_application(app_name):
    try:
        subprocess.run(["open", "-a", app_name])
        print(f"{app_name} is opening.")
    except Exception as e:
        print(f"Error opening {app_name}: {e}")


# ---- 6. Bilgisayar Kapatma Fonksiyonu ----
def shutdown_computer():
    subprocess.run(["sudo", "shutdown", "-h", "now"])
    print("💻 Shutting down the computer...")


# ---- 7. Twitter'a Tweet Atma Fonksiyonu ----
def post_on_twitter(tweet):
    auth = tweepy.OAuthHandler("API_KEY", "API_SECRET_KEY")
    auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")
    api = tweepy.API(auth)

    api.update_status(tweet)
    print("📱 Tweet posted!")


# ---- 8. Hava Durumu Fonksiyonu ----
def get_weather(city):
    print(f"🌡️ Weather function for {city} is not available right now.")


# ---- 9. Spotify Entegrasyonu Fonksiyonu ----
def play_spotify_song(song_name):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                                   client_secret="YOUR_CLIENT_SECRET",
                                                   redirect_uri="http://localhost:8888/callback",
                                                   scope="user-library-read user-library-modify user-read-playback-state user-modify-playback-state"))

    results = sp.search(q=song_name, limit=1, type='track')
    track = results['tracks']['items'][0]
    track_url = track['external_urls']['spotify']
    track_name = track['name']

    speak(f"Song {track_name} found. Now playing.", language="en")

    sp.start_playback(uris=[track['uri']])
    print(f"🎶 Now playing: {track_name} - {track_url}")
    return track_name


# ---- 10. Ana Fonksiyon - Jarvis Asistanı ----
def main():
    speak("Hello Mert! I am Jarvis, how can I help you?", language="en")

    # Kullanıcıya hangi dili kullanmak istediğini soruyoruz
    language = input("Select language (tr for Turkish, en for English): ").strip().lower()

    while True:
        print("🎧 Waiting for a command...")
        audio_path = record_audio(duration=5)
        question = transcribe_audio(audio_path, language=language)

        if "shutdown" in question.lower() or "kapat" in question.lower():
            speak("Shutting down the computer...", language=language)
            shutdown_computer()
            break
        elif "open" in question.lower() or "aç" in question.lower():
            app_name = question.split("open")[1].strip() if "open" in question.lower() else question.split("aç")[
                1].strip()
            speak(f"{app_name} is opening.", language=language)
            open_application(app_name)
        elif "tweet" in question.lower() or "tweet at" in question.lower():
            tweet = question.split("tweet")[1].strip() if "tweet" in question.lower() else question.split("tweet at")[
                1].strip()
            speak("Tweet is being posted.", language=language)
            post_on_twitter(tweet)
        elif "weather" in question.lower() or "hava" in question.lower():
            city = question.split("weather")[1].strip() if "weather" in question.lower() else question.split("hava")[
                1].strip()
            get_weather(city)
        elif "spotify" in question.lower():
            song_name = question.split("spotify")[1].strip()
            play_spotify_song(song_name)
        elif "exit" in question.lower() or "quit" in question.lower():
            speak("Goodbye Mert!", language=language)
            break
        else:
            speak("Sorry, I couldn't understand that. Please try again.", language=language)


# Jarvis'i başlatma
if __name__ == "__main__":
    main()
