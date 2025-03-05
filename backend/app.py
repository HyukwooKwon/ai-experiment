import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from routes.chat import chat_bp
from routes.kakao import kakao_bp
from routes.naver import naver_bp
from routes.telegram import telegram_bp
from dotenv import load_dotenv

load_dotenv()

# ✅ 로그 설정 추가 (DEBUG 레벨까지 출력)
logging.basicConfig(level=logging.DEBUG)  
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": ["http://localhost:3000", "https://4e065685d8e7.ngrok.app", "https://your-vercel-project-url.vercel.app"]}})

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

if __name__ == "__main__":
    logger.info("🚀 Flask 서버 시작됨 (PORT: 5002)")  
    app.run(host="0.0.0.0", port=5002, debug=True)  # ✅ debug=True 설정
