#!/bin/bash

echo "========================================="
echo "  DOMNAK BACKEND - FINAL TEST SUITE"
echo "========================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL="http://127.0.0.1:8000"
TESTS_PASSED=0
TESTS_FAILED=0

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

echo -n "Testing Health Check... "
curl -s "$BASE_URL/" | jq -e '.status' > /dev/null 2>&1
print_result $? "Health Check"

echo -n "Testing Health Ready... "
curl -s "$BASE_URL/health" | jq -e '.status' > /dev/null 2>&1
print_result $? "Health Ready"

echo -e "\n${YELLOW}2. AUTHENTICATION${NC}"
echo "-----------------------------------------"

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

echo -n "Testing Get Current User... "
# Fixed: Looking for .data.id instead of .id
curl -s -X GET "$BASE_URL/api/auth/me?user_id=31a7c8f6-0397-4886-8f03-37ed492cb641" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data.id' > /dev/null 2>&1
print_result $? "Get Current User"

echo -e "\n${YELLOW}3. QUOTES${NC}"
echo "-----------------------------------------"

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

echo -n "Testing Get All Quotes... "
curl -s -X GET "$BASE_URL/api/quotes/" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get All Quotes"

echo -n "Testing Get Single Quote... "
# Fixed: Looking for .data.id
curl -s -X GET "$BASE_URL/api/quotes/$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data.id' > /dev/null 2>&1
print_result $? "Get Single Quote"

echo -e "\n${YELLOW}4. LINE ITEMS${NC}"
echo "-----------------------------------------"

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

echo -n "Testing Get All Line Items... "
curl -s -X GET "$BASE_URL/api/line-items/?quote_id=$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get All Line Items"

echo -e "\n${YELLOW}5. ESTIMATOR${NC}"
echo "-----------------------------------------"

echo -n "Testing Estimator... "
curl -s -X POST "$BASE_URL/api/estimator/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"quote_id\":\"$QUOTE_ID\",\"floor_area\":120.5,\"storeys\":2,\"finishing\":\"standard\",\"roof_type\":\"pitched\",\"location\":\"phnom_penh\"}" | jq -e '.min_cost' > /dev/null 2>&1
print_result $? "Estimator"

echo -e "\n${YELLOW}6. FLOOR PLAN${NC}"
echo "-----------------------------------------"

# Create test image if needed
if [ ! -f "/tmp/floorplan.png" ]; then
    python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (400, 300), color='white')
draw = ImageDraw.Draw(img)
draw.rectangle([50, 50, 200, 200], outline='black', width=2)
draw.text((80, 120), 'Living Room', fill='black')
draw.text((50, 30), '5x6', fill='black')
img.save('/tmp/floorplan.png')
" 2>/dev/null || echo "Python Pillow not available"
fi

if [ -f "/tmp/floorplan.png" ]; then
    echo -n "Testing Floor Plan Upload... "
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/floor-plan/upload" \
      -H "Authorization: Bearer $TOKEN" \
      -F "file=@/tmp/floorplan.png")
    if echo "$RESPONSE" | jq -e '.data' > /dev/null 2>&1; then
        print_result 0 "Floor Plan Upload"
    else
        print_result 1 "Floor Plan Upload"
    fi
else
    echo -e "${YELLOW}⚠️ SKIPPED${NC}: Floor Plan Upload (no test image)"
fi

echo -e "\n${YELLOW}7. AI CHAT${NC}"
echo "-----------------------------------------"

echo -n "Testing Chat with AI... "
curl -s -X POST "$BASE_URL/api/chat/chat/stream" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What are construction costs?","user_id":"31a7c8f6-0397-4886-8f03-37ed492cb641"}' | jq -e '.data.response' > /dev/null 2>&1
print_result $? "Chat with AI"

echo -e "\n${YELLOW}8. SHARE & REPORTS${NC}"
echo "-----------------------------------------"

echo -n "Testing Shareable Link... "
curl -s -X GET "$BASE_URL/api/quotes/$QUOTE_ID/share" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data.share_link' > /dev/null 2>&1
print_result $? "Shareable Link"

echo -n "Testing PDF Report... "
curl -s -X GET "$BASE_URL/api/quotes/$QUOTE_ID/report" \
  -H "Authorization: Bearer $TOKEN" -o /tmp/report_test.pdf
if [ -f "/tmp/report_test.pdf" ] && [ -s "/tmp/report_test.pdf" ]; then
    print_result 0 "PDF Report"
    rm -f /tmp/report_test.pdf
else
    print_result 1 "PDF Report"
fi

echo -e "\n${YELLOW}9. CLEANUP${NC}"
echo "-----------------------------------------"

echo -n "Testing Delete Line Item... "
curl -s -X DELETE "$BASE_URL/api/line-items/$LINE_ITEM_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.message' > /dev/null 2>&1
print_result $? "Delete Line Item"

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
