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

def extract_stock_symbol(user_query):
    prompt = f"""
Identify the financial asset mentioned in this sentence.

User query:
{user_query}

Return ONLY the ticker symbol.
No explanation.
No markdown.
No extra text.

Examples:
Apple -> AAPL
Microsoft -> MSFT
Tesla -> TSLA
Nvidia -> NVDA
Amazon -> AMZN
Google -> GOOGL
Bitcoin -> BTC
Ethereum -> ETH

If no financial asset is found, return UNKNOWN.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Return only the financial ticker symbol."
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
            .upper()
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

def get_stock(symbol):

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol.upper(),
        "apikey": ALPHA_VANTAGE_KEY
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=8
        )

        response.raise_for_status()

        data = response.json()

        # API errors / rate limits
        if "Note" in data:

            return {
                "error": data["Note"]
            }

        if "Error Message" in data:

            return {
                "error": data["Error Message"]
            }

        quote = data.get(
            "Global Quote"
        )

        if not quote:

            return {
                "error": "No stock data found"
            }

        return {
            "symbol": quote.get(
                "01. symbol"
            ),

            "price": quote.get(
                "05. price"
            ),

            "change": quote.get(
                "09. change"
            ),

            "change_percent": quote.get(
                "10. change percent"
            ),

            "volume": quote.get(
                "06. volume"
            ),

            "latest_trading_day": quote.get(
                "07. latest trading day"
            )
        }

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

The following data was retrieved:

{formatted_data}

Convert this information into a short, natural response for the user.

Rules:
- Address the user as "Sir".
- Answer the user's question directly.
- Include the current price.
- Include the price change and percentage change when available.
- Include the date or market status when available.
- Include other useful financial details only if they are present in the data.
- Keep it concise, around 2-4 sentences.
- Sound natural and professional, like a personal AI assistant.
- Do not mention APIs, JSON, tools, prompts, or internal systems.
- Do not invent or assume any information.
- If the data contains an error, clearly explain the problem.
- Do not use markdown.
- Return ONLY the final response.

Example style:
"Sir, Apple stock is currently trading at $325.13, up $8.28 (+2.61%) from the previous close. The latest available data is from September 1, 2026."

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
            return "Sorry Sir, I couldn't process the market information."

        return result.strip()

    except Exception as e:
        return f"Sorry Sir, I couldn't process the market information."
    
def stocks(query):
    symbol = extract_stock_symbol(query)
    stock_data = get_stock(symbol)
    result = simplify_with_groq(query, stock_data)
    return result

if __name__ == "__main__":
    while True:
        user_query = input(">>> ")
        response = get_stock(user_query)
        print(response)