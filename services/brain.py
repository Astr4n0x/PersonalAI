from groq import Groq
from dotenv import dotenv_values
from chatbot import chatbot
from realtime import AI_analysics
from stocks import stocks
from crypto import crypto
from text_to_speach import speak
from weather import weather
from open_apps import AppOpen, AppClose
from youtube import youtube_search
from movies import response

# Load environment variables from .env file
env = dotenv_values(".env")

# Get additional info from environment variables
GroqAPIkey = env.get("GroqAPIkey")
AI_model = env.get("AI_model")

# Initialize the Groq client with the API key
client = Groq(api_key=GroqAPIkey)

func = [ 
    "general", "realtime", "open", "close", "exit", "play",
    "system", "generate image", "content", "google search",
    "youtube search", "reminder", "stocks", "crypto"
]

massages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversatithis math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?onal ai assistant) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with ' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
-> Respond with 'stocks (query)' if a query is asking about stock prices, stock market data, company shares, stock performance, stock changes, market capitalization, or any other information specifically related to stocks or publicly traded companies. For example, if the query is 'what is Apple's stock price?' respond with 'stocks what is Apple's stock price?', if the query is 'how is Tesla stock doing today?' respond with 'stocks how is Tesla stock doing today?', if the query is 'what is the current price of Microsoft shares?' respond with 'stocks what is the current price of Microsoft shares?', and so on. Use 'stocks (query)' whenever the query requires current or recent stock market information.
-> Respond with 'crypto (query)' if a query is asking about cryptocurrency prices, crypto market data, cryptocurrency performance, market capitalization, price changes, or any other information specifically related to cryptocurrencies. For example, if the query is 'what is the price of Bitcoin?' respond with 'crypto what is the price of Bitcoin?', if the query is 'how is Ethereum doing today?' respond with 'crypto how is Ethereum doing today?', if the query is 'what is the current price of Solana?' respond with 'crypto what is the current price of Solana?', and so on. Use 'crypto (query)' whenever the query requires current or recent cryptocurrency market information.\
-> Respond with 'weather (query)' if a query is asking about the current weather, temperature, forecast, rain, humidity, wind, or other weather-related information for any location.
-> Respond with 'movies (query)' if a query is asking about movie ratings, reviews, cast, crew, release dates, box office performance, or any other information specifically related to movies. For example, if the query is 'what is the rating of The Godfather?' respond with 'movies what is the rating of The Godfather?', if the query is 'who directed Inception?' respond with 'movies who directed Inception?', and so on. Use 'movies (query)' whenever the query requires current or recent movie information.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

chatHistory = [
    {"role": "user", "content": "how are you?"},
    {"role": "assistant", "content": "general how are you?"},
    {"role": "user", "content": "who is akbar?"},
    {"role": "assistant", "content": "general who is akbar?"},
    {"role": "user", "content": "who is bangladeshi prime minister?"},
    {"role": "assistant", "content": "realtime who is bangladeshi prime minister?"},
    {"role": "user", "content": "open facebook, telegram and close whatsapp."},
    {"role": "assistant", "content": "open facebook, open telegram, close whatsapp."},
    {"role": "user", "content": "play afsanay by ys and let her go."},
    {"role": "assistant", "content": "play afsanay by ys, play let her go."},
    {"role": "user", "content": "generate image of a lion and a cat."},
    {"role": "assistant", "content": "generate image of a lion, generate image of a cat."},
    {"role": "user", "content": "set a reminder at 9:00pm on 25th june for my business meeting."},
    {"role": "assistant", "content": "reminder 9:00pm 25th june business meeting."},
    {"role": "user", "content": "mute the system and volume up."},
    {"role": "assistant", "content": "system mute, system volume up."},
    {"role": "user", "content": "write an application for leave and write a code to add two numbers."},
    {"role": "assistant", "content": "content application for leave, content code to add two numbers."},
    {"role": "user", "content": "search about python programming language on google and search about machine learning on youtube."},
    {"role": "assistant", "content": "google search python programming language, youtube search machine learning."},
    {"role": "user", "content": "open chrome and tell me about Dr Younus."},
    {"role": "assistant", "content": "open chrome, general tell me about Dr Younus."},
    {"role": "user", "content" : "what's the time?"},  
    {"role": "assistant", "content": "general what's the time?"},
    {"role": "user", "content": "bye jarvis."},
    {"role": "assistant", "content": "exit"}
]

def DecisionMakingModel(prompt: str):
    chatHistory.append({"role": "user", "content": prompt})
    
    model = client.chat.completions.create(
        model = AI_model,
        messages=[
        {
            "role": "system",
            "content": preamble
        },

        *chatHistory,

        {
            "role": "user",
            "content": prompt
        }
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    response = model.choices[0].message.content
    chatHistory.append({"role": "assistant", "content": response})
    return response

def route(decision: str):
    decision = decision.lower()

    if decision.startswith("general"):
        query = decision.replace("general", "", 1).strip()
        return chatbot(query)
    elif decision.startswith("realtime"):
        query = decision.replace("realtime", "", 1).strip()
        return AI_analysics(query)
    elif decision.startswith("open"):
        query = decision.replace("open", "", 1).strip()
        return AppOpen(query)
    elif decision.startswith("close"):
        query = decision.replace("close", "", 1).strip()
        return AppClose(query)
    elif decision.startswith("stocks"):
        query = decision.replace("stocks", "", 1).strip()
        return stocks(query)
    elif decision.startswith("crypto"):
        query = decision.replace("crypto", "", 1).strip()
        return crypto(query)
    elif decision.startswith("youtube search"):
        query = decision.replace("youtube search", "", 1).strip()
        return youtube_search(query)
    elif decision.startswith("weather"):
        query = decision.replace("weather", "", 1).strip()
        return weather(query)
    elif decision.startswith("movies"):
        query = decision.replace("movies", "", 1).strip()
        return response(query)

if __name__ == "__main__":
    while True:
        decision = DecisionMakingModel(input(">>> "))
        if decision.startswith("open"):
            text = decision.split()
            speak(f"opening {text[1]}")
            result = route(decision)
        else:
            result = route(decision)
            speak(result)