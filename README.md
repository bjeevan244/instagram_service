# Instagram Service – Local AWS Simulation (Lambda, S3, API Gateway, DynamoDB)

This is a small demo project that simulates a serverless image upload service using **AWS Lambda**, **API Gateway**, **S3**, and **DynamoDB** — all running locally through **LocalStack** and **Docker**.  
It was built as part of a coding test to demonstrate hands-on knowledge of AWS, Python, and DevOps automation.

---

## What this project does

The app exposes four simple endpoints:

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/upload` | POST | Uploads a base64-encoded image, stores it in S3, and saves metadata in DynamoDB |
| `/list` | GET | Lists all uploaded images |
| `/view/{imageId}` | GET | Returns metadata for a single image |
| `/delete/{imageId}` | DELETE | Removes the image and its metadata |

Everything runs locally — no real AWS account needed.

---

## Prerequisites

Make sure you have these installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Python 3.9+**
- **pip** (comes with Python)
- **LocalStack** and **AWS CLI Local**

Install dependencies:
```bash
pip3 install localstack awscli-local boto3


# Check versions to confirm:

python3 --version
docker --version
localstack --version
awslocal --version

# Start LocalStack
docker-compose up


# Deploy Everything in One Go
All resources (S3, DynamoDB, Lambda, and API Gateway) can be created with one script.

Run this:

chmod +x setup_localstack.sh
./setup_localstack.sh

The script will:

Create an S3 bucket and DynamoDB table

Package and deploy the Lambda

Create API Gateway routes

Connect everything together


Example output:
✅ LocalStack setup complete!
🌍 API Base URL: http://localhost:4566/_aws/execute-api/ngwzal2kc8/dev


# Test the API Endpoints
Once the setup finishes, replace <your_api_id> with the one shown above and try the following requests:

1️⃣ Upload an image:

API_ID=<your_api_id>

curl -X POST http://localhost:4566/_aws/execute-api/$API_ID/dev/upload \
  -H "Content-Type: application/json" \
  -d '{"userId": "u1", "tags": ["test"], "image": "'$(echo -n "hello world" | base64)'"}'

Expected response:
{"message": "Upload success", "imageId": "a2b7e7e1-9813-4f9b-8d6e-682f4bca0e1a"}

2️⃣ List all images
curl -X GET http://localhost:4566/_aws/execute-api/$API_ID/dev/list

3️⃣ View one image
IMAGE_ID=<image_id_from_upload>
curl -X GET http://localhost:4566/_aws/execute-api/$API_ID/dev/view/$IMAGE_ID


4️⃣ Delete an image
curl -X DELETE http://localhost:4566/_aws/execute-api/$API_ID/dev/delete/$IMAGE_ID


| Test                | Action              | Expected Result              |
| ------------------- | ------------------- | ---------------------------- |
| Upload valid data   | POST /upload        | Returns 200 with new imageId |
| Upload invalid data | Missing body        | Returns error                |
| List                | GET /list           | Returns list of images       |
| View valid ID       | GET /view/{id}      | Returns metadata             |
| Delete              | DELETE /delete/{id} | Deletes from S3 & DynamoDB   |


Cleanup
To stop everything:

docker-compose down


To clear all test data:

awslocal s3 rb s3://images-bucket --force
awslocal dynamodb delete-table --table-name images_metadata
awslocal lambda delete-function --function-name imageService

## Running Tests

We use `pytest` to run unit tests and validate API routes and AWS client integrations.

Run all tests:

```bash
pytest



Notes

The Lambda handler automatically routes between /upload, /list, /view, and /delete based on the request path.

The LocalStack service simulates AWS completely offline — perfect for local testing or interviews.

Everything runs in Docker; nothing touches your real AWS account.