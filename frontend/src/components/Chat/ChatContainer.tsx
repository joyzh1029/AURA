import React, { useEffect, useRef } from 'react';
import { useChat } from '@/contexts/ChatContext';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { Button } from '@/components/ui/button';
import { RefreshCcw } from 'lucide-react';

const ChatContainer: React.FC = () => {
  const { messages, clearChat, isLoading } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 메시지 변경 시 메시지가 제일 아래로 이동
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-col border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">AURA 챗봇</h2>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={clearChat}
            disabled={isLoading}
            className="text-muted-foreground hover:text-foreground"
          >
            <RefreshCcw className="h-4 w-4 mr-2" />
            대화 초기화
          </Button>
        </div>
        <p className="text-sm text-muted-foreground mt-1">이미지,영상및 음악의 교차점을 탐색하세요</p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 border-t">
        <ChatInput />
      </div>
    </div>
  );
};

export default ChatContainer;
