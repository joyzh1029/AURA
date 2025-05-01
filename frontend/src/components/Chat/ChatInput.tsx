
import React, { useState, useRef } from 'react';
import { useChat } from '@/contexts/ChatContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Mic, MicOff, Send, Image as ImageIcon, Music } from 'lucide-react';
import ImagePreview from '@/components/ImagePreview/ImagePreview';
import { sendChatMessage } from '@/services/api';

const ChatInput = () => {
  const { addMessage, isLoading, setIsLoading, uploadedImage, uploadedVideo, uploadedMusic, setUploadedImage, setUploadedVideo, setUploadedMusic } = useChat();
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() && !uploadedImage && !uploadedVideo && !uploadedMusic) return;

    const messageText = inputValue;
    setInputValue('');

    // Add user message
    addMessage({
      content: messageText,
      type: 'text',
      sender: 'user',
    });

    // Track media URLs to send to the backend
    let imageUrl = null;
    let audioUrl = null;
    let videoUrl = null;

    if (uploadedImage) {
      addMessage({
        content: '',
        type: 'image',
        sender: 'user',
        attachmentUrl: uploadedImage,
      });
      imageUrl = uploadedImage;
    }

    if (uploadedVideo) {
      addMessage({
        content: '',
        type: 'video',
        sender: 'user',
        attachmentUrl: uploadedVideo,
      });
      videoUrl = uploadedVideo;
    }

    if (uploadedMusic) {
      addMessage({
        content: '',
        type: 'music',
        sender: 'user',
        attachmentUrl: uploadedMusic,
      });
      audioUrl = uploadedMusic;
    }

    setIsLoading(true);

    try {
      // Send message to LangChain-powered backend
      const response = await sendChatMessage({
        message: messageText,
        image_url: imageUrl,
        audio_url: audioUrl,
        video_url: videoUrl
      });
      
      // Add bot response
      addMessage({
        content: response.response,
        type: 'text',
        sender: 'bot',
      });
    } catch (error) {
      console.error('Error processing request:', error);
      addMessage({
        content: '요청 처리 중 오류가 발생했습니다. 다시 시도해 주세요.',
        type: 'text',
        sender: 'bot',
      });
    } finally {
      setIsLoading(false);
      setUploadedImage(null);
      setUploadedVideo(null);
      setUploadedMusic(null);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Here you would implement actual voice recording functionality
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2">
      {uploadedImage && (
        <div className="absolute bottom-full mb-2 left-0">
          <ImagePreview 
            imageUrl={uploadedImage} 
            className="h-20 w-20"
            aspectRatio="square"
            onRemove={() => setUploadedImage(null)}
          />
        </div>
      )}
      
      <div className="flex-1 relative">
        <Input
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="메시지 입력..."
          className="pr-20"
          disabled={isLoading}
        />
      </div>
      
      <Button
        type="button"
        size="icon"
        variant="outline"
        onClick={toggleRecording}
        className={isRecording ? 'text-red-500' : ''}
      >
        {isRecording ? <MicOff /> : <Mic />}
      </Button>
      
      <Button type="submit" size="icon" disabled={(!inputValue.trim() && !uploadedImage && !uploadedMusic) || isLoading}>
        <Send className="h-4 w-4" />
      </Button>
    </form>
  );
};

export default ChatInput;
