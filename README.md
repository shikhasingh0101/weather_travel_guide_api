# weather_travel_guide_api
# 🌦️ Weather & Travel Guide API (Flask Backend)

This is a Flask-based backend that powers a Weather Summarizer and AI-based Travel Assistant. It supports:

- 🌤️ Weather summary extraction from natural language
- 🏨 Accommodation suggestions
- 🧳 Full travel guides with itineraries and summaries

---

## 🚀 Features

- Extracts **location** and **date** from a user query
- Connects with Ollama (LLM) for AI-powered responses
- Provides travel accommodation suggestions
- Generates detailed day-wise itineraries

---

## 📁 Folder Structure

weather_app_backend/
│
├── app.py / whether.py # Main Flask app
├── requirements.txt # Python dependencies
├── render.yaml # Deployment config for Render
└── README.md # You’re here!



---

## 🧪 Setup Locally

### 1. Clone the Repo

```bash
git clone https://github.com/shikhasingh0101/weather_travel_guide_api.git
cd weather_travel_guide_api
2. Create a Virtual Environment (Optional but Recommended)

python3 -m venv aienvshikhasingh
source aienvshikhasingh/bin/activate
3. Install Dependencies

pip install -r requirements.txt
4. Run the Flask Server

python whether.py
Server will run on: http://127.0.0.1:5000

🌐 API Endpoints
Endpoint	Method	Description
/extract_location_date	POST	Extracts location, date, and weather summary
/travel_guide	POST	Suggests travel accommodations
/full_travel_guide	POST	Full itinerary and travel guide

🌍 Deploy on Render
Go to https://render.com

Click New > Web Service

Connect your GitHub repo

Choose:

Build Command: pip install -r requirements.txt

Start Command: python whether.py

Environment: Python 3.x

Render reads render.yaml and auto-deploys the backend.

✨ Example Request (for /extract_location_date)

{
  "message": "What's the weather in Goa on 2025-06-20?"
}
💡 Notes
Ensure your Ollama LLM or any API key-based AI model is running and reachable.

If using CORS, install flask-cors.
pip install flask-cors

🧠 Author
Shikha Singh
GitHub: @shikhasingh0101

