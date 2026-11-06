from ddgs import DDGS
from groq import Groq
from dotenv import dotenv_values

# Load environment variables from .env file
env = dotenv_values(".env")

# Get additional info from environment variables
GroqAPIkey = env.get("GroqAPIkey")
AI_model = env.get("AI_model")

# Initialize the Groq client with the API key
client = Groq(api_key=GroqAPIkey)

preamble = """
You are an AI search summarizer.

Your task is to analyze the provided search results and give a short, clear, and accurate response to the user's question.

Rules:
- Always use matric systems.
- Keep responses concise and direct.
- Use only the information provided in the search results.
- Do not mention search results, sources, or links unless asked.
- Do not explain unnecessarily.
- If the information is unclear or missing, say:
  'I couldn't find accurate information about that.'
- Give the most relevant and up-to-date answer possible.
- Keep the tone natural and conversational.
- Limit responses to 2-4 sentences maximum.

Example:

User Question:
What is the current price of Bitcoin?

Search Results:
Bitcoin is trading around $104,000 today...

Response:
Bitcoin is currently trading at around $104,000.

User Question:
Who is the current president of France?

Search Results:
Emmanuel Macron is serving as the president of France...

Response:
The current president of France is Emmanuel Macron.
"""

def DecisionMakingModel(prompt: str, results: str):
    
    model = client.chat.completions.create(
        model = AI_model,
        messages=[
        {
            "role": "system",
            "content": preamble
        },
        {
            "role": "user",
            "content": f"Question: {prompt}\nSearch Results: {results}"
        }
        ],
        temperature=0,
        max_tokens=1000
    )
    
    response = model.choices[0].message.content
    return response

def realtime_search(query: str):

    results = []

    for r in DDGS().text(query, max_results=3):

        results.append(
            f"{r['body']}"
        )
        
    return "\n".join(results)

def AI_analysics(query: str):
    results = realtime_search(query)
    
    # print(f"Search results:\n{results}\n")
    
    return DecisionMakingModel(query, results)

if __name__ == "__main__":
    while True:
        query = input(">>> ")
        results = realtime_search(query)
        print(AI_analysics(query))