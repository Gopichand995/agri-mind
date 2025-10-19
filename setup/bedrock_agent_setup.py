import boto3
import json
import time

REGION = "us-east-1"
AGENT_NAME = "AgriMindAgent"
FOUNDATION_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"

# Initialize client for Bedrock AgentCore
client = boto3.client("bedrock-agent", region_name=REGION)

def create_agent():
    print("🚀 Creating Bedrock AgentCore agent...")

    response = client.create_agent(
        agentName=AGENT_NAME,
        description="Autonomous agent for AgriMind: analyzes IoT sensor data and recommends irrigation/fertilizer strategy.",
        instruction="You are an agronomist. Read soil, weather, and sensor context to produce a concise JSON with keys: advice, confidence, reason.",
        foundationModel=FOUNDATION_MODEL,
        agentResourceRoleArn="arn:aws:iam::906510885130:role/BedrockAgentExecutionRole",
        orchestrationType="DEFAULT",
        idleSessionTTLInSeconds=300,
    )

    agent_id = response["agent"]["agentId"]
    print(f"✅ Agent created successfully with ID: {agent_id}")
    return agent_id


def create_alias(agent_id):
    print("🔗 Creating alias for agent...")
    alias_name = "v1"
    response = client.create_agent_alias(
        agentId=agent_id,
        agentAliasName=alias_name,
        description="Primary alias for AgriMind Agent (v1)"
    )

    alias_id = response["agentAlias"]["agentAliasId"]
    print(f"✅ Alias created successfully with ID: {alias_id}")
    return alias_id


def deploy_agent(agent_id):
    """Deploys the agent to make it ready for invocation"""
    print("⚙️ Deploying agent...")
    deploy_resp = client.prepare_agent(agentId=agent_id)
    print(f"🟢 Agent deployment started. Version: {deploy_resp['agentVersion']}")
    return deploy_resp


if __name__ == "__main__":
    agent_id = create_agent()
    time.sleep(3)
    deploy_agent(agent_id)
    time.sleep(3)
    alias_id = create_alias(agent_id)

    result = {"agentId": agent_id, "aliasId": alias_id}
    print("\n✅ Final Agent Details:")
    print(json.dumps(result, indent=2))
    # Optionally store locally
    with open("agent_details.json", "w") as f:
        json.dump(result, f, indent=2)
    print("📝 Saved agent details to agent_details.json")
