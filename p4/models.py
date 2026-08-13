from datetime import datetime
from db import db

class WeatherCache(db.Model):
    __tablename__ = 'weather_cache'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), unique=True, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        
        return {
            "city": self.city,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "description": self.description,
            "cached_at": self.updated_at.isoformat()
        }