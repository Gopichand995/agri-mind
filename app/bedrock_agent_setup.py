# app/bedrock_agent_setup.py
import boto3
import json

client = boto3.client("bedrock-agent", region_name="us-east-1")  # replace with correct service name if differs

def create_agent():
    payload = {
        "agentName": "AgriMindAgent",
        "description": "Agent for AgriMind: reasoning on sensor data to recommend irrigation/fertilizer",
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "instructions": "You are an agronomist. Use sensor context to produce short JSON: {advice, confidence, reason}.",
        "tools": []
    }
    resp = client.create_agent(**payload)
    print("Agent created:", resp)
    # get agentId and aliasId from response
    return resp

if __name__ == "__main__":
    create_agent()
