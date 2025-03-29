# CloudWatch Logs MCP Server

An MCP (Model Context Protocol) server that provides tools for accessing AWS CloudWatch logs. This server allows AI assistants to list log groups and read log entries from AWS CloudWatch.

## Features

- List available CloudWatch log groups
- Read log entries from specific log groups
- Support for filtering logs by pattern
- Support for time-based filtering (absolute and relative times)
- Customizable AWS region
- Standard AWS authentication
- Built with FastMCP for easy integration

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

The application uses UV inline scripts for dependency management. You can run it using:

```bash
uv run main.py
```

Or alternatively:

```bash
python -m uv.run main.py
```

#### Command-line Options

The server supports the following command-line options:

- `--log-level`: Set the logging level (choices: DEBUG, INFO, WARNING, ERROR, CRITICAL; default: INFO)

Example with debug logging enabled:

```bash
uv run main.py --log-level DEBUG
```

The server runs using stdio transport, which allows it to be used with MCP clients like Claude Desktop.

#### Dependencies

Dependencies are defined directly in the main.py file using UV inline scripts:

```python
# /// script
# dependencies = [
#   "mcp[cli]>=1.6.0",  # Note: Comma is required between dependencies
#   "boto3>=1.28.0"
# ]
# ///
```

This makes the script self-contained and easier to run without needing to install dependencies separately.

### Configuring MCP Settings

To use this server with Claude Desktop or other MCP clients, add it to your MCP settings configuration:

For Claude Desktop, edit the configuration file at:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

Add the following to the `mcpServers` section:

```json
{
  "mcpServers": {
    "cloudwatch-logs": {
      "command": "python3",
      "args": ["/path/to/cloudwatch-logs-mcp/main.py"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For more detailed logging, you can add the `--log-level` argument:

```json
{
  "mcpServers": {
    "cloudwatch-logs": {
      "command": "python3",
      "args": ["/path/to/cloudwatch-logs-mcp/main.py", "--log-level", "DEBUG"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Important**: You must provide AWS credentials for the server to access CloudWatch logs. Add them as environment variables in your configuration:

```json
{
  "mcpServers": {
    "cloudwatch-logs": {
      "command": "python3",
      "args": ["/path/to/cloudwatch-logs-mcp/main.py"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "YOUR_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY": "YOUR_SECRET_ACCESS_KEY"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

You can also use an AWS profile instead of explicit credentials:

```json
{
  "mcpServers": {
    "cloudwatch-logs": {
      "command": "python3",
      "args": ["/path/to/cloudwatch-logs-mcp/main.py"],
      "env": {
        "AWS_REGION": "us-west-2",
        "AWS_PROFILE": "default"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For Cursor, edit the configuration files at:

```
~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
~/.cursor/mcp.json
```

Use the same configuration format as shown above for Claude Desktop.

> **Important**: Make sure to include the `"disabled": false` and `"autoApprove": []` fields in your configuration, as they are required for proper MCP server operation.

## Available Tools

### list_groups

Lists available CloudWatch log groups.

**Parameters:**

- `prefix` (optional): Log group name prefix
- `region` (optional): AWS region
- `accessKeyId` (optional): AWS access key ID
- `secretAccessKey` (optional): AWS secret access key
- `sessionToken` (optional): AWS session token

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

### Getting Logs

```json
{
  "logGroupName": "/aws/lambda/my-function",
  "startTime": "1h",
  "filterPattern": "ERROR",
  "region": "us-west-2"
}
```

## Implementation Details

This server is built using the FastMCP class from the MCP SDK, which provides a simple way to create MCP servers. The server exposes two main tools:

1. `list_groups`: Lists available CloudWatch log groups
2. `get_logs`: Reads log entries from specific log groups

Each tool is implemented as an async function decorated with `@mcp.tool()`. The server uses the boto3 library to interact with the AWS CloudWatch Logs API.

## Architecture

### System Architecture

```mermaid
flowchart LR
    Claude[Claude/Cursor] <--> |MCP Protocol| Server[CloudWatch Logs MCP Server]
    Server <--> |AWS SDK| AWS[AWS CloudWatch Logs]

    subgraph MCP Server
        FastMCP[FastMCP SDK]
        Tools[Tools:\nlist_groups\nget_logs]
        Boto3[Boto3 AWS SDK]
    end

    FastMCP --- Tools
    Tools --- Boto3
```

## Testing

The server has been successfully tested with both Claude Desktop and Cursor as MCP clients. The following operations have been verified:

- Listing CloudWatch log groups
- Retrieving logs from specific log groups

When testing with your own AWS account, make sure you have the appropriate permissions to access CloudWatch logs. You can test the server by asking Claude or Cursor to:

- "List all CloudWatch log groups"
- "Get logs from [log group name] for the last hour"

## License

MIT
