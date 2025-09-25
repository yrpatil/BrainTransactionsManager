#!/bin/bash

# BrainTransactionsManager v2.0.0 Stop Script
# Blessed by Goddess Laxmi for Infinite Abundance 🙏
#
# This script cleanly stops the BrainTransactionsManager v2.0.0 server
# and all its background components without affecting PostgreSQL database
# which is shared with other projects.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping BrainTransactionsManager v2.0.0...${NC}"
echo "=========================================="

# Function to check if process is running
is_process_running() {
    local process_name="$1"
    pgrep -f "$process_name" > /dev/null 2>&1
}

# Function to stop process gracefully
stop_process() {
    local process_name="$1"
    local description="$2"
    
    if is_process_running "$process_name"; then
        echo -e "${YELLOW}⏳ Stopping $description...${NC}"
        
        # Try graceful shutdown first
        pkill -TERM -f "$process_name" 2>/dev/null || true
        
        # Wait up to 10 seconds for graceful shutdown
        local count=0
        while is_process_running "$process_name" && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if is_process_running "$process_name"; then
            echo -e "${YELLOW}⚠️  Force stopping $description...${NC}"
            pkill -KILL -f "$process_name" 2>/dev/null || true
            sleep 2
        fi
        
        # Verify stopped
        if is_process_running "$process_name"; then
            echo -e "${RED}❌ Failed to stop $description${NC}"
            return 1
        else
            echo -e "${GREEN}✅ $description stopped successfully${NC}"
            return 0
        fi
    else
        echo -e "${BLUE}ℹ️  $description is not running${NC}"
        return 0
    fi
}

# Function to check port availability
check_port() {
    local port="$1"
    local service_name="$2"
    
    if lsof -i:$port > /dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is still in use by $service_name${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port is free${NC}"
        return 0
    fi
}

# Main stop sequence
echo -e "${BLUE}🔍 Checking running processes...${NC}"

# 1. Stop BrainTransactionsManager v2.0.0 server
stop_process "python server.py" "BrainTransactionsManager v2.0.0 Server"

# 2. Stop any background monitoring processes
stop_process "background_monitor" "Background Monitor"

# 3. Stop any polling processes
stop_process "poll_and_reconcile" "Background Polling"

# 4. Stop any migration processes
stop_process "alembic" "Database Migration"

# 5. Stop any FastAPI/uvicorn processes
stop_process "uvicorn" "FastAPI Server"

# 6. Stop any Python processes related to our project
stop_process "braintransactions" "BrainTransactions Python Processes"

# 7. Stop any processes using our port
if lsof -i:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8000 is still in use. Stopping processes...${NC}"
    lsof -ti:8000 | xargs kill -TERM 2>/dev/null || true
    sleep 2
    lsof -ti:8000 | xargs kill -KILL 2>/dev/null || true
fi

# 8. Verify all components are stopped
echo -e "${BLUE}🔍 Verifying shutdown...${NC}"

# Check if main server is stopped
if is_process_running "python server.py"; then
    echo -e "${RED}❌ BrainTransactionsManager server is still running${NC}"
    exit 1
else
    echo -e "${GREEN}✅ BrainTransactionsManager server is stopped${NC}"
fi

# Check port availability
check_port 8000 "BrainTransactionsManager"

# 9. Clean up any temporary files
echo -e "${BLUE}🧹 Cleaning up temporary files...${NC}"
rm -f *.pid 2>/dev/null || true
rm -f logs/*.log 2>/dev/null || true

# 10. Verify PostgreSQL is still running (should not be affected)
echo -e "${BLUE}🔍 Verifying PostgreSQL is still running...${NC}"
if pgrep -f "postgres" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is still running (shared database preserved)${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL is not running (this is normal if not started by this project)${NC}"
fi

# 11. Final status report
echo ""
echo -e "${GREEN}🎉 BrainTransactionsManager v2.0.0 shutdown complete!${NC}"
echo ""
echo -e "${BLUE}📊 Shutdown Summary:${NC}"
echo "• ✅ Server processes stopped"
echo "• ✅ Background monitoring stopped"
echo "• ✅ Port 8000 freed"
echo "• ✅ Temporary files cleaned"
echo "• ✅ PostgreSQL database preserved (shared with other projects)"
echo ""
echo -e "${BLUE}🚀 To restart the server:${NC}"
echo "  cd api_versions/v2.0.0"
echo "  python server.py &"
echo ""
echo -e "${BLUE}🙏 Blessed by Goddess Laxmi for Infinite Abundance!${NC}"

exit 0
