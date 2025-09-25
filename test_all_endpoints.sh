#!/bin/bash

# Comprehensive API Endpoint Testing for BrainTransactionsManager v2.0.0
# Blessed by Goddess Laxmi for Infinite Abundance 🙏

echo "🚀 Testing BrainTransactionsManager v2.0.0 API Endpoints"
echo "=================================================="

BASE_URL="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_status="$5"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "\n${BLUE}Testing: $name${NC}"
    echo "URL: $method $url"
    
    if [ -n "$data" ]; then
        echo "Data: $data"
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" -H "Content-Type: application/json" -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url")
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract response body (all lines except last)
    body=$(echo "$response" | head -n -1)
    
    echo "Status: $status_code"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "Expected: $expected_status, Got: $status_code"
        echo "Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo -e "\n${YELLOW}=== 1. HEALTH & SYSTEM ENDPOINTS ===${NC}"
test_endpoint "Health Check" "GET" "$BASE_URL/health" "" "200"
test_endpoint "Detailed Health" "GET" "$BASE_URL/health/detailed" "" "200"
test_endpoint "Configuration Status" "GET" "$BASE_URL/config/status" "" "200"

echo -e "\n${YELLOW}=== 2. MARKET DATA ENDPOINTS ===${NC}"
test_endpoint "Market Data - AAPL" "GET" "$BASE_URL/market/data/AAPL" "" "200"
test_endpoint "Market Data - BTCUSD" "GET" "$BASE_URL/market/data/BTCUSD" "" "200"
test_endpoint "Exchanges Info" "GET" "$BASE_URL/exchanges" "" "200"

echo -e "\n${YELLOW}=== 3. PORTFOLIO ENDPOINTS ===${NC}"
test_endpoint "Account Info" "GET" "$BASE_URL/portfolio/account" "" "200"
test_endpoint "Positions" "GET" "$BASE_URL/portfolio/positions" "" "200"
test_endpoint "Portfolio Summary" "GET" "$BASE_URL/portfolio/summary" "" "200"

echo -e "\n${YELLOW}=== 4. ORDER MANAGEMENT ENDPOINTS ===${NC}"
test_endpoint "Orders (Pending)" "GET" "$BASE_URL/orders" "" "200"
# Skipped: /orders/statistics endpoint removed
test_endpoint "Test Orders" "GET" "$BASE_URL/test/orders" "" "200"

echo -e "\n${YELLOW}=== 5. TRADING ENDPOINTS ===${NC}"
test_endpoint "Buy Order" "POST" "$BASE_URL/buy" '{"symbol": "AAPL", "quantity": 1, "strategy_name": "test"}' "200"
test_endpoint "Sell Order" "POST" "$BASE_URL/sell" '{"symbol": "AAPL", "quantity": 1, "strategy_name": "test"}' "200"

echo -e "\n${YELLOW}=== 6. POSITION MANAGEMENT ENDPOINTS ===${NC}"
test_endpoint "Close Position" "POST" "$BASE_URL/close/AAPL" "" "200"

echo -e "\n${YELLOW}=== 7. STRATEGY ENDPOINTS ===${NC}"
test_endpoint "Strategy Summary" "GET" "$BASE_URL/portfolio/strategy/default" "" "200"

echo -e "\n${YELLOW}=== 8. EMERGENCY CONTROL ENDPOINTS ===${NC}"
test_endpoint "Kill Switch Status" "GET" "$BASE_URL/kill-switch/status" "" "200"
test_endpoint "Activate Kill Switch" "POST" "$BASE_URL/kill-switch" '{"action": "activate", "reason": "testing"}' "200"
test_endpoint "Deactivate Kill Switch" "POST" "$BASE_URL/kill-switch" '{"action": "deactivate", "reason": "testing complete"}' "200"

echo -e "\n${YELLOW}=== 9. DATABASE MIGRATION ENDPOINTS ===${NC}"
test_endpoint "Migration Status" "GET" "$BASE_URL/migrations/status" "" "200"

echo -e "\n${YELLOW}=== 10. API DOCUMENTATION ===${NC}"
test_endpoint "Swagger UI" "GET" "$BASE_URL/docs" "" "200"
test_endpoint "ReDoc" "GET" "$BASE_URL/redoc" "" "200"

echo -e "\n${YELLOW}=== TEST SUMMARY ===${NC}"
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! BrainTransactionsManager v2.0.0 is working perfectly!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Please review the issues above.${NC}"
    exit 1
fi
