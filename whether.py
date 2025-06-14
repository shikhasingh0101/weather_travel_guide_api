from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
import datetime
import json
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

api_key = 'cfe0eb21c36c4ab0bd954615252805'
cities = ["Mumbai", "Delhi", "Chennai", "Kolkata", "Bangalore", "Hyderabad", "Paris", "London", "New York", "Tokyo", "Dubai"]

ollama_url = "http://localhost:11434/api/chat"

def is_weather_prompt(prompt):
    return "weather" in prompt.lower() or "climate" in prompt.lower()

def extract_city(message):
    for city in cities:
        if city.lower() in message.lower():
            return city
    match = re.search(r'\b(?:trip to |travel to |visiting |visit |to |in )([A-Z][a-z]+)', message)
    return match.group(1) if match else None

def extract_date(message):
    match = re.search(r'(next week|tomorrow|today|\d{1,2} \w+)', message, re.IGNORECASE)
    return match.group(1).lower() if match else "next week"

@app.route('/extract_location_date', methods=['POST'])
def extract_location_date():
    data = request.get_json()
    msg = data.get("message", "")
    if not msg:
        return jsonify({"error": "Message is required"}), 400

    loc = extract_city(msg)
    date = extract_date(msg)

    if loc and is_weather_prompt(msg):
        api_url2 = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q={loc}&dt={date}"
        wresp = requests.get(api_url2)
        if wresp.status_code == 200:
            wdata = wresp.json()["forecast"]["forecastday"][0]["day"]
            summary_payload = {
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": "Summarize weather data in 3-5 lines."},
                    {"role": "user", "content": json.dumps({"location": loc, "forecast": wdata})}
                ],
                "stream": False
            }
            summ = requests.post(ollama_url, json=summary_payload).json()
            weather_summary = summ.get("message", {}).get("content", "")
            return jsonify({"weather_summary": weather_summary})

    # For general question
    payload_general = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": "Be assistant for any general question."},
            {"role": "user", "content": msg}
        ],
        "stream": False
    }
    genet = requests.post(ollama_url, json=payload_general).json()
    ans = genet.get("message", {}).get("content", "")
    return jsonify({"answer": ans})

@app.route('/weather', methods=['POST'])
def weather():
    return extract_location_date()

@app.route('/travel_guide', methods=['POST'])
def travel_guide():
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    city = extract_city(message)
    date = extract_date(message)

    if city:
        # Travel-related question
        return jsonify(get_accommodation_summary_internal(city))
    else:
        # General non-travel question
        payload_general = {
            "model": "llama3.2",
            "messages": [
                {"role": "system", "content": "Be assistant for any general question."},
                {"role": "user", "content": message}
            ],
            "stream": False
        }
        genet = requests.post(ollama_url, json=payload_general).json()
        ans = genet.get("message", {}).get("content", "")
        return jsonify({"answer": ans})



@app.route('/full_travel_guide', methods=['POST'])
def full_travel_guide():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "The 'message' field is required"}), 400

    # 1. Try extracting location and date using Ollama
    extract_payload = {
        "model": "llama3.2",
        "messages": [
            {
                "role": "system",
                "content": "Extract 'location' and 'date' from this message. Return ONLY JSON: {\"location\": \"city\", \"date\": \"YYYY-MM-DD\"}."
            },
            {"role": "user", "content": user_message}
        ],
        "stream": False
    }

    response = requests.post(ollama_url, json=extract_payload)
    content = response.json().get('message', {}).get('content', '').strip()
    json_match = re.search(r"\{.*\}", content, re.DOTALL)

    location = None
    date = None

    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            location = parsed.get("location", "").strip()
            date = parsed.get("date", "").strip()
        except Exception as e:
            print("JSON parsing error:", e)

    # 2. Manual fallback if Ollama extraction fails
    if not location:
        location = extract_city(user_message)
    if not date:
        date = extract_date(user_message)

    # 3. If still no location, treat as general question
    if not location:
        payload_general = {
            "model": "llama3.2",
            "messages": [
                {"role": "system", "content": "Be assistant for any general question."},
                {"role": "user", "content": user_message}
            ],
            "stream": False
        }
        genet = requests.post(ollama_url, json=payload_general).json()
        ans = genet.get("message", {}).get("content", "")
        return jsonify({"answer": ans})

    # 4. Proceed with travel guide summary
    itinerary_response = get_itinerary_summary_internal(location, date)
    itinerary_data = itinerary_response.get_json()

    travel_summary = generate_travel_summary("Your City", location)
    travel_data = travel_summary.get_json()

    return jsonify({
        "formatted_response": f"Travel Guide for {location} on {date}:",
        "itinerary": itinerary_data,
        "travel_summary": travel_data
    })


def get_accommodation_summary_internal(city):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": "AIzaSyBJryQHS3a_vWNF2M8zKvhATFgAdyNAwQU",
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel,places.rating"
    }
    payload = {"textQuery": f"Hotels in {city}"}
    response = requests.post(url, json=payload, headers=headers)
    hotel_data = response.json()

    summary_payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": "Summarize hotel list in 3-5 lines."},
            {"role": "user", "content": json.dumps(hotel_data.get("places", []))}
        ],
        "stream": False
    }
    summary_response = requests.post(ollama_url, json=summary_payload)
    summary_text = summary_response.json().get('message', {}).get('content', '').strip()

    return {"city": city, "summary": summary_text}

def get_itinerary_summary_internal(city, date):
    itinerary_data = {
        "day1": ["Visit the museum", "Explore market"],
        "day2": ["See landmarks", "Cultural evening"]
    }
    summary_payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": "Summarize a 2-day itinerary."},
            {"role": "user", "content": json.dumps({"city": city, "date": date, "itinerary": itinerary_data})}
        ],
        "stream": False
    }
    response = requests.post(ollama_url, json=summary_payload)
    summary_text = response.json().get("message", {}).get("content", "").strip()

    return jsonify({"summary": summary_text, "itinerary": itinerary_data})

def generate_travel_summary(from_city, to_city):
    travel_plan_text = (
        f"Travel from {from_city} to {to_city} by train takes approx 6 hours and costs around $25. Other options: bus/flight."
    )
    summary_payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": "Summarize the following travel plan."},
            {"role": "user", "content": travel_plan_text}
        ],
        "stream": False
    }
    response = requests.post(ollama_url, json=summary_payload)
    summary_text = response.json().get('message', {}).get('content', '').strip()
    return jsonify({"summary": summary_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get port from environment, default to 5000
    app.run(host="0.0.0.0", port=port)