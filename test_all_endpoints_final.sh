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

echo -n "Testing Root... "
curl -s "$BASE_URL/" | jq -e '.status' > /dev/null 2>&1
print_result $? "Root"

echo -n "Testing Health Check... "
curl -s "$BASE_URL/health" | jq -e '.status' > /dev/null 2>&1
print_result $? "Health Check"

echo -n "Testing Health Ready... "
curl -s "$BASE_URL/health/ready" | jq -e '.status' > /dev/null 2>&1
print_result $? "Health Ready"

echo -e "\n${YELLOW}2. AUTHENTICATION${NC}"
echo "-----------------------------------------"

# Signup first
EMAIL="testscript$(date +%s)@gmail.com"

echo -n "Testing Signup... "
curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"full_name\":\"Test User\",\"email\":\"$EMAIL\",\"password\":\"password123\",\"role\":\"homeowner\",\"phone_number\":\"012345678\"}" | jq -e '.data' > /dev/null 2>&1
print_result $? "Signup"

# Login
echo -n "Testing Login... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"password123\"}")
TOKEN=$(echo $RESPONSE | jq -r '.access_token // .data.access_token')
USER_ID=$(echo $RESPONSE | jq -r '.user_id // .data.user_id')
if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    print_result 0 "Login (Token received)"
else
    print_result 1 "Login"
    echo "Response: $RESPONSE"
fi

# Get me
echo -n "Testing Get Current User... "
curl -s -X GET "$BASE_URL/api/v1/auth/me?user_id=$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data.id' > /dev/null 2>&1
print_result $? "Get Current User"

echo -e "\n${YELLOW}3. QUOTES${NC}"
echo "-----------------------------------------"

# Create quote
echo -n "Testing Create Quote... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/quotes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contractor_name":"ABC Construction","total_amount":15000.5}')
QUOTE_ID=$(echo $RESPONSE | jq -r '.data[0].id // .data.id')
if [ "$QUOTE_ID" != "null" ] && [ -n "$QUOTE_ID" ]; then
    print_result 0 "Create Quote (ID: $QUOTE_ID)"
else
    print_result 1 "Create Quote"
    echo "Response: $RESPONSE"
fi

# Get all quotes
echo -n "Testing Get All Quotes... "
curl -s -X GET "$BASE_URL/api/v1/quotes/" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get All Quotes"

# Get single quote
echo -n "Testing Get Single Quote... "
curl -s -X GET "$BASE_URL/api/v1/quotes/$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data.id' > /dev/null 2>&1
print_result $? "Get Single Quote"

# Update quote
echo -n "Testing Update Quote... "
curl -s -X PATCH "$BASE_URL/api/v1/quotes/$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"contractor_name":"Updated Construction"}' | jq -e '.data' > /dev/null 2>&1
print_result $? "Update Quote"

# Shareable link
echo -n "Testing Shareable Link... "
curl -s -X GET "$BASE_URL/api/v1/quotes/$QUOTE_ID/share" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data.share_link' > /dev/null 2>&1
print_result $? "Shareable Link"

echo -e "\n${YELLOW}4. LINE ITEMS${NC}"
echo "-----------------------------------------"

# Create line item
echo -n "Testing Create Line Item... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/line-items/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"quote_id\":\"$QUOTE_ID\",\"material_name\":\"Cement\",\"quantity\":50,\"unit\":\"bag\",\"unit_price\":8.5}")
LINE_ITEM_ID=$(echo $RESPONSE | jq -r '.data[0].id // .data.id')
if [ "$LINE_ITEM_ID" != "null" ] && [ -n "$LINE_ITEM_ID" ]; then
    print_result 0 "Create Line Item (ID: $LINE_ITEM_ID)"
else
    print_result 1 "Create Line Item"
    echo "Response: $RESPONSE"
fi

# Get line items
echo -n "Testing Get All Line Items... "
curl -s -X GET "$BASE_URL/api/v1/line-items/?quote_id=$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get All Line Items"

# Update line item
echo -n "Testing Update Line Item... "
curl -s -X PATCH "$BASE_URL/api/v1/line-items/$LINE_ITEM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"unit_price":7.50}' | jq -e '.data' > /dev/null 2>&1
print_result $? "Update Line Item"

echo -e "\n${YELLOW}5. ESTIMATOR${NC}"
echo "-----------------------------------------"

echo -n "Testing Estimator... "
curl -s -X POST "$BASE_URL/api/v1/estimator/" \
  -H "Content-Type: application/json" \
  -d '{"floor_area":120,"storeys":1,"finishing":"standard","roof_type":"flat","location":"phnom_penh"}' | jq -e '.data.min_cost' > /dev/null 2>&1
print_result $? "Estimator"

echo -e "\n${YELLOW}6. SUPPLIERS${NC}"
echo "-----------------------------------------"

echo -n "Testing Get All Suppliers... "
RESPONSE=$(curl -s "$BASE_URL/api/v1/suppliers/")
SUPPLIER_ID=$(echo $RESPONSE | jq -r '.data[0].id')
curl -s "$BASE_URL/api/v1/suppliers/" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get All Suppliers"

echo -n "Testing Get Suppliers by Material... "
curl -s "$BASE_URL/api/v1/suppliers/Cement" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get Suppliers by Material"

echo -n "Testing Track Click... "
curl -s -X POST "$BASE_URL/api/v1/suppliers/$SUPPLIER_ID/click" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.message' > /dev/null 2>&1
print_result $? "Track Supplier Click"

echo -e "\n${YELLOW}7. ANALYSIS${NC}"
echo "-----------------------------------------"

echo -n "Testing Analyze Quote... "
curl -s -X POST "$BASE_URL/api/v1/analysis/$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data' > /dev/null 2>&1
print_result $? "Analyze Quote"

echo -n "Testing Get Analysis... "
curl -s -X GET "$BASE_URL/api/v1/analysis/$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.data' > /dev/null 2>&1
print_result $? "Get Analysis"

echo -e "\n${YELLOW}8. CLEANUP${NC}"
echo "-----------------------------------------"

echo -n "Testing Delete Line Item... "
curl -s -X DELETE "$BASE_URL/api/v1/line-items/$LINE_ITEM_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.message' > /dev/null 2>&1
print_result $? "Delete Line Item"

echo -n "Testing Delete Quote... "
curl -s -X DELETE "$BASE_URL/api/v1/quotes/$QUOTE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -e '.message' > /dev/null 2>&1
print_result $? "Delete Quote"

echo -e "\n========================================="
echo -e "${YELLOW}TEST SUMMARY${NC}"
echo "========================================="
echo -e "${GREEN}PASSED: $TESTS_PASSED${NC}"
echo -e "${RED}FAILED: $TESTS_FAILED${NC}"
echo -e "TOTAL: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
else
    echo -e "\n${RED}⚠️ Some tests failed. Check errors above.${NC}"
fi