import React from "react";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import Chatbot from "./components/Chatbot";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<h1>홈페이지</h1>} />
                <Route path="/chatbot" element={<Chatbot />} />
                <Route path="*" element={<h1>404 Not Found</h1>} />
            </Routes>
        </Router>
    );
};

export default App;
