import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useTypewriter } from './useTypewriter';
import { Send, Paperclip } from 'lucide-react'; 
import './App.css';

const SunIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg> );
const MoonIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg> );
const AgentMessage = ({ text }) => { const displayText = useTypewriter(text, 10); return <p>{displayText}</p>; };

function App() {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const fileInputRef = useRef(null);
  const chatHistoryRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => { document.body.className = isDarkMode ? 'dark-mode' : 'light-mode'; }, [isDarkMode]);
  useEffect(() => { if (chatHistoryRef.current) { chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight; } }, [messages, isLoading]);


  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [prompt]);


  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setIsLoading(true);
    setMessages(prev => [...prev, { sender: 'system', text: `Uploading ${file.name}...` }]);
    try {
      const response = await axios.post(' https://51c3df8a9b4b.ngrok-free.app/ingest', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      setMessages(prev => [...prev, { sender: 'system', text: response.data.message }]);
    } catch (error) {
      setMessages(prev => [...prev, { sender: 'system', text: 'Error uploading file.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!prompt.trim() || isLoading) return;
    const userMessage = { sender: 'user', text: prompt };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setIsLoading(true);
    setPrompt('');
    try {
      const response = await axios.post(' https://51c3df8a9b4b.ngrok-free.app/ask', {
        question: prompt,
        history: newMessages.slice(0, -1).map(msg => ({ role: msg.sender === 'user' ? 'user' : 'assistant', content: msg.text }))
      });
      const agentMessage = { sender: 'agent', text: response.data.answer };
      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      const errorMessage = { sender: 'agent', text: 'Sorry, something went wrong.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h3>BrainFog</h3>
        <button className="theme-toggle" onClick={() => setIsDarkMode(!isDarkMode)} title="Toggle Theme">
          {isDarkMode ? <SunIcon /> : <MoonIcon />}
        </button>
      </header>

      <main className="chat-canvas" ref={chatHistoryRef}>
        {messages.length === 0 && !isLoading && (
          <div className="welcome-message">
            <h2>Nexa</h2>
            <p>Welcome to a New age of learning.</p>
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <div className="message-content">
              {msg.sender === 'agent' ? <AgentMessage text={msg.text} /> : <p>{msg.text}</p>}
            </div>
          </div>
        ))}
        {isLoading && <div className="message agent"><div className="message-content"><p><i>Thinking...</i></p></div></div>}
      </main>

      <footer className="chat-footer">
        <div className="ai-input-container">
          <form onSubmit={handleSubmit} className="ai-input-form">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              title="Upload File"
            >
              <Paperclip size={20} />
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              style={{ display: 'none' }}
              accept=".pdf,.txt"
            />
            <textarea
              ref={textareaRef}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Upload and Ask Nexa anything..."
              rows={1}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="send-btn"
              disabled={!prompt.trim() || isLoading}
              title="Send Message"
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </footer>
    </div>
  );
}

export default App;