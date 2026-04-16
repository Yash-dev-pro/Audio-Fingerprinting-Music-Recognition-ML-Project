from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import shutil
import warnings
import subprocess
import imageio_ffmpeg as imageio
from matching_engine import build_database, identify_song

warnings.filterwarnings('ignore')

app = FastAPI(title="OptiTune API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Starting server and loading ML models...")
build_database()

from fastapi.responses import FileResponse

@app.get("/")
def home():
    return {"message": "Audio Fingerprinting API is running!"}

@app.get("/library")
def get_library():
    try:
        library_path = "music_library"
        if not os.path.exists(library_path):
            return {"status": "error", "message": "Directory not found", "files": []}
            
        files = [f for f in os.listdir(library_path) if f.endswith(('.mp3', '.wav'))]
        return {"status": "success", "files": files}
    except Exception as e:
        return {"status": "error", "message": str(e), "files": []}

@app.get("/audio/{filename}")
def get_audio(filename: str):
    file_path = os.path.join("music_library", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"status": "error", "message": "File not found"}

@app.post("/identify")
async def identify_audio(file: UploadFile = File(...)):
    temp_original_path = f"temp_{file.filename}"
    wav_path = "temp_clean.wav"
    
    try:
        # 1. Save the incoming messy browser file
        with open(temp_original_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. DIRECT FFMPEG CONVERSION (Bypassing pydub entirely!)
        print(f"Converting {temp_original_path} to WAV format...")
        ffmpeg_exe = imageio.get_ffmpeg_exe()
        
        # This commands FFmpeg directly via your system to convert the file
        subprocess.run([
            ffmpeg_exe, 
            "-y",                     # Overwrite output file if it exists
            "-i", temp_original_path, # Input file
            wav_path                  # Output file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # 3. Run the ML engine on the perfectly clean WAV file
        print("Running ML extraction...")
        result = identify_song(wav_path)
        
        # 4. Clean up the hard drive
        if os.path.exists(temp_original_path): os.remove(temp_original_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        print(f"Server Error: {str(e)}")
        # Safe cleanup so Windows doesn't throw PermissionError
        try:
            if os.path.exists(temp_original_path): os.remove(temp_original_path)
            if os.path.exists(wav_path): os.remove(wav_path)
        except:
            pass
            
        return {"status": "error", "message": f"System Conversion Error. Check terminal."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)