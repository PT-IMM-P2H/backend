"""Test bcrypt dengan password yang sebenarnya"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password yang dicoba di login
test_password = "yunnifa12062003"

print(f"Testing password: '{test_password}'")
print(f"Length: {len(test_password)} characters")
print(f"Bytes: {len(test_password.encode('utf-8'))} bytes")
print()

# Test hashing
try:
    hashed = pwd_context.hash(test_password)
    print(f"✅ Hash berhasil dibuat:")
    print(f"   {hashed[:60]}...")
    print()
    
    # Test verifikasi
    result = pwd_context.verify(test_password, hashed)
    print(f"✅ Verifikasi: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
