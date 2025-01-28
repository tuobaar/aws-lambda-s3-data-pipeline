# AWS Lambda S3 Data Pipeline

This project demonstrates an AWS Lambda-based data pipeline that processes data from an API, filters it using Pandas, and uploads the result to an S3 bucket. The pipeline also sends notifications using AWS SNS to indicate success or failure.

## Features
- **API Integration**: Fetch raw data from an API endpoint.
- **Data Processing**: Use Pandas to filter and format the data.
- **S3 Upload**: Upload the processed data to an Amazon S3 bucket with retry logic.
- **Notifications**: Use AWS SNS for success and failure notifications.
- **Deployment Options**:
  - AWS Lambda with aws and custom layers (Python 3.9).
  - Dockerized deployment (Python 3.11 runtime).

---

## Architecture Overview

1. **Step 1**: Fetch raw data from an API.
2. **Step 2**: Filter and process data using Pandas.
3. **Step 3**: Upload processed data to an S3 bucket.
4. **Step 4**: Send SNS notifications for success or failure.
5. **Step 5**: Monitor execution using AWS CloudWatch Logs and EventBridge.

---

## Requirements
- Python 3.9 or 3.11
- AWS CLI configured with credentials
- Pandas, Requests, Boto3

## Deployment Instructions

### **1. Set Up AWS Resources**
1. **Create an S3 Bucket**:
   - Log in to the AWS Console and create a bucket.
   - Note the bucket name (e.g., `my-data-pipeline-bucket`).

2. **Create an SNS Topic**:
   - Go to the SNS Console and create a topic (e.g., `data-pipeline-notifications`).
   - Subscribe to the topic (e.g., with your email).
   - Copy the Topic ARN (e.g., `arn:aws:sns:region:account-id:topic-name`).

3. **Create IAM Role**:
   - Go to IAM > Roles and create a role for Lambda.
   - Attach the following policies:
     - `AmazonS3FullAccess`
     - `AmazonSNSFullAccess`
     - `AWSLambdaBasicExecutionRole`

---

### **2. Lambda Deployment**

#### Option 1: Using AWS Layers
1. Use AWS-provided layers for **Pandas** and custom layers for other libraries:
   - Add the **Pandas** layer:
     ```plaintext
     arn:aws:lambda:<region>:770693421928:layer:AWSLambda-Pandas:<version>
     ```
   - Create a custom layer for `requests`:
     ```bash
     mkdir requests-layer && cd requests-layer
     pip install requests -t .
     zip -r requests-layer.zip .
     ```
   - Add the layer to your Lambda function.

2. Deploy the function:
   - Upload `main.py` to Lambda via the AWS Console or CLI.

#### Option 2: Docker Deployment
1. **Create a Dockerfile**:
   ```dockerfile
    # Use the Amazon Linux 2 base image with the Lambda runtime for Python 3.11 (or later if needed)
    FROM public.ecr.aws/lambda/python:3.11
    
    # Copy the requirements file to the container
    COPY requirements.txt ${LAMBDA_TASK_ROOT}
    
    # Install dependencies
    RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
    
    # Copy your function code to the container
    COPY main.py ${LAMBDA_TASK_ROOT}
    
    # Command for Lambda to run your handler
    CMD ["main.lambda_handler"]

2. **Build and push the image**:
    ```bash
    docker build -t aws-data-pipeline .
    docker tag aws-data-pipeline:latest <your-account-id>.dkr.ecr.<region>.amazonaws.com/aws-lambda-s3-data-pipeline:latest
    docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/aws-lambda-s3-data-pipeline:latest

3. **Deploy the image to Lambda**:
   - Go to the AWS Lambda Console and choose Container Image during function creation.

## Environment Variables
- Set the following environment variables in AWS Lambda:
  - API_URL: The API endpoint to fetch data.
  - S3_BUCKET: The S3 bucket name.
  - S3_KEY: The object key for the uploaded file (e.g., output/processed_data.txt).
  - SNS_TOPIC_ARN: The ARN of the SNS topic for notifications.

## Testing
1. Trigger the Lambda Function:
    - Manually invoke the Lambda function via the AWS Console or CLI.
2. Check Logs:
   - Monitor logs in AWS CloudWatch.
3. Verify Outputs:
   - Check the S3 bucket for the uploaded file.
   - Confirm receipt of SNS notifications.