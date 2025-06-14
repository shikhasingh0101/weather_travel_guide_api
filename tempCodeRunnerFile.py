from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# OpenWeatherMap API key
api_key = 'a6fc7de15b9e44e299d52d2163bcfc03'

# API Endpoint: Get current weather
def get_weather_data(location):
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={api_key}"
    print("Requesting URL:", api_url)  # ✅ This will now print correctly when function is called
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error response:", response.text)  # Add this to debug 403
        return None


# API Endpoint: Chat Response
@app.route('/chat', methods=['POST'])
def handle_message():
    try:
        data = request.get_json()
        location = data.get('location')
        date = data.get('date')

        if not location:
            return jsonify({"error": "Location is required"}), 400

        weather_data = get_weather_data(location)

        if weather_data and 'main' in weather_data:
            temperature = weather_data['main']['temp']
            weather_desc = weather_data['weather'][0]['description']
            today = datetime.now().strftime("%d-%m-%Y")
            response = f"The weather in {location} on {today} is {temperature}°C with {weather_desc}."
            return jsonify({"location": location, "date": today, "response": response})
        else:
            return jsonify({"error": "Could not fetch weather for this location."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)


