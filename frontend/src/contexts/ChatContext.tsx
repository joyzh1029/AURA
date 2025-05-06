import React, { createContext, useState, useContext, ReactNode } from 'react';

export type MessageType = 'text' | 'image' | 'video' | 'music' | 'system';

export interface Message {
  id: string;
  content: string;
  type: MessageType;
  sender: 'user' | 'bot';
  timestamp: Date;
  attachmentUrl?: string;
  metadata?: Record<string, any>;
}

interface ChatContextProps {
  messages: Message[];
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  uploadedImage: string | null;
  setUploadedImage: (image: string | null) => void;
  uploadedVideo: string | null;
  setUploadedVideo: (video: string | null) => void;
  uploadedMusic: string | null;
  setUploadedMusic: (music: string | null) => void;
  generatedImage: string | null;
  setGeneratedImage: (image: string | null) => void;
  clearChat: () => void;
}

const ChatContext = createContext<ChatContextProps | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const welcomeMessage = '안녕하세요! AURA입니다. 무엇을 도와드릴까요?';
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: welcomeMessage,
      type: 'text',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [uploadedVideo, setUploadedVideo] = useState<string | null>(null);
  const [uploadedMusic, setUploadedMusic] = useState<string | null>(null);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage = {
      ...message,
      id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const clearChat = () => {
    setMessages([
      {
        id: '1',
        content: welcomeMessage,
        type: 'text',
        sender: 'bot',
        timestamp: new Date(),
      },
    ]);
    setUploadedImage(null);
    setUploadedVideo(null);
    setUploadedMusic(null);
    setGeneratedImage(null);
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        addMessage,
        isLoading,
        setIsLoading,
        uploadedImage,
        setUploadedImage,
        uploadedVideo,
        setUploadedVideo,
        uploadedMusic,
        setUploadedMusic,
        generatedImage,
        setGeneratedImage,
        clearChat
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextProps => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
