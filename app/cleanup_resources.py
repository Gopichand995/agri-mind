# app/cleanup_resources.py
import boto3, time

REGION = "us-east-1"
STREAM_NAME = "agrimind-stream"
BUCKET = "smart-farming-tips"
API_NAME = "agrimind-api"

kinesis = boto3.client("kinesis", region_name=REGION)
s3 = boto3.resource("s3", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)
apigw = boto3.client("apigateway", region_name=REGION)

def delete_kinesis():
    try:
        kinesis.delete_stream(StreamName=STREAM_NAME, EnforceConsumerDeletion=True)
        print("Deleted stream")
    except Exception as e:
        print("Kinesis delete error:", e)

def empty_and_delete_bucket():
    try:
        bucket = s3.Bucket(BUCKET)
        bucket.objects.all().delete()
        bucket.delete()
        print("Deleted bucket")
    except Exception as e:
        print("S3 delete error:", e)

def delete_api_gateway():
    """Find and delete the API Gateway REST API by name."""
    try:
        apis = apigw.get_rest_apis(limit=500)
        target_api = next((api for api in apis["items"] if api["name"] == API_NAME), None)
        if not target_api:
            print(f"⚠️ API Gateway named '{API_NAME}' not found.")
            return
        api_id = target_api["id"]
        apigw.delete_rest_api(restApiId=api_id)
        print(f"✅ Deleted API Gateway: {API_NAME} (ID: {api_id})")
    except Exception as e:
        print("⚠️ API Gateway delete error:", e)

def delete_lambdas():
    """Delete all Lambda functions starting with 'AgriMind' or 'agrimind'."""
    try:
        functions = lambda_client.list_functions(MaxItems=100)["Functions"]
        to_delete = [f for f in functions if f["FunctionName"].lower().startswith("agrimind")]
        if not to_delete:
            print("⚠️ No Lambda functions found with prefix 'AgriMind'.")
            return

        for f in to_delete:
            fn_name = f["FunctionName"]
            lambda_client.delete_function(FunctionName=fn_name)
            print(f"✅ Deleted Lambda function: {fn_name}")

    except Exception as e:
        print("⚠️ Lambda delete error:", e)


if __name__ == "__main__":
    delete_kinesis()
    time.sleep(5)
    empty_and_delete_bucket()
    delete_api_gateway()
    delete_lambdas()
    print("\n✅ Cleanup complete!")
