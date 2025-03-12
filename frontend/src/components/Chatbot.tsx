import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import styles from "../components/chatbot.module.css";
import { useSearchParams } from "react-router-dom";

// 메시지 타입 별도 정의
interface Message {
  sender: "user" | "bot";
  text: string;
}

const Chatbot = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState("");
  const [contact, setContact] = useState("");
  const [inquiry, setInquiry] = useState("");
  const [showInquiryForm, setShowInquiryForm] = useState(false);
  const [loading, setLoading] = useState(false);

  const [searchParams] = useSearchParams();
  const companyName = searchParams.get("company") || process.env.REACT_APP_COMPANY_NAME || "default";
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://bot-back-a.onrender.com";

  useEffect(() => {
    console.log(`🔍 [DEBUG] 회사명: ${companyName}`);
    console.log(`🔍 [DEBUG] 백엔드 요청 URL: ${BACKEND_URL}/chatbot/${companyName}`);
  }, [companyName, BACKEND_URL]);

  // 메시지 전송 함수 최적화
  const sendMessage = useCallback(async () => {
    if (!userInput.trim()) return;

    setMessages(prev => [...prev, { sender: "user", text: userInput }]);
    setUserInput("");
    setLoading(true);

    try {
      const response = await axios.post(`${BACKEND_URL}/chatbot/${companyName}`, { message: userInput });
      setMessages(prev => [...prev, { sender: "bot", text: response.data.reply }]);
    } catch (error) {
      console.error("🚨 AI 응답 오류:", error);
      setMessages(prev => [...prev, { sender: "bot", text: "❌ 서버 오류 발생. 다시 시도해주세요." }]);
    } finally {
      setLoading(false);
    }
  }, [userInput, BACKEND_URL, companyName]);

  // 문의 제출 함수 최적화
  const submitInquiry = useCallback(async () => {
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
  }, [contact, inquiry, BACKEND_URL, companyName]);

  // Enter 키 이벤트 핸들러
  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && !loading) {
      sendMessage();
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.chatContainer}>
        <h2>💬 AI Chatbot ({companyName})</h2>

        <div className={styles.chatBox}>
          {messages.map((msg, index) => (
            <ChatMessage key={index} message={msg} />
          ))}
          {loading && <p className={styles.loading}>⏳ AI 응답 대기 중...</p>}
        </div>

        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="메시지를 입력하세요..."
        />

        <button onClick={sendMessage} disabled={loading}>
          📩 전송
        </button>

        <button
          className={styles.inquiryButton}
          onClick={() => setShowInquiryForm(true)}
        >
          📩 문의 남기기
        </button>
      </div>

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
            <button
              className={styles.closeButton}
              onClick={() => setShowInquiryForm(false)}
            >
              ❌ 닫기
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// 메시지 컴포넌트 별도 분리 (선택적)
const ChatMessage = React.memo(({ message }: { message: Message }) => (
  <p className={message.sender === "user" ? styles.userMessage : styles.botMessage}>
    {message.text}
  </p>
));

export default Chatbot;
