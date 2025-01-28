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
