# AWS Lambda S3 Data Pipeline

This project demonstrates an AWS Lambda-based data pipeline that processes data from an API, filters it using Pandas, uploads the result to an S3 bucket, and sends notifications using AWS SNS  to indicate success or failure.
 This project is fully deployable using AWS Lambda layers or Docker.

---

## Features
- **API Integration**: Fetch raw data from an API endpoint with retry logic.
- **Data Processing**: Use Pandas to filter and format the data.
- **S3 Upload**: Upload the processed data to an Amazon S3 bucket with retry logic.
- **Notifications**: Use AWS SNS for success and failure notifications.
- **Monitoring**: Leverage AWS CloudWatch for logs and EventBridge for scheduled executions.
- **Deployment Options**:
  - AWS Lambda with custom layers (Python 3.9 runtime).
  - Dockerized deployment (Python 3.11 runtime).

---

## Architecture Overview

1. **Step 1**: Fetch raw data from an API.
2. **Step 2**: Filter and process data using Pandas.
3. **Step 3**: Upload processed data to an S3 bucket.
4. **Step 4**: Send SNS notifications for success or failure.
5. **Step 5**: Monitor execution using AWS CloudWatch Logs and EventBridge.

---

## Prerequisite Skills

### **1. AWS Services**
This project assumes prior knowledge of the following AWS services:
- **AWS Lambda**: Creating functions, managing layers, roles, and permissions.
- **Amazon S3**: Creating buckets and managing objects.
- **Amazon SNS**: Creating topics and subscriptions.
- **AWS IAM**: Creating roles and attaching policies.
- **Amazon ECR**: If deploying with Docker, you must know how to create and push images to Amazon ECR.

If you're new to these services, refer to the [AWS Documentation](https://aws.amazon.com/documentation/) for guidance.

### **2. Docker Knowledge (For Containerized Deployment)**
- If you choose to deploy this project using **Docker**, prior experience with Docker is required.
- You should know how to:
  - Build Docker images.
  - Tag and push images to **Amazon ECR**.
  - Deploy containerized applications to **AWS Lambda**.

If you're new to Docker, refer to the [Docker Documentation](https://docs.docker.com/) or other suitable online resources.

#### Despite the above prerequisite skills, the steps provided here are quite exhaustive.

---

## Requirements
- Python 3.9 or 3.11
- Pandas, Requests, Boto3
- AWS CLI configured with credentials

---

## Setting Up AWS CLI

AWS CLI allows you to interact with AWS services via the command line, enabling you to deploy and manage AWS resources efficiently.

### **Step 1: Install AWS CLI**
#### **Mac/Linux (Using Homebrew)**
    ```bash
    brew install awscli
    
#### **Linux**
    ```bash
    pip3 install awscli

#### **Windows**

