# OptiTune 🎵

OptiTune is a modern, deep metric learning-powered audio fingerprinting and music recognition application. It allows users to instantly identify tracks acting as an "Acoustic Engine" by recording from a microphone or uploading an audio file. Furthermore, it features a sleek streaming-platform aesthetic with a functional interactive music library.

## ✨ Features
- **Acoustic Fingerprinting**: Uses `librosa` to extract 128-dimensional mathematical feature vectors (MFCCs) from audio waves.
- **Smart Matching Engine**: Implements sliding window frame-level analysis and similarity distance logic to find the closest matching audio segment with extremely high accuracy.
- **Direct System FFmpeg Integration**: Rapidly captures, filters, and standardizes web audio formats directly on the backend using `imageio_ffmpeg`.
- **My Library Streaming**: A dynamic dashboard loaded with playable local tracks inside interactive glassmorphic tiles representing your custom `music_library/` folder. Native UI components include play/pause state caching and a real-time seek bar.
- **Premium Frontend Aesthetics**: Modern responsive design using React and Vanilla CSS (Dark mode, neon glows, hover states, fluid carousels).

---

## 🛠️ Technology Stack
- **Frontend**: React 19, Vite, Vanilla CSS
- **Backend**: FastAPI, Python, Uvicorn
- **Machine Learning**: Librosa, NumPy

---

## 🚀 How to Run Locally

### 1. Prerequisites
- **Node.js** (v18 or higher recommended)
- **Python** (v3.8 or higher)

### 2. Clone the Repository
```bash
git clone https://github.com/rishabh0456/Audio-Fingerprinting-Music-Recognition-ML-Project.git
cd Audio-Fingerprinting-Music-Recognition-ML-Project
```

### 3. Backend Setup (FastAPI & ML Engine)
Open a terminal in the root directory of the project:
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - **Windows**: `.\venv\Scripts\activate`
   - **Mac/Linux**: `source venv/bin/activate`
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend ML server:
   ```bash
   python server.py
   ```
   *The API will start running perfectly at `http://127.0.0.1:8000`.*

### 4. Frontend Setup (React/Vite)
Open a *new* terminal, separate from the running backend:
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The application will boot up at `http://localhost:5173`. Open this URL in your web browser!*

### 5. Managing Your Music Library
To add songs to your internal system player (the **My Library** tab):
- Drop any `.mp3` or `.wav` music files directly inside the `music_library/` folder located in the root of the project.
- The web app dynamically creates a tile for every track dropped in that directory!

---

## 📄 License
MIT License - copy, modify, and distribute out of the box!
