#!/usr/bin/env python3
"""
CloudWatch Logs MCP Server

An MCP server that provides tools for accessing AWS CloudWatch logs.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("cloudwatch-logs")


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
    """List available CloudWatch log groups.

    Args:
        prefix: Log group name prefix
        region: AWS region
        accessKeyId: AWS access key ID
        secretAccessKey: AWS secret access key
        sessionToken: AWS session token

    Returns:
        JSON string with the list of log groups
    """
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

    return json.dumps(formatted_groups, indent=2)


@mcp.tool(
    description="List available CloudWatch log streams in a log group"
)
async def list_streams(
    logGroupName: str,
    region: Optional[str] = None,
    accessKeyId: Optional[str] = None,
    secretAccessKey: Optional[str] = None,
    sessionToken: Optional[str] = None,
) -> str:
    """List available CloudWatch log streams in a log group.

    Args:
        logGroupName: The name of the log group
        region: AWS region
        accessKeyId: AWS access key ID
        secretAccessKey: AWS secret access key
        sessionToken: AWS session token

    Returns:
        JSON string with the list of log streams
    """
    client = _get_cloudwatch_client(
        region=region,
        access_key_id=accessKeyId,
        secret_access_key=secretAccessKey,
        session_token=sessionToken,
    )

    # List log streams
    response = client.describe_log_streams(logGroupName=logGroupName)
    log_streams = response.get("logStreams", [])

    # Format the response
    formatted_streams = []
    for stream in log_streams:
        formatted_streams.append(
            {
                "logStreamName": stream.get("logStreamName"),
                "creationTime": stream.get("creationTime"),
                "firstEventTimestamp": stream.get("firstEventTimestamp"),
                "lastEventTimestamp": stream.get("lastEventTimestamp"),
                "storedBytes": stream.get("storedBytes"),
            }
        )

    return json.dumps(formatted_streams, indent=2)


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
    """Get CloudWatch logs from a specific log group and stream.

    Args:
        logGroupName: The name of the log group
        logStreamName: The name of the log stream
        startTime: Start time in ISO format or relative time (e.g., "5m", "1h", "1d")
        endTime: End time in ISO format
        filterPattern: Filter pattern for the logs
        region: AWS region
        accessKeyId: AWS access key ID
        secretAccessKey: AWS secret access key
        sessionToken: AWS session token

    Returns:
        JSON string with the log events
    """
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
            timestamp = datetime.fromtimestamp(timestamp / 1000).isoformat()

        formatted_events.append(
            {
                "timestamp": timestamp,
                "message": event.get("message"),
                "logStreamName": event.get("logStreamName"),
            }
        )

    return json.dumps(formatted_events, indent=2)


def _get_cloudwatch_client(
    region: Optional[str] = None,
    access_key_id: Optional[str] = None,
    secret_access_key: Optional[str] = None,
    session_token: Optional[str] = None,
) -> Any:
    """Get a CloudWatch Logs client.

    Args:
        region: AWS region
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
        session_token: AWS session token

    Returns:
        A CloudWatch Logs client
    """
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
    session = boto3.Session(**session_kwargs)
    return session.client("logs")


def _parse_relative_time(time_str: str) -> Optional[int]:
    """Parse a relative time string into a timestamp.

    Args:
        time_str: A relative time string (e.g., "5m", "1h", "1d")

    Returns:
        The timestamp in milliseconds

    Raises:
        ValueError: If the time string is invalid
    """
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
    # Run the MCP server
    mcp.run(transport="stdio")
