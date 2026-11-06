import os
import json
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

model = os.getenv("AI_model")

client = Groq(
    api_key=os.getenv("GroqAPIkey")
)


def extract_city_name(user_query):
    prompt = f"""
Identify the city mentioned in this sentence and return the city name along with its country.

User query:

{user_query}

Return ONLY the city and country in this exact format:

City, Country

No explanation.
No markdown.
No extra text.

Examples:
What is the weather in Khulna? -> Khulna, Bangladesh
What's the weather like in Dhaka? -> Dhaka, Bangladesh
Tell me the temperature in London. -> London, United Kingdom
How's the weather in New York? -> New York, United States
What's the weather in Tokyo? -> Tokyo, Japan
Tell me the temperature in Paris. -> Paris, France
How hot is it in Dubai? -> Dubai, United Arab Emirates
What's the weather in Sydney? -> Sydney, Australia

If no city is found, return UNKNOWN.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Return only the city and country."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=100
        )

        raw = response.choices[0].message.content

        if not raw:
            return "UNKNOWN"

        return (
            raw.strip()
            .replace("`", "")
            .replace('"', "")
            .replace("'", "")
            .strip()
        )

    except Exception:
        return "UNKNOWN"


def get_coordinates(location):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results")

        if not results:
            return None

        place = results[0]

        return {
            "name": place.get("name"),
            "country": place.get("country"),
            "latitude": place.get("latitude"),
            "longitude": place.get("longitude")
        }

    except Exception as e:
        print("Geocoding error:", e)
        return None


def weather_code_description(code):

    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    return weather_codes.get(
        code,
        "Unknown weather condition"
    )


def get_weather(location):

    coordinates = get_coordinates(location)

    if not coordinates:
        return {
            "error": "Location not found"
        }

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),

        "timezone": "auto",
        "forecast_days": 3
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        weather_code = current.get("weather_code")

        result = {
            "location": coordinates["name"],
            "country": coordinates["country"],

            "current": {
                "time": current.get("time"),
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "feels_like": current.get("apparent_temperature"),
                "precipitation": current.get("precipitation"),
                "condition": weather_code_description(weather_code),
                "wind_speed": current.get("wind_speed_10m")
            },

            "forecast": {
                "dates": daily.get("time", []),
                "max_temperature": daily.get(
                    "temperature_2m_max",
                    []
                ),
                "min_temperature": daily.get(
                    "temperature_2m_min",
                    []
                ),
                "rain_probability": daily.get(
                    "precipitation_probability_max",
                    []
                )
            }
        }

        return result

    except Exception as e:
        return {
            "error": str(e)
        }


def simplify_with_groq(user_query, json_data):

    formatted_data = json.dumps(
        json_data,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are Jarvis, a personal AI assistant.

The user asked:
"{user_query}"

The following weather data was retrieved:

{formatted_data}

Convert this information into a very short, natural response.

Rules:

- Address the user as "Sir".
- Answer the user's question directly.
- Use ONLY the information provided in the weather data.
- Do not calculate or invent information.
- Mention the location when useful.
- For current weather, prioritize temperature, feels-like temperature, weather condition, rain, and wind.
- For forecast questions, provide only the requested days.
- Do not mention humidity unless it is relevant.
- Do not mention technical fields or weather codes.
- Keep the response to 1-3 short sentences.
- Sound natural and professional, like a personal AI assistant.
- Do not mention APIs, JSON, tools, prompts, or internal systems.
- If the data contains an error, clearly explain the problem.
- Do not use markdown.
- Return ONLY the final response.

Example:

"Sir, it's currently 30.7°C in Khulna, but it feels like 36.7°C. There's a thunderstorm with a 99% chance of rain today."

Now generate the response.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are Jarvis, a concise and professional personal AI assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=200
        )

        result = response.choices[0].message.content

        if not result:
            return "Sorry Sir, I couldn't process the weather information."

        return result.strip()

    except Exception as e:
        print("Groq error:", type(e).__name__, str(e))
        return "Sorry Sir, I couldn't process the weather information."

def save_weather_data(weather_data):

    with open(
        "database/weather.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            weather_data,
            file,
            indent=4,
            ensure_ascii=False
        )


def weather(query):
    city_name = extract_city_name(query)
    weather = get_weather(city_name)
    save_weather_data(weather)
    response = simplify_with_groq(query, weather)
    return response


if __name__ == "__main__":
    while True:
        user_query = input(">>> ")
        weather_info = weather(user_query)
        print(weather_info)