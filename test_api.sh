#!/bin/bash

echo "=========================================="
echo "Testing NetSentry Public Read-Only APIs"
echo "=========================================="
echo ""

BASE_URL="http://localhost:5000/api"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -e "${BLUE}Testing: ${description}${NC}"
    echo -e "${YELLOW}GET ${BASE_URL}${endpoint}${NC}"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}${endpoint}")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ Status: ${http_code}${NC}"
        echo "$body" | python -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ Status: ${http_code}${NC}"
        echo "$body"
    fi
    echo ""
    echo "---"
    echo ""
}

# 1. Health check
test_endpoint "/health" "Health Check"

# 2. Dashboard summary
test_endpoint "/dashboard/summary" "Dashboard Summary (KPIs)"

# 3. All devices
test_endpoint "/devices" "List All Devices"

# 4. Specific device (ID=1)
test_endpoint "/devices/1" "Get Device Details (ID=1)"

# 5. Device ports (ID=1)
test_endpoint "/devices/1/ports" "Get Device Ports (ID=1)"

# 6. All ports
test_endpoint "/ports" "List All Ports"

# 7. Filtered ports (OPEN only)
test_endpoint "/ports?status=OPEN" "Filter Ports - OPEN only"

# 8. Filtered ports (by protocol)
test_endpoint "/ports?protocol=TCP" "Filter Ports - TCP only"

# 9. Traffic statistics
test_endpoint "/traffic" "Traffic Statistics"

# 10. All alerts
test_endpoint "/alerts" "List All Alerts"

# 11. Unacknowledged alerts
test_endpoint "/alerts?acknowledged=false" "Filter Alerts - Unacknowledged"

# 12. High severity alerts
test_endpoint "/alerts?severity=HIGH" "Filter Alerts - HIGH Severity"

echo "=========================================="
echo "API Testing Complete!"
echo "=========================================="
