import requests
import json
import time
import random

BASE_URL = "http://127.0.0.1:8000"
TESTS_PASSED = 0
TESTS_FAILED = 0

# Generate unique email for each test run
EMAIL = f"testscript{int(time.time())}@gmail.com"
PASSWORD = "password123"

token = None
user_id = None
quote_id = None
item_id = None
supplier_id = None

def print_result(name, passed, response=None):
    global TESTS_PASSED, TESTS_FAILED
    if passed:
        print(f"✅ PASSED: {name}")
        TESTS_PASSED += 1
    else:
        print(f"❌ FAILED: {name}")
        TESTS_FAILED += 1
        if response:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data)[:200]}")
            except:
                print(f"   Response: {response.text[:200]}")

def section(title):
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")

# ============================================================
section("1. HEALTH CHECKS")
# ============================================================

res = requests.get(f"{BASE_URL}/")
print_result("Root", res.status_code == 200 and res.json().get("status"), res)

res = requests.get(f"{BASE_URL}/health")
print_result("Health Check", res.status_code == 200 and res.json().get("status"), res)

res = requests.get(f"{BASE_URL}/health/ready")
print_result("Health Ready", res.status_code == 200 and res.json().get("status"), res)

# ============================================================
section("2. AUTHENTICATION")
# ============================================================

# Signup
res = requests.post(f"{BASE_URL}/api/v1/auth/signup", json={
    "full_name": "Test User",
    "email": EMAIL,
    "password": PASSWORD,
    "role": "homeowner",
    "phone_number": "012345678"
})
data = res.json()
print_result("Signup", res.status_code == 200 and not data.get("error"), res)

# Login
res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": EMAIL,
    "password": PASSWORD
})
data = res.json()

# Handle both flat and nested response
if data.get("access_token"):
    token = data["access_token"]
    user_id = data["user_id"]
elif data.get("data") and data["data"].get("access_token"):
    token = data["data"]["access_token"]
    user_id = data["data"]["user_id"]

print_result("Login", token is not None, res)
if token:
    print(f"   Token saved ✓ (user_id: {user_id})")

headers = {"authorization": f"Bearer {token}"}

# Get me
res = requests.get(f"{BASE_URL}/api/v1/auth/me?user_id={user_id}")
data = res.json()
print_result("Get Current User", res.status_code == 200 and (data.get("data") or data.get("id")), res)

# ============================================================
section("3. QUOTES")
# ============================================================

# Create quote
res = requests.post(f"{BASE_URL}/api/v1/quotes/", json={
    "contractor_name": "Sokha Construction",
    "total_amount": 42000
}, headers=headers)
data = res.json()

if data.get("data"):
    d = data["data"]
    if isinstance(d, list) and len(d) > 0:
        quote_id = d[0]["id"]
    elif isinstance(d, dict):
        quote_id = d.get("id")

print_result("Create Quote", quote_id is not None, res)
if quote_id:
    print(f"   Quote ID: {quote_id}")

# Get all quotes
res = requests.get(f"{BASE_URL}/api/v1/quotes/", headers=headers)
data = res.json()
print_result("Get All Quotes", res.status_code == 200 and data.get("data") is not None, res)

# Get single quote
if quote_id:
    res = requests.get(f"{BASE_URL}/api/v1/quotes/{quote_id}", headers=headers)
    data = res.json()
    print_result("Get Single Quote", res.status_code == 200 and data.get("data"), res)

# Update quote
if quote_id:
    res = requests.patch(f"{BASE_URL}/api/v1/quotes/{quote_id}", json={
        "contractor_name": "Updated Construction"
    }, headers=headers)
    data = res.json()
    print_result("Update Quote", res.status_code == 200 and not data.get("error"), res)

# Shareable link
if quote_id:
    res = requests.get(f"{BASE_URL}/api/v1/quotes/{quote_id}/share", headers=headers)
    data = res.json()
    print_result("Shareable Link", res.status_code == 200 and data.get("data", {}).get("share_link"), res)

# ============================================================
section("4. LINE ITEMS")
# ============================================================

