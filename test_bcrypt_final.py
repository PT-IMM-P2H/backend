"""Quick test bcrypt after reinstall"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

test_password = "yunnifa12062003"

print(f"Testing password: '{test_password}'")
print(f"Passlib + Bcrypt test...")

try:
    # Test hash
    hashed = pwd_context.hash(test_password)
    print(f"✅ Hash success: {hashed[:60]}...")
    
    # Test verify
    result = pwd_context.verify(test_password, hashed)
    print(f"✅ Verify success: {result}")
    
    if result:
        print("\n🎉 BCRYPT WORKING PERFECTLY!")
    else:
        print("\n❌ Verify failed")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
