import requests
import json

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = "4bce4bb56e823562660d81a40ccc257b"
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city):
        """Get current weather for a city"""
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.status_code, response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            return None, str(e)
    
    def get_forecast(self, city):
        """Get 5-day forecast for a city"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.status_code, response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            return None, str(e)