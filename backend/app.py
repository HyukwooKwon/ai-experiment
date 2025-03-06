import logging
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from routes.chat import chat_bp
from routes.kakao import kakao_bp
from routes.naver import naver_bp
from routes.telegram import telegram_bp

# 환경 변수 로드
load_dotenv()

# ✅ Flask 앱 생성
app = Flask(__name__)

# ✅ CORS 설정 (Netlify & Local 환경 허용)
CORS(app, resources={r"/*": {
    "origins": [
        "https://astonishing-pavlova-71a9ea.netlify.app",
        "http://localhost:3000"
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# ✅ 로그 설정 추가
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ✅ API 라우트 등록
app.register_blueprint(chat_bp)
app.register_blueprint(kakao_bp)
app.register_blueprint(naver_bp)
app.register_blueprint(telegram_bp)

@app.route("/")  # 루트 경로 추가
def home():
    logger.info("✅ 홈 페이지 요청이 들어옴!")
    return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ✅ Flask 앱 전역 오류 핸들러 추가 (모든 예외 출력)
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"❌ 서버 오류 발생: {str(e)}")  # ✅ 오류 메시지 출력
    return jsonify({"error": "서버 내부 오류 발생"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    return {"reply": "백엔드와 연결 성공!"}

if __name__ == "__main__":
    logger.info("🚀 Flask 서버 시작됨 (PORT: 5002)")
    app.run(host="0.0.0.0", port=5002, debug=True)
