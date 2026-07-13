import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase import supabase
from dotenv import load_dotenv
import time

load_dotenv()

def create_admin(email: str, password: str, name: str):
    try:
        # Step 1 — create auth user directly via admin API
        auth_res = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True  # skip email confirmation
        })

        if not auth_res.user:
            print("Failed to create auth user")
            return

        user_id = auth_res.user.id
        print(f"Auth user created: {user_id}")

        # Step 2 — insert into public.users with admin role
        time.sleep(1)
        supabase.table("users").insert({
            "id": user_id,
            "full_name": name,
            "role": "admin",
            "phone_number": "000000000"
        }).execute()

        print(f"Admin created successfully")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User ID: {user_id}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 scripts/make_admin.py email password name")
        print("Example: python3 scripts/make_admin.py admin@buildsafe.com Admin@2026 'BuildSafe Admin'")
        sys.exit(1)

    create_admin(sys.argv[1], sys.argv[2], sys.argv[3])