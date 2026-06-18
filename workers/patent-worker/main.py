from kafka import KafkaConsumer, KafkaProducer
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
import os, json
from dotenv import load_dotenv
load_dotenv()
BOOTSTRAP_SERVER=""
def create_consumer(topic, group):
    return KafkaConsumer(topic, bootstrap_servers=BOOTSTRAP_SERVER, group_id=group, auto_offset_reset="earliest", value_deserializer=lambda x: json.loads(x.decode()))

producer=KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER, value_serializer=lambda x:json.loads(x).encode("utf-8"))
consumer=create_consumer("patent-topic", "patent-group")
for msg in consumer:
    event = msg.value
    text, job_id=event.get("user_input"), event.get("job_id")
    prompt=f"""
     You are a Patent Intelligence Agent simulating USPTO/Derwent/Clarivate patent data.
Generate synthetic but realistic patent landscape analytics.
STRICT RULES:
- Output ONLY raw JSON (no markdown, no ```json).
- No explanations.
- Follow EXACTLY this structure:
{{
  "patents": [
    {{
      "patent_number": "",
      "assignee": "",
      "priority_year": <number>,
      "filing_year": <number>,
      "expiry_year": <number>,
      "status": "active|expired|pending",
      "fto_risk": "low|medium|high"
    }}
  ],
  "expiry_timeline": [
    {{"year": <year>, "count": <number>}},
    {{"year": <year>, "count": <number>}}
  ],
  "competitive_heatmap": [
    {{"company": "", "score": <0-10>}},
    {{"company": "", "score": <0-10>}}
  ],
  "excerpts": [
    "",
    ""
  ]
}}
User Query:
{text}
    """
    raw=llm.invoke(prompt)
    raw=raw.strip()
    if raw.startswith(("```"):
        raw= raw.replace("```json", "").replace("```", "").strip()
    try:
        data=json.loads(raw)
    except:
        data = {}
    eve= {"job_id": job_id, "patent_res": data}
    producer.send("patent-worker", key=job_id.encode(), value=eve)
    producer.flush()
