# app/routes.py
import json
import base64
import uuid
from datetime import datetime

from aws_clients import get_s3_client, get_dynamo_table
from config import S3_BUCKET

def upload_image(event):
    s3 = get_s3_client()
    table = get_dynamo_table()

    try:
        body = json.loads(event.get("body", "{}"))
        image_data = base64.b64decode(body["image"])
        user_id = body["userId"]
        tags = body.get("tags", [])
    except Exception:
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid input"})}

    image_id = str(uuid.uuid4())
    file_key = f"{user_id}/{image_id}.jpg"

    s3.put_object(Bucket=S3_BUCKET, Key=file_key, Body=image_data)

    metadata = {
        "imageId": image_id,
        "userId": user_id,
        "tags": tags,
        "createdAt": datetime.utcnow().isoformat(),
        "s3Key": file_key,
    }
    table.put_item(Item=metadata)

    return {"statusCode": 200, "body": json.dumps({"message": "Upload success", "imageId": image_id})}


def list_images(event):
    table = get_dynamo_table()

    params = event.get("queryStringParameters") or {}
    user_id = params.get("userId")
    tag = params.get("tag")

    res = table.scan()
    items = res.get("Items", [])

    if user_id:
        items = [i for i in items if i["userId"] == user_id]
    if tag:
        items = [i for i in items if tag in i.get("tags", [])]

    return {"statusCode": 200, "body": json.dumps(items)}


def view_image(event):
    s3 = get_s3_client()
    table = get_dynamo_table()

    image_id = event.get("pathParameters", {}).get("imageId")
    if not image_id:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing imageId"})}

    item = table.get_item(Key={"imageId": image_id}).get("Item")
    if not item:
        return {"statusCode": 404, "body": json.dumps({"message": "Image not found"})}

    file_key = item["s3Key"]
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": file_key},
        ExpiresIn=3600,
    )
    return {"statusCode": 200, "body": json.dumps({"url": url})}


def delete_image(event):
    s3 = get_s3_client()
    table = get_dynamo_table()

    image_id = event.get("pathParameters", {}).get("imageId")
    if not image_id:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing imageId"})}

    item = table.get_item(Key={"imageId": image_id}).get("Item")
    if not item:
        return {"statusCode": 404, "body": json.dumps({"message": "Image not found"})}

    s3.delete_object(Bucket=S3_BUCKET, Key=item["s3Key"])
    table.delete_item(Key={"imageId": image_id})
    return {"statusCode": 200, "body": json.dumps({"message": "Deleted successfully"})}
