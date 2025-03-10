import React, { useState } from "react";
import axios from "axios";
import styles from "../components/chatbot.module.css";

const Chatbot = () => {
    const [messages, setMessages] = useState<string[]>([]);
    const [input, setInput] = useState("");
    const [contact, setContact] = useState("");
    const [inquiry, setInquiry] = useState("");

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000";

    const sendMessage = async () => {
        if (!input.trim()) return;

        setMessages(prevMessages => [...prevMessages, `👤 사용자: ${input}`]);

        try {
            const response = await axios.post(`${BACKEND_URL}/chatbot`, {
                message: input
            });

            setMessages(prevMessages => [...prevMessages, `🤖 AI: ${response.data.reply}`]);

        } catch (error) {
            setMessages(prevMessages => [...prevMessages, "❌ 오류: 응답을 받을 수 없습니다."]);
        }

        setInput("");
    };

    const submitInquiry = async () => {
        if (!contact.trim() || !inquiry.trim()) {
            alert("연락처와 문의 내용을 입력해주세요.");
            return;
        }

        try {
            await axios.post(`${BACKEND_URL}/submit-inquiry`, {
                contact,
                inquiry
            });
            alert("문의가 접수되었습니다!");
            setContact("");
            setInquiry("");
        } catch (error) {
            alert("문의 접수에 실패했습니다. 다시 시도해주세요.");
        }
    };

    return (
        <div className={styles.container}>
            {/* 왼쪽 - 챗봇 UI */}
            <div className={styles.chatContainer}>
                <h2>💬 AI Chatbot</h2>
                <div className={styles.chatBox}>
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
                <button onClick={sendMessage}>📩 전송</button>
            </div>

            {/* 오른쪽 - 문의 남기기 폼 */}
            <div className={styles.inquiryContainer}>
                <h2>📩 문의 남기기</h2>
                <input
                    type="text"
                    value={contact}
                    onChange={(e) => setContact(e.target.value)}
                    placeholder="연락처 입력"
                />
                <textarea
                    value={inquiry}
                    onChange={(e) => setInquiry(e.target.value)}
                    placeholder="문의 내용을 입력하세요..."
                />
                <button onClick={submitInquiry}>✅ 문의 제출</button>
            </div>
        </div>
    );
};

export default Chatbot;
