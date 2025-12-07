from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import json
from .state import State
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)
def iqvia_node(state: State):
    prompt = f"""
You are an IQVIA-style analytics generator.
Generate synthetic but realistic pharma market insights based on the user query.
Follow the strict rules as mentioned. 
STRICT RULES:
- Output ONLY raw JSON.
- NO markdown.
- NO backticks.
- NO ```json.
- NO explanation.
- NO text above or below JSON.
User query:
{state.user_input}

Provide:
- Market size (numbers)
- CAGR trend (numbers)
- Competitor market shares (table)
- Volume trend (list of year-value)
STRICT JSON OUTPUT:
{{
    "market_size_usd": <number>,
    "cagr": <number>,
    "competitors": [
        {{ "company": "", "share": <number> }},
        ...
    ],
    "volume_trend": [
        {{ "year": 2021, "value": <number> }},
        ...
    ]
}}
"""

    res = llm.invoke(prompt).content
    raw = res.strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    return {"iqvia": raw}
