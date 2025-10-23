import streamlit as st
import boto3
import json
import time
import datetime

# --- AWS Kinesis setup ---
STREAM_NAME = "test-stream"
kinesis = boto3.client("kinesis")

# --- Functions ---
def send_event(user_id: str, action: str):
    event = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    resp = kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(event),
        PartitionKey=user_id
    )
    return event, resp["SequenceNumber"]

def read_from_stream(limit=10):
    desc = kinesis.describe_stream(StreamName=STREAM_NAME)
    shard_id = desc["StreamDescription"]["Shards"][0]["ShardId"]

    shard_it = kinesis.get_shard_iterator(
        StreamName=STREAM_NAME,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON"
    )["ShardIterator"]

    records = []
    out = kinesis.get_records(ShardIterator=shard_it, Limit=limit)
    for rec in out["Records"]:
        data = json.loads(rec["Data"])
        records.append(data)
    return records

# --- Streamlit UI ---
st.set_page_config(page_title="Kinesis Test Dashboard", layout="wide")
st.title("🚀 AWS Kinesis Data Stream - Test Dashboard")

col1, col2 = st.columns(2)

# --- Producer side ---
with col1:
    st.subheader("📤 Send Data to Kinesis")
    user_id = st.text_input("User ID", "user1")
    action = st.text_input("Action", "login")
    if st.button("Send Event"):
        event, seq = send_event(user_id, action)
        st.success(f"Sent event: {event}\nSequence: {seq}")

# --- Consumer side ---
with col2:
    st.subheader("📥 Live Data from Stream")
    refresh_rate = st.slider("Refresh every (sec)", 2, 10, 3)
    placeholder = st.empty()

    if st.button("Start Live View"):
        st.info("Streaming live data...")
        while True:
            data = read_from_stream()
            placeholder.table(data)
            time.sleep(refresh_rate)
