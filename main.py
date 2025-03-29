#!/usr/bin/env python3
# /// script
# dependencies = [
#   "mcp[cli]>=1.6.0",  # Note: Comma is required between dependencies
#   "boto3>=1.28.0"
# ]
# ///
"""
CloudWatch Logs MCP Server

An MCP server that provides tools for accessing AWS CloudWatch logs.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import traceback
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mcp.server.fastmcp import FastMCP

# Add this near the top of your file to debug module structure
try:
    import mcp
    print(f"MCP module available at: {mcp.__file__}", file=sys.stderr)
    print(f"MCP version: {getattr(mcp, '__version__', 'unknown')}", file=sys.stderr)
    print(f"Available mcp submodules: {dir(mcp)}", file=sys.stderr)
except ImportError as e:
    print(f"Error importing mcp: {e}", file=sys.stderr)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="CloudWatch Logs MCP Server")
parser.add_argument(
    "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="INFO",
    help="Set the logging level (default: INFO)",
)
args = parser.parse_args()

# Configure simpler logging to just stderr to avoid any file permission issues
logging.basicConfig(
    level=getattr(logging, args.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("cloudwatch-logs-mcp")

# Add diagnostic output
print("Starting CloudWatch Logs MCP Server...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current working directory: {os.getcwd()}", file=sys.stderr)

try:
    # Initialize the MCP server
    logger.info("Initializing CloudWatch Logs MCP")
    mcp = FastMCP("cloudwatch-logs")
    print("MCP server initialized successfully", file=sys.stderr)
except Exception as e:
    print(f"Failed to initialize MCP server: {str(e)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

@mcp.tool(
    description="List available CloudWatch log groups"
)
async def list_groups(
    prefix: Optional[str] = None,
    region: Optional[str] = None,
    accessKeyId: Optional[str] = None,
    secretAccessKey: Optional[str] = None,
    sessionToken: Optional[str] = None,
) -> str:
    """List available CloudWatch log groups."""
    try:
        print(f"Listing CloudWatch log groups (prefix: {prefix}, region: {region})", file=sys.stderr)
        client = _get_cloudwatch_client(
            region=region,
            access_key_id=accessKeyId,
            secret_access_key=secretAccessKey,
            session_token=sessionToken,
        )

        # List log groups
        kwargs = {}
        if prefix:
            kwargs["logGroupNamePrefix"] = prefix

        response = client.describe_log_groups(**kwargs)
        log_groups = response.get("logGroups", [])

        # Format the response
        formatted_groups = []
        for group in log_groups:
            formatted_groups.append(
                {
                    "logGroupName": group.get("logGroupName"),
                    "creationTime": group.get("creationTime"),
                    "storedBytes": group.get("storedBytes"),
                }
            )

        response_json = json.dumps(formatted_groups, ensure_ascii=True)
        print(f"Returning {len(formatted_groups)} log groups", file=sys.stderr)
        return response_json
    except Exception as e:
        print(f"Error in list_groups: {str(e)}", file=sys.stderr)
        # Return error as JSON instead of raising
        return json.dumps({"error": str(e)}, ensure_ascii=True)


@mcp.tool(
    description="Get CloudWatch logs from a specific log group and stream"
)
async def get_logs(
    logGroupName: str,
    logStreamName: Optional[str] = None,
    startTime: Optional[str] = None,
    endTime: Optional[str] = None,
    filterPattern: Optional[str] = None,
    region: Optional[str] = None,
    accessKeyId: Optional[str] = None,
    secretAccessKey: Optional[str] = None,
    sessionToken: Optional[str] = None,
) -> str:
    """Get CloudWatch logs from a specific log group and stream."""
    try:
        print(
            f"Getting CloudWatch logs for group: {logGroupName}, stream: {logStreamName}",
            file=sys.stderr
        )
        client = _get_cloudwatch_client(
            region=region,
            access_key_id=accessKeyId,
            secret_access_key=secretAccessKey,
            session_token=sessionToken,
        )

        # Parse start and end times
        start_time_ms = None
        if startTime:
            start_time_ms = _parse_relative_time(startTime)

        end_time_ms = None
        if endTime:
            end_time_ms = _parse_relative_time(endTime)

        # Get logs
        kwargs = {
            "logGroupName": logGroupName,
        }

        if logStreamName:
            kwargs["logStreamNames"] = [logStreamName]

        if filterPattern:
            kwargs["filterPattern"] = filterPattern

        if start_time_ms:
            kwargs["startTime"] = start_time_ms

        if end_time_ms:
            kwargs["endTime"] = end_time_ms

        # Use filter_log_events for more flexible querying
        response = client.filter_log_events(**kwargs)
        events = response.get("events", [])

        # Format the response
        formatted_events = []
        for event in events:
            timestamp = event.get("timestamp")
            if timestamp:
                try:
                    timestamp = datetime.fromtimestamp(timestamp / 1000).isoformat()
                except Exception:
                    timestamp = str(timestamp)

            formatted_events.append(
                {
                    "timestamp": timestamp,
                    "message": event.get("message"),
                    "logStreamName": event.get("logStreamName"),
                }
            )

        # Be very careful with JSON serialization
        response_json = json.dumps(formatted_events, ensure_ascii=True, default=str)
        print(f"Returning {len(formatted_events)} log events", file=sys.stderr)
        return response_json
    except Exception as e:
        print(f"Error in get_logs: {str(e)}", file=sys.stderr)
        # Return error as JSON
        return json.dumps({"error": str(e)}, ensure_ascii=True)


def _get_cloudwatch_client(
    region: Optional[str] = None,
    access_key_id: Optional[str] = None,
    secret_access_key: Optional[str] = None,
    session_token: Optional[str] = None,
) -> Any:
    """Get a CloudWatch Logs client."""
    # Create session with credentials if provided
    session_kwargs = {}
    if region:
        session_kwargs["region_name"] = region

    if access_key_id and secret_access_key:
        session_kwargs["aws_access_key_id"] = access_key_id
        session_kwargs["aws_secret_access_key"] = secret_access_key
        if session_token:
            session_kwargs["aws_session_token"] = session_token

    # Create session and client
    try:
        session = boto3.Session(**session_kwargs)
        return session.client("logs")
    except Exception as e:
        print(f"Error creating CloudWatch client: {str(e)}", file=sys.stderr)
        raise


def _parse_relative_time(time_str: str) -> Optional[int]:
    """Parse a relative time string into a timestamp."""
    if not time_str:
        return None

    # Check if it's an ISO format date
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except ValueError:
        pass

    # Parse relative time
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if time_str[-1] in units and time_str[:-1].isdigit():
        value = int(time_str[:-1])
        unit = time_str[-1]
        seconds = value * units[unit]
        dt = datetime.now() - timedelta(seconds=seconds)
        return int(dt.timestamp() * 1000)

    raise ValueError(f"Invalid time format: {time_str}")


if __name__ == "__main__":
    try:
        print("Starting main execution block", file=sys.stderr)

        # Skip AWS auth validation for now
        print("Skipping AWS auth check to avoid early failures", file=sys.stderr)

        # Run the MCP server without any extras
        print("Starting CloudWatch Logs MCP server with stdio transport", file=sys.stderr)

        # Explicitly handle synchronous initialization
        print("Running MCP server...", file=sys.stderr)
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
