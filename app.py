import logging
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from weather import weather_bp

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key" 

# ロギング設定（起動時に1回）
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

jwt = JWTManager(app)

app.register_blueprint(weather_bp)

# ✅ ログインしてトークンを取得
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # 仮の認証処理（本番ではDB確認など）
    if username != "admin" or password != "password":
        return jsonify({"msg": "Bad credentials"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# ✅ トークンが必要なAPI
@app.route('/api/secure-data', methods=['GET'])
@jwt_required()
def secure_data():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user, data="これは守られたデータです")

@app.route('/')
def index():
    logger.debug("DEBUGログ：ルートにアクセスされました")
    logger.info("INFOログ：こんにちは")
    logger.warning("WARNINGログ：これは警告です")
    logger.error("ERRORログ：エラーが発生しました")
    return "Hello Flask + logging"


# 起動時（開発用）
if __name__ == "__main__":
    app.run(debug=True)