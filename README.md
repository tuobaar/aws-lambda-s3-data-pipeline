# AWS Lambda S3 Data Pipeline

This project demonstrates an AWS Lambda-based data pipeline that:
- **Fetches** data from an API with retry logic.
- **Processes** data using Pandas.
- **Uploads** the results to an Amazon S3 bucket.
- **Sends notifications** via AWS SNS upon success or failure.

The project can be deployed using:
- **AWS Lambda Layers** (Python 3.9 runtime)
- **Dockerized AWS Lambda Deployment** (Python 3.11 runtime)

---

## **Features**
- **API Integration**: Fetch raw data from an API endpoint.
- **Data Processing**: Use Pandas to filter and format the data.
- **S3 Upload**: Upload the processed data to an S3 bucket with retry logic.
- **Notifications**: Use AWS SNS for success and failure alerts.
- **Monitoring**: AWS CloudWatch for logs, AWS EventBridge for scheduling.

---

## **Architecture Overview**
1. **Step 1**: Fetch raw data from an API.
2. **Step 2**: Process and filter data using Pandas.
3. **Step 3**: Upload processed data to S3.
4. **Step 4**: Send SNS notifications for success or failure.
5. **Step 5**: Monitor execution with AWS CloudWatch and EventBridge.

---

## **Prerequisite Skills**
### **1. AWS Knowledge**
This project assumes prior experience with:
- **AWS Lambda** (creating functions, managing layers, roles, permissions)
- **Amazon S3** (creating buckets, managing objects)
- **Amazon SNS** (creating topics, subscriptions)
- **AWS IAM** (creating roles, attaching policies)
- **Amazon ECR** (for Docker deployment)

