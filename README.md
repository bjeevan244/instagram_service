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