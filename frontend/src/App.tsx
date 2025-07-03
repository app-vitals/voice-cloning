import { useState } from 'react';
import { LiveKitRoom, AudioConference } from '@livekit/components-react';
import '@livekit/components-styles';
import './App.css';
import { TranscriptionDisplay } from './components/TranscriptionDisplay';
import { VoiceIndicator } from './components/VoiceIndicator';

function App() {
  const [token, setToken] = useState<string>('');
  const [url, setUrl] = useState<string>('');
  const [participantName, setParticipantName] = useState<string>('');
  const [connected, setConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const connect = async () => {
    if (!participantName.trim()) {
      alert('Please enter your name.');
      return;
    }

    setIsConnecting(true);
    try {
      const response = await fetch(`http://localhost:8000/api/get-token?participant=${encodeURIComponent(participantName)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setToken(data.token);
      setUrl(data.url);
      setConnected(true);
    } catch (e) {
      console.error('Connection error:', e);
      alert('Failed to connect to voice cloning demo. Is the backend running? Check console for details.');
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnect = () => {
    setConnected(false);
    setToken('');
    setUrl('');
    console.log('Disconnected from voice cloning demo');
  };

  const onConnected = () => {
    console.log('Connected to voice cloning demo room');
  };

  const onDisconnected = () => {
    setConnected(false);
    setToken('');
    setUrl('');
    console.log('Disconnected from voice cloning demo room');
  };

  const onError = (error: Error) => {
    console.error('LiveKit error:', error);
    alert(`Connection error: ${error.message}`);
  };

  return (
    <div className="demo-container" data-lk-theme="default">
      <header className="demo-header">
        <div className="demo-header-content">
          <div className="demo-header-text">
            <h1>🎤 Voice Cloning Demo</h1>
            <p className="demo-subtitle">Real-time voice conversation with AI</p>
          </div>
        </div>
        <p className="demo-description">
          Experience voice cloning technology powered by Resemble AI and LiveKit. 
          Have a natural conversation with an AI assistant using cloned voices.
        </p>
      </header>
      
      {!connected ? (
        <div className="demo-connect-card">
          <h2>Ready to try voice cloning?</h2>
          <p>Enter your name to start a conversation with our AI assistant...</p>
          
          <div className="form-group">
            <label htmlFor="participant">Your Name:</label>
            <input
              id="participant"
              type="text"
              value={participantName}
              onChange={(e) => setParticipantName(e.target.value)}
              placeholder="Enter your name"
              onKeyPress={(e) => e.key === 'Enter' && !isConnecting && connect()}
              disabled={isConnecting}
            />
          </div>
          
          <button 
            onClick={connect} 
            disabled={isConnecting || !participantName.trim()}
            className="demo-connect-btn"
          >
            {isConnecting ? 'Connecting...' : 'Start Voice Demo'}
          </button>
          
          <div className="demo-tips">
            <h3>About this demo:</h3>
            <ul>
              <li>Real-time voice conversation with AI</li>
              <li>Powered by Resemble AI voice synthesis</li>
              <li>Uses LiveKit for low-latency audio</li>
              <li>Try asking questions or having a natural chat</li>
            </ul>
          </div>
        </div>
      ) : (
        <div className="demo-room">
          <div className="demo-room-header">
            <h2>🎙️ Voice Cloning Demo Session</h2>
            <button onClick={disconnect} className="demo-disconnect-btn">
              End Demo
            </button>
          </div>
          
          <LiveKitRoom
            serverUrl={url}
            token={token}
            connect={true}
            onConnected={onConnected}
            onDisconnected={onDisconnected}
            onError={onError}
            audio={true}
            video={false}
          >
            <div className="demo-audio-interface">
              <AudioConference />
              <VoiceIndicator />
              <TranscriptionDisplay />
            </div>
          </LiveKitRoom>
        </div>
      )}
      
      <footer className="demo-footer">
        <p>
          Voice cloning technology demonstration using{' '}
          <a href="https://www.resemble.ai/" target="_blank" rel="noopener noreferrer">
            Resemble AI
          </a>
          {' '}and{' '}
          <a href="https://livekit.io/" target="_blank" rel="noopener noreferrer">
            LiveKit
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
