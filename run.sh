if netstat -tuln | grep -q ":51000 "; then
    echo "❌ Error: Port 51000 is already in use!"
    echo "Please stop any running CLIP server or use a different port."
    exit 1
fi

# Start the clip server and capture its output
echo "Starting CLIP server..."
python -m clip_server > server_output.log 2>&1 &
SERVER_PID=$!
echo "CLIP server started with main process PID $SERVER_PID"

# Wait for server to start and log addresses
echo "Waiting for server to initialize..."
timeout=30  # 30 seconds timeout
counter=0
while ! grep -q "Endpoint" server_output.log && [ $counter -lt $timeout ]; do
    sleep 1
    counter=$((counter+1))
done

# Check if server started successfully
if [ $counter -eq $timeout ]; then
    echo "❌ Error: Server failed to start within $timeout seconds"
    echo "Check server_output.log for details"
    # Kill all CLIP server processes
    pkill -f "python -m clip_server"
    exit 1
fi

# Extract protocol info
PROTOCOL=$(grep -o "Protocol[[:space:]]*[A-Z]\+" server_output.log | awk '{print $NF}')

if [ -z "$PROTOCOL" ]; then
    PROTOCOL="GRPC"
    echo "Protocol not found in log, using default: $PROTOCOL"
fi

# Extract server addresses with more robust regex patterns
LOCAL_ADDR=$(grep "Local" server_output.log | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}:[0-9]\+\|0\.0\.0\.0:[0-9]\+')
PRIVATE_ADDR=$(grep "Private" server_output.log | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}:[0-9]\+')
PUBLIC_ADDR=$(grep "Public" server_output.log | grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}:[0-9]\+')

echo "Debug - Extracted addresses:"
echo "PROTOCOL: $PROTOCOL"
echo "LOCAL_ADDR: $LOCAL_ADDR"
echo "PRIVATE_ADDR: $PRIVATE_ADDR" 
echo "PUBLIC_ADDR: $PUBLIC_ADDR"

echo "✅ CLIP server started successfully"
echo "Running connection test..."

# Pass the addresses to the connection checker
python ./postprocessing/check_connection.py --protocol "$PROTOCOL" --local-addr "$LOCAL_ADDR" --private-addr "$PRIVATE_ADDR" --public-addr "$PUBLIC_ADDR"
