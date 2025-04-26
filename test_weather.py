import unittest
from unittest.mock import patch
from app import app  # app.pyでFlaskインスタンスが定義されていることが前提
from flask_jwt_extended import create_access_token

class WeatherTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        self.token = create_access_token(identity='admin')
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    def tearDown(self):
        # コンテキストの終了処理も追加
        self.ctx.pop()

    @patch('weather.requests.get')
    def test_get_weather(self, mock_get):
        # モックのレスポンスを設定
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "name": "Tokyo",
            "weather": [{"description": "晴れ"}],
            "main": {"temp": 25}
        }

        response = self.app.get('/api/weather?city=Tokyo', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["city"], "Tokyo")
        self.assertEqual(data["weather"], "晴れ")

    @patch('weather.requests.get')
    def test_get_geo_weather(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "weather": [{"description": "くもり"}],
            "main": {"temp": 22}
        }

        response = self.app.get('/api/weather/geo?lat=35.68&lon=139.76', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("weather", data)
        self.assertEqual(data["weather"], "くもり")

    def test_weather_unauthorized(self):
        response = self.app.get('/api/weather?city=Tokyo')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