For more information, see the [AWS Documentation](https://aws.amazon.com/documentation/).

### **2. Docker Knowledge (For Containerized Deployment)**
- If deploying via Docker, you should know how to:
  - Build Docker images.
  - Push images to **Amazon ECR**.
  - Deploy containerized applications to **AWS Lambda**.

For more information, refer to the [Docker Documentation](https://docs.docker.com/).

Despite the above prerequisite skills, this readme is quite exhaustive.

---

## **Requirements**
- Python 3.9 or 3.11
- Pandas, Requests, Boto3
- AWS CLI (configured with credentials)

---

## **Fetch Project Files**
1. Clone the repository (or download ZIP):
    ```bash
    git clone https://github.com/tuobaar/aws-lambda-s3-data-pipeline
    ```
2. Continue the rest of the steps in the AWS cloud environment.

---

## **Installing & Configuring AWS CLI**
AWS CLI allows you to manage AWS services from the command line.

### **Step 1: Install AWS CLI**
#### **Mac/Linux (Using Homebrew)**
```bash
brew install awscli
```
#### **Linux (Using pip)**
```bash
brew install awscli
```
#### **Windows**
1. Download the [AWS CLI Installer](https://awscli.amazonaws.com/AWSCLIV2.msi).
2. Run the .msi installer and follow the instructions.

#### **Verify Installation**
```bash
aws --version
```
#### **Example output**:
```plaintext
aws-cli/2.x.x Python/3.x.x Linux/x86_64
```

### **Step 2: Configure AWS CLI**
You should already have your security credentials. Otherwise, go to Identity and Access Management (IAM) and generate your Access Key and Secret Access Key. 
```bash
aws configure
```
#### **Enter the following details**:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., us-east-1, eu-north-1)
- Output format (json, or leave blank)

#### **Your credentials are stored in**:

```plaintext
~/.aws/credentials (Linux/Mac)
C:\Users\YOUR_USER\.aws\credentials (Windows)
```

### **Step 3: Test AWS CLI**
```bash
aws s3 ls
```
- If configured correctly, this will list your S3 buckets.
- For more details, see the [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

---

## **Deployment Instructions**

### **1. AWS Setup**

#### **a. Create an S3 Bucket**:
1. Open AWS S3 Console → Click Create Bucket.
2. Enter a unique name (e.g., aws-lambda-s3-data-pipeline-bucket).
3. Note the bucket name for later.

#### **b. Create an SNS Topic**:
1. Go to AWS SNS Console → Click Create Topic.
2. Enter a name (e.g., aws-lambda-s3-data-pipeline-topic).
3. Subscribe to the topic with your email.
4. Copy the Topic ARN for later use.

#### **c. Create an IAM Role for Lambda**:
1. Open AWS IAM Console → Click Roles → Create Role. 
2. Enter a name (e.g., aws-lambda-s3-data-pipeline-role).
3. Attach the following policies:
   - `AmazonS3FullAccess`
   - `AmazonSNSFullAccess`
   - `AWSLambdaBasicExecutionRole`
4. Copy the role ARN for later use.
- NOTE: 
```plaintext
A 'service-role' is automatically attached to your lambda function the first time you create it. If that is the case, just make sure to go to the Configuration tab in your lambda function, Permissions, Set Permissions, Add Policies and then ensure that the above policies are added if absent.
```


### **2. Deploying AWS Lambda Function**

AWS Lambda is the core of this pipeline, where the Python script will execute on a serverless environment. Follow these steps to create and configure the function:

#### **Option 1: AWS Lambda Layers (Python 3.9)**:
1. Create a Lambda Function:
   - Go to AWS Lambda Console → Click Create Function.
   - Select Author from scratch → Enter a name (e.g., aws-lambda-s3-data-pipeline).
   - Choose Python 3.9.
   - Under Permissions, select the IAM role created earlier.
   - Click Create function.
2. Upload Code:
   - In the Code source section (EXPLORER), delete the default lambda_function.py.
   - Upload main.py as a ZIP file. Click Upload from → Select .zip file.
   - Click Deploy.
   ```plaintext
   - Alternatively, one can create a new file (main.py) at the Code source section (EXPLORER), and then copy and paste the code from the original main.py.
   ```
3. Attach AWS-Provided `Pandas` Layer:
   - In the Function Overview, scroll to Layers → Click Add a layer.
   - Select AWS Provided Layer → AWS Layers.
   - Choose AWSSDKPandas-Python39 → Select a version.
   - Click Add.
   - `Alternatively`, instead of AWS Layers, choose Specify an ARN and enter an ARN of the form:
     ```plaintext
     arn:aws:lambda:<region>:770693421928:layer:AWSLambda-Pandas:<version>
     ```
     ```plaintext
     Example:
     arn:aws:lambda:eu-north-1:336392948345:layer:AWSSDKPandas-Python39:30
     ```
     - You may need to set permissions to specify an ARN. 
     - You can find a complete list of ARNs for specific regions and python runtimes [here](https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html).
4. Use Custom layers for the `requests` library:
   - A zipped package for the requests library is provided in the project directory 'my-lambda-layers/requests_layer.zip'.
   - If needed, create a zipped package for the requests library using the following (or any suitable method):
       ```bash
       mkdir requests-layer && cd requests-layer
       pip install requests -t .
       zip -r requests-layer.zip .
       ```
   - Create a custom layer for the `requests` library:
     - Click on the top left menu (3 horizontal short parallel bars), Layers, Create layer.
     - Enter a name for the new layer (e.g., requests-layer), choose Python 3.9 under Compatible runtimes.
     - Click on Create/Save.
   - Attach/Add the layer to your Lambda function.
     - In the Function Overview, scroll to Layers → Click Add a layer.
     - Under Layer source, Custom layers choose the **requests-layer** created earlier and select a version.
     - Click Add.
5. Change the `main entry point` of your lambda function:
   - AWS Lambda expects the handler function (e.g., lambda_handler) to be in a specific location and referenced as <file_name>.<function_name>. 
   - For example:
   Since your lambda_handler function is in main.py, the handler should be specified as:
      ```plaintext
      main.lambda_handler
      ```
   ##### **How to Update the Lambda Handler**:
   - Open the AWS Lambda Console.
   - Navigate to your Lambda function.
   - In the Configuration tab, find the Runtime settings section.
   - Click Edit.
   - Update the Handler field as: `main.lambda_handler`.
   - Save the changes.


#### **Option 2: Docker Deployment (Python 3.11)**:
1. **Create an Amazon ECR Repository**:
   - Using AWS Management Console:
      - Open the AWS Management Console.
      - Navigate to Amazon Elastic Container Registry (ECR).
      - Click Create Repository.
      - Choose Private and enter a name (e.g., aws-lambda-s3-data-pipeline-docker).
      - Copy the repository URI (e.g., 123456789012.dkr.ecr.eu-north-1.amazonaws.com/aws-lambda-s3-data-pipeline-docker).
   - Using `AWS CLI` (Optional):
      -  Log in to ECR: Authenticate Docker to your AWS ECR registry:
     ```bash
     aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<your-region>.amazonaws.com
     ```
     - Create an ECR Repository: Create a repository in ECR to hold your image:
     ```bash
     aws ecr create-repository --repository-name aws-lambda-s3-data-pipeline-docker
     ```
2. **Authenticate Docker to ECR**:
   ```bash
   aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<your-region>.amazonaws.com
   ```
   - Example for eu-north-1:
   ```bash
   aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.eu-north-1.amazonaws.com
   ```
3. **Create a Dockerfile (Optional)**:
   - A Dockerfile is already provided in the project files. If needed, create a new file in the project directory with the following contents and save as Dockerfile.
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
    docker build -t aws-lambda-s3-data-pipeline-docker .

5. **Tag the image for ECR**:    
   ```bash 
   docker tag lambda-docker-project:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/aws-lambda-s3-docker-project-docker:latest
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
   ```
7. **Deploy the docker image to AWS Lambda**:
   - Go to the AWS Lambda Console.
   - Create a new function.
   - Choose Container Image as the deployment package.
   - Enter (paste) the ECR image URI you copied in 1.
   - Or in previous step, click on Browse images and select the desired Amazon ECR Image Repository (e.g. aws-lambda-s3-data-pipeline-docker) and Image.
   - Click on Save.

---

## **Configure Environment Variables**
Set the following environment variables in AWS Lambda:
1. Navigate to the Configuration tab.
2. Select Environment Variables → Click Edit → Add environment variable.
3. Add the following key-value pairs:

| Key             | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| `API_URL`       | `https://fakestoreapi.com/products`                                   |
| `S3_BUCKET`     | `aws-lambda-s3-data-pipeline-bucket`                                  |
| `S3_KEY`        | `processed/processed_data.txt`                                        |
| `SNS_TOPIC_ARN` | `arn:aws:sns:<region>:<account-id>:aws-lambda-s3-data-pipeline-topic` |

---

## **Grant the IAM Role SNS Publish Permissions**
You need to attach a policy to the IAM role that explicitly allows the sns:Publish action on the specific SNS topic.
1. Identify the Lambda Execution Role
   - Open the AWS Lambda Console.
   - Navigate to your Lambda function.
   - Go to the Configuration tab → Permissions.
   - Note the execution role name: (e.g. aws-lambda-s3-data-pipeline-docker-role...).

2. Update the IAM Role Policy
   - Open the IAM Console: https://console.aws.amazon.com/iam/.
   - Go to Roles and search for aws-s3-data-pipeline-docker-role.
   - Select the role and go to the Permissions tab.
   - Click Add permissions → Create inline policy.
   - Choose the JSON editor and paste the following policy:
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
   - Save the policy with a name like AllowSNSPublish.

---

## **Testing & Monitoring**
### **Set Up a Test Event**
1. In AWS lambda, navigate to the Test tab.
2. Click Create new test event.
3. Enter an event name (e.g., test-run).
4. Use the following JSON payload:
    ```json
    {
      "test": "lambda execution"
    }
5. Click Save.

### **Test the Lambda Function**
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
---

## **Automating Scheduled Runs with EventBridge**

To schedule automatic executions of this Lambda function, AWS **EventBridge** can be used to trigger the function at predefined intervals.

### **How to Set Up an EventBridge Rule for Scheduling Runs**
1. Go to **AWS EventBridge Console**.
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

---

## **Future Improvements**
- Use AWS Secrets Manager to securely manage sensitive credentials.
- Automate deployments using CI/CD pipelines with AWS CodePipeline or GitHub Actions.
