# CloudWatch Logs MCP Server

An MCP (Model Context Protocol) server that provides tools for accessing AWS CloudWatch logs. This server allows AI assistants to list log groups and read log entries from AWS CloudWatch.

## Available Tools

### list_groups

Lists available CloudWatch log groups.

**Parameters:**

- `prefix` (optional): Log group name prefix
- `region` (optional): AWS region
- `accessKeyId` (optional): AWS access key ID
- `secretAccessKey` (optional): AWS secret access key
- `sessionToken` (optional): AWS session token

**Returns:** JSON string with the list of log groups, including `logGroupName`, `creationTime`, and `storedBytes`.

### get_logs

Gets CloudWatch logs from a specific log group.

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

**Returns:** JSON string with the log events, including `timestamp`, `message`, and `logStreamName`.

## Setup

### AWS Credentials

Ensure you have AWS credentials configured. You can set them up using the AWS CLI or by setting environment variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Usage with Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cloudwatch-logs": {
      "command": "python3",
      "args": ["/path/to/cloudwatch-logs-mcp/main.py"],
      "env": {
        "AWS_ACCESS_KEY_ID": "<YOUR_ACCESS_KEY_ID>",
        "AWS_SECRET_ACCESS_KEY": "<YOUR_SECRET_ACCESS_KEY>",
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Docker

If you prefer to run the server in a Docker container, you can set up a Dockerfile and use the following configuration:

```json
{
  "mcpServers": {
    "cloudwatch-logs": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "AWS_ACCESS_KEY_ID",
        "-e",
        "AWS_SECRET_ACCESS_KEY",
        "mcp/cloudwatch-logs"
      ],
      "env": {
        "AWS_ACCESS_KEY_ID": "<YOUR_ACCESS_KEY_ID>",
        "AWS_SECRET_ACCESS_KEY": "<YOUR_SECRET_ACCESS_KEY>",
      }
    }
  }
}
```

## Implementation Details

This server is built using the FastMCP class from the MCP SDK, which provides a simple way to create MCP servers. The server exposes two main tools:

1. `list_groups`: Lists available CloudWatch log groups
2. `get_logs`: Reads log entries from specific log groups

Each tool is implemented as an async function decorated with `@mcp.tool()`. The server uses the boto3 library to interact with the AWS CloudWatch Logs API.

## License

MIT
