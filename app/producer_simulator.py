# app/producer_simulator.py
import boto3, json, time, random
from datetime import datetime

STREAM_NAME = "agrimind-stream"   # adjust to CloudFormation-created stream name
REGION = "us-east-1"

kinesis = boto3.client("kinesis", region_name=REGION)

def generate_record(farm_id="FARM_1"):
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "farm_id": farm_id,
        "soil_moisture": round(random.uniform(10, 60),2),  # percent
        "soil_temperature": round(random.uniform(15,35),2),
        "air_temperature": round(random.uniform(20,38),2),
        "humidity": round(random.uniform(30,90),2),
        "rain_mm": round(random.uniform(0,20),2),
        "ph": round(random.uniform(5.5,7.5),2)
    }

def send_record(record):
    kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(record),
        PartitionKey=record["farm_id"]
    )

if __name__ == "__main__":
    # Demo: send 6 events every 10 seconds (short run to save cost)
    for i in range(1):
        rec = generate_record(f"FARM_{random.randint(1,3)}")
        print("Sending:", rec)
        send_record(rec)
        time.sleep(10)
