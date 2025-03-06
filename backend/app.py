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

# ✅ CORS 설정 완전 수정 (Netlify와 모든 요청 허용)
CORS(app, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# ✅ API 라우트 등록
app.register_blueprint(chat_bp)
app.register_blueprint(kakao_bp)
app.register_blueprint(naver_bp)
app.register_blueprint(telegram_bp)

@app.route("/")  # 루트 경로 추가
def home():
    return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ✅ Flask 앱 전역 오류 핸들러 추가 (모든 예외 출력)
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "서버 내부 오류 발생"}), 500

@app.route("/chat", methods=["OPTIONS"])
def chat_options():
    return '', 204  # ✅ OPTIONS 요청 허용 (Preflight 문제 해결)

@app.route("/chat", methods=["POST"])
def chat():
    return jsonify({"reply": "백엔드와 연결 성공!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
