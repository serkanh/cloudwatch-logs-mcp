# Product Context

## Purpose

This project creates an MCP (Model Context Protocol) server to read AWS CloudWatch logs remotely. It's designed to connect to MCP clients like Claude Desktop, allowing them to access and display CloudWatch logs.

## Problems Solved

- Enables AI assistants to access CloudWatch logs data through the MCP protocol
- Provides a standardized interface for retrieving CloudWatch logs
- Allows for remote monitoring and analysis of CloudWatch logs without direct AWS console access

## How It Should Work

- The server should connect to AWS CloudWatch using the AWS SDK
- It should provide tools to list available log groups and streams
- It should allow reading log entries from specified log groups/streams
- The region should be customizable to access logs from different AWS regions
- Authentication should be handled through standard AWS credentials
