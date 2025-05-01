
import React, { useState, useRef, useEffect } from 'react';
import { PlayCircle, PauseCircle, Volume2, VolumeX, SkipForward, SkipBack, Repeat } from 'lucide-react';
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";

interface MusicPlayerProps {
  title: string;
  artist: string;
  coverImageUrl: string;
  audioUrl?: string;
}

const MusicPlayer: React.FC<MusicPlayerProps> = ({ 
  title, 
  artist, 
  coverImageUrl,
  audioUrl
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isMuted, setIsMuted] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);
  
  // Using a sample audio file as we're in demo mode
  const demoAudioUrl = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3";
  const audioSource = audioUrl || demoAudioUrl;

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const setAudioData = () => {
      setDuration(audio.duration);
    };

    const setAudioTime = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleEnd = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    // Set up event listeners
    audio.addEventListener('loadedmetadata', setAudioData);
    audio.addEventListener('timeupdate', setAudioTime);
    audio.addEventListener('ended', handleEnd);

    // Clean up
    return () => {
      audio.removeEventListener('loadedmetadata', setAudioData);
      audio.removeEventListener('timeupdate', setAudioTime);
      audio.removeEventListener('ended', handleEnd);
    };
  }, []);
  
  // Handle volume change
  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (value: number[]) => {
    setVolume(value[0]);
    if (isMuted) setIsMuted(false);
  };

  const handleSeek = (value: number[]) => {
    const audio = audioRef.current;
    if (audio) {
      audio.currentTime = value[0];
      setCurrentTime(value[0]);
    }
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  // Generate bars for the audio wave effect
  const generateWaveBars = (count: number) => {
    return Array.from({ length: count }).map((_, index) => (
      <div 
        key={index} 
        className="audio-wave-bar" 
        style={{ 
          animationDelay: `${index * 0.1}s`,
          height: `${20 + Math.random() * 30}px`
        }}
      />
    ));
  };

  return (
    <div className="bg-card rounded-lg shadow-lg overflow-hidden relative">
      <div className="flex flex-col md:flex-row items-center p-4">
        <div className="relative w-32 h-32 rounded-lg overflow-hidden shadow-md">
          <img 
            src={coverImageUrl} 
            alt={`${title} by ${artist}`}
            className="w-full h-full object-cover"
          />
          {isPlaying && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="audio-wave">{generateWaveBars(5)}</div>
            </div>
          )}
        </div>

        <div className="flex flex-col flex-1 ml-0 md:ml-4 mt-4 md:mt-0 w-full">
          <div className="mb-2">
            <h3 className="text-lg font-semibold line-clamp-1">{title}</h3>
            <p className="text-sm text-muted-foreground">{artist}</p>
          </div>

          <div className="flex flex-col w-full">
            <audio ref={audioRef} src={audioSource} preload="metadata" />
            
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs text-muted-foreground w-10">
                {formatTime(currentTime)}
              </span>
              <Slider
                defaultValue={[0]}
                value={[currentTime]}
                max={duration || 100}
                step={0.01}
                onValueChange={handleSeek}
                className="flex-grow"
              />
              <span className="text-xs text-muted-foreground w-10">
                {formatTime(duration)}
              </span>
            </div>

            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center space-x-2">
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="text-muted-foreground hover:text-primary"
                >
                  <SkipBack size={18} />
                </Button>
                
                <Button 
                  variant="ghost" 
                  size="icon"
                  className="text-primary hover:text-primary/80 h-12 w-12"
                  onClick={togglePlay}
                >
                  {isPlaying ? (
                    <PauseCircle size={36} />
                  ) : (
                    <PlayCircle size={36} />
                  )}
                </Button>
                
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="text-muted-foreground hover:text-primary"
                >
                  <SkipForward size={18} />
                </Button>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground hover:text-primary"
                  onClick={toggleMute}
                >
                  {isMuted || volume === 0 ? (
                    <VolumeX size={18} />
                  ) : (
                    <Volume2 size={18} />
                  )}
                </Button>
                <Slider
                  defaultValue={[0.7]}
                  value={[isMuted ? 0 : volume]}
                  max={1}
                  step={0.01}
                  onValueChange={handleVolumeChange}
                  className="w-20"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MusicPlayer;