1. Download the 64-bt MSI installer from [AWS CLI Download link](https://awscli.amazonaws.com/AWSCLIV2.msi).
2. Run the .msi installer and follow the setup instructions.

#### **Verify Installation**
    ```shell
    aws --version

#### **Example Output**:
    ```plaintext
    aws-cli/2.x.x Python/3.x.x Linux/x86_64
    
### **Step 2: Configure AWS CLI with Credentials**
1. Run:
    ```shell
    aws configure

2. Enter the following details:
- AWS Access Key ID: your-access-key
- AWS Secret Access Key: your-secret-key
- Default region name (e.g., eu-north-1 or us-east-1).
- Output format: json (or leave blank).

    #### **Your credentials are now stored in**:
        ```plaintext
        ~/.aws/credentials (Linux/Mac)
        C:\Users\YOUR_USER\.aws\credentials (Windows)

### **Step 3: Test AWS CLI**

##### **Run the following command to list your S3 buckets**:
    ```shell
    aws s3 ls

- If configured correctly, you will see a list of your S3 buckets.
- For more details, see the [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

----

## Deployment Instructions

### **1. AWS Preliminary Setup**
#### a. Create an S3 Bucket
1. Open the **S3 Console** and create a bucket (e.g., `aws-lambda-s3-data-pipeline-bucket`).
2. Note the bucket name. To be used in setting up the environment variables.

#### b. Create an SNS Topic
1. Go to the **SNS Console** and create a topic (e.g., `aws-lambda-s3-data-pipeline-topic`).
2. Subscribe to the topic (e.g., your email).
3. Copy the Topic ARN. To be used in setting up the environment variables.

#### c. Create an IAM Role for Lambda
1. Open the **IAM Console**.
2. Create a role named (e.g., `aws-lambda-s3-data-pipeline-role`) with the following policies:
   - `AmazonS3FullAccess`
   - `AmazonSNSFullAccess`
   - `AWSLambdaBasicExecutionRole`

- You will later attach the created role along with its policies to your Lambda function.
- Alternatively: Note that a 'service-role' is usually or automatically created for your lambda function the first time you create it. Since it will be automatically attached to your lambda function, just make sure to go to the Configuration Tab in your lambda function, Permissions, Set Permissions, Add Policies and then add the above policies to the role.

### **2. Lambda Deployment**

#### Create an AWS Lambda Function

AWS Lambda is the core of this pipeline, where the Python script will execute on a serverless environment. Follow these steps to create and configure the function:

#### Step 1: Create the Lambda Function
1. Go to the AWS Lambda Console. 
2. Click Create function.
3. Choose Author from scratch.
4. Provide a function name (e.g., aws-lambda-s3-data-pipeline).
5. Select Runtime: 
   - Choose Python 3.9 if using AWS Lambda layers (See: Option 1 - below).
   - Choose Python 3.11 (or later) if deploying via Docker (See: Option 2 - below).
6. Under Permissions, select Use an existing role and choose the IAM role created earlier (aws-lambda-s3-data-pipeline-role).
7. Click Create function.

#### Step 2: Upload the Function Code

#### Option 1: Deploy via AWS Layers
##### Step a: Upload a zipped main.py via AWS Console:
   1. In the Code source section, delete the default lambda_function.py file.
   2. Click Upload from → Select .zip file.
   3. Upload your deployment package containing main.py.
   4. Click Deploy.
   5. Alternatively, one can create a new file (main.py) at the Code source section, EXPLORER. Then copy the code(text) from your local main.py to the new main.py

##### Step b: Attach layers to the lambda function:
1. Use AWS-provided layers for the **Pandas** library:
   - At the Function overview of the lambda, click on Layers (or In the Code source section, scroll down to Layers).
   - Click on Add a layer.
   - Under Layer source, AWS Layers choose: AWSSDKPandas-Python39 and choose a version. Click on Add to finish.
   - Alternatively, instead AWS Layers, choose Specify an ARN and enter an ARN of the form:
     ```plaintext
     arn:aws:lambda:<region>:770693421928:layer:AWSLambda-Pandas:<version>
     ```
     ```plaintext
     Example:
     arn:aws:lambda:eu-north-1:336392948345:layer:AWSSDKPandas-Python39:30
     ```
     You can find a complete list of ARNs for specific regions and python runtimes [here](https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html).

2. Use Custom layers for the request library:

   - A zipped package for the requests library is provided in the project directory 'my-lambda-layers/requests_layer.zip'.
   - If needed, create a zipped package for the requests library using the following (or any suitable method):
       ```bash
       mkdir requests-layer && cd requests-layer
       pip install requests -t .
       zip -r requests-layer.zip .
       ```
   - Create a custom layer for the `requests` library:
     - Click on the top left menu (3 horizontal short parallel bars), Layers, Create layer.
     - Alternatively, at the Add a layer section of 1. above, click on the hyperlink 'create a new layer'.
     - Enter a name for the new layer (e.g. requests-layer), choose Python 3.9 under Compatible runtimes.
     - Click on Create/Save.
   - Attach/Add the layer to your Lambda function.
     - At the Function overview of the lambda function, click on Layers (or In the Code source section, scroll down to Layers).
     - Click on Add a layer.
     - Under Layer source, Customer layers choose the **requests-layer** created earlier and select a version.
     - Click on Add to finish.

3. Change the main entry point of your lambda function:
   - AWS Lambda expects the handler function (e.g., lambda_handler) to be in a specific location and referenced as <file_name>.<function_name>. 
   - For example:
   Since your lambda_handler function is in main.py, the handler should be specified as:
      ```plaintext
      main.lambda_handler

#### Option 2: Docker Deployment

1. **Create an Amazon ECR Repository**:
   - Open the AWS Management Console.
   - Navigate to Amazon Elastic Container Registry (ECR).
   - Click Create Repository.
   - Choose Private and enter a name (e.g., aws-lambda-s3-data-pipeline-docker).
   - Copy the repository URI (e.g., 123456789012.dkr.ecr.eu-north-1.amazonaws.com/aws-lambda-s3-data-pipeline-docker).

2. **Authenticate Docker to ECR**:
   ```bash
   aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<your-region>.amazonaws.com
   ```
   - Example for eu-north-1:
   ```bash
   aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.eu-north-1.amazonaws.com
   ```
3. **Create a Dockerfile (if needed)**:
   - A Dockerfile is already provided. If needed, create a new file with the following content and save as Dockerfile.
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
    ```
4. **Build the docker image**:
    ```bash
    docker build -t aws-lambda-s3-data-pipeline .

5. **Tag the image for ECR**:    
   ```bash 
   docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/aws-lambda-s3-data-pipeline-docker:latest
   ```
   - Example:
   ```bash
   docker tag aws-lambda-s3-data-pipeline-docker:latest 123456789012.dkr.ecr.eu-north-1.amazonaws.com/aws-lambda-s3-data-pipeline-docker:latest

6. **Push the Image to ECR**:
   ```bash
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/aws-lambda-s3-data-pipeline-docker:latest
   ```
   - Example:
   ```bash
   docker push 123456789012.dkr.ecr.eu-north-1.amazonaws.com/aws-lambda-s3-data-pipeline-docker:latest

7. **Deploy the docker image to AWS Lambda**:
   - Go to the AWS Lambda Console.
   - Create a new function.
   - Choose Container Image as the deployment package.
   - Enter (paste) the ECR image URI you copied in Option 2, step 1.
   - Or in previous step, click on Browse images and select the desired Amazon ECR Image Repository (e.g. aws-lambda-s3-data-pipeline-docker) and Image.
   - Click on Save.

---

## Configure Environment Variables
Set the following environment variables in AWS Lambda:
1. Navigate to the Configuration tab.
2. Select Environment Variables → Click Edit → Add environment variable.
3. Add the following key-value pairs. (Ignore the descriptions in parentheses.):

    | Key    | Value                                                                                                                       |
    |--------|-----------------------------------------------------------------------------------------------------------------------------|
    | `API_URL` | `https://fakestoreapi.com/products (The API endpoint to fetch data.)`                                                       |
    | `S3_BUCKET` | `aws-lambda-s3-data-pipeline-bucket (The S3 bucket name.)`                                                                  |
    | `S3_KEY`     | `processed/processed_data.txt (The object key for the uploaded file.)`                                                      |
    | `SNS_TOPIC_ARN`| `arn:aws:sns:<region>:<account-id>:aws-lambda-s3-data-pipeline-topic (The ARN of the SNS topic for notifications.)` |
 
## Grant the IAM Role SNS Publish Permissions
You need to attach a policy to the IAM role that explicitly allows the sns:Publish action on the specific SNS topic.
1. Identify the Lambda Execution Role
   1. Open the AWS Lambda Console.
   2. Navigate to your Lambda function.
   3. Go to the Configuration tab > Permissions.
   4. Note the execution role name: (e.g. aws-lambda-s3-data-pipeline-docker-role...).

2. Update the IAM Role Policy
   1. Open the IAM Console: https://console.aws.amazon.com/iam/.
   2. Go to Roles and search for aws-s3-data-pipeline-docker-role-rm1h3y7m.
   3. Select the role and go to the Permissions tab.
   4. Click Add permissions > Create inline policy.
   5. Choose the JSON editor and paste the following policy:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sns:Publish",
                "Resource": "arn:aws:sns:<region>:<account-id>:aws-lambda-s3-data-pipeline-topic"
            }
        ]
    }
    ```
   6. Save the policy with a name like AllowSNSPublish.


## Set Up a Test Event
1. In AWS lambda, navigate to the Test tab.
2. Click Create new test event.
3. Enter an event name (e.g., test-run).
4. Use the following JSON payload:
    ```json
    {
      "test": "lambda execution"
    }
