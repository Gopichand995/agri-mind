# 🌾 AgriMind Prototype – AgentCore + Kinesis Integration

An AWS-powered smart agriculture demo using **AgentCore (Bedrock Agents)**, **Kinesis Data Streams**, and **Lambda** for real-time reasoning from IoT weather & soil sensors.

---

## ⚙️ Architecture Overview

**Flow:**
IoT Sensors → Kinesis Stream → Lambda Consumer → AgentCore (Bedrock) → S3 + API Gateway

**Key Components**
- **Amazon Kinesis:** Streams sensor data in near real-time.  
- **AWS Lambda:** Processes data and invokes AgentCore reasoning.  
- **Amazon Bedrock (AgentCore):** Provides LLM-driven agricultural insights.  
- **Amazon API Gateway:** Exposes REST API for querying agent insights.  
- **Amazon S3:** Stores agent responses & logs.

---

## 🧭 Deployment & Testing Steps

### 1. Set Region
Use **us-east-1** (required for Bedrock & AgentCore).

```bash
aws configure set region us-east-1
```

---

### 2. Deploy CloudFormation Stack
Creates stream, S3 bucket, IAM roles, Lambdas, and API Gateway.

```bash
aws cloudformation deploy   --template-file infra/template.yaml   --stack-name agrimind-prototype   --parameter-overrides Prefix=agrimind S3BucketName=<your-unique-bucket-name>
```

---

### 3. Upload Lambda Code
Package and upload your application code:

```bash
cd app/
zip -r consumer.zip consumer/
zip -r query.zip query/

aws lambda update-function-code --function-name agrimind-consumer --zip-file fileb://consumer.zip
aws lambda update-function-code --function-name agrimind-query --zip-file fileb://query.zip
```

Alternatively, deploy via **AWS SAM** or **Serverless Framework**.

---

### 4. Configure AgentCore
Create an Agent in **Bedrock Console** or via script:

```bash
python setup/bedrock_agent_setup.py
```

Note:
- `AGENT_ID`
- `AGENT_ALIAS_ID`

Set as environment variables in both Lambda functions:
```
S3_BUCKET=<your-bucket>
AGENT_ID=<your-agent-id>
AGENT_ALIAS_ID=<your-alias-id>
AWS_REGION=us-east-1
```

---

### 5. Connect Kinesis to Lambda
Attach the Kinesis stream trigger to the **consumer Lambda** (CloudFormation usually handles this).

If needed manually:
```bash
aws lambda create-event-source-mapping   --function-name agrimind-consumer   --event-source-arn arn:aws:kinesis:us-east-1:<account-id>:stream/agrimind-stream   --starting-position LATEST
```

---

### 6. Test Streaming Pipeline
Simulate IoT sensor data:
```bash
python app/producer_simulator.py
```

Monitor logs:
```bash
aws logs tail /aws/lambda/agrimind-consumer --follow
```
✅ You should see Kinesis events processed and AgentCore responses written to S3.

---

### 7. Query the Agent
Use the deployed **API Gateway** endpoint.

**POST Query:**
```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/query   -H "Content-Type: application/json"   -d '{"question":"What should I do for soil moisture 22%?"}'
```

**GET Insight:**
```bash
curl "https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/query"
```

---

### 8. Cleanup (Avoid Costs)
After testing:
```bash
python app/cleanup_resources.py
aws cloudformation delete-stack --stack-name agrimind-prototype
```

---

## 💸 Cost Optimization
| Service | Usage | Est. Monthly Cost |
|----------|--------|------------------|
| Kinesis (1 shard) | Light test | $12–15 |
| Lambda (100K exec) | Free-tier | <$1 |
| API Gateway | 50K calls | $2–3 |
| Bedrock (Claude 3 Haiku) | 1K prompts | $2–5 |
| **Total (Testing)** |  | **~$20–25/month** |

Use **hourly or on-demand updates** and **delete inactive resources** to stay within free-tier.

---

## 🧪 Safe Testing Tips
- Simulate data using `producer_simulator.py` or **Kinesis Data Generator**.  
- Start with **1 shard** only.  
- Use **Claude 3 Haiku** for cost-effective reasoning.  
- Monitor logs and delete stack post-demo.

---

## 📦 Folder Structure

```
agrimind/
├── app/
│   ├── producer_simulator.py
│   ├── consumer/
│   ├── query/
│   ├── cleanup_resources.py
├── infra/
│   └── template.yaml
├── setup/
│   └── bedrock_agent_setup.py
└── README.md
```

---

## 🧠 Summary

AgriMind demonstrates **real-time AI reasoning on live IoT streams**, combining:
- **Kinesis streaming ingestion**
- **AgentCore for LLM reasoning**
- **Lambda + API Gateway orchestration**

Ideal for precision agriculture, sustainability monitoring, and predictive farming.
