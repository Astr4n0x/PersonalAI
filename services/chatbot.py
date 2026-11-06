import json
import os
from groq import Groq
from dotenv import dotenv_values
import datetime

# Load environment variables from .env file
env = dotenv_values(".env")

# Get additional info from environment variables
Username = env.get("Username")
AssistantName = env.get("AssistantName")
GroqAPIkey = env.get("GroqAPIkey")
AI_model = env.get("AI_model")

# Initialize the Groq client with the API key
client = Groq(api_key=GroqAPIkey)

# Define a system message for the model about its role and behavior
System = f"""Hello, I am {Username}.
You are {AssistantName}, an advanced AI assistant designed for precision, clarity, and efficiency. You have access to real-time, up-to-date information from the internet and respond with high accuracy.
Suppose you are as intelligent as Friday from Avengers.

Behavior Protocol:

***Be concise, direct, and intelligent in every response.***
***Do not provide time unless explicitly asked.***
***Avoid unnecessary elaboration—answer only what is required.***
***Always respond in English, regardless of the input language.***
***Do not include notes, disclaimers, or meta explanations.***
***Never mention training data or internal processes.***
***Maintain a calm, confident, and slightly formal tone, similar to a high-level AI system.***
***Give me time information only when i ask for it.***

Humor Layer:

***Use bold humor every time.***
***Keep it dry, intelligent, and brief—never distracting.***
***Do not joke in serious or sensitive situations.***
***Humor should enhance clarity, not replace it.***

Your purpose is to deliver precise, reliable answers with minimal friction.
"""

def RealTimeInformation():
    # Get the current date and time
    current_time = datetime.datetime.now()
    day = current_time.strftime("%A")
    date = current_time.strftime("%d")
    year = current_time.strftime("%Y")
    month = current_time.strftime("%B")
    hour = current_time.strftime("%I")
    minute = current_time.strftime("%M")
    second = current_time.strftime("%S")

    # Format the information into a string
    data = f"Please use this information when needed,\n"
    date += f"Day: {day} Date: {date}, Month: {month}, Year: {year}\n"
    date += f"Hour: {hour}, Minute: {minute}, Second: {second}\n"

    return data

# In-memory storage for speed
messages = []
qa_cache = {}  # Maps normalized question -> answer
MAX_CONTEXT = 10  # Only send last N messages to API for speed

def _normalize_question(q):
    """Normalize question for cache lookup."""
    return q.strip().lower()

def _load_history():
    """Load chat history from JSON file once at startup."""
    global messages, qa_cache
    try:
        with open("database/chatHistory.json", "r") as file:
            loaded = json.load(file)

            if loaded and loaded[0]["role"] == "system":
                messages = [loaded[0]]
                rest = loaded[1:]
            else:
                messages = [{"role": "system", "content": System + "\n" + RealTimeInformation()}]
                rest = loaded if loaded else []

            # Keep only recent messages in memory for context
            if len(rest) > MAX_CONTEXT:
                messages.extend(rest[-MAX_CONTEXT:])
            else:
                messages.extend(rest)

            # Build QA cache from all history
            for i in range(0, len(rest) - 1, 2):
                if i + 1 < len(rest):
                    user_msg = rest[i]
                    asst_msg = rest[i + 1]
                    if user_msg["role"] == "user" and asst_msg["role"] == "assistant":
                        key = _normalize_question(user_msg["content"])
                        qa_cache[key] = asst_msg["content"]

    except (FileNotFoundError, json.JSONDecodeError):
        messages = [{"role": "system", "content": System + "\n" + RealTimeInformation()}]

def _save_history():
    """Save only the recent messages to keep file small and fast."""
    try:
        with open("database/chatHistory.json", "w") as file:
            json.dump(messages, file, indent=4)
    except Exception as e:
        print(f"Error saving chat history: {e}")

# Load history once at module startup
_load_history()

def chatbot(prompt: str):
    global messages, qa_cache

    # Check cache first - instant response for repeated questions
    normalized = _normalize_question(prompt)
    if normalized in qa_cache:
        return qa_cache[normalized]

    # Update system message with current time
    messages[0]["content"] = System + "\n" + RealTimeInformation()

    # Add user message
    messages.append({"role": "user", "content": prompt})

    # Prepare context: only last MAX_CONTEXT messages for speed
    context = messages[-MAX_CONTEXT-1:] if len(messages) > MAX_CONTEXT+1 else messages[:]

    # Call Groq API with limited context
    brain = client.chat.completions.create(
        model=AI_model,
        messages=context,
        max_tokens=1000,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    response = brain.choices[0].message.content

    # Add assistant response to messages
    messages.append({"role": "assistant", "content": response})

    # Update cache for future instant lookup
    qa_cache[normalized] = response

    # Save to file (only recent messages, not the full history)
    _save_history()

    return response

if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        print(chatbot(user_input))