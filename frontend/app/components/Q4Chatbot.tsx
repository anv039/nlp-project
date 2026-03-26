'use client';

import { useState, useRef, useEffect, useTransition } from 'react';
import { sendChatMessage, type ChatResult } from '../actions';

interface Message {
  role: 'user' | 'bot';
  content: string;
  intent?: string;
  timestamp: Date;
}

export default function Q4Chatbot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'bot',
      content: "Hi! NLP Assistant. Ask about NER, POS, sentiment, AI chatbots.",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isPending, startTransition] = useTransition();
  const [isTyping, setIsTyping] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  const handleSend = async () => {
    if (!input.trim() || isPending) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');

    const formData = new FormData();
    formData.append('message', currentInput);
    formData.append('history', JSON.stringify(messages.slice(-5).map(m => ({role: m.role, content: m.content}))));

    setIsTyping(true);
    try {
      const response = await fetch('/api/chat?action=chat', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();

      if (result.success) {
        const botMessage: Message = {
          role: 'bot',
          content: result.data.response,
          intent: result.data.intent,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Network error');
    } finally {
      setIsTyping(false);
    }
  };


  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg border">
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 rounded-t-lg">
        <div className="flex items-center space-x-2">
          {/* <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
            <span className="text-blue-600 text-xl">🤖</span>
          </div> */}
          <div>
            <h3 className="font-semibold">NLP Chatbot</h3>
            <p className="text-sm opacity-90">NER, POS, Sentiment</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50 to-white text-black">
        {messages.map((message, idx) => (
          <div key={idx} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] p-3 rounded-2xl ${message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border shadow-sm'}`}>
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.intent && message.role === 'bot' && (
                <p className="text-xs mt-1 opacity-75 font-mono">{message.intent}</p>
              )}
            </div>
            {/* <div className={`ml-2 mr-2 w-8 h-8 rounded-full flex items-center justify-center ${message.role === 'user' ? 'bg-blue-600' : 'bg-gray-300'}`}>
              <span className="text-white text-xs">
                {message.role === 'user' ? '👤' : '🤖'}
              </span>
            </div> */}
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm rounded-2xl p-3 animate-pulse">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 bg-blue-200 rounded-full animate-spin"></div>
                <span className="text-sm text-gray-500 font-medium">Bot is typing...</span>
                <div className="flex space-x-1 ml-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0s]"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="p-3 bg-red-100 border-t border-red-200 text-red-800 text-sm">
          Error: {error}
        </div>
      )}

      <div className="border-t border-gray-200 p-4 bg-white rounded-b-lg">
        <div className="flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about NLP..."
            className="flex-1 px-4 py-3 border text-black border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
            disabled={isPending}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isPending) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={isPending || !input.trim()}
            className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
          >
            {/* <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-2-9-9 2 2 9z" />
            </svg> */}
            ►
          </button>
        </div>
      </div>
    </div>
  );
}

