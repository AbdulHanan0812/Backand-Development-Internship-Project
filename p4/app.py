import os

try:
    import requests  # type: ignore
except ImportError:
    requests = None

from flask import Flask, jsonify, request
from dotenv import load_dotenv
from db import db
from models import WeatherCache


load_dotenv()

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///weather.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

with app.app_context():
    db.create_all()


API_KEY = os.getenv("WEATHER_API_KEY")
EXTERNAL_API_URL = "https://api.openweathermap.org/data/2.5/weather"
TIMEOUT_LIMIT = 5 


@app.route('/api/weather', methods=['GET'])
def get_weather():
    
    city = request.args.get('city', 'Seattle')
    
    if requests is None:
        return jsonify({"error": "Server misconfiguration: 'requests' library is not installed."}), 500

    if not API_KEY:
        return jsonify({"error": "Configuration Error: API key missing on server."}), 500

    try:
       
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(EXTERNAL_API_URL, params=params, timeout=TIMEOUT_LIMIT)
        
      
        if response.status_code != 200:
            error_data = response.json()
            error_message = error_data.get('message', 'External provider error.')
            
        
            if 400 <= response.status_code < 500:
                return jsonify({"error": f"Client request error: {error_message}"}), response.status_code
            
           
            raise requests.exceptions.RequestException("Third-party server error.")

        raw_data = response.json()

       
        client_ready_data = {
            "city": raw_data.get("name"),
            "temperature": raw_data.get("main", {}).get("temp"),
            "humidity": raw_data.get("main", {}).get("humidity"),
            "description": raw_data.get("weather", [{}])[0].get("description", "N/A")
        }

       
        cached_record = WeatherCache.query.filter_by(city=city).first()
        if cached_record:
            cached_record.temperature = client_ready_data["temperature"]
            cached_record.humidity = client_ready_data["humidity"]
            cached_record.description = client_ready_data["description"]
        else:
            new_cache = WeatherCache(
                city=client_ready_data["city"],
                temperature=client_ready_data["temperature"],
                humidity=client_ready_data["humidity"],
                description=client_ready_data["description"]
            )
            db.session.add(new_cache)
        db.session.commit()

        return jsonify({
            "status": "success",
            "source": "live_api",
            "data": client_ready_data
        }), 200

    except requests.exceptions.Timeout:
        
        return serve_cached_fallback(city, "Network Timeout. Serving last known cached data.")

    except requests.exceptions.RequestException as e:
      
        return serve_cached_fallback(city, f"Provider unavailable: {str(e)}")


def serve_cached_fallback(city, error_reason):
    """Helper implementing Graceful Degradation using local database storage[cite: 3]."""
    cached_record = WeatherCache.query.filter_by(city=city).first()
    if cached_record:
        return jsonify({
            "status": "fallback",
            "message": error_reason,
            "data": cached_record.to_dict()
        }), 200
    
    return jsonify({
        "status": "error",
        "message": f"{error_reason} No local cache available for this location."
    }), 503


if __name__ == '__main__':
    app.run(debug=True, port=5000)