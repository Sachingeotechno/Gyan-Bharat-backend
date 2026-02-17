from app.database import engine
from sqlalchemy import text

def update_schema():
    with engine.connect() as conn:
        print("Checking for missing columns...")
        # Check if college_id exists
        try:
             # Postgres syntax to add column if not exists is tricky in one line without specialized functions,
             # but we can just try to add it and catch error if it exists, roughly.
             # Or better, just execute ALTER TABLE.
             conn.execute(text("ALTER TABLE user_profiles ADD COLUMN college_id INTEGER REFERENCES colleges(id)"))
             print("Added college_id column.")
        except Exception as e:
            print(f"college_id might already exist or error: {e}")
            
        try:
             conn.execute(text("ALTER TABLE user_profiles ADD COLUMN course_id INTEGER REFERENCES courses_kyc(id)"))
             print("Added course_id column.")
        except Exception as e:
            print(f"course_id might already exist or error: {e}")
            
        conn.commit()
        print("Schema update completed.")

if __name__ == "__main__":
    update_schema()
