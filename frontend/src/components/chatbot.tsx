import React, { useState } from "react";
import styles from "../components/chatbot.module.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000/chatbot/default"; // ✅ 기본값 수정

const Chatbot = () => {
    const [messages, setMessages] = useState<string[]>([]);
    const [input, setInput] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return;

        setMessages(prevMessages => [...prevMessages, `사용자: ${input}`]);

        try {
            const response = await fetch(`${BACKEND_URL}`, { // ✅ 이미 업체별 URL이 포함된 상태
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: input })
            });

            const data = await response.json();
            setMessages(prevMessages => [...prevMessages, `AI: ${data.reply}`]);
        } catch (error) {
            setMessages(prevMessages => [...prevMessages, "❌ 오류: 응답을 받을 수 없습니다."]);
        }

        setInput("");
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
                placeholder="메시지를 입력하세요..."
            />
            <button onClick={sendMessage}>전송</button>
        </div>
    );
};

export default Chatbot;
