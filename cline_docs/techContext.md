# Technical Context

## Technologies Used

- Python 3.12+
- MCP (Model Context Protocol) SDK v1.6.0+
- AWS SDK for Python (boto3)
- UV for Python package management

## Development Setup

- Python 3.12 or higher required
- MCP CLI tools installed
- AWS credentials configured for CloudWatch access
- UV package manager for dependency management

## Technical Constraints

- Must use stdio transport for MCP communication
- Must support standard AWS authentication methods
- Should work with Claude Desktop as an MCP client
- Should handle large log volumes efficiently
- Must implement proper error handling for AWS API failures

## Dependencies

- mcp[cli]>=1.6.0: Core MCP SDK with CLI support
- boto3: AWS SDK for Python (to be added)
- Other dependencies will be managed through UV inline scripts

## Configuration

- AWS region should be configurable
- AWS credentials should be provided through standard AWS credential chain
- MCP server should be configurable through environment variables or command-line arguments
