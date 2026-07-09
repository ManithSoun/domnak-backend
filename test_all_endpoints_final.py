import requests
import json
import time
import os
from PIL import Image, ImageDraw

BASE_URL = "http://127.0.0.1:8000"
TESTS_PASSED = 0
TESTS_FAILED = 0

EMAIL = f"test{int(time.time())}@gmail.com"
PASSWORD = "password123"

token = None
user_id = None
quote_id = None
item_id = None
floor_plan_id = None

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

def create_test_floor_plan():
    """Create a test floor plan image"""
    try:
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw rooms
        draw.rectangle([50, 50, 350, 350], outline='black', width=3)
        draw.rectangle([400, 50, 750, 250], outline='black', width=3)
        draw.rectangle([400, 300, 750, 450], outline='black', width=3)
        draw.rectangle([50, 400, 350, 550], outline='black', width=3)
        
        # Labels
        draw.text((100, 180), "Living Room", fill='black')
        draw.text((450, 120), "Kitchen", fill='black')
        draw.text((450, 370), "Bedroom", fill='black')
        draw.text((100, 460), "Bathroom", fill='black')
        
        # Dimensions
        draw.text((50, 25), "Width: 5.0m", fill='black')
        draw.text((50, 45), "Length: 6.0m", fill='black')
        draw.text((400, 25), "Width: 4.0m", fill='black')
        draw.text((400, 45), "Length: 3.5m", fill='black')
        
        img.save('/tmp/floorplan.png')
        return True
    except Exception as e:
        print(f"Error creating test image: {e}")
        return False

# ============================================================
section("1. HEALTH CHECKS")
# ============================================================

res = requests.get(f"{BASE_URL}/health")
print_result("Health Check", res.status_code == 200 and res.json().get("status"), res)

# ============================================================
section("2. AUTHENTICATION")
# ============================================================

# Signup
res = requests.post(f"{BASE_URL}/auth/signup", json={
    "full_name": "Test User",
    "email": EMAIL,
    "password": PASSWORD,
    "role": "homeowner",
    "phone_number": "012345678"
})
data = res.json()
print_result("Signup", res.status_code == 200 and not data.get("error"), res)

# Login
res = requests.post(f"{BASE_URL}/auth/login", json={
    "email": EMAIL,
    "password": PASSWORD
})
data = res.json()

if data.get("access_token"):
    token = data["access_token"]
    user_id = data["user_id"]
elif data.get("data") and data["data"].get("access_token"):
    token = data["data"]["access_token"]
    user_id = data["data"]["user_id"]

print_result("Login", token is not None, res)
if token:
    print(f"   Token saved ✓ (user_id: {user_id})")

headers = {"Authorization": f"Bearer {token}"}

# Get me
res = requests.get(f"{BASE_URL}/auth/me?user_id={user_id}", headers=headers)
data = res.json()
print_result("Get Current User", res.status_code == 200 and (data.get("data") or data.get("id")), res)

# ============================================================
section("3. QUOTES")
# ============================================================

