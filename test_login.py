#!/usr/bin/env python3
"""Test login endpoint"""
import httpx
import json

# Test data
test_users = [
    {"phone_number": "081234567890", "password": "budi15051990", "name": "Budi (User)"},
    {"phone_number": "085754538366", "password": "yunnifa12062003", "name": "Yunnifa (Superadmin)"},
]

print("=" * 60)
print("Testing Login Endpoint")
print("=" * 60)

for user in test_users:
    print(f"\n🔄 Testing: {user['name']}")
    print(f"   Phone: {user['phone_number']}")
    print(f"   Password: {user['password']}")
    
    try:
        response = httpx.post(
            "http://127.0.0.1:8001/auth/login",
            json={
                "phone_number": user["phone_number"],
                "password": user["password"]
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                user_data = data.get("payload", {}).get("user", {})
                print(f"   ✅ LOGIN BERHASIL!")
                print(f"   👤 Nama: {user_data.get('full_name')}")
                print(f"   🎭 Role: {user_data.get('role')}")
                print(f"   🔑 Token: {data.get('payload', {}).get('access_token', '')[:50]}...")
            else:
                print(f"   ❌ GAGAL: {data.get('message')}")
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            
    except httpx.ConnectError:
        print(f"   ❌ Tidak bisa connect ke server. Pastikan backend running di http://127.0.0.1:8001")
        break
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 60)
