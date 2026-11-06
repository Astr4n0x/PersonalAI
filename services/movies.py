import os
import json
import requests

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GroqAPIKey = os.getenv("GroqAPIkey")
TMDB_API_KEY = os.getenv("TMDB_API_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"
model = os.getenv("AI_model")

client = Groq(
    api_key=os.getenv("GroqAPIkey")
)

TMDB_HEADERS = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}


def extract_movie_title_groq(user_query):
    prompt = f"""
Classify this user query.

Query: {user_query}

Return exactly one of these formats:
Details <title> Movie
Cast <title> Movie
Details <title> TV
Cast <title> TV
Trending Movies
Trending TV Shows

Rules:
- Identify the actual movie or TV show title.
- Use Movie for films and TV for television series.
- Use Details for questions about ratings, plots, or information.
- Use Cast for questions about actors.
- Do not include angle brackets.
- Return only the result.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100
        )

        raw = response.choices[0].message.content

        if not raw:
            # print("Empty response:", response.choices[0].finish_reason)
            return "UNKNOWN"

        return raw.strip()

    except Exception as e:
        # print(type(e).__name__, str(e))
        return "UNKNOWN"


def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        "query" : query,
        "language" : "en-US",
        "page" : 1
    }

    response = requests.get(url, params=params, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results")
        first_result = results[0]
        return first_result
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def search_tv_shows(query):
    url = f"{BASE_URL}/search/tv"
    params = {
        "query" : query,
        "language" : "en-US",
        "page" : 1
    }

    response = requests.get(url, params=params, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results")
        first_result = results[0]
        return first_result
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def movie_id(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        "query" : query,
        "language" : "en-US",
        "page" : 1
    }

    response = requests.get(url, params=params, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results")
        first_result = results[0]
        first_id = first_result["id"]
        return first_id
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def tv_show_id(query):
    url = f"{BASE_URL}/search/tv"
    params = {
        "query" : query,
        "language" : "en-US",
        "page" : 1
    }

    response = requests.get(url, params=params, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results")
        first_result = results[0]
        first_id = first_result["id"]
        return first_id
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def movie_details(query):
    id = movie_id(query)
    url = f"{BASE_URL}/movie/{id}"

    response = requests.get(url, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()

        output = {
            "title": data["original_title"],
            "overview": data["overview"],
            "tagline" : data["tagline"],
            "adult" : data["adult"],
            "release_date": data["release_date"],
            "runtime": data["runtime"],
            "rating": data["vote_average"],
            "genres": [genre["name"] for genre in data["genres"]]
        }

        return output
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def tv_show_details(query):
    id = tv_show_id(query)
    url = f"{BASE_URL}/tv/{id}"

    response = requests.get(url, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()

        output = {
            "title": data["original_name"],
            "overview": data["overview"],
            "tagline" : data["tagline"],
            "adult" : data["adult"],
            "first_air_date": data["first_air_date"],
            "last_air_date": data["last_air_date"],
            "number_of_seasons": data["number_of_seasons"],
            "number_of_episodes": data["number_of_episodes"],
            "rating": data["vote_average"],
            "genres": [genre["name"] for genre in data["genres"]]
        }

        return output
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def movie_casts(query):
    id = movie_id(query)
    url = f"{BASE_URL}/movie/{id}/credits"

    response = requests.get(url, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()

        return {actor["name"]: actor["character"] for actor in data.get("cast", [])}
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def tv_show_casts(query):
    id = tv_show_id(query)
    url = f"{BASE_URL}/tv/{id}/credits"

    response = requests.get(url, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()

        return {actor["name"]: actor["character"] for actor in data.get("cast", [])}
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def tranding_movies():
    url = f"{BASE_URL}/trending/movie/week"

    response = requests.get(url, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()
        response = [
            {
            "title" : d.get("title"),
            "overview" : d.get("overview"),
            "vote_average" : d.get("vote_average"),
            "language" : d.get("original_language"),
            "release_date" : d.get("release_date"),
            "genres" : [genre["name"] for genre in d.get("genres", [])],
            "adult" : d.get("adult"),
            }

            for d in data.get("results", [])
        ]
        return response
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def tranding_tv_shows():
    url = f"{BASE_URL}/trending/tv/week"

    response = requests.get(url, headers=TMDB_HEADERS)

    if response.status_code == 200:
        data = response.json()
        response = [
            {
            "title" : d.get("title"),
            "overview" : d.get("overview"),
            "vote_average" : d.get("vote_average"),
            "language" : d.get("original_language"),
            "release_date" : d.get("first_air_date"),
            "genres" : [genre["name"] for genre in d.get("genres", [])],
            "number_of_seasons" : d.get("number_of_seasons"),
            "number_of_episodes" : d.get("number_of_episodes"),
            "adult" : d.get("adult"),
            }
            for d in data.get("results", [])
        ]
        return response
    else:
        return {"error": f"Failed to fetch data from TMDB API. Status code: {response.status_code}"}

def rephrase_output_groq(user_query, json_data):
    formatted_data = json.dumps(
        json_data,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are Jarvis, a personal AI assistant.
The user asked: {user_query}

The following is the data retrieved from the API:
{formatted_data}

Convert this information into a short, natural response for the user.

Rules:
- Address the user as "Sir".
- Answer the user's question directly.
- Keep it concise, around 2-4 sentences.
- Sound natural and professional, like a personal AI assistant.
- Do not mention APIs, JSON, tools, prompts, or internal systems.
- Do not invent or assume any information.
- If the data contains an error, clearly explain the problem.
- Do not use markdown.
- Return ONLY the final response.

Example style:
"Sir, The movie 'Inception' is a science fiction thriller directed by Christopher Nolan. It has a rating of 8.8/10 and was released on July 16, 2010. The film explores the concept of dream manipulation and features a talented cast including Leonardo DiCaprio, Joseph Gordon-Levitt, and Ellen Page."

Now generate the response.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Return only the final response."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=200
        )

        raw = response.choices[0].message.content

        if not raw:
            return "UNKNOWN"

        return raw.strip()

    except Exception as e:
        return "UNKNOWN"


def response(query):
    name = extract_movie_title_groq(query)
    words = name.split()

    if not words:
        return "UNKNOWN"

    task = words[0].lower()
    media_type = words[-1].lower()
    movie_name = " ".join(words[1:-1])

    if task == "details" and media_type == "movie":
        movie_data = movie_details(movie_name)
        return rephrase_output_groq(query, movie_data)

    elif task == "cast" and media_type == "movie":
        cast_data = movie_casts(movie_name)
        return rephrase_output_groq(query, cast_data)

    elif task == "details" and media_type == "tv":
        movie_data = tv_show_details(movie_name)
        return rephrase_output_groq(query, movie_data)

    elif task == "cast" and media_type == "tv":
        cast_data = tv_show_casts(movie_name)
        return rephrase_output_groq(query, cast_data)

    elif name.lower() == "trending movies":
        trending_movies_data = tranding_movies()
        return rephrase_output_groq(query, trending_movies_data)

    elif name.lower() == "trending tv shows":
        trending_tv_data = tranding_tv_shows()
        return rephrase_output_groq(query, trending_tv_data)

    return "UNKNOWN"


# user_query = "What is the rating of The Godfather?"
# print(rephrase_output_groq(user_query, extract_movie_title_groq(user_query)))

if __name__ == "__main__":
    while True:
        user_query = input(">>> ")
        if user_query.lower() in ["exit", "quit"]:
            break
        result = response(user_query)
        print(result)