#!/bin/bash
set -e
STACK="agrimind-prototype"
REGION="us-east-1"
BUCKET="smart-farming-tips"

echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file infra/template.yaml \
  --stack-name $STACK \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides Prefix=agrimind S3BucketName=$BUCKET \
  --region $REGION

echo "Zipping Lambdas..."
cd app
zip -r ../consumer.zip kinesis_consumer.py requirements.txt
zip -r ../query.zip query_api.py requirements.txt
cd ..

echo "Updating Lambda functions..."
aws lambda update-function-code --function-name agrimind-kinesis-consumer --zip-file fileb://consumer.zip --region $REGION
aws lambda update-function-code --function-name agrimind-query --zip-file fileb://query.zip --region $REGION

echo "Deployment completed."
