from fastapi.testclient import TestClient
from main import app
import sys

client = TestClient(app)

def get_auth_token():
    # Helper to get auth token
    email = "instructor@example.com"
    password = "Password123"
    
    # Register/Login
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    if response.status_code == 401:
        # Register if not exists
        client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "Instructor"})
        response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    
    if response.status_code != 200:
        print(f"Auth failed: {response.text}")
        sys.exit(1)
        
    return response.json()["access_token"]

def verify_courses():
    print("Testing Course Management APIs...")
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Course
    print("\n1. Creating Course...")
    course_data = {
        "title": "Python for Beginners",
        "description": "Learn Python from scratch",
        "price": 49.99,
        "level": "beginner",
        "is_published": True
    }
    response = client.post("/api/v1/courses/", json=course_data, headers=headers)
    if response.status_code != 201:
        print(f"Create course failed: {response.text}")
        sys.exit(1)
    
    course = response.json()
    course_id = course["id"]
    print(f"Course created: {course['title']} (ID: {course_id})")
    
    # 2. Add Lesson
    print("\n2. Adding Lesson...")
    lesson_data = {
        "title": "Introduction to Variables",
        "description": "Understanding variables in Python",
        "duration": 600,
        "order": 1
    }
    response = client.post(f"/api/v1/courses/{course_id}/lessons", json=lesson_data, headers=headers)
    if response.status_code != 201:
        print(f"Add lesson failed: {response.text}")
        sys.exit(1)
        
    lesson = response.json()
    lesson_id = lesson["id"]
    print(f"Lesson added: {lesson['title']} (ID: {lesson_id})")
    
    # 3. Get Course Details
    print("\n3. Getting Course Details...")
    response = client.get(f"/api/v1/courses/{course_id}")
    if response.status_code != 200:
        print(f"Get course failed: {response.text}")
        sys.exit(1)
        
    data = response.json()
    lessons = data.get("lessons", [])
    if len(lessons) != 1:
        print(f"Error: Expected 1 lesson, found {len(lessons)}")
        sys.exit(1)
    print("Course details retrieved successfully.")
    
    # 4. List Courses
    print("\n4. Listing Courses...")
    response = client.get("/api/v1/courses/")
    if response.status_code != 200:
        print(f"List courses failed: {response.text}")
        sys.exit(1)
    
    courses = response.json()
    if not any(c["id"] == course_id for c in courses):
        print("Error: Created course not found in list")
        sys.exit(1)
    print(f"Found {len(courses)} courses.")
    
    # 5. Update Course
    print("\n5. Updating Course...")
    update_data = {"price": 59.99}
    response = client.put(f"/api/v1/courses/{course_id}", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"Update course failed: {response.text}")
        sys.exit(1)
    if response.json()["price"] != 59.99:
        print("Error: Price not updated")
        sys.exit(1)
    print("Course updated successfully.")
    
    # Cleanup (Optional)
    # client.delete(f"/api/v1/courses/{course_id}", headers=headers)

    print("\nCourse Management Verification Completed Successfully!")

if __name__ == "__main__":
    verify_courses()
