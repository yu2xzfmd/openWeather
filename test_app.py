import unittest
from app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Flaskのテストクライアントを作成
        self.app = app.test_client()
        self.app.testing = True

    def test_login_success(self):
        # 正しいユーザーでログインしてトークン取得
        response = self.app.post('/login', json={
            "username": "admin",
            "password": "password"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)

    def test_login_failure(self):
        # 認証失敗
        response = self.app.post('/login', json={
            "username": "wrong",
            "password": "wrong"
        })
        self.assertEqual(response.status_code, 401)

    def test_secure_data_with_token(self):
        # トークン取得 → 認証付きエンドポイントにアクセス
        login_response = self.app.post('/login', json={
            "username": "admin",
            "password": "password"
        })
        token = login_response.get_json()['access_token']

        response = self.app.get('/api/secure-data', headers={
            "Authorization": f"Bearer {token}"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('logged_in_as', response.get_json())

    def test_secure_data_without_token(self):
        # トークンなしアクセスは失敗する
        response = self.app.get('/api/secure-data')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
