from fastapi.testclient import TestClient
from main import app
import sys

client = TestClient(app)

def get_tokens(email, password, name):
    # Register/Login helper
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    if response.status_code == 401:
        client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": name})
        response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    
    if response.status_code != 200:
        print(f"Auth failed for {email}: {response.text}")
        sys.exit(1)
    return response.json()["access_token"]

def verify_enrollments():
    print("Testing Enrollment APIs...")
    
    # 1. Setup: Create Instructor & Course
    print("\n1. Setup: Creating Instructor & Course...")
    instructor_token = get_tokens("prof@example.com", "Pass1234", "Professor X")
    instr_headers = {"Authorization": f"Bearer {instructor_token}"}
    
    course_data = {
        "title": "Advanced Python",
        "price": 99.99,
        "is_published": True
    }
    response = client.post("/api/v1/courses/", json=course_data, headers=instr_headers)
    course_id = response.json()["id"]
    print(f"Course created: {course_id}")
    
    # 2. Setup: Student Token
    print("\n2. Setup: Getting Student Token...")
    student_token = get_tokens("student@example.com", "Pass1234", "Student Y")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # 3. Enroll
    print("\n3. Enrolling in Course...")
    enroll_data = {"course_id": course_id}
    response = client.post("/api/v1/enrollments/", json=enroll_data, headers=student_headers)
    if response.status_code != 201:
        print(f"Enrollment failed: {response.text}")
        sys.exit(1)
        
    enrollment = response.json()
    enrollment_id = enrollment["id"]
    print(f"Enrolled successfully! ID: {enrollment_id}, Progress: {enrollment['progress']}%")
    
    # 4. Get My Enrollments
    print("\n4. Getting My Enrollments...")
    response = client.get("/api/v1/enrollments/", headers=student_headers)
    enrollments = response.json()
    if not any(e["id"] == enrollment_id for e in enrollments):
        print("Error: Enrollment not found in list")
        sys.exit(1)
    print(f"Found {len(enrollments)} enrollments.")
    
    # 5. Update Progress
    print("\n5. Updating Progress...")
    progress_data = {"progress": 50.0}
    response = client.patch(f"/api/v1/enrollments/{enrollment_id}/progress", json=progress_data, headers=student_headers)
    if response.status_code != 200:
        print(f"Update progress failed: {response.text}")
        sys.exit(1)
    
    updated = response.json()
    if updated["progress"] != 50.0:
        print(f"Error: Progress not updated. Got {updated['progress']}")
        sys.exit(1)
    print(f"Progress updated to {updated['progress']}%")
    
    # 6. Complete Course
    print("\n6. Completing Course...")
    progress_data = {"progress": 100.0}
    response = client.patch(f"/api/v1/enrollments/{enrollment_id}/progress", json=progress_data, headers=student_headers)
    completed = response.json()
    
    if not completed["is_completed"]:
        print("Error: Course not marked as completed")
        sys.exit(1)
    print("Course marked as completed!")

    print("\nEnrollment Verification Completed Successfully!")

if __name__ == "__main__":
    verify_enrollments()
