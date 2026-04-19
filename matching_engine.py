import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import librosa
import warnings

warnings.filterwarnings('ignore')

DATABASE = []

import scipy.signal

def extract_vector(y, sr):
    y = librosa.util.normalize(y)
    
    # 1. EXPLICIT NOISE FILTERING STAGE:
    # Remove laptop fan rumbles (under 300Hz) and high-pitch static/hiss (over 3400Hz)
    b, a = scipy.signal.butter(4, [300 / (sr / 2), 3400 / (sr / 2)], btype='bandpass')
    y_filtered = scipy.signal.filtfilt(b, a, y)
    
    # Apply pre-emphasis to further crush ambient background hum
    y_clean = librosa.effects.preemphasis(y_filtered)
    
    # 2. MELODY RECOGNITION:
    # Now that the noise is filtered out, we extract the pure musical notes
    try:
        chroma = librosa.feature.chroma_stft(y=y_clean, sr=sr)
        blocks = np.array_split(chroma, 5, axis=1)
        means = [np.mean(b, axis=1) for b in blocks]
        
        fingerprint = np.concatenate(means)
        norm = np.linalg.norm(fingerprint)
        if norm > 0:
            fingerprint = fingerprint / norm
            
        return fingerprint
    except:
        return None

def build_database(music_folder="music_library"):
    print(f"\nBuilding Noise-Resistant Database from '{music_folder}'...")
    DATABASE.clear() 
    
    if not os.path.exists(music_folder):
        os.makedirs(music_folder)
        return False

    for filename in os.listdir(music_folder):
        if filename.endswith(".mp3") or filename.endswith(".wav"):
            filepath = os.path.join(music_folder, filename)
            print(f"Extracting & slicing: {filename}...")
            
            try:
                y, sr = librosa.load(filepath, sr=22050)
                chunk_length_samples = 5 * sr 
                # Slice the 3-minute song into searchable 5-second chunks
                for i in range(0, len(y), chunk_length_samples):
                    y_chunk = y[i : i + chunk_length_samples]
                    if len(y_chunk) >= 3 * sr:
                        # Skip purely silent or low energy chunks to prevent noise amplification
                        if np.max(np.abs(y_chunk)) < 0.01:
                            continue
                            
                        vector = extract_vector(y_chunk, sr)
                        if vector is not None:
                            DATABASE.append({"song": filename, "vector": vector})
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                
    print(f"\nDatabase built! Indexed {len(DATABASE)} unique chunks.")
    return len(DATABASE) > 0

def identify_song(query_audio_path):
    try:
        y_query, sr_query = librosa.load(query_audio_path, sr=22050)
    except Exception:
        return "Error reading query audio."

    best_match = "Unknown"
    highest_score = -1

    chunk_samples = 5 * sr_query
    hop_samples = int(2.5 * sr_query)

    # Convert query into sliding windows to properly find alignment with 5-second chunks
    for i in range(0, max(1, len(y_query) - chunk_samples + 1), hop_samples):
        y_chunk = y_query[i : i + chunk_samples]
        
        # Only process if chunk has enough audio (at least 1 second)
        if len(y_chunk) >= 1 * sr_query:
            if np.max(np.abs(y_chunk)) < 0.01:
                continue
                
            query_vector = extract_vector(y_chunk, sr_query)
            if query_vector is None:
                continue
                
            for item in DATABASE:
                score = cosine_similarity(query_vector.reshape(1, -1), item["vector"].reshape(1, -1))[0][0]
                if score > highest_score:
                    highest_score = score
                    best_match = item["song"]

    if highest_score < 0.85:
        return "No audible match found."

    match_percentage = highest_score * 100
    
    return f"Match Found: {best_match} (Confidence: {match_percentage:.2f}%)"