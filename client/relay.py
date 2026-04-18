import requests
import pyaudio
import wave
import os

# Config
SERVER_URL = "http://localhost:8000/process_voice"
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5

def record_and_send():
    p = pyaudio.PyAudio()
    
    print("\nListening... (Speak now)")
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        frames.append(stream.read(CHUNK))
    
    print("Sending to Docker...")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save to temporary file
    with wave.open("temp_req.wav", 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Send to Docker Server
    with open("temp_req.wav", 'rb') as f:
        response = requests.post(SERVER_URL, files={'file': f})

    if response.status_code == 200:
        with open("temp_res.wav", 'wb') as f:
            f.write(response.content)
        
        # Play the response (Uses Windows default player)
        os.system("start temp_res.wav")
    else:
        print("Error from server:", response.text)

if __name__ == "__main__":
    while True:
        record_and_send()
