import requests

url = "http://localhost:8000/api/v1/auth/register"
data = {
    "email": "user@example.com",
    "password": "password",
    "full_name": "Test User"
}

try:
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print("User created successfully")
    elif response.status_code == 400 and "already registered" in response.text:
        print("User already exists")
    else:
        print(f"Failed to create user: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error: {e}")
