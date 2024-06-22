"""
AWS Lambda Function to Monitor CloudWatch Logs for Errors and Exceptions

This Lambda function is designed to run periodically (e.g., hourly) and scan all
CloudWatch log groups associated with Lambda functions (excluding its own) in specified
AWS regions. It looks for log entries containing the keywords 'error' and 'exception'
in the most recent log stream of each Lambda function. If any such entries are found,
it sends a detailed notification to an Amazon SNS topic.

Environment Variables:
- REGIONS: A comma-separated list of AWS regions to scan for Lambda log groups (e.g., 'us-east-1,us-west-2').
- SNS_TOPIC_ARN: The ARN of the SNS topic where error/exception notifications will be sent.

IAM Role Requirements:
The Lambda function's execution role must have the following permissions:
- AWSLambdaBasicExecutionRole: Basic Lambda execution role.
- CloudWatchLogsReadOnlyAccess: Permission to read CloudWatch logs across the specified regions.
- AmazonSNSFullAccess (or restricted to sns:Publish for the specified topic): Permission to publish messages to the SNS topic.

Functionality:
1. Iterates through the specified AWS regions.
2. Lists all CloudWatch log groups with the prefix '/aws/lambda/'.
3. Skips the log group corresponding to the current Lambda function to avoid self-referencing.
4. For each remaining log group, retrieves the most recent log stream.
5. Scans the latest log events for the keywords 'error' and 'exception' (case-insensitive).
6. Collects any found errors/exceptions, including the Lambda function name, timestamp, and log message.
7. Constructs a notification message summarizing the found errors/exceptions.
8. Sends the notification message to the specified SNS topic.

Returns:
- statusCode: HTTP status code indicating the result of the function execution (200 for success).
- body: A message indicating the number of errors/exceptions found and reported.

Example Output:
{
    'statusCode': 200,
    'body': '3 errors/exceptions found and reported.'
}

Usage:
Deploy this function as an AWS Lambda function, configure the necessary environment variables,
and set up a CloudWatch Events rule to trigger it periodically.
"""

import os
from datetime import datetime

import boto3


def lambda_handler(event, context):
    regions = os.environ['REGIONS'].split(',')
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']

    error_keywords = ['error', 'exception']
    errors_found = []

    # Construct the log group name of the current function
    current_log_group_name = f'/aws/lambda/{context.function_name}'

    for region in regions:
        logs_client = boto3.client('logs', region_name=region)
        log_groups = logs_client.describe_log_groups(logGroupNamePrefix='/aws/lambda/')

        for log_group in log_groups.get('logGroups', []):
            log_group_name = log_group['logGroupName']

            if log_group_name == current_log_group_name:
                continue

            log_streams = logs_client.describe_log_streams(logGroupName=log_group_name, orderBy='LastEventTime',
                                                           descending=True, limit=1)

            for log_stream in log_streams.get('logStreams', []):
                log_stream_name = log_stream['logStreamName']
                log_events = logs_client.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name,
                                                        limit=1)

                for event in log_events.get('events', []):
                    message = event['message'].lower()
                    if any(keyword in message for keyword in error_keywords):
                        errors_found.append({
                            'lambda_name': log_group_name,
                            'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000).isoformat(),
                            'message': event['message']
                        })

    if errors_found:
        message = "Errors/Exceptions found in the following Lambda functions:\n"
        for error in errors_found:
            message += f"Lambda: {error['lambda_name']}\nTime: {error['timestamp']}\nMessage: {error['message']}\n\n"

        sns_client = boto3.client('sns')
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject='Lambda Errors/Exceptions Notification',
            Message=message
        )

    return {
        'statusCode': 200,
        'body': f"{len(errors_found)} errors/exceptions found and reported."
    }
