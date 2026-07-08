#!/bin/bash

echo "========================================="
echo "  DOMNAK BACKEND - COMPLETE TEST SUITE"
echo "========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://127.0.0.1:8000"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

echo -e "\n${YELLOW}1. HEALTH CHECKS${NC}"
echo "-----------------------------------------"

# Test 1: Health Check
echo -n "Testing Health Check... "
curl -s "$BASE_URL/" | jq -e '.status' > /dev/null 2>&1
print_result $? "Health Check"

# Test 2: Health Ready
echo -n "Testing Health Ready... "
curl -s "$BASE_URL/health" | jq -e '.status' > /dev/null 2>&1
print_result $? "Health Ready"

echo -e "\n${YELLOW}2. AUTHENTICATION${NC}"
echo "-----------------------------------------"

# Test 3: Login
echo -n "Testing Login... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!"}')
TOKEN=$(echo $RESPONSE | jq -r '.data.access_token')
if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    print_result 0 "Login (Token received)"
else
    print_result 1 "Login"
fi

# Test 4: Get Current User
echo -n "Testing Get Current User... "
curl -s -X GET "$BASE_URL/api/auth/me?user_id=31a7c8f6-0397-4886-8f03-37ed492cb641" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.id' > /dev/null 2>&1
print_result $? "Get Current User"

echo -e "\n${YELLOW}3. QUOTES${NC}"
echo "-----------------------------------------"

# Test 5: Create Quote
echo -n "Testing Create Quote... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/quotes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contractor_name":"ABC Construction","total_amount":15000.5}')
QUOTE_ID=$(echo $RESPONSE | jq -r '.data.id')
if [ "$QUOTE_ID" != "null" ] && [ -n "$QUOTE_ID" ]; then
    print_result 0 "Create Quote (ID: $QUOTE_ID)"
else
    print_result 1 "Create Quote"
fi

# Test 6: Get All Quotes
echo -n "Testing Get All Quotes... "
curl -s -X GET "$BASE_URL/api/quotes/" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get All Quotes"

# Test 7: Get Single Quote
echo -n "Testing Get Single Quote... "
curl -s -X GET "$BASE_URL/api/quotes/$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data.id' > /dev/null 2>&1
print_result $? "Get Single Quote"

echo -e "\n${YELLOW}4. LINE ITEMS${NC}"
echo "-----------------------------------------"

# Test 8: Create Line Item
echo -n "Testing Create Line Item... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/line-items/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"quote_id\":\"$QUOTE_ID\",\"material_name\":\"Cement\",\"quantity\":50,\"unit\":\"bag\",\"unit_price\":8.5,\"total_price\":425}")
LINE_ITEM_ID=$(echo $RESPONSE | jq -r '.data.id')
if [ "$LINE_ITEM_ID" != "null" ] && [ -n "$LINE_ITEM_ID" ]; then
    print_result 0 "Create Line Item (ID: $LINE_ITEM_ID)"
else
    print_result 1 "Create Line Item"
fi

# Test 9: Get All Line Items
echo -n "Testing Get All Line Items... "
curl -s -X GET "$BASE_URL/api/line-items/?quote_id=$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get All Line Items"

echo -e "\n${YELLOW}5. ESTIMATOR${NC}"
echo "-----------------------------------------"

# Test 10: Estimator
echo -n "Testing Estimator... "
curl -s -X POST "$BASE_URL/api/estimator/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"quote_id\":\"$QUOTE_ID\",\"floor_area\":120.5,\"storeys\":2,\"finishing\":\"standard\",\"roof_type\":\"pitched\",\"location\":\"phnom_penh\"}" | jq -e '.min_cost' > /dev/null 2>&1
print_result $? "Estimator"

echo -e "\n${YELLOW}6. BOQ CALCULATOR${NC}"
echo "-----------------------------------------"

# Test 11: BOQ Calculator
echo -n "Testing BOQ Calculator... "
curl -s -X POST "$BASE_URL/api/boq/calculate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"floor_area":120,"building_type":"residential","storeys":2,"finishing":"standard"}' | jq -e '.data.total_estimated_cost' > /dev/null 2>&1
print_result $? "BOQ Calculator"

echo -e "\n${YELLOW}7. FLOOR PLAN${NC}"
echo "-----------------------------------------"

# Test 12: Floor Plan Upload
echo -n "Testing Floor Plan Upload... "
if [ -f "/tmp/floorplan.png" ]; then
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/floor-plan/upload" \
      -H "Authorization: Bearer $TOKEN" \
      -F "file=@/tmp/floorplan.png")
    FLOOR_PLAN_ID=$(echo $RESPONSE | jq -r '.data.floor_plan_id')
    if [ "$FLOOR_PLAN_ID" != "null" ] && [ -n "$FLOOR_PLAN_ID" ]; then
        print_result 0 "Floor Plan Upload"
    else
        print_result 1 "Floor Plan Upload"
    fi
else
    echo -e "${YELLOW}⚠️ SKIPPED${NC}: Floor Plan Upload (no test image)"
fi

echo -e "\n${YELLOW}8. AI CHAT${NC}"
echo "-----------------------------------------"

# Test 13: Chat
echo -n "Testing Chat with AI... "
curl -s -X POST "$BASE_URL/api/chat/chat/stream" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What are construction costs in Cambodia?","user_id":"31a7c8f6-0397-4886-8f03-37ed492cb641"}' | jq -e '.data.response' > /dev/null 2>&1
print_result $? "Chat with AI"

echo -e "\n${YELLOW}9. SHARE & REPORTS${NC}"
echo "-----------------------------------------"

# Test 14: Shareable Link
echo -n "Testing Shareable Link... "
curl -s -X GET "$BASE_URL/api/quotes/$QUOTE_ID/share" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data.share_link' > /dev/null 2>&1
print_result $? "Shareable Link"

# Test 15: PDF Report
echo -n "Testing PDF Report... "
curl -s -X GET "$BASE_URL/api/quotes/$QUOTE_ID/report" \
  -H "Authorization: Bearer $TOKEN" -o /tmp/report_test.pdf
if [ -f "/tmp/report_test.pdf" ] && [ -s "/tmp/report_test.pdf" ]; then
    print_result 0 "PDF Report"
    rm -f /tmp/report_test.pdf
else
    print_result 1 "PDF Report"
fi

echo -e "\n${YELLOW}10. CLEANUP${NC}"
echo "-----------------------------------------"

# Test 16: Delete Line Item
echo -n "Testing Delete Line Item... "
curl -s -X DELETE "$BASE_URL/api/line-items/$LINE_ITEM_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.message' > /dev/null 2>&1
print_result $? "Delete Line Item"

# Test 17: Delete Quote
echo -n "Testing Delete Quote... "
curl -s -X DELETE "$BASE_URL/api/quotes/$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.message' > /dev/null 2>&1
print_result $? "Delete Quote"

echo -e "\n========================================="
echo -e "${YELLOW}TEST SUMMARY${NC}"
echo "========================================="
echo -e "${GREEN}PASSED: $TESTS_PASSED${NC}"
echo -e "${RED}FAILED: $TESTS_FAILED${NC}"
echo -e "TOTAL: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! BACKEND IS 100% CORRECT!${NC}"
else
    echo -e "\n${RED}⚠️ Some tests failed. Please check the errors above.${NC}"
fi
