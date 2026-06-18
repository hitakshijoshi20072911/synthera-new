from fastapi import FastAPI, HTTPException
from kafka import KafkaConsumer, KafkaProducer
import os, json
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)
import os,json
BOOTSTRAP_SERVER="" #TODO: to be filled when helm chart of kafka will be installed in this cluster
def create_consumer(topic, group):
    return KafkaConsumer(topic, bootstrap_servers=BOOTSTRAP_SERVER, group_id=group, auto_offset_reset="earliest", value_deserializer=lambda x: json.loads(x.decode()))

producer=KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER, value_serializer=lambda x: json.dumps(x).encode("utf-8"))
consumer=create_consumer("iqvia-topic", "iqvia-group")
for msg in consumer:
    event=msg.value 
    text, job_id= event.get("user_input"), event.get("job_id")
    prompt=f"""
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
{text}

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
    res=llm.invoke(prompt).content
    raw=res.strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        data=json.loads(raw)
    except:
        data = {}
    eve = {"job_id": job_id, "iqvia_res": data}
    producer.send("iqvia-worker", key=job_id.encode(), value=eve)
    producer.flush()
