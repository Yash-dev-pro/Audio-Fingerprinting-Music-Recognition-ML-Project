import librosa
import numpy as np
import warnings

# Suppress minor audio warnings for a cleaner terminal
warnings.filterwarnings('ignore')

def generate_fingerprint(audio_path):
    """
    Takes an audio file and returns a 128-dimensional mathematical vector.
    """
    try:
        # 1. Load the audio file. 
        # sr=22050 standardizes the sample rate so all files are treated equally.
        y, sr = librosa.load(audio_path, sr=22050)
        
        # 2. Extract Features (The ML Magic)
        # We extract 128 distinct frequency patterns (MFCCs) from the audio wave.
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=128)
        
        # 3. Dimensionality Reduction
        # The mfccs variable is a 2D matrix (128 x Time). 
        # We average it across the time axis to get a single, flat 128-number array.
        fingerprint_vector = np.mean(mfccs.T, axis=0)
        
        return fingerprint_vector
        
    except Exception as e:
        print(f"Error processing {audio_path}: {e}")
        return None

# --- TESTING THE SCRIPT ---
if __name__ == "__main__":
    print("Initializing Machine Learning Extractor...")
    
    # To test this, place any small .mp3 or .wav file in the same folder 
    # and rename it to 'test_song.mp3', or change the name below.
    test_file = "test_song.mp3" 
    
    vector = generate_fingerprint(test_file)
    
    if vector is not None:
        print(f"\nSuccess! Extracted a {vector.shape[0]}-dimensional fingerprint.")
        print("Here are the first 5 numbers of the vector:")
        print(vector[:5])
    else:
        print("\nPlease add an audio file named 'test_song.mp3' to your folder to test.")