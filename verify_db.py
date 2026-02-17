from app.database import Base, engine
from app.models import User, Course, Lesson, Enrollment
import sys

def init_db():
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        
        # Verify tables (basic check)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables found: {tables}")
        
        required_tables = {"users", "user_profiles", "user_sessions", "courses", "lessons", "enrollments"}
        missing = required_tables - set(tables)
        
        if missing:
            print(f"Error: Missing tables: {missing}")
            sys.exit(1)
        else:
            print("All required tables are present.")
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
