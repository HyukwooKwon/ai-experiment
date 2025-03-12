import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Chatbot from "./components/Chatbot";

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<Chatbot />} />
    </Routes>
  </Router>
);

export default App;
