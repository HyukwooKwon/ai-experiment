import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from "../components/chatbot.module.css";
import { useSearchParams } from "react-router-dom";

const Chatbot = () => {
    const [messages, setMessages] = useState<{ sender: string, text: string }[]>([]);
    const [input, setInput] = useState("");
    const [contact, setContact] = useState("");
    const [inquiry, setInquiry] = useState("");
    const [showInquiryForm, setShowInquiryForm] = useState(false);
    const [loading, setLoading] = useState(false);

    // ✅ URL에서 companyName 가져오기
    const [searchParams] = useSearchParams();
    const companyName = searchParams.get("company") || process.env.REACT_APP_COMPANY_NAME || "default";

    // ✅ 한 서버에서 모든 업체 지원 → 백엔드 URL 통일
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://bot-back-a.onrender.com";

    // ✅ 디버깅 로그 추가 (백엔드 URL 및 회사명 확인)
    useEffect(() => {
        console.log(`🔍 [DEBUG] 회사명: ${companyName}`);
        console.log(`🔍 [DEBUG] 백엔드 요청 URL: ${BACKEND_URL}/chatbot/${companyName}`);
    }, [companyName]);

    // ✅ 메시지 전송 함수 (AI 챗봇 요청)
    const sendMessage = async () => {
        if (!input.trim()) return;  // 공백 문자 입력 방지

        // ✅ 사용자 메시지 추가
        setMessages(prevMessages => [...prevMessages, { sender: "user", text: input }]);
        setInput("");
        setLoading(true);

        try {
            const response = await axios.post(`${BACKEND_URL}/chatbot/${companyName}`, { message: input });
            setMessages(prevMessages => [...prevMessages, { sender: "bot", text: response.data.reply }]);
        } catch (error) {
            setMessages(prevMessages => [...prevMessages, { sender: "bot", text: "❌ 서버 오류 발생. 다시 시도해주세요." }]);
            console.error("🚨 AI 응답 오류:", error);
        } finally {
            setLoading(false);
        }
    };

    // ✅ 엔터 키 입력 시 자동 전송
    const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter" && !loading) {
            sendMessage();
        }
    };

    // ✅ 문의 제출 함수 (업체별 API 요청)
    const submitInquiry = async () => {
        if (!contact.trim() || !inquiry.trim()) {
            alert("📩 연락처와 문의 내용을 입력해주세요.");
            return;
        }

        try {
            await axios.post(`${BACKEND_URL}/submit-inquiry/${companyName}`, { contact, inquiry });
            alert("✅ 문의가 접수되었습니다!");
            setContact("");
            setInquiry("");
            setShowInquiryForm(false);
        } catch (error) {
            alert("❌ 문의 접수에 실패했습니다. 다시 시도해주세요.");
            console.error("🚨 문의 제출 오류:", error);
        }
    };

    return (
        <div className={styles.container}>
            {/* 챗봇 UI */}
            <div className={styles.chatContainer}>
                <h2>💬 AI Chatbot ({companyName})</h2>
                <div className={styles.chatBox}>
                    {messages.map((msg, index) => (
                        <p key={index} className={msg.sender === "user" ? styles.userMessage : styles.botMessage}>
                            {msg.text}
                        </p>
                    ))}
                    {loading && <p className={styles.loading}>⏳ AI 응답 대기 중...</p>}
                </div>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="메시지를 입력하세요..."
                />
                <button onClick={sendMessage} disabled={loading}>📩 전송</button>

                {/* 문의 남기기 버튼 추가 */}
                <button className={styles.inquiryButton} onClick={() => setShowInquiryForm(true)}>📩 문의 남기기</button>
            </div>

            {/* 문의 남기기 팝업 */}
            {showInquiryForm && (
                <div className={styles.popupOverlay}>
                    <div className={styles.popupContainer}>
                        <h2>📩 문의 남기기 ({companyName})</h2>
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
                        <button className={styles.closeButton} onClick={() => setShowInquiryForm(false)}>❌ 닫기</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Chatbot;
