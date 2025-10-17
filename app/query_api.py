# app/query_api.py
import json
import boto3
import os
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "agri-mind-prototype-bucket-<YOUR_SUFFIX>")
AGENT_ID = os.environ.get("AGENT_ID", "replace-with-agent-id")
AGENT_ALIAS_ID = os.environ.get("AGENT_ALIAS_ID", "replace-with-alias-id")

s3 = boto3.client("s3", region_name=REGION)
agent_runtime = boto3.client("bedrock-agent-runtime", region_name=REGION)

def invoke_agent_text(question, session_id="web-session"):
    resp = agent_runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=question
    )
    text = ""
    for chunk in resp.get("completion", []):
        if "chunk" in chunk and "bytes" in chunk["chunk"]:
            try:
                text += chunk["chunk"]["bytes"].decode("utf-8")
            except:
                pass
    return text.strip()

def get_latest_insight(sensor_id):
    # List objects prefixed by sensor and pick latest (simple approach)
    try:
        prefix = f"insights/{sensor_id}"
        resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        items = resp.get("Contents", [])
        if not items:
            return None
        latest = sorted(items, key=lambda x: x["LastModified"], reverse=True)[0]
        obj = s3.get_object(Bucket=S3_BUCKET, Key=latest["Key"])
        return json.loads(obj["Body"].read().decode("utf-8"))
    except ClientError as e:
        return None

def lambda_handler(event, context):
    method = event.get("httpMethod", "GET")
    if method == "POST":
        body = json.loads(event.get("body", "{}"))
        question = body.get("question", "Provide general farm advice")
        agent_resp = invoke_agent_text(question, session_id="ui-session")
        return {
            "statusCode": 200,
            "body": json.dumps({"response": agent_resp})
        }
    else:
        qs = event.get("queryStringParameters") or {}
        sensor = qs.get("sensor_id", "FARM_1")
        insight = get_latest_insight(sensor)
        if insight:
            return {"statusCode": 200, "body": json.dumps(insight)}
        else:
            return {"statusCode": 404, "body": json.dumps({"error":"no insight"})}
