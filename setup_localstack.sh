#!/bin/bash
set -e

echo "Starting LocalStack setup for Instagram Service..."

# Configuration
AWS_REGION="us-east-1"
FUNCTION_NAME="imageService"
ZIP_FILE="lambda.zip"
BUCKET_NAME="images-bucket"
TABLE_NAME="images_metadata"
API_NAME="ImageServiceAPI"

export AWS_REGION=$AWS_REGION
export AWS_DEFAULT_REGION=$AWS_REGION

# Delete old resources if they exist
echo "Deleting old resources if they exist..."
awslocal s3 rb s3://$BUCKET_NAME --force || true
awslocal dynamodb delete-table --table-name $TABLE_NAME || true
awslocal lambda delete-function --function-name $FUNCTION_NAME || true
echo "Old resources deleted"


# Create S3 bucket
echo "Creating S3 bucket..."
awslocal s3 mb s3://$BUCKET_NAME || true

# Create DynamoDB table
echo "Creating DynamoDB table..."
awslocal dynamodb create-table \
  --table-name $TABLE_NAME \
  --attribute-definitions AttributeName=imageId,AttributeType=S \
  --key-schema AttributeName=imageId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST || true

# Package Lambda
echo "Packaging Lambda..."
cd app
zip -r ../$ZIP_FILE . >/dev/null
cd ..

# Create or update Lambda function
if awslocal lambda get-function --function-name $FUNCTION_NAME >/dev/null 2>&1; then
  echo "Updating existing Lambda..."
  awslocal lambda update-function-code --function-name $FUNCTION_NAME --zip-file fileb://$ZIP_FILE >/dev/null
else
  echo "Creating new Lambda..."
  awslocal lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.9 \
    --handler handler.lambda_handler \
    --zip-file fileb://$ZIP_FILE \
    --role arn:aws:iam::000000000000:role/lambda-role >/dev/null
fi

# Create API Gateway
echo "Creating API Gateway..."
API_ID=$(awslocal apigateway create-rest-api --name "$API_NAME" --query 'id' --output text)
ROOT_ID=$(awslocal apigateway get-resources --rest-api-id $API_ID --query 'items[0].id' --output text)
LAMBDA_ARN=$(awslocal lambda list-functions --query "Functions[?FunctionName=='$FUNCTION_NAME'].FunctionArn" --output text)

# Helper function
create_resource() {
  local path_part=$1
  local method=$2
  local parent_id=$3
  RESOURCE_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $parent_id --path-part $path_part --query 'id' --output text)
  awslocal apigateway put-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method $method --authorization-type "NONE"
  awslocal apigateway put-integration --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method $method \
    --type AWS_PROXY --integration-http-method POST \
    --uri arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations
  echo $RESOURCE_ID
}

# /upload
create_resource "upload" "POST" $ROOT_ID >/dev/null

# /list
create_resource "list" "GET" $ROOT_ID >/dev/null

# /view/{imageId}
VIEW_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part view --query 'id' --output text)
VIEW_PARAM_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $VIEW_ID --path-part '{imageId}' --query 'id' --output text)
awslocal apigateway put-method --rest-api-id $API_ID --resource-id $VIEW_PARAM_ID --http-method GET --authorization-type "NONE"
awslocal apigateway put-integration --rest-api-id $API_ID --resource-id $VIEW_PARAM_ID --http-method GET \
  --type AWS_PROXY --integration-http-method POST \
  --uri arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations

# /delete/{imageId}
DEL_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part delete --query 'id' --output text)
DEL_PARAM_ID=$(awslocal apigateway create-resource --rest-api-id $API_ID --parent-id $DEL_ID --path-part '{imageId}' --query 'id' --output text)
awslocal apigateway put-method --rest-api-id $API_ID --resource-id $DEL_PARAM_ID --http-method DELETE --authorization-type "NONE"
awslocal apigateway put-integration --rest-api-id $API_ID --resource-id $DEL_PARAM_ID --http-method DELETE \
  --type AWS_PROXY --integration-http-method POST \
  --uri arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations

# Deploy API
awslocal apigateway create-deployment --rest-api-id $API_ID --stage-name dev >/dev/null

# Print endpoints
echo ""
echo "LocalStack setup complete!"
echo "API Base URL: http://localhost:4566/_aws/execute-api/$API_ID/dev"
echo ""
EXAMPLE_IMAGE_ID="<imageId>"

echo "Try test upload:"
echo "curl -X POST http://localhost:4566/_aws/execute-api/$API_ID/dev/upload \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"userId\":\"u1\",\"tags\":[\"test\"],\"image\":\"'$(echo -n 'hello world' | base64)'\"}'"
echo ""
echo "List all images for a user:"
echo "curl -X GET 'http://localhost:4566/_aws/execute-api/$API_ID/dev/list'"
echo ""
echo "List images filter:"
echo "curl -X GET 'http://localhost:4566/_aws/execute-api/$API_ID/dev/list?userId=u1'"
echo ""
echo "View a specific image (replace <imageId> with actual id from upload response):"
echo "curl -X GET 'http://localhost:4566/_aws/execute-api/$API_ID/dev/view/$EXAMPLE_IMAGE_ID'"
echo ""
echo "Delete a specific image (replace <imageId> with actual id from upload response):"
echo "curl -X DELETE 'http://localhost:4566/_aws/execute-api/$API_ID/dev/delete/$EXAMPLE_IMAGE_ID'"
echo ""