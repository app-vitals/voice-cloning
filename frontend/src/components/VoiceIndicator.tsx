import { useParticipants, useIsSpeaking } from '@livekit/components-react';

function ParticipantIndicator({ participant, label, avatar }: { participant: any, label: string, avatar: string }) {
  const isSpeaking = useIsSpeaking(participant);
  
  return (
    <div className={`speaker-indicator ${isSpeaking ? 'speaking' : ''}`}>
      <div className="speaker-avatar">{avatar}</div>
      <span className="speaker-label">{label}</span>
      {isSpeaking && <div className="speaking-pulse"></div>}
    </div>
  );
}

export function VoiceIndicator() {
  const participants = useParticipants();
  const localParticipant = participants.find(p => p.isLocal);
  const remoteParticipant = participants.find(p => !p.isLocal);

  return (
    <div className="voice-indicator">
      <div className="voice-status">
        {localParticipant ? (
          <ParticipantIndicator 
            participant={localParticipant} 
            label="You" 
            avatar="👤" 
          />
        ) : (
          <div className="speaker-indicator">
            <div className="speaker-avatar">👤</div>
            <span className="speaker-label">Connecting...</span>
          </div>
        )}
        
        <div className="voice-connection">
          <div className="connection-line"></div>
        </div>
        
        {remoteParticipant ? (
          <ParticipantIndicator 
            participant={remoteParticipant} 
            label="AI Assistant" 
            avatar="🤖" 
          />
        ) : (
          <div className="speaker-indicator">
            <div className="speaker-avatar">🤖</div>
            <span className="speaker-label">Waiting for AI...</span>
          </div>
        )}
      </div>
    </div>
  );
}