import React from 'react';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
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

<Router>
  <Routes>
    <Route path="/chatbot" element={<Chatbot />} />
  </Routes>
</Router>

export default App;
