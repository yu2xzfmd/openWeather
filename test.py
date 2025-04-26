from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"

jwt = JWTManager(app)

@app.route('/')
def hello():
    return "Hello from Flask on Apache!"

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # 仮の認証処理（本番ではDB確認など）
    if username != "admin" or password != "password":
        return jsonify({"msg": "Bad credentials"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

if __name__ == "__main__":
    app.run()
