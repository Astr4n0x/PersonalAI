import os
import requests
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("AI_model")

client = Groq(
    api_key=os.getenv("GroqAPIkey")
)

def extract_coin_name(user_query):
    prompt = f"""
Identify the cryptocurrency mentioned in this sentence.

User query:

{user_query}

Return ONLY the cryptocurrency name.

No explanation.

No markdown.

No extra text.

Examples:

Bitcoin -> bitcoin
Ethereum -> ethereum
Solana -> solana
Dogecoin -> dogecoin
Cardano -> cardano
XRP -> xrp
BNB -> bnb
Polygon -> polygon
Avalanche -> avalanche
Chainlink -> chainlink

If no cryptocurrency is found, return UNKNOWN.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Return only the cryptocurrency name."
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
            .lower()
            .replace("`", "")
            .replace('"', "")
            .replace("'", "")
            .strip()
        )

    except Exception:
        return "UNKNOWN"


ALPHA_VANTAGE_KEY = os.getenv(
    "ALPHAVANTAGE_API_KEY"
)

def get_crypto_price(coin: str):
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": coin,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_24hr_high": "true",
        "include_24hr_low": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            return {"error": f"No data found for {coin}."}

        return data

    except requests.exceptions.RequestException as e:
        print(f"CoinGecko error: {e}")
        return {"error": "Unable to retrieve cryptocurrency data."}

    except ValueError:
        return {"error": "Invalid JSON response from CoinGecko."}

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

The following cryptocurrency data was retrieved:

{formatted_data}

Convert this information into a short, natural response for the user.

Rules:
- Address the user as "Sir".
- Answer the user's question directly.
- Include the current cryptocurrency price.
- Include the price change and percentage change when available.
- Include the 24-hour high and low when available.
- Include market capitalization or trading volume when available.
- Include the date or market status when available.
- Include other useful cryptocurrency details only if they are present in the data.
- Keep it concise, around 2-4 sentences.
- Sound natural and professional, like a personal AI assistant.
- Do not mention APIs, JSON, tools, prompts, or internal systems.
- Do not invent or assume any information.
- If the data contains an error, clearly explain the problem.
- Do not use markdown.
- Return ONLY the final response.

Example style:
"Sir, Bitcoin is currently trading at $77,383, up 0.27% over the last 24 hours."

Now generate the response.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
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
            return "Sorry Sir, I couldn't process the market information."

        return result.strip()

    except Exception as e:
        return f"Sorry Sir, I couldn't process the market information."
    
def crypto(query):
    name = extract_coin_name(query)
    price_data = get_crypto_price(name)
    response = simplify_with_groq(query, price_data)
    return response

if __name__ == "__main__":
    while True:
        user_input = input(">> ")
        response = crypto(user_input)
        print(response)

# response = crypto("What is the current price of ethereum?")
# print(response)

# print(extract_coin_name("What is the current price of ethereum?"))
# print(get_crypto_price("ethereum"))
# print(simplify_with_groq("What is the current price of ethereum?", get_crypto_price("ethereum")))