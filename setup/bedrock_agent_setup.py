import boto3
import json

client = boto3.client("bedrock-agent", region_name="us-east-1")

def create_agent():
    payload = {
        "agentName": "AgriMindAgent",
        "description": "Agent for AgriMind: reasoning on sensor data to recommend irrigation/fertilizer.",
        "instruction": "You are an agronomist. Use sensor data to produce concise JSON with keys: advice, confidence, and reason.",
        "foundationModel": "anthropic.claude-3-haiku-20240307-v1:0",
        "orchestrationType": "DEFAULT",  # optional, use "DEFAULT" unless using custom orchestration
        "idleSessionTTLInSeconds": 300
    }

    response = client.create_agent(**payload)
    print("✅ Agent created successfully!")
    print(json.dumps(response, indent=2, default=str))
    return response

if __name__ == "__main__":
    create_agent()
