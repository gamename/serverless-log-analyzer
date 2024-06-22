# serverless-log-analyzer
scan all the lambda logs on cloudwatch.  Send alerts if problems detected.

### Summary

This AWS Lambda function is designed to periodically scan CloudWatch logs for errors and exceptions in Lambda functions
across multiple AWS regions. It identifies log entries containing the keywords 'error' and 'exception' in the most
recent log streams of each Lambda function (excluding its own logs). When such entries are found, it sends a detailed
notification to a specified Amazon SNS topic.

### Features

- Scans CloudWatch logs across multiple AWS regions.
- Identifies and collects log entries containing 'error' and 'exception' keywords.
- Sends notifications with details of the found errors/exceptions to an SNS topic.

### Prerequisites

- AWS account with the necessary IAM roles and permissions.
- An SNS topic to receive notifications.
- Environment variables set for regions and SNS topic ARN.

### Environment Variables

- `REGIONS`: Comma-separated list of AWS regions to scan (e.g., 'us-east-1,us-west-2').
- `SNS_TOPIC_ARN`: ARN of the SNS topic for sending notifications.

### IAM Role Requirements

- `AWSLambdaBasicExecutionRole`
- `CloudWatchLogsReadOnlyAccess`
- `AmazonSNSFullAccess` (or restricted to `sns:Publish` for the specified topic)

### Deployment

1. Create an IAM role with the required permissions.
2. Deploy the Lambda function using the provided code.
3. Set the environment variables `REGIONS` and `SNS_TOPIC_ARN`.
4. Configure a CloudWatch Events rule to trigger the Lambda function periodically (e.g., every hour).

### Example Output

```json
{
  "statusCode": 200,
  "body": "3 errors/exceptions found and reported."
}
```
