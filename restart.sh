#!/bin/bash

# Find and kill existing claude-code-proxy processes
echo "Checking for existing claude-code-proxy processes..."
PIDS=$(ps -ef | grep "claude-code-proxy" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    echo "Found running processes with PIDs: $PIDS"
    echo "Killing existing claude-code-proxy processes..."
    echo "$PIDS" | xargs kill -9
    echo "Processes killed."
else
    echo "No existing claude-code-proxy processes found."
fi

# Wait a moment for processes to fully terminate
sleep 2

# Start the service again
echo "Starting claude-code-proxy..."
nohup uv run claude-code-proxy > ./logs.out 2> ./logs.err &

echo "Service restarted. Logs will be written to logs.out and logs.err"
echo "Process ID: $!"
