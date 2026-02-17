from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def add_columns():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE enrollments ADD COLUMN expires_at TIMESTAMP"))
            print("Added expires_at column")
        except Exception as e:
            print(f"Could not add expires_at: {e}")

if __name__ == "__main__":
    add_columns()
