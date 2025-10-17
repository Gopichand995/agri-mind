# app/kinesis_consumer.py
import json
import base64
import boto3
import os
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "agri-mind-prototype-bucket-<YOUR_SUFFIX>")
AGENT_ID = os.environ.get("AGENT_ID", "replace-with-agent-id")
AGENT_ALIAS_ID = os.environ.get("AGENT_ALIAS_ID", "replace-with-alias-id")

agent_runtime = boto3.client("bedrock-agent-runtime", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)

def build_agent_prompt(record):
    # summarize sensors for agent
    prompt = (
        f"Sensor reading: farm {record.get('farm_id')}, time {record.get('timestamp')}. "
        f"Soil moisture {record.get('soil_moisture')}%, soil temp {record.get('soil_temperature')}°C, "
        f"air temp {record.get('air_temperature')}°C, humidity {record.get('humidity')}%, rain {record.get('rain_mm')}mm, pH {record.get('ph')}. "
        "As an agronomist, provide a short (<40 words) actionable recommendation for irrigation or fertilizer, and a confidence score 0-100. "
        "Respond in JSON with keys: advice, confidence, reason."
    )
    return prompt

def store_insight(sensor_id, insight):
    key = f"insights/{sensor_id}-{int(__import__('time').time())}.json"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(insight).encode("utf-8"))
    return key

def invoke_agent(prompt, session_id="sim-session"):
    # Invoke AgentCore runtime; API shape may vary — this is a generic example:
    try:
        resp = agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=prompt
        )
        # Response 'completion' may be a stream of events; aggregate text chunks
        text = ""
        for chunk in resp.get("completion", []):
            if "chunk" in chunk and "bytes" in chunk["chunk"]:
                try:
                    text += chunk["chunk"]["bytes"].decode("utf-8")
                except Exception:
                    pass
        # fallback: check resp['output'] or resp structure per SDK docs
        return text.strip()
    except ClientError as e:
        print("Agent invocation failed:", e)
        return None

def lambda_handler(event, context):
    results = []
    for rec in event.get("Records", []):
        # Kinesis record payload is base64; boto already decodes for Lambda event, but event format may differ
        kinesis_data = rec.get("kinesis", {}).get("data")
        try:
            raw = base64.b64decode(kinesis_data).decode("utf-8")
            data = json.loads(raw)
        except Exception:
            # Some Lambda event deliveries already decode data into record['data']
            try:
                data = json.loads(rec.get("body") or "{}")
            except Exception:
                data = {}

        sensor_id = data.get("farm_id", "unknown")
        prompt = build_agent_prompt(data)
        agent_text = invoke_agent(prompt, session_id=f"session-{sensor_id}")
        if not agent_text:
            agent_text = '{"advice":"could not generate","confidence":0,"reason":"invoke failed"}'

        # If agent returned plain text, try to parse JSON; else store raw text
        try:
            parsed = json.loads(agent_text)
        except Exception:
            parsed = {"advice": agent_text, "confidence": None, "reason": ""}

        insight = {
            "sensor": data,
            "insight": parsed,
            "agent_raw": agent_text
        }

        s3_key = store_insight(sensor_id, insight)
        results.append({"s3_key": s3_key, "insight": parsed})

    return {"statusCode": 200, "processed": results}
