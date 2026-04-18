import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from groq import Groq
from faster_whisper import WhisperModel
import subprocess

app = FastAPI()

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "PASTE_YOUR_KEY_HERE")
PIPER_MODEL = "/app/voices/voice.onnx"
PIPER_CONFIG = "/app/voices/voice.onnx.json"

client = Groq(api_key=GROQ_API_KEY)
stt_model = WhisperModel("tiny", device="cpu", compute_type="int8")

@app.post("/process_voice")
async def process_voice(file: UploadFile = File(...)):
    # 1. Save incoming audio
    with open("input.wav", "wb") as f:
        f.write(await file.read())

    # 2. Speech to Text (Ears)
    segments, _ = stt_model.transcribe("input.wav")
    user_text = " ".join([segment.text for segment in segments]).strip()
    print(f"User said: {user_text}")

    # 3. Brain (Groq)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": user_text}],
        model="llama3-8b-8192",
    )
    bot_response = chat_completion.choices[0].message.content
    print(f"Bot response: {bot_response}")

    # 4. Text to Speech (Voice)
    # We output to a file called output.wav
    command = f'echo "{bot_response}" | piper --model {PIPER_MODEL} --config {PIPER_CONFIG} --output_file output.wav'
    subprocess.run(command, shell=True)

    return FileResponse("output.wav", media_type="audio/wav")
