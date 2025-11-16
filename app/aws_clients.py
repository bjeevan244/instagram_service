# aws_clients.py
import boto3
from config import AWS_ENDPOINT, AWS_REGION, DYNAMO_TABLE

def get_s3_client():
    if AWS_ENDPOINT:
        return boto3.client("s3", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)
    return boto3.client("s3", region_name=AWS_REGION)

def get_dynamo_table():
    resource = boto3.resource("dynamodb", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION) if AWS_ENDPOINT else boto3.resource("dynamodb", region_name=AWS_REGION)
    return resource.Table(DYNAMO_TABLE)

