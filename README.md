# CloudWatch Logs MCP Server

An MCP (Model Context Protocol) server that provides tools for accessing AWS CloudWatch logs. This server allows AI assistants to list log groups, list log streams, and read log entries from AWS CloudWatch.

## Features

- List available CloudWatch log groups
- List log streams within a log group
- Read log entries from specific log groups and streams
- Support for filtering logs by pattern
- Support for time-based filtering (absolute and relative times)
- Customizable AWS region
- Standard AWS authentication

## Installation

This project requires Python 3.12 or higher.

```bash
# Clone the repository
git clone https://github.com/yourusername/cloudwatch-logs-mcp.git
cd cloudwatch-logs-mcp

# Install dependencies
pip install -e .
```

## Usage

### Running the Server

```bash
python main.py
```

The server runs using stdio transport, which allows it to be used with MCP clients like Claude Desktop.

### Configuring MCP Settings

To use this server with Claude Desktop or other MCP clients, add it to your MCP settings configuration:

```json
{
  "mcpServers": {
    "cloudwatch-logs": {
      "command": "python",
      "args": ["/path/to/cloudwatch-logs-mcp/main.py"],
      "env": {
        "AWS_REGION": "us-west-2",  // Optional: Default AWS region
        "AWS_PROFILE": "default"     // Optional: AWS profile to use
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Available Tools

### list_groups

Lists available CloudWatch log groups.

**Parameters:**

- `prefix` (optional): Log group name prefix
- `region` (optional): AWS region
- `accessKeyId` (optional): AWS access key ID
- `secretAccessKey` (optional): AWS secret access key
- `sessionToken` (optional): AWS session token

### list_streams

Lists available CloudWatch log streams in a log group.

**Parameters:**

- `logGroupName` (required): The name of the log group
- `region` (optional): AWS region
- `accessKeyId` (optional): AWS access key ID
- `secretAccessKey` (optional): AWS secret access key
- `sessionToken` (optional): AWS session token

### get_logs

Gets CloudWatch logs from a specific log group and stream.

**Parameters:**

- `logGroupName` (required): The name of the log group
- `logStreamName` (optional): The name of the log stream
- `startTime` (optional): Start time in ISO format or relative time (e.g., "5m", "1h", "1d")
- `endTime` (optional): End time in ISO format
- `filterPattern` (optional): Filter pattern for the logs
- `region` (optional): AWS region
- `accessKeyId` (optional): AWS access key ID
- `secretAccessKey` (optional): AWS secret access key
- `sessionToken` (optional): AWS session token

## Authentication

The server supports the following authentication methods:

1. **Environment variables**: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
2. **AWS credentials file**: ~/.aws/credentials
3. **IAM roles**: For EC2 instances or other AWS services
4. **Explicit credentials**: Provided in the tool parameters

## Examples

### Listing Log Groups

```json
{
  "prefix": "aws/lambda",
  "region": "us-west-2"
}
```

### Listing Log Streams

```json
{
  "logGroupName": "/aws/lambda/my-function",
  "region": "us-west-2"
}
```

### Getting Logs

```json
{
  "logGroupName": "/aws/lambda/my-function",
  "logStreamName": "2023/03/29/[$LATEST]abcdef123456",
  "startTime": "1h",
  "filterPattern": "ERROR",
  "region": "us-west-2"
}
```

## License

MIT