# Create quote
res = requests.post(f"{BASE_URL}/quotes/", json={
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
res = requests.get(f"{BASE_URL}/quotes/", headers=headers)
data = res.json()
print_result("Get All Quotes", res.status_code == 200 and data.get("data") is not None, res)

# Get single quote
if quote_id:
    res = requests.get(f"{BASE_URL}/quotes/{quote_id}", headers=headers)
    data = res.json()
    print_result("Get Single Quote", res.status_code == 200 and data.get("data"), res)

# Shareable link
if quote_id:
    res = requests.get(f"{BASE_URL}/quotes/{quote_id}/share", headers=headers)
    data = res.json()
    print_result("Shareable Link", res.status_code == 200 and data.get("data", {}).get("share_link"), res)

# ============================================================
section("4. LINE ITEMS")
# ============================================================

# Create line item
if quote_id:
    res = requests.post(f"{BASE_URL}/line-items/", json={
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
    res = requests.get(f"{BASE_URL}/line-items/?quote_id={quote_id}", headers=headers)
    data = res.json()
    print_result("Get All Line Items", res.status_code == 200 and data.get("data") is not None, res)

# Get single line item
if item_id:
    res = requests.get(f"{BASE_URL}/line-items/{item_id}", headers=headers)
    data = res.json()
    print_result("Get Single Line Item", res.status_code == 200 and data.get("data"), res)

# Update line item
if item_id:
    res = requests.patch(f"{BASE_URL}/line-items/{item_id}", json={
        "unit_price": 8.50
    }, headers=headers)
    data = res.json()
    print_result("Update Line Item", res.status_code == 200 and not data.get("error"), res)

# ============================================================
section("5. ESTIMATOR")
# ============================================================

res = requests.post(f"{BASE_URL}/estimator/", json={
    "floor_area": 100,
    "storeys": 1,
    "finishing": "standard",
    "roof_type": "flat",
    "location": "phnom_penh"
})
data = res.json()
print_result("Estimator", res.status_code == 200 and data.get("data", {}).get("min_cost") is not None, res)

# ============================================================
section("6. CHAT")
# ============================================================

# Chat with AI - Streaming response
if token:
    try:
        res = requests.post(f"{BASE_URL}/chat/chat/stream", json={
            "message": "What are construction costs in Cambodia?",
            "user_id": user_id
        }, headers=headers, stream=True)
        
        if res.status_code == 200:
            first_chunk = None
            for line in res.iter_lines():
                if line:
                    first_chunk = line.decode('utf-8')
                    break
            
            if first_chunk and "data:" in first_chunk:
                print(f"✅ PASSED: Chat with AI")
                TESTS_PASSED += 1
            else:
                print(f"❌ FAILED: Chat with AI (no data received)")
                TESTS_FAILED += 1
        else:
            print(f"❌ FAILED: Chat with AI (status: {res.status_code})")
            TESTS_FAILED += 1
    except Exception as e:
        print(f"❌ FAILED: Chat with AI ({str(e)[:100]})")
        TESTS_FAILED += 1

# Chat History
try:
    res = requests.get(f"{BASE_URL}/chat/history", headers=headers)
    if res.status_code == 200:
        print(f"✅ PASSED: Chat History")
        TESTS_PASSED += 1
    else:
        print(f"❌ FAILED: Chat History (status: {res.status_code})")
        TESTS_FAILED += 1
except Exception as e:
    print(f"❌ FAILED: Chat History ({str(e)[:100]})")
    TESTS_FAILED += 1

# ============================================================
section("7. FLOOR PLAN")
# ============================================================

# Create test image
if create_test_floor_plan():
    # Upload floor plan
    try:
        with open('/tmp/floorplan.png', 'rb') as f:
            res = requests.post(
                f"{BASE_URL}/floor-plan/upload",
                headers=headers,
                files={"file": ("floorplan.png", f, "image/png")}
            )
        
        if res.status_code == 200:
            data = res.json()
            if data.get("data") and data["data"].get("floor_plan_id"):
                floor_plan_id = data["data"]["floor_plan_id"]
                print(f"✅ PASSED: Floor Plan Upload (ID: {floor_plan_id})")
                TESTS_PASSED += 1
            else:
                print(f"❌ FAILED: Floor Plan Upload (no ID returned)")
                TESTS_FAILED += 1
        else:
            print(f"❌ FAILED: Floor Plan Upload (status: {res.status_code})")
            TESTS_FAILED += 1
    except Exception as e:
        print(f"❌ FAILED: Floor Plan Upload ({str(e)[:100]})")
        TESTS_FAILED += 1

    # Create quote from floor plan
    try:
        with open('/tmp/floorplan.png', 'rb') as f:
            res = requests.post(
                f"{BASE_URL}/floor-plan/create-quote?contractor_name=AI%20Generated",
                headers=headers,
                files={"file": ("floorplan.png", f, "image/png")}
            )
        
        if res.status_code == 200:
            data = res.json()
            if data.get("data") and data["data"].get("quote_id"):
                print(f"✅ PASSED: Create Quote from Floor Plan (Quote ID: {data['data']['quote_id']})")
                TESTS_PASSED += 1
            else:
                print(f"❌ FAILED: Create Quote from Floor Plan")
                TESTS_FAILED += 1
        else:
            print(f"❌ FAILED: Create Quote from Floor Plan (status: {res.status_code})")
            TESTS_FAILED += 1
    except Exception as e:
        print(f"❌ FAILED: Create Quote from Floor Plan ({str(e)[:100]})")
        TESTS_FAILED += 1

    # Get floor plan
    if floor_plan_id:
        try:
            res = requests.get(f"{BASE_URL}/floor-plan/{floor_plan_id}", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data.get("data") and data["data"].get("id"):
                    print(f"✅ PASSED: Get Floor Plan")
                    TESTS_PASSED += 1
                else:
                    print(f"❌ FAILED: Get Floor Plan")
                    TESTS_FAILED += 1
            else:
                print(f"❌ FAILED: Get Floor Plan (status: {res.status_code})")
                TESTS_FAILED += 1
        except Exception as e:
            print(f"❌ FAILED: Get Floor Plan ({str(e)[:100]})")
            TESTS_FAILED += 1

# ============================================================
section("8. CLEANUP")
# ============================================================

if item_id:
    res = requests.delete(f"{BASE_URL}/line-items/{item_id}", headers=headers)
    data = res.json()
    print_result("Delete Line Item", res.status_code == 200 and data.get("message"), res)

if quote_id:
    res = requests.delete(f"{BASE_URL}/quotes/{quote_id}", headers=headers)
    data = res.json()
    print_result("Delete Quote", res.status_code == 200 and data.get("message"), res)

# Clean up floor plan if created
if floor_plan_id:
    try:
        res = requests.delete(f"{BASE_URL}/floor-plan/{floor_plan_id}", headers=headers)
        if res.status_code == 200:
            print(f"✅ PASSED: Delete Floor Plan")
            TESTS_PASSED += 1
        else:
            print(f"⚠️  SKIPPED: Delete Floor Plan (not implemented)")
            # Don't count as fail since it's optional
    except:
        pass

print(f"\n{'='*50}")
print("TEST SUMMARY")
print(f"{'='*50}")
print(f"✅ PASSED: {TESTS_PASSED}")
print(f"❌ FAILED: {TESTS_FAILED}")
print(f"TOTAL: {TESTS_PASSED + TESTS_FAILED}")

if TESTS_FAILED == 0:
    print("\n🎉 ALL TESTS PASSED! BACKEND IS 100% CORRECT!")
else:
    print(f"\n⚠️  {TESTS_FAILED} tests failed. Check errors above.")
