import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import Chatbot from './components/Chatbot';

function App() {
  return (
    <Router>
      <div className="App">
        <Chatbot />
      </div>
    </Router>
  );
}

export default App;
