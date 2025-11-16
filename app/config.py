# app/config.py

import os

AWS_REGION = "us-east-1"
S3_BUCKET = os.getenv("S3_BUCKET", "images-bucket")
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE", "images_metadata")

# LocalStack endpoint
USE_LOCALSTACK = os.getenv("TEST_MODE") != "true"
AWS_ENDPOINT = "http://localstack:4566" if USE_LOCALSTACK else None
