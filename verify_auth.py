from fastapi.testclient import TestClient
from main import app
from app.database import Base, engine
import sys

# Re-create tables for clean state (optional, but good for testing)
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_auth_flow():
    print("Testing Authentication Flow...")
    
    # 1. Register
    print("\n1. Testing Registration...")
    email = "testuser@example.com"
    password = "Password123"
    
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        }
    )
    
    if response.status_code == 400 and "already registered" in response.text:
         print("User already registered, proceeding to login.")
    elif response.status_code != 201:
        print(f"Registration failed: {response.text}")
        sys.exit(1)
    else:
        print("Registration successful!")
        data = response.json()
        assert data["email"] == email

    # 2. Login
    print("\n2. Testing Login...")
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)
        
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    print("Login successful! Got tokens.")
    
    # 3. Get Current User (Protected Route)
    print("\n3. Testing Protected Route (/auth/me)...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    
    if response.status_code != 200:
        print(f"Protected route access failed: {response.text}")
        sys.exit(1)
        
    user_data = response.json()
    print(f"Protected route accessed! User: {user_data['email']}")
    
    # 4. Refresh Token
    print("\n4. Testing Token Refresh...")
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    if response.status_code != 200:
        print(f"Refresh failed: {response.text}")
        sys.exit(1)
        
    new_tokens = response.json()
    print("Token refresh successful!")
    
    print("\nAuthentication Flow Verification Completed Successfully!")

if __name__ == "__main__":
    test_auth_flow()
