import os
from dotenv import load_dotenv
load_dotenv()
from kafka import KafkaConsumer, KafkaProducer
import json
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
BOOTSTRAP_SERVER="" #to be filled when helm chart of kafka will be installed in this cluster
def create_consumer(topic, group):
    return KafkaConsumer(topic, bootstrap_servers=BOOTSTRAP_SERVER, group_id=group, auto_offset_reset="earliest", value_deserializer=lambda x: json.loads(x.decode()))

producer=KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER, value_serializer=lambda y: json.dumps(y).encode("utf-8"))
consumer=create_consumer("exim-topic", "exim-group")
while msg in consumer:
    event= msg.value 
    text, job_id = event.get("user_input"), event.get("job_id")
    prompt = f"""
    You are an EXIM (Export-Import) analytics generator for pharma APIs.

Generate realistic synthetic EXIM data based on the user query.

STRICT RULES:
- Output ONLY raw JSON.
- NO markdown.
- NO backticks.
- NO comments.
- Use ONLY the following JSON format:

{{
  "import_volume_mt": [
    {{"year": 2021, "value": <number>}},
    {{"year": 2022, "value": <number>}},
    {{"year": 2023, "value": <number>}}
  ],
  "export_volume_mt": [
    {{"year": 2021, "value": <number>}},
    {{"year": 2022, "value": <number>}},
    {{"year": 2023, "value": <number>}}
  ],
  "top_import_sources": [
    {{"country": "", "percent": <number>}},
    {{"country": "", "percent": <number>}},
    {{"country": "", "percent": <number>}}
  ],
  "dependency_risk": "",
  "sourcing_insights": ["", "", ""]
}}

User query:
{text}
    """
    raw= llm.invoke(prompt)
    raw=raw.strip()
    if raw.startswith("```"):
        raw =raw.replace("```json", "").replace("```", "").strip()
    try:
        data=json.loads(raw)
    except:
        data= {}
    eve= {"job_id": job_id, "exim_res": data}
    producer.send("exim-worker", key=job_id.encode("utf-8"), value=eve)
    producer.flush()


