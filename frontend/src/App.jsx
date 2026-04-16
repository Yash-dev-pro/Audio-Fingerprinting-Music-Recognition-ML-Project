import React, { useState, useRef, useEffect } from 'react';
import './index.css';

const LibraryTile = ({ song, currentlyPlaying, setCurrentlyPlaying }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef(null);

  useEffect(() => {
    if (currentlyPlaying !== song && isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  }, [currentlyPlaying, song, isPlaying]);

  const togglePlay = () => {
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
      setCurrentlyPlaying(song);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current.duration) {
      setProgress((audioRef.current.currentTime / audioRef.current.duration) * 100);
    }
  };

  const handleLoadedMetadata = () => {
    setDuration(audioRef.current.duration);
  };

  const handleSeek = (e) => {
    const seekTime = (e.target.value / 100) * duration;
    audioRef.current.currentTime = seekTime;
    setProgress(Number(e.target.value));
  };

  const formatTime = (time) => {
    if (!time || isNaN(time)) return "0:00";
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  return (
    <div className="tile-card">
      <audio 
        ref={audioRef} 
        src={`http://127.0.0.1:8000/audio/${encodeURIComponent(song)}`}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => { setIsPlaying(false); setProgress(0); }}
      />
      <div className="tile-icon playback" onClick={togglePlay}>
        <i className={`fa-solid ${isPlaying ? 'fa-pause' : 'fa-play'}`}></i>
      </div>
      <div className="tile-info">
        <h3 className="tile-title" title={song}>{song.replace(/\.[^/.]+$/, "")}</h3>
        <div className="seek-container">
          <input 
            type="range" 
            className="seek-bar" 
            value={progress || 0} 
            onChange={handleSeek} 
          />
          <div className="time-display">
            <span>{audioRef.current ? formatTime(audioRef.current.currentTime) : "0:00"}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const [currentTab, setCurrentTab] = useState('Engine');
  const [librarySongs, setLibrarySongs] = useState([]);
  const [status, setStatus] = useState('Identify any song instantly');
  const [result, setResult] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (currentTab === 'My Library') {
      fetch('http://127.0.0.1:8000/library')
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            setLibrarySongs(data.files);
          }
        })
        .catch(err => console.error("Error fetching library:", err));
    }
  }, [currentTab]);

  // --- CORE API FUNCTION ---
  const sendToAPI = async (formData) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/identify", {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setStatus('Match Found');
        // Clean up the extension from the result string for a cleaner look
        let cleanResult = data.result.replace("Match Found: ", "").replace(".mp3", "");
        setResult(cleanResult);
      } else {
        setStatus('Error analyzing audio.');
        setResult(data.message);
      }
    } catch (err) {
      setStatus('Server Offline');
      setResult('Is FastAPI running on port 8000?');
    }
  };

  // --- MANUAL MICROPHONE LOGIC ---
  const handleMicClick = async () => {
    if (isRecording) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.addEventListener('dataavailable', (e) => {
        audioChunksRef.current.push(e.data);
      });

      mediaRecorderRef.current.addEventListener('stop', () => {
        setIsRecording(false);
        setStatus('Analyzing acoustic fingerprint...');
        
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');
        
        sendToAPI(formData);
        stream.getTracks().forEach(track => track.stop());
      });

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setStatus('Listening... Tap again to search');
      setResult('');

    } catch (err) {
      setStatus('Microphone access denied.');
    }
  };

  // --- UPLOAD LOGIC ---
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setStatus(`Extracting features...`);
    setResult('');
    
    const formData = new FormData();
    formData.append('file', file, file.name);
    
    sendToAPI(formData);
    e.target.value = ''; 
  };

  return (
    <>
      <nav className="navbar">
        <div className="nav-left">
          <a href="#" className="nav-logo">
            <i className="fa-solid fa-waveform"></i> OptiTune
          </a>
          <div className="nav-links">
            <a href="#" className={currentTab === 'Engine' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setCurrentTab('Engine'); }}>Engine</a>
            <a href="#" className={currentTab === 'My Library' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setCurrentTab('My Library'); }}>My Library</a>
          </div>
        </div>
      </nav>

      {currentTab === 'Engine' ? (
      <header className="hero-section">
        <div className="hero-bg"></div>
        <div className="hero-vignette"></div>
        
        <div className="hero-content">
          <div className="recording-widget">
            <div className="hero-tag">Acoustic Engine</div>
            <h1 className="hero-title">Recognize</h1>
            <p className="hero-subtitle">Let OptiTune listen to your environment and instantly identify the track, artist, and album using deep metric learning.</p>
            
            <button 
              className={`mic-btn ${isRecording ? 'recording' : ''}`} 
              onClick={handleMicClick}
              title="Tap to identify"
            >
              <i className={`fa-solid ${isRecording ? 'fa-stop' : 'fa-microphone'}`}></i>
            </button>
            
            <div className="status-text">{status}</div>
            {result && <div className="result-text">{result}</div>}

            <button className="upload-btn" onClick={() => fileInputRef.current.click()}>
              <i className="fa-solid fa-arrow-up-from-bracket"></i> Select Audio File
            </button>
            <input 
              type="file" 
              accept="audio/*" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              onChange={handleFileUpload} 
            />
          </div>
        </div>
      </header>
      ) : (
      <section className="library-section">
        <h2 className="section-title">My Library Tracks</h2>
        <div className="tiles-grid">
          {librarySongs.length === 0 ? (
            <p className="status-text">No tracks found in the library.</p>
          ) : (
            librarySongs.map((song, index) => (
              <LibraryTile 
                key={index} 
                song={song} 
                currentlyPlaying={currentlyPlaying} 
                setCurrentlyPlaying={setCurrentlyPlaying} 
              />
            ))
          )}
        </div>
      </section>
      )}


    </>
  );
}

export default App;