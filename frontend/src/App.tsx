import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Chatbot from "./components/Chatbot";



function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Chatbot />} />
                <Route path="/chatbot" element={<Chatbot />} />
            </Routes>
        </Router>
    );
}

export default App;
