import React from 'react';
import FileUpload from './components/FileUpload';
import ChatBox from './components/ChatBox';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>LMS Agentic RAG System</h1>
      </header>
      <main className="main-content">
        <FileUpload />
        <ChatBox />
      </main>
    </div>
  );
}

export default App;