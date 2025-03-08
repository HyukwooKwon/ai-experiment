import React, { useState } from "react";
import BACKEND_URL from "../config";  
import styles from "../components/chatbot.module.css";  // ✅ CSS 모듈로 변경



const Chatbot = () => {
    const [messages, setMessages] = useState<string[]>([]);
    const [input, setInput] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return;

        setMessages([...messages, `사용자: ${input}`]);

        const response = await fetch(`${BACKEND_URL}/chat`, {  // ✅ 백엔드 URL 적용
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: input })
        });

        const data = await response.json();
        setMessages([...messages, `사용자: ${input}`, `AI: ${data.reply}`]);
        setInput("");
    };

    // ✅ 엔터 키 입력 시 메시지 전송
    const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    };

    return (
      <div className={styles.chatContainer}>
            <h2>AI Chatbot</h2>
            <div className="chat-box">
                {messages.map((msg, index) => (
                    <p key={index}>{msg}</p>
                ))}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}  // ✅ 엔터 키 이벤트 추가
                placeholder="메시지를 입력하세요..."
            />
            <button onClick={sendMessage}>전송</button>
        </div>
    );
};

export default Chatbot;
