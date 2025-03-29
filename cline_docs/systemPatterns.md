# System Patterns

## Architecture

- MCP (Model Context Protocol) server architecture
- AWS SDK integration for CloudWatch logs access
- Command-line interface using stdio transport for MCP communication

## Key Technical Decisions

- Using the MCP protocol to expose CloudWatch logs functionality to AI assistants
- Implementing as a Python-based MCP server
- Using UV inline scripts for dependency management
- Modular design with separate functions for different CloudWatch operations

## Design Patterns

- Tool-based API design following MCP conventions
- Asynchronous operations for AWS API calls
- Clear separation between AWS SDK interaction and MCP protocol handling
- Consistent error handling and response formatting

## Code Organization

- Main server initialization and configuration
- Tool definitions for CloudWatch operations
- AWS SDK integration layer
- Utility functions for formatting and processing log data
