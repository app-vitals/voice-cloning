import { useEffect, useMemo, useState } from 'react';
import { Participant, RoomEvent, TrackPublication } from 'livekit-client';
import type { TranscriptionSegment } from 'livekit-client';
import { useConnectionState, useMaybeRoomContext } from '@livekit/components-react';

export function useTranscriber() {
  const state = useConnectionState();
  const room = useMaybeRoomContext();
  const [transcriptions, setTranscriptions] = useState<{
    [id: string]: {
      segment: TranscriptionSegment;
      participantName?: string;
      isLocal?: boolean;
    };
  }>({});

  useEffect(() => {
    if (!room) return;

    const updateTranscriptions = (
      segments: TranscriptionSegment[],
      participant?: Participant,
      publication?: TrackPublication
    ) => {
      console.log('Received transcription:', segments, 'from participant:', participant?.name);
      setTranscriptions((prev) => {
        const newTranscriptions = { ...prev };
        for (const segment of segments) {
          const isLocal = participant?.isLocal || false;
          
          newTranscriptions[segment.id] = {
            segment,
            participantName: isLocal ? 'You' : 'AI Assistant',
            isLocal,
          };
        }
        return newTranscriptions;
      });
    };

    room.on(RoomEvent.TranscriptionReceived, updateTranscriptions);
    return () => {
      room.off(RoomEvent.TranscriptionReceived, updateTranscriptions);
    };
  }, [room, state]);

  return { state, transcriptions };
}

export function TranscriptionDisplay() {
  const { transcriptions } = useTranscriber();
  
  const transcriptionSegments = useMemo(() => 
    Object.values(transcriptions)
      .sort((a, b) => a.segment.firstReceivedTime - b.segment.firstReceivedTime),
    [transcriptions]
  );
  
  if (transcriptionSegments.length === 0) {
    return (
      <div className="transcription-display">
        <h3>Conversation</h3>
        <p className="transcription-placeholder">
          Start speaking to see the conversation...
        </p>
      </div>
    );
  }

  return (
    <div className="transcription-display">
      <h3>Conversation</h3>
      <div className="transcription-list">
        {transcriptionSegments.map((item) => (
          <div 
            key={item.segment.id} 
            className={`transcription-item ${item.isLocal ? 'local' : 'remote'}`}
          >
            <span className="speaker-name">
              {item.participantName}:
            </span>
            <span className="transcription-text">{item.segment.text}</span>
            {!item.segment.final && <span className="interim-indicator"> ...</span>}
          </div>
        ))}
      </div>
    </div>
  );
}