# Create line item
if quote_id:
    res = requests.post(f"{BASE_URL}/api/v1/line-items/", json={
        "quote_id": quote_id,
        "material_name": "Cement",
        "quantity": 150,
        "unit": "bag",
        "unit_price": 9.50
    }, headers=headers)
    data = res.json()

    if data.get("data"):
        d = data["data"]
        if isinstance(d, list) and len(d) > 0:
            item_id = d[0]["id"]
        elif isinstance(d, dict):
            item_id = d.get("id")

    print_result("Create Line Item", item_id is not None, res)
    if item_id:
        print(f"   Item ID: {item_id}")

# Get line items
if quote_id:
    res = requests.get(f"{BASE_URL}/api/v1/line-items/?quote_id={quote_id}", headers=headers)
    data = res.json()
    print_result("Get All Line Items", res.status_code == 200 and data.get("data") is not None, res)

# Get single line item
if item_id:
    res = requests.get(f"{BASE_URL}/api/v1/line-items/{item_id}", headers=headers)
    data = res.json()
    print_result("Get Single Line Item", res.status_code == 200 and data.get("data"), res)

# Update line item
if item_id:
    res = requests.patch(f"{BASE_URL}/api/v1/line-items/{item_id}", json={
        "unit_price": 8.50
    }, headers=headers)
    data = res.json()
    print_result("Update Line Item", res.status_code == 200 and not data.get("error"), res)

# ============================================================
section("5. ESTIMATOR")
# ============================================================

res = requests.post(f"{BASE_URL}/api/v1/estimator/", json={
    "floor_area": 100,
    "storeys": 1,
    "finishing": "standard",
    "roof_type": "flat",
    "location": "phnom_penh"
})
data = res.json()
print_result("Estimator", res.status_code == 200 and data.get("data", {}).get("min_cost") is not None, res)

# ============================================================
section("6. SUPPLIERS")
# ============================================================

res = requests.get(f"{BASE_URL}/api/v1/suppliers/")
data = res.json()
print_result("Get All Suppliers", res.status_code == 200 and data.get("data") is not None, res)

if data.get("data") and len(data["data"]) > 0:
    supplier_id = data["data"][0]["id"]

res = requests.get(f"{BASE_URL}/api/v1/suppliers/Cement")
data = res.json()
print_result("Get Suppliers by Material", res.status_code == 200 and data.get("data") is not None, res)

if supplier_id:
    res = requests.post(f"{BASE_URL}/api/v1/suppliers/{supplier_id}/click", headers=headers)
    data = res.json()
    print_result("Track Supplier Click", res.status_code == 200 and data.get("message"), res)

# ============================================================
section("7. ANALYSIS")
# ============================================================

if quote_id:
    res = requests.post(f"{BASE_URL}/api/v1/analysis/{quote_id}", headers=headers)
    data = res.json()
    print_result("Analyze Quote", res.status_code == 200 and not data.get("error"), res)

    res = requests.get(f"{BASE_URL}/api/v1/analysis/{quote_id}", headers=headers)
    data = res.json()
    print_result("Get Analysis", res.status_code == 200 and data.get("data") is not None, res)

# ============================================================
section("8. CLEANUP")
# ============================================================

if item_id:
    res = requests.delete(f"{BASE_URL}/api/v1/line-items/{item_id}", headers=headers)
    data = res.json()
    print_result("Delete Line Item", res.status_code == 200 and data.get("message"), res)

if quote_id:
    res = requests.delete(f"{BASE_URL}/api/v1/quotes/{quote_id}", headers=headers)
    data = res.json()
    print_result("Delete Quote", res.status_code == 200 and data.get("message"), res)

# ============================================================
print(f"\n{'='*50}")
print("TEST SUMMARY")
print(f"{'='*50}")
print(f"✅ PASSED: {TESTS_PASSED}")
print(f"❌ FAILED: {TESTS_FAILED}")
print(f"TOTAL: {TESTS_PASSED + TESTS_FAILED}")

if TESTS_FAILED == 0:
    print("\n🎉 ALL TESTS PASSED!")
else:
    print(f"\n⚠️  {TESTS_FAILED} tests failed. Check errors above.")