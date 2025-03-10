import React, { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";

// ✅ 환경변수에서 백엔드 URL 가져오기
const BASE_BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000";

const Chatbot = () => {
    const [messages, setMessages] = useState<string[]>([]);
    const [input, setInput] = useState("");
    const chatBoxRef = useRef<HTMLDivElement | null>(null);

    const [searchParams] = useSearchParams();
    const companyName = searchParams.get("company") || process.env.REACT_APP_COMPANY_NAME || "default";

    // ✅ 업체별로 다른 백엔드 URL 선택
    const BACKEND_URL = companyName === "companyA"
        ? process.env.REACT_APP_BACKEND_URL_companyA || BASE_BACKEND_URL
        : process.env.REACT_APP_BACKEND_URL_companyB || BASE_BACKEND_URL;

    useEffect(() => {
        console.log(`🔍 현재 업체: ${companyName}`);
        console.log(`🔍 백엔드 URL: ${BACKEND_URL}`);
    }, [companyName]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        setMessages(prevMessages => [...prevMessages, `사용자: ${input}`]);

        try {
            const response = await axios.post(`${BACKEND_URL}/chatbot/${companyName}`, {
                message: input
            });

            setMessages(prevMessages => [...prevMessages, `AI: ${response.data.reply}`]);

            if (chatBoxRef.current) {
                chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
            }
        } catch (error) {
            setMessages(prevMessages => [...prevMessages, "❌ 오류: 응답을 받을 수 없습니다."]);
        }

        setInput("");
    };

    return (
        <div>
            <h2>{companyName} AI Chatbot</h2>
            <div className="chat-box" ref={chatBoxRef}>
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
