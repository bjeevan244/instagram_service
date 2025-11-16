# app/handler.py
import json
import logging
from routes import upload_image, list_images, view_image, delete_image

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context=None):
    """Main Lambda entry point routing API Gateway requests."""
    path = event.get("path", "")
    method = event.get("httpMethod", "").upper()
    logger.info(f"Received {method} {path}")

    if path.endswith("/upload") and method == "POST":
        return upload_image(event)
    elif path.endswith("/list") and method == "GET":
        return list_images(event)
    elif "/view/" in path and method == "GET":
        return view_image(event)
    elif "/delete/" in path and method == "DELETE":
        return delete_image(event)
    else:
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid route"})}