5. Click Save.

## Test the Lambda Function
1. Click Test to manually trigger the function.
2. Check CloudWatch Logs to verify the execution:
   - Go to Amazon CloudWatch Console.
   - Navigate to Log Groups → Find /aws/lambda/aws-lambda-s3-data-pipeline.
   - Click the latest log stream to review execution logs.
3. Verify Outputs:
   - Check the S3 bucket for the uploaded file.
   - Confirm receipt of SNS notifications.
     - Failure notification email for failed runs/tests.
     - Success notification emails for successful runs/tests.

## Automating Scheduled Runs with EventBridge

To schedule automatic executions of this Lambda function, AWS **EventBridge** can be used to trigger the function at predefined intervals.

### **How to Set Up an EventBridge Rule for Scheduling Runs**
1. **Go to AWS EventBridge Console**.
2. Click **Create Rule**.
3. Provide a name, e.g., `aws-lamda-s3-data-pipeline-schedule`.
4. Select **Event Source** → Choose **Schedule**.
5. Under **Schedule pattern**, define the execution interval:
   - **Every 1 hour**: `rate(1 hour)`
   - **Every day at midnight**: `cron(0 0 * * ? *)`
6. Select **Target** → Choose **AWS Lambda**.
7. Select the **Lambda function** you deployed.
8. Click **Create**.

### **Testing the Scheduled Event**
- Check **AWS CloudWatch Logs** to confirm that the function runs at the scheduled time.
- If needed, modify the schedule later under **EventBridge → Rules**.

For more details, refer to the [AWS EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html).


## Future Improvements
- Use AWS Secrets Manager to securely manage sensitive credentials.
- Automate deployments using CI/CD pipelines with AWS CodePipeline or GitHub Actions.
