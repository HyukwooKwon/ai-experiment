import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Chatbot from './components/Chatbot';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/chatbot" replace />} />
        <Route path="/chatbot" element={<Chatbot />} />
      </Routes>
    </Router>
  );
}

export default App;
