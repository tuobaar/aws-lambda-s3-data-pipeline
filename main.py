# Import libraries
import os  # For operating system-related tasks, such as reading environment variables
import time  # For adding delays between retries during S3 uploads
import logging  # For logging pipeline progress and errors
import requests  # For making API requests
import pandas as pd  # For data processing and manipulation
import boto3  # AWS SDK for interacting with S3
from botocore.exceptions import BotoCoreError, ClientError  # Handle AWS S3-specific errors
from io import StringIO  # For handling in-memory text streams (e.g., saving processed data)
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Stream logs to console (useful for Lambda monitoring)
    ]
)

# ----------------------------
# Step 1: Fetch Data from API
# ----------------------------
def fetch_data_with_retry(api_url):
    """
    Fetches data from a specified API endpoint with retry logic.

    Args:
        api_url (str): The URL of the API to fetch data from.

    Returns:
        list or None: A list of dictionaries containing the data from the API, or None if an error occurs.
    """
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,  # Exponential backoff (2s, 4s, 8s)
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]  # Only retry GET requests
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        logging.info("📡 Fetching data from API...")
        response = session.get(api_url, timeout=10)
        response.raise_for_status()  # Raise exception for 4xx/5xx responses
        logging.info(f"✅ Data fetched successfully! Status Code: {response.status_code}")

        # Validate response is JSON
        try:
            return response.json()
        except ValueError:
            logging.error("❌ API response is not valid JSON. Returning None.")
            return None

    except requests.exceptions.ConnectionError:
        logging.error("❌ Network error! Could not connect to the API. Check the API URL and internet connection.")
    except requests.exceptions.Timeout:
        logging.error("⏳ Request timed out! The API took too long to respond.")
    except requests.exceptions.HTTPError as e:
        if e.response is not None:  # Ensure response exists
            logging.error(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
        else:
            logging.error(f"❌ HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Request failed: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error occurred: {e}")

    return None


# ---------------------------------
# Step 2: Process the Data (Pandas)
# ---------------------------------
def process_data(data):
    """
    Processes the raw data into a filtered and structured TXT format.

    Args:
        data (list): Raw data as a list of dictionaries.

    Returns:
        StringIO: An in-memory file object containing the processed TXT data, or None if an error occurs.
    """
    try:
        # Validate that data is not empty
        if not data:
            raise ValueError("No data provided for processing")

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(data)
        logging.info("🔄 Original Data:")
        logging.info(df.head().to_string())

        # Filter: Example - Only include products with a price greater than 50
        df_filtered = df[df['price'] > 50]
        logging.info("🔄 Filtered Data (Price > 50):")
        logging.info(df_filtered.head().to_string())

        # Save the filtered data to an in-memory TXT file
        txt_buffer = StringIO()
        df_filtered.to_csv(txt_buffer, sep="\t", index=False)
        logging.info("✅ Data processed and saved to TXT format!")
        return txt_buffer
    except ValueError as e:
        logging.error(f"❌ ValueError: {e}")
    except Exception as e:
        logging.error(f"❌ An unexpected error occurred while processing data: {e}")
    return None


# --------------------------------------
# Step 3: Upload the TXT to an S3 Bucket
# --------------------------------------
def upload_to_s3(txt_buffer, bucket_name, s3_key, retries=3, delay=5):
    """
    Uploads the processed TXT data to an S3 bucket with retry logic.

    Args:
        txt_buffer (StringIO): In-memory buffer containing TXT data to upload.
        bucket_name (str): Name of the S3 bucket.
        s3_key (str): S3 key (path) where the file will be uploaded.
        retries (int): Number of retry attempts for failed uploads.
        delay (int): Delay (in seconds) between retry attempts.

    Returns:
        str: "upload_successful" or "upload_failed"
    """
    for attempt in range(1, retries + 1):
        try:
            # Reset buffer position
            txt_buffer.seek(0)

            # Initialize S3 client
            s3_client = boto3.client('s3')

            # Upload the file
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=txt_buffer.getvalue(),
                ContentType='text/plain'
            )
            logging.info(f"✅ File successfully uploaded to S3: s3://{bucket_name}/{s3_key}")
            return "upload_successful"
        except (BotoCoreError, ClientError) as e:
            logging.error(f"❌ Upload attempt {attempt} failed: {e}")
            if attempt < retries:
                logging.info(f"🔄 Retrying in {delay} seconds...")
                logging.warning(f"🔄 Retrying upload attempt {attempt + 1} in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error("❌ All retry attempts failed. Giving up.")
                return "upload_failed"


# ----------------------------------------------
# Step 4: AWS Lambda Handler and helper function
# ----------------------------------------------

def validate_environment_vars(required_vars):
    """
    Validates the presence of required environment variables.

    Args:
        required_vars (list): A list of required environment variable names.

    Returns:
        dict: A dictionary of environment variable values, or None if a variable is missing.
    """
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logging.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return None
    return {var: os.getenv(var) for var in required_vars}


def lambda_handler(event, context):
    """
    AWS Lambda entry point for the data pipeline.

    Args:
        event: AWS Lambda event object (not used here).
        context: AWS Lambda context object (not used here).
    """
    logging.info("🚀 Starting the AWS S3 pipeline...")

    # Read environment variables
    api_url = os.getenv("API_URL")
    s3_bucket = os.getenv("S3_BUCKET")
    s3_key = os.getenv("S3_KEY")

    env_vars = validate_environment_vars(["API_URL", "S3_BUCKET", "S3_KEY", "SNS_TOPIC_ARN"])
    if not env_vars:
        notify_failure("❌ Missing required environment variables.")
        return {
            "statusCode": 500,
            "body": "Missing required environment variables."
        }

    # Step 1: Fetch the data
    raw_data = fetch_data_with_retry(api_url)
    if not raw_data:
        error_message = "❌ Data pipeline failed at the Fetch Data stage."
        logging.error(error_message)
        notify_failure(error_message)
        return {
            "statusCode": 500,
            "body": "Data fetch failed."
        }

    # Step 2: Process the data
    txt_buffer = process_data(raw_data)
    if not txt_buffer:
        error_message = "❌ Data pipeline failed at the Process Data stage."
        logging.error(error_message)
        notify_failure(error_message)
        return {
            "statusCode": 500,
            "body": "Data processing failed."
        }

    # Step 3: Upload to S3
    upload_status = upload_to_s3(txt_buffer, s3_bucket, s3_key)
    if upload_status == "upload_failed":
        error_message = "❌ Data pipeline failed during S3 upload."
        logging.error(error_message)
        notify_failure(error_message)
        return {
            "statusCode": 500,
            "body": "S3 upload failed."
        }

    if upload_status == "upload_successful":
        success_message = "🏁 ✅ All pipeline processes completed successfully!"
        logging.info(success_message)
        notify_success(success_message)
        return {
            "statusCode": 200,
            "body": "Pipeline completed successfully."
        }


# --------------------------------------------------------
# Step 5: AWS Simple Notification Service (SNS) - Optional
# --------------------------------------------------------

def notify_failure(message):
    """
    Publishes a failure notification to an SNS topic.
    Args:
        message (str): The message to send to the SNS topic.
    """
    try:
        sns_client = boto3.client('sns')
        sns_topic_arn = os.getenv("SNS_TOPIC_ARN")

        # Validate the Topic ARN
        if not sns_topic_arn:
            logging.error("❌ SNS_TOPIC_ARN is not set. Cannot send failure notification.")
            return

        # Publish the failure notification
        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="Data Pipeline Failure Notification"
        )
        logging.info(f"✅ Failure notification sent: {response['MessageId']}")
    except Exception as e:
        logging.error(f"❌ Failed to send SNS notification: {e}")


def notify_success(message):
    """
    Publishes a success notification to an SNS topic.
    Args:
        message (str): The message to send to the SNS topic.
    """
    try:
        sns_client = boto3.client('sns')
        sns_topic_arn = os.getenv("SNS_TOPIC_ARN")

        # Validate the Topic ARN
        if not sns_topic_arn:
            logging.error("❌ SNS_TOPIC_ARN is not set. Cannot send success notification.")
            return

        # Publish the success notification
        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="Data Pipeline Success Notification"
        )
        logging.info(f"✅ Success notification sent: {response['MessageId']}")
    except Exception as e:
        logging.error(f"❌ Failed to send SNS success notification: {e}")

