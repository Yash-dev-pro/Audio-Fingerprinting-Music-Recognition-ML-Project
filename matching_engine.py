import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import librosa
import warnings

warnings.filterwarnings('ignore')

DATABASE = []

def extract_vector(y, sr):
    """The Ultimate Feature Extractor: Filters noise, normalizes volume, extracts melody."""
    
    # 1. NOISE FILTER: Applies a pre-emphasis filter to boost the actual song and kill background hum
    y = librosa.effects.preemphasis(y)
    
    # 2. VOLUME NORMALIZER: Forces the mic recording to match the exact volume of the MP3
    y = librosa.util.normalize(y)
    
    # 3. TEXTURE (MFCC): Reduced to 40 features to ignore generic noise
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    mfccs_mean = np.mean(mfccs[1:].T, axis=0) # [1:] Drops the raw volume metric
    
    # 4. MELODY (Chroma): Listens strictly to the musical notes (A, B, C, D)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma.T, axis=0)
    
    # 5. MATHEMATICAL SCALING: Merges them and scales the vector to prevent false overlaps
    fingerprint = np.concatenate((mfccs_mean, chroma_mean))
    norm = np.linalg.norm(fingerprint)
    if norm > 0:
        fingerprint = fingerprint / norm
        
    return fingerprint

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

    if highest_score == -1:
        return "No audible match found."

    match_percentage = round(highest_score * 100, 2)
    
    # It will ALWAYS return the absolute best match it found out of your 3 songs
    return f"Match Found: {best_match} (Confidence: {match_percentage}%)"