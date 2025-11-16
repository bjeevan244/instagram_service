import json
import base64
import pytest
from app.routes import upload_image, list_images, view_image, delete_image
from app.aws_clients import get_dynamo_table, get_s3_client
from app.config import S3_BUCKET

@pytest.fixture
def sample_image():
    """Returns a base64-encoded sample image."""
    return base64.b64encode(b"Hello World").decode("utf-8")


@pytest.fixture
def setup_s3_dynamo():
    """Clean S3 bucket and DynamoDB table before each test."""
    s3 = get_s3_client()
    table = get_dynamo_table()

    # Remove all S3 objects
    objects = s3.list_objects_v2(Bucket=S3_BUCKET).get("Contents", [])
    for obj in objects:
        s3.delete_object(Bucket=S3_BUCKET, Key=obj["Key"])

    # Remove all items from DynamoDB table
    items = table.scan().get("Items", [])
    for item in items:
        table.delete_item(Key={"imageId": item["imageId"]})

    return s3, table


def test_upload_image(sample_image, setup_s3_dynamo):
    s3, table = setup_s3_dynamo

    event = {
        "httpMethod": "POST",
        "path": "/upload",
        "body": json.dumps({
            "userId": "u1",
            "tags": ["test", "demo"],
            "image": sample_image
        })
    }

    response = upload_image(event)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert "imageId" in body

    # Check DynamoDB item
    item = table.get_item(Key={"imageId": body["imageId"]}).get("Item")
    assert item is not None
    assert item["userId"] == "u1"

    # Check S3 object exists
    s3_key = item["s3Key"]
    s3.head_object(Bucket=S3_BUCKET, Key=s3_key)  # raises if object does not exist


def test_list_images(sample_image, setup_s3_dynamo):
    s3, table = setup_s3_dynamo

    # Upload two images
    for i in range(2):
        upload_image({
            "httpMethod": "POST",
            "path": "/upload",
            "body": json.dumps({
                "userId": "u1" if i == 0 else "u2",
                "tags": ["test"],
                "image": sample_image
            })
        })

    # List without filters
    event = {"httpMethod": "GET", "path": "/list", "queryStringParameters": None}
    response = list_images(event)
    items = json.loads(response["body"])
    assert len(items) == 2

    # List filtered by userId
    event["queryStringParameters"] = {"userId": "u1"}
    response = list_images(event)
    items = json.loads(response["body"])
    assert all(i["userId"] == "u1" for i in items)


def test_view_image(sample_image, setup_s3_dynamo):
    s3, table = setup_s3_dynamo

    # Upload image
    upload_resp = upload_image({
        "httpMethod": "POST",
        "path": "/upload",
        "body": json.dumps({
            "userId": "u1",
            "tags": ["test"],
            "image": sample_image
        })
    })
    image_id = json.loads(upload_resp["body"])["imageId"]

    # View image
    event = {
        "httpMethod": "GET",
        "path": f"/view/{image_id}",
        "pathParameters": {"imageId": image_id}
    }
    response = view_image(event)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert "url" in body


def test_delete_image(sample_image, setup_s3_dynamo):
    s3, table = setup_s3_dynamo

    # Upload image
    upload_resp = upload_image({
        "httpMethod": "POST",
        "path": "/upload",
        "body": json.dumps({
            "userId": "u1",
            "tags": ["test"],
            "image": sample_image
        })
    })
    image_id = json.loads(upload_resp["body"])["imageId"]

    # Delete image
    event = {
        "httpMethod": "DELETE",
        "path": f"/delete/{image_id}",
        "pathParameters": {"imageId": image_id}
    }
    response = delete_image(event)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["message"] == "Deleted successfully"

    # Verify removal from DynamoDB
    item = table.get_item(Key={"imageId": image_id}).get("Item")
    assert item is None
