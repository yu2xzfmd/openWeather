import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import os


# APIキーの読み込み
def load_api_key(filepath=None):
    if filepath is None:
        # このファイルの場所を基準にフルパスにする
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "apikey.txt")
    
    try:
        with open(filepath, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise RuntimeError(f"API key file '{filepath}' not found.")


weather_bp = Blueprint('weather', __name__, url_prefix='/api')

API_KEY = load_api_key()

@weather_bp.route('/weather', methods=['GET'])
@jwt_required()
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify(error="Missing 'city' parameter"), 400

    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "ja"}
    res = requests.get(url, params=params)

    if res.status_code != 200:
        return jsonify(error="Failed to get weather data"), res.status_code

    data = res.json()
    return jsonify({
        "city": data["name"],
        "weather": data["weather"][0]["description"],
        "temperature": data["main"]["temp"]
    })

@weather_bp.route('/weather/forecast', methods=['GET'])
@jwt_required()
def get_forecast():
    city = request.args.get('city')
    if not city:
        return jsonify(error="Missing 'city' parameter"), 400

    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "ja"}
    res = requests.get(url, params=params)

    if res.status_code != 200:
        return jsonify(error="Failed to get forecast data"), res.status_code

    data = res.json()
    forecasts = []
    for entry in data["list"][:8]:  # 24時間分（3hごと × 8）
        forecasts.append({
            "time": entry["dt_txt"],
            "weather": entry["weather"][0]["description"],
            "temp": entry["main"]["temp"]
        })

    return jsonify(city=data["city"]["name"], forecast=forecasts)


# ✅ 2. 緯度経度で現在の天気
@weather_bp.route('/weather/geo', methods=['GET'])
@jwt_required()
def get_weather_by_geo():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify(error="Missing 'lat' or 'lon' parameter"), 400

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric", "lang": "ja"}
    res = requests.get(url, params=params)

    if res.status_code != 200:
        return jsonify(error="Failed to get weather data"), res.status_code

    data = res.json()
    return jsonify({
        "location": f"{lat},{lon}",
        "weather": data["weather"][0]["description"],
        "temperature": data["main"]["temp"]
    })


# ✅ 3. 大気汚染（AQI）
@weather_bp.route('/weather/air', methods=['GET'])
@jwt_required()
def get_air_quality():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify(error="Missing 'lat' or 'lon' parameter"), 400

    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": API_KEY}
    res = requests.get(url, params=params)

    if res.status_code != 200:
        return jsonify(error="Failed to get air quality data"), res.status_code

    data = res.json()
    aqi = data["list"][0]["main"]["aqi"]
    components = data["list"][0]["components"]
    return jsonify({
        "aqi": aqi,
        "components": components
    })


# ✅ 4. 雨雲アラート（代替案：降水量で判断）
@weather_bp.route('/weather/alert', methods=['GET'])
@jwt_required()
def get_rain_alert():
    city = request.args.get('city')
    if not city:
        return jsonify(error="Missing 'city' parameter"), 400

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "ja"}
    res = requests.get(url, params=params)

    if res.status_code != 200:
        return jsonify(error="Failed to get weather data"), res.status_code

    data = res.json()
    rain = data.get("rain", {}).get("1h", 0)
    alert = "雨が降っています☔" if rain else "雨は降っていません🌤"

    return jsonify({
        "city": data["name"],
        "alert": alert,
        "rain_mm_last_hour": rain
    })
