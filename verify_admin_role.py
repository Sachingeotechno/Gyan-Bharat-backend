import requests

base_url = "http://localhost:8000/api/v1"
email = "admin@example.com"
password = "password"

# Login
response = requests.post(f"{base_url}/auth/login", json={"email": email, "password": password})
if response.status_code != 200:
    print(f"Login failed: {response.text}")
    exit(1)

token = response.json()["access_token"]
print("Login successful")

# Get Me
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{base_url}/auth/me", headers=headers)
if response.status_code != 200:
    print(f"Get Me failed: {response.text}")
    exit(1)

user_info = response.json()
print("User Info:", user_info)
print("Role:", user_info.get("role"))
print("Type of Rol:", type(user_info.get("role")))
