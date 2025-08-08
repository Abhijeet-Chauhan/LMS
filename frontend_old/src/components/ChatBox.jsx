import React, { useState } from 'react';
import axios from 'axios';

const ChatBox = () => {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!prompt.trim() || isLoading) return;

    const userMessage = { sender: 'user', text: prompt };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    
    setIsLoading(true);
    setPrompt('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/ask', {
        question: prompt,
        history: newMessages.slice(0, -1) // Send previous messages as history
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

  return (
    <div className="chat-container">
      <h2>2. Chat With Your Agent</h2>
      <div className="chat-history">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
          </div>
        ))}
        {isLoading && <div className="message agent"><p><i>Typing...</i></p></div>}
      </div>
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask a question..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !prompt.trim()}>Send</button>
      </form>
    </div>
  );
};

export default ChatBox;