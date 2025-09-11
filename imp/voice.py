import ollama
import speech_recognition as sr
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess

# Record audio using sounddevice
def record_audio(filename="input.wav", duration=5, fs=44100):
    print("🎙️ Speak now (recording)...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    write(filename, fs, audio)
    print("✅ Recording saved as", filename)

# Convert speech to text
def speech_to_text(filename="input.wav"):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except (sr.UnknownValueError, sr.RequestError):
        return ""

# Normal ORION chat
def ask_orion_chat(prompt):
    response = ollama.chat(
        model="orion",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# Special mode: force Orion to generate pytest code
def ask_orion_tests(function_code):
    cmd = [
        "ollama", "run", "orion",
        f"Generate pytest test cases for the following function. "
        f"Output ONLY Python code, no explanations:\n{function_code}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip()

# Speak response
def speak(text, enable=True):
    if not enable:
        return
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    print(f"ORION: {text}")
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# Main loop
if __name__ == "__main__":
    speak("Ahoy Sir, ORION voice interface online.", enable=True)
    print("Choose mode: 'type', 'voice', or 'both'")
    mode = input(">> Your choice: ").strip().lower()

    if mode not in ["type", "voice", "both"]:
        print("Invalid choice. Defaulting to 'type' mode.")
        mode = "type"

    # Enable speaking only for voice or both
    speak_enable = mode in ["voice", "both"]

    while True:
        if mode == "type":
            user_text = input("You: ")
            if user_text.lower() in ["exit", "quit"]:
                if speak_enable:
                    speak("Shutting down. Goodbye, Sir.", enable=speak_enable)
                else:
                    print("Shutting down. Goodbye, Sir.")
                break

        elif mode == "voice":
            input(">> Press Enter to speak (or type 'exit'): ")
            record_audio()
            user_text = speech_to_text()
            if not user_text:
                speak("Sorry Sir, I didn’t catch that.", enable=speak_enable)
                continue
            print("You:", user_text)
            if user_text.lower() in ["exit", "quit"]:
                speak("Shutting down. Goodbye, Sir.", enable=speak_enable)
                break

        elif mode == "both":
            cmd = input(">> Type your message, or press Enter for voice: ").strip()
            if cmd.lower() in ["exit", "quit"]:
                speak("Shutting down. Goodbye, Sir.", enable=speak_enable)
                break
            if cmd == "":
                record_audio()
                user_text = speech_to_text()
                if not user_text:
                    speak("Sorry Sir, I didn’t catch that.", enable=speak_enable)
                    continue
                print("You:", user_text)
            else:
                user_text = cmd

        # Decide whether it's a test case request
        if "test case" in user_text.lower() or "pytest" in user_text.lower():
            if speak_enable:
                speak("Please provide the Python function for which I should generate test cases.", enable=speak_enable)
            else:
                print("Please provide the Python function for which I should generate test cases.")

            print("Paste function code (end with a single line 'END'):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            function_code = "\n".join(lines)

            orion_reply = ask_orion_tests(function_code)
            print("\n=== Generated Test Cases ===\n")
            print(orion_reply)
            print("\n===========================\n")
            speak("Test cases generated successfully, Sir.", enable=speak_enable)
        else:
            # Normal chat
            orion_reply = ask_orion_chat(user_text)
            if speak_enable:
                speak(orion_reply, enable=speak_enable)
            else:
                print(f"ORION: {orion_reply}")
