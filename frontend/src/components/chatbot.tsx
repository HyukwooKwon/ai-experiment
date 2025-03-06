import React, { useState } from "react";
import "./chatbot.css"; // CSS 파일 추가

const Chatbot: React.FC = () => {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const sendMessage = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      setResponse(data.reply);
    } catch (error) {
      console.error("Error fetching data:", error);
      setResponse("Error: 백엔드와 연결할 수 없습니다.");
    }
  };

  return (
    <div className="chatbot-container">
      <h2 className="chatbot-title">AI Chatbot</h2>
      <input
        type="text"
        className="chatbot-input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="메시지를 입력하세요..."
      />
      <button className="chatbot-button" onClick={sendMessage}>
        전송
      </button>
      <p className="chatbot-response">응답: {response}</p>
    </div>
  );
};

export default Chatbot;
