from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def add_columns():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN validity_type VARCHAR(50) DEFAULT 'lifetime'"))
            print("Added validity_type column")
        except Exception as e:
            print(f"Could not add validity_type: {e}")

        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN validity_days INTEGER"))
            print("Added validity_days column")
        except Exception as e:
            print(f"Could not add validity_days: {e}")
            
        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN validity_date TIMESTAMP"))
            print("Added validity_date column")
        except Exception as e:
            print(f"Could not add validity_date: {e}")

if __name__ == "__main__":
    add_columns()
