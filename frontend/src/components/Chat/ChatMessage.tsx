import React from 'react';
import { Message as MessageType } from '@/contexts/ChatContext';
import { Avatar } from '@/components/ui/avatar';
import { AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import ImagePreview from '../ImagePreview/ImagePreview';
import MusicPlayer from '../MusicPlayer/MusicPlayer';

interface ChatMessageProps {
  message: MessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isBot = message.sender === 'bot';
  const formattedTime = message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  const renderContent = () => {
    switch (message.type) {
      case 'image':
        return (
          <div className="my-2">
            <ImagePreview 
              imageUrl={message.attachmentUrl || ''}
              alt="업로드된 이미지" 
              aspectRatio="auto"
            />
            {message.content && (
              <p className="text-sm mt-2">{message.content}</p>
            )}
          </div>
        );
      
      case 'video':
        return (
          <div className="my-2">
            {message.attachmentUrl && (
              <video 
                controls 
                className="w-full rounded-md max-h-[300px] object-contain bg-black"
                src={message.attachmentUrl}
              />
            )}
            {message.content && (
              <p className="text-sm mt-2">{message.content}</p>
            )}
          </div>
        );
      
      case 'music':
        if (message.metadata?.musicData) {
          const { title, artist, coverImageUrl, audioUrl } = message.metadata.musicData;
          return (
            <div className="my-2">
              <MusicPlayer
                title={title}
                artist={artist}
                coverImageUrl={coverImageUrl}
                audioUrl={audioUrl}
              />
              {message.content && (
                <p className="text-sm mt-2">{message.content}</p>
              )}
            </div>
          );
        }
        return <p>{message.content}</p>;
      
      case 'system':
        return (
          <div className="bg-muted/50 py-2 px-3 rounded-md text-xs text-center">
            {message.content}
          </div>
        );
      
      case 'text':
      default:
        return <p>{message.content}</p>;
    }
  };

  // Skip standard message container for system messages
  if (message.type === 'system') {
    return (
      <div className="mx-auto my-2 max-w-[80%]">
        {renderContent()}
      </div>
    );
  }

  return (
    <div className={cn(
      "flex",
      isBot ? "justify-start" : "justify-end"
    )}>
      <div className={cn(
        "flex gap-3 max-w-[80%]",
        isBot ? "flex-row" : "flex-row-reverse"
      )}>
        <Avatar className="h-10 w-10 mt-1 ring-2 ring-offset-2 ring-music-600/40">
          {isBot ? (
            <>
              <AvatarImage 
                src="/wave.jpg" 
                alt="AURA" 
                className="object-cover"
              />
              <AvatarFallback className="bg-music-600 text-white">AU</AvatarFallback>
            </>
          ) : (
            <>
              <AvatarImage 
                src="/placeholder.svg" 
                className="object-cover"
              />
              <AvatarFallback className="bg-slate-600 text-white">U</AvatarFallback>
            </>
          )}
        </Avatar>

        <div>
          <div className={cn(
            "rounded-lg px-4 py-2 mb-1 shadow-sm",
            isBot 
              ? "bg-card border text-card-foreground" 
              : "bg-primary text-primary-foreground"
          )}>
            {renderContent()}
          </div>
          <div className={cn(
            "text-xs text-muted-foreground", 
            isBot ? "text-left" : "text-right"
          )}>
            {formattedTime}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
