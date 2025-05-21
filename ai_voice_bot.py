import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
import google.generativeai as genai

# Set your Gemini API Key
genai.configure(api_key=st.secrets.get("gemini_api_key", "AIzaSyC6ptAJgrYxq_9ZopJteK2cFpgI3gIdg5Q"))

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash-002')

# Page setup
st.set_page_config(page_title="Gemini Voice Bot", layout="centered")
st.title("🎙️ Gemini AI Voice Bot")
st.markdown("Talk to your AI bot using **voice or text** and hear it speak back!")

# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Language and toggles
lang = st.selectbox("🌍 Choose Language for TTS", ["en", "hi", "ta", "te", "fr", "es"])
voice_input = st.toggle("🎤 Voice Input", value=False)
voice_output = st.toggle("🔊 Voice Output", value=True)

# Function: STT
def listen_microphone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.WaitTimeoutError:
            return "No speech detected."
        except Exception as e:
            return f"Error: {str(e)}"

# Function: Gemini AI response
def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini Error: {e}"

# Function: TTS
def speak_text(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio = AudioSegment.from_file(mp3_fp, format="mp3")
        play(audio)
    except Exception as e:
        st.error(f"TTS Error: {e}")

# Input
if voice_input:
    if st.button("🎙️ Speak Now"):
        user_input = listen_microphone()
        st.write("You said:", user_input)
    else:
        user_input = None
else:
    user_input = st.text_input("💬 Type your message:")

# Get response
if user_input:
    response = get_gemini_response(user_input)
    st.success(response)

    # Save history
    st.session_state.history.append((user_input, response))

    if voice_output:
        speak_text(response, lang=lang)

# Show history
with st.expander("🕓 Chat History"):
    for i, (user, bot) in enumerate(st.session_state.history, 1):
        st.markdown(f"**You {i}:** {user}")
        st.markdown(f"**Bot {i}:** {bot}")